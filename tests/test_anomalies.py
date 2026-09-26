from pathlib import Path

import duckdb

from dental_procurement_intelligence.analytics import build_price_signals


def _create_awards_table(database: Path, prices: list[float]) -> None:
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards (
                item_number BIGINT,
                product_category VARCHAR,
                presentation VARCHAR,
                shade VARCHAR,
                normalized_quantity_unit VARCHAR,
                normalized_quantity_value DOUBLE,
                awarded_price_per_base_unit DOUBLE
            )
            """
        )
        for index, price in enumerate(prices, start=1):
            connection.execute(
                """
                INSERT INTO silver_awards VALUES (
                    ?, 'composite_resin', 'syringe', 'A2', 'g', 4.0, ?
                )
                """,
                [index, price],
            )


def test_modified_z_score_flags_extreme_price(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    _create_awards_table(database, [9.0, 10.0, 10.0, 11.0, 40.0])

    result = build_price_signals(database)

    assert result.eligible_row_count == 5
    assert result.signal_count == 1

    with duckdb.connect(str(database), read_only=True) as connection:
        row = connection.execute(
            """
            SELECT awarded_price_per_base_unit, detection_method, is_price_signal
            FROM price_anomalies
            """
        ).fetchone()

    assert row == (40.0, "modified_z_score", True)


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
