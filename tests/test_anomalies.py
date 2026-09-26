from pathlib import Path

import duckdb

from dental_procurement_intelligence.analytics import build_price_signals


def _create_awards_table(
    database: Path,
    prices: list[float],
    *,
    state_code: str = "CE",
    macroregion: str = "Nordeste",
    year: int = 2026,
    quarter: str = "2026-T3",
    concentration_percent: float | None = None,
) -> None:
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards (
                item_number BIGINT,
                product_category VARCHAR,
                presentation VARCHAR,
                shade VARCHAR,
                concentration_percent DOUBLE,
                package_count BIGINT,
                unit_quantity_unit VARCHAR,
                unit_quantity_value DOUBLE,
                normalized_quantity_unit VARCHAR,
                normalized_quantity_value DOUBLE,
                awarded_price_per_base_unit DOUBLE,
                price_normalization_status VARCHAR,
                state_code VARCHAR,
                macroregion VARCHAR,
                analysis_year BIGINT,
                analysis_quarter VARCHAR
            )
            """
        )
        for index, price in enumerate(prices, start=1):
            connection.execute(
                """
                INSERT INTO silver_awards VALUES (
                    ?, 'composite_resin', 'syringe', 'A2', ?,
                    NULL, 'g', 4.0, 'g', 4.0, ?, 'defensible',
                    ?, ?, ?, ?
                )
                """,
                [
                    index,
                    concentration_percent,
                    price,
                    state_code,
                    macroregion,
                    year,
                    quarter,
                ],
            )


def test_modified_z_score_uses_most_specific_sufficient_scope(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    _create_awards_table(database, [9.0, 10.0, 10.0, 11.0, 40.0])

    result = build_price_signals(database)

    assert result.eligible_row_count == 5
    assert result.signal_count == 1

    with duckdb.connect(str(database), read_only=True) as connection:
        row = connection.execute(
            """
            SELECT
                awarded_price_per_base_unit,
                comparison_scope,
                detection_method,
                is_price_signal
            FROM price_anomalies
            """
        ).fetchone()

    assert row == (40.0, "uf_trimestre", "modified_z_score", True)


def test_small_groups_do_not_generate_signals(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    _create_awards_table(database, [9.0, 10.0, 11.0, 40.0])

    result = build_price_signals(database)

    assert result.eligible_row_count == 4
    assert result.signal_count == 0

    with duckdb.connect(str(database), read_only=True) as connection:
        methods = {
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT detection_method FROM gold_price_signals"
            ).fetchall()
        }

    assert methods == {"insufficient_sample"}


def test_review_price_normalization_is_excluded_from_signals(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    _create_awards_table(database, [9.0, 10.0, 10.0, 11.0, 40.0])

    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            UPDATE silver_awards
            SET price_normalization_status = 'review'
            WHERE awarded_price_per_base_unit = 40.0
            """
        )

    result = build_price_signals(database)

    assert result.eligible_row_count == 4
    assert result.signal_count == 0
