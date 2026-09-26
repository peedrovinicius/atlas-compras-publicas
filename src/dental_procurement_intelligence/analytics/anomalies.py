from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb


@dataclass(frozen=True, slots=True)
class PriceSignalBuildResult:
    eligible_row_count: int
    signal_count: int
    comparison_group_count: int
    minimum_group_size: int
    modified_z_threshold: float
    iqr_multiplier: float
    database_path: str


def _validate_parameters(
    minimum_group_size: int,
    modified_z_threshold: float,
    iqr_multiplier: float,
) -> None:
    if minimum_group_size < 3:
        raise ValueError("minimum_group_size deve ser pelo menos 3")
    if modified_z_threshold <= 0:
        raise ValueError("modified_z_threshold deve ser positivo")
    if iqr_multiplier <= 0:
        raise ValueError("iqr_multiplier deve ser positivo")


def build_price_signals(
    database_path: str | Path,
    *,
    minimum_group_size: int = 5,
    modified_z_threshold: float = 3.5,
    iqr_multiplier: float = 1.5,
) -> PriceSignalBuildResult:
    """Cria sinais robustos de preço sobre resultados homologados comparáveis."""

    _validate_parameters(
        minimum_group_size,
        modified_z_threshold,
        iqr_multiplier,
    )
    database = Path(database_path)

    with duckdb.connect(str(database)) as connection:
        table_exists = connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'silver_awards'
            """
        ).fetchone()[0]

        if not table_exists:
            raise ValueError(
                "A tabela silver_awards não existe. Execute build-awards primeiro."
            )

        connection.execute("DROP VIEW IF EXISTS price_anomalies")
        connection.execute("DROP TABLE IF EXISTS gold_price_signals")
        connection.execute(
            f"""
            CREATE TABLE gold_price_signals AS
            WITH eligible AS (
                SELECT
                    *,
                    CONCAT(
                        product_category, '|',
                        COALESCE(presentation, '∅'), '|',
                        COALESCE(shade, '∅'), '|',
                        normalized_quantity_unit, '|',
                        CAST(normalized_quantity_value AS VARCHAR)
                    ) AS comparison_key
                FROM silver_awards
                WHERE product_category <> 'unknown'
                  AND presentation IS NOT NULL
                  AND normalized_quantity_value IS NOT NULL
                  AND normalized_quantity_unit IS NOT NULL
                  AND awarded_price_per_base_unit IS NOT NULL
                  AND awarded_price_per_base_unit > 0
            ),
            group_stats AS (
                SELECT
                    comparison_key,
                    COUNT(*) AS group_size,
                    MEDIAN(awarded_price_per_base_unit) AS median_price,
                    QUANTILE_CONT(awarded_price_per_base_unit, 0.25) AS q1_price,
                    QUANTILE_CONT(awarded_price_per_base_unit, 0.75) AS q3_price
                FROM eligible
                GROUP BY comparison_key
            ),
            with_stats AS (
                SELECT
                    eligible.*,
                    group_stats.group_size,
                    group_stats.median_price,
                    group_stats.q1_price,
                    group_stats.q3_price,
                    group_stats.q3_price - group_stats.q1_price AS iqr_price
                FROM eligible
                JOIN group_stats USING (comparison_key)
            ),
            mad_stats AS (
                SELECT
                    comparison_key,
                    MEDIAN(
                        ABS(awarded_price_per_base_unit - median_price)
                    ) AS mad_price
                FROM with_stats
                GROUP BY comparison_key
            )
            SELECT
                with_stats.*,
                mad_stats.mad_price,
                CASE
                    WHEN mad_stats.mad_price > 0
                    THEN
                        0.6744897501960817
                        * (awarded_price_per_base_unit - median_price)
                        / mad_stats.mad_price
                    ELSE NULL
                END AS modified_z_score,
                CASE
                    WHEN group_size < {minimum_group_size} THEN 'insufficient_sample'
                    WHEN mad_stats.mad_price > 0 THEN 'modified_z_score'
                    WHEN iqr_price > 0 THEN 'iqr_fallback'
                    ELSE 'insufficient_variation'
                END AS detection_method,
                CASE
                    WHEN group_size < {minimum_group_size} THEN FALSE
                    WHEN mad_stats.mad_price > 0 THEN
                        ABS(
                            0.6744897501960817
                            * (awarded_price_per_base_unit - median_price)
                            / mad_stats.mad_price
                        ) >= {modified_z_threshold}
                    WHEN iqr_price > 0 THEN
                        awarded_price_per_base_unit
                            < q1_price - ({iqr_multiplier} * iqr_price)
                        OR awarded_price_per_base_unit
                            > q3_price + ({iqr_multiplier} * iqr_price)
                    ELSE FALSE
                END AS is_price_signal
            FROM with_stats
            JOIN mad_stats USING (comparison_key)
            """
        )
        connection.execute(
            """
            CREATE VIEW price_anomalies AS
            SELECT *
            FROM gold_price_signals
            WHERE is_price_signal
            ORDER BY
                ABS(COALESCE(modified_z_score, 0)) DESC,
                awarded_price_per_base_unit DESC
            """
        )

        eligible_row_count = connection.execute(
            "SELECT COUNT(*) FROM gold_price_signals"
        ).fetchone()[0]
        signal_count = connection.execute(
            "SELECT COUNT(*) FROM price_anomalies"
        ).fetchone()[0]
        comparison_group_count = connection.execute(
            "SELECT COUNT(DISTINCT comparison_key) FROM gold_price_signals"
        ).fetchone()[0]

    return PriceSignalBuildResult(
        eligible_row_count=eligible_row_count,
        signal_count=signal_count,
        comparison_group_count=comparison_group_count,
        minimum_group_size=minimum_group_size,
        modified_z_threshold=modified_z_threshold,
        iqr_multiplier=iqr_multiplier,
        database_path=database.as_posix(),
    )


def anomaly_summary(database_path: str | Path) -> list[dict[str, Any]]:
    with duckdb.connect(str(database_path), read_only=True) as connection:
        cursor = connection.execute(
            """
            SELECT
                product_category,
                COUNT(*) AS signal_count,
                COUNT(DISTINCT comparison_key) AS affected_groups,
                MEDIAN(awarded_price_per_base_unit) AS median_signaled_price,
                MAX(ABS(modified_z_score)) AS max_abs_modified_z
            FROM price_anomalies
            GROUP BY product_category
            ORDER BY signal_count DESC, product_category
            """
        )
        columns = [column[0] for column in cursor.description]
        return [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]
