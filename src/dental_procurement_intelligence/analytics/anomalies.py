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
    """Gera sinais com contexto temporal, geográfico e técnico."""

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
                "A tabela silver_awards não existe. Execute build-award-dataset primeiro."
            )

        column_types = {
            row[1]: str(row[2]).upper()
            for row in connection.execute(
                "PRAGMA table_info('silver_awards')"
            ).fetchall()
        }
        columns = set(column_types)
        required_columns = {
            "package_count",
            "measurement_candidate_count",
            "measurement_resolution",
            "unit_quantity_value",
            "unit_quantity_unit",
            "price_normalization_status",
        }
        missing_columns = sorted(required_columns - columns)
        if missing_columns:
            raise ValueError(
                "silver_awards precisa ser reconstruída com a versão atual. "
                f"Campos ausentes: {', '.join(missing_columns)}"
            )

        price_type = column_types.get("awarded_price_per_base_unit", "")
        if not price_type.startswith("DECIMAL("):
            raise ValueError(
                "silver_awards precisa ser reconstruída com precisão decimal. "
                "awarded_price_per_base_unit deve ser DECIMAL."
            )

        connection.execute("DROP VIEW IF EXISTS price_anomalies")
        connection.execute("DROP VIEW IF EXISTS anomaly_scope_summary")
        connection.execute("DROP TABLE IF EXISTS gold_price_signals")

        connection.execute(
            f"""
            CREATE TABLE gold_price_signals AS
            WITH eligible AS (
                SELECT
                    ROW_NUMBER() OVER () AS analysis_row_id,
                    *,
                    CONCAT(
                        product_category, '|',
                        COALESCE(presentation, '∅'), '|',
                        COALESCE(shade, '∅'), '|',
                        COALESCE(CAST(concentration_percent AS VARCHAR), '∅'), '|',
                        COALESCE(CAST(package_count AS VARCHAR), '∅'), '|',
                        COALESCE(unit_quantity_unit, '∅'), '|',
                        COALESCE(CAST(unit_quantity_value AS VARCHAR), '∅'), '|',
                        normalized_quantity_unit, '|',
                        CAST(normalized_quantity_value AS VARCHAR)
                    ) AS product_key
                FROM silver_awards
                WHERE product_category <> 'unknown'
                  AND presentation IS NOT NULL
                  AND normalized_quantity_value IS NOT NULL
                  AND normalized_quantity_unit IS NOT NULL
                  AND awarded_price_per_base_unit IS NOT NULL
                  AND awarded_price_per_base_unit > 0
                  AND price_normalization_status = 'defensible'
                  AND measurement_resolution IN (
                      'single',
                      'package_derived',
                      'package_total_confirmed'
                  )
                  AND analysis_year IS NOT NULL
            ),
            scope_rows AS (
                SELECT
                    *,
                    1 AS scope_priority,
                    'uf_trimestre' AS comparison_scope,
                    state_code AS comparison_geography,
                    analysis_quarter AS comparison_period,
                    CONCAT(product_key, '|UF|', state_code, '|', analysis_quarter)
                        AS scope_group_key
                FROM eligible
                WHERE state_code IS NOT NULL AND analysis_quarter IS NOT NULL

                UNION ALL

                SELECT
                    *,
                    2 AS scope_priority,
                    'regiao_trimestre' AS comparison_scope,
                    macroregion AS comparison_geography,
                    analysis_quarter AS comparison_period,
                    CONCAT(
                        product_key, '|REGIAO|', macroregion, '|', analysis_quarter
                    ) AS scope_group_key
                FROM eligible
                WHERE macroregion IS NOT NULL AND analysis_quarter IS NOT NULL

                UNION ALL

                SELECT
                    *,
                    3 AS scope_priority,
                    'brasil_trimestre' AS comparison_scope,
                    'Brasil' AS comparison_geography,
                    analysis_quarter AS comparison_period,
                    CONCAT(product_key, '|BR|', analysis_quarter) AS scope_group_key
                FROM eligible
                WHERE analysis_quarter IS NOT NULL

                UNION ALL

                SELECT
                    *,
                    4 AS scope_priority,
                    'regiao_ano' AS comparison_scope,
                    macroregion AS comparison_geography,
                    CAST(analysis_year AS VARCHAR) AS comparison_period,
                    CONCAT(
                        product_key, '|REGIAO|', macroregion, '|',
                        CAST(analysis_year AS VARCHAR)
                    ) AS scope_group_key
                FROM eligible
                WHERE macroregion IS NOT NULL

                UNION ALL

                SELECT
                    *,
                    5 AS scope_priority,
                    'brasil_ano' AS comparison_scope,
                    'Brasil' AS comparison_geography,
                    CAST(analysis_year AS VARCHAR) AS comparison_period,
                    CONCAT(
                        product_key, '|BR|', CAST(analysis_year AS VARCHAR)
                    ) AS scope_group_key
                FROM eligible
            ),
            group_stats AS (
                SELECT
                    scope_group_key,
                    COUNT(*) AS group_size,
                    MEDIAN(awarded_price_per_base_unit) AS median_price,
                    QUANTILE_CONT(awarded_price_per_base_unit, 0.25) AS q1_price,
                    QUANTILE_CONT(awarded_price_per_base_unit, 0.75) AS q3_price
                FROM scope_rows
                GROUP BY scope_group_key
            ),
            with_stats AS (
                SELECT
                    scope_rows.*,
                    group_stats.group_size,
                    group_stats.median_price,
                    group_stats.q1_price,
                    group_stats.q3_price,
                    group_stats.q3_price - group_stats.q1_price AS iqr_price
                FROM scope_rows
                JOIN group_stats USING (scope_group_key)
            ),
            mad_stats AS (
                SELECT
                    scope_group_key,
                    MEDIAN(
                        ABS(awarded_price_per_base_unit - median_price)
                    ) AS mad_price
                FROM with_stats
                GROUP BY scope_group_key
            ),
            ranked AS (
                SELECT
                    with_stats.*,
                    mad_stats.mad_price,
                    ROW_NUMBER() OVER (
                        PARTITION BY analysis_row_id
                        ORDER BY
                            CASE
                                WHEN group_size >= {minimum_group_size} THEN 0
                                ELSE 1
                            END,
                            CASE
                                WHEN group_size >= {minimum_group_size}
                                THEN scope_priority
                                ELSE NULL
                            END,
                            CASE
                                WHEN group_size < {minimum_group_size}
                                THEN group_size
                                ELSE NULL
                            END DESC,
                            scope_priority
                    ) AS scope_rank
                FROM with_stats
                JOIN mad_stats USING (scope_group_key)
            ),
            selected AS (
                SELECT *
                FROM ranked
                WHERE scope_rank = 1
            )
            SELECT
                selected.* EXCLUDE (scope_rank),
                CASE
                    WHEN group_size < {minimum_group_size} THEN NULL
                    WHEN mad_price > 0
                    THEN
                        0.6744897501960817
                        * (awarded_price_per_base_unit - median_price)
                        / mad_price
                    ELSE NULL
                END AS modified_z_score,
                CASE
                    WHEN group_size < {minimum_group_size} THEN 'insufficient_sample'
                    WHEN mad_price > 0 THEN 'modified_z_score'
                    WHEN iqr_price > 0 THEN 'iqr_fallback'
                    ELSE 'insufficient_variation'
                END AS detection_method,
                CASE
                    WHEN group_size < {minimum_group_size} THEN FALSE
                    WHEN mad_price > 0 THEN
                        ABS(
                            0.6744897501960817
                            * (awarded_price_per_base_unit - median_price)
                            / mad_price
                        ) >= {modified_z_threshold}
                    WHEN iqr_price > 0 THEN
                        awarded_price_per_base_unit
                            < q1_price - ({iqr_multiplier} * iqr_price)
                        OR awarded_price_per_base_unit
                            > q3_price + ({iqr_multiplier} * iqr_price)
                    ELSE FALSE
                END AS is_price_signal
            FROM selected
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
        connection.execute(
            """
            CREATE VIEW anomaly_scope_summary AS
            SELECT
                comparison_scope,
                comparison_geography,
                comparison_period,
                COUNT(*) AS analyzed_rows,
                SUM(CASE WHEN is_price_signal THEN 1 ELSE 0 END) AS signal_count,
                MEDIAN(group_size) AS median_group_size
            FROM gold_price_signals
            GROUP BY
                comparison_scope,
                comparison_geography,
                comparison_period
            ORDER BY comparison_period DESC, comparison_scope
            """
        )

        eligible_row_count = connection.execute(
            "SELECT COUNT(*) FROM gold_price_signals"
        ).fetchone()[0]
        signal_count = connection.execute(
            "SELECT COUNT(*) FROM price_anomalies"
        ).fetchone()[0]
        comparison_group_count = connection.execute(
            "SELECT COUNT(DISTINCT scope_group_key) FROM gold_price_signals"
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
                comparison_scope,
                product_category,
                COUNT(*) AS signal_count,
                COUNT(DISTINCT scope_group_key) AS affected_groups,
                MEDIAN(awarded_price_per_base_unit) AS median_signaled_price,
                MAX(ABS(modified_z_score)) AS max_abs_modified_z
            FROM price_anomalies
            GROUP BY comparison_scope, product_category
            ORDER BY signal_count DESC, comparison_scope, product_category
            """
        )
        columns = [column[0] for column in cursor.description]
        return [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]
