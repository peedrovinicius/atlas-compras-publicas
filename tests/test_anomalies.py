from decimal import Decimal
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
                measurement_candidate_count BIGINT,
                measurement_resolution VARCHAR,
                unit_quantity_unit VARCHAR,
                unit_quantity_value DOUBLE,
                normalized_quantity_unit VARCHAR,
                normalized_quantity_value DOUBLE,
                awarded_price_per_base_unit DECIMAL(38, 12),
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
                    NULL, 1, 'single', 'g', 4.0, 'g', 4.0,
                    ?, 'defensible', ?, ?, ?, ?
                )
                """,
                [
                    index,
                    concentration_percent,
                    Decimal(str(price)),
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

    assert row == (
        Decimal("40.000000000000"),
        "uf_trimestre",
        "modified_z_score",
        True,
    )


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


def test_different_package_configurations_use_different_comparison_groups(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    _create_awards_table(database, [10.0, 10.0, 10.0, 10.0, 10.0, 5.0])

    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            UPDATE silver_awards
            SET
                package_count = 2,
                normalized_quantity_value = 8.0
            WHERE item_number = 6
            """
        )

    result = build_price_signals(database)

    assert result.eligible_row_count == 6
    assert result.comparison_group_count == 2
    assert result.signal_count == 0

    with duckdb.connect(str(database), read_only=True) as connection:
        groups = connection.execute(
            """
            SELECT item_number, group_size
            FROM gold_price_signals
            ORDER BY item_number
            """
        ).fetchall()

    assert groups[-1] == (6, 1)


def test_old_awards_schema_requires_rebuild(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"

    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards (
                item_number BIGINT,
                package_count BIGINT,
                unit_quantity_value DOUBLE,
                unit_quantity_unit VARCHAR,
                price_normalization_status VARCHAR
            )
            """
        )

    try:
        build_price_signals(database)
    except ValueError as error:
        message = str(error)
    else:
        raise AssertionError("Schema antigo deveria exigir reconstrução")

    assert "measurement_candidate_count" in message
    assert "measurement_resolution" in message


def test_float_price_schema_requires_rebuild(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"

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
                measurement_candidate_count BIGINT,
                measurement_resolution VARCHAR,
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

    try:
        build_price_signals(database)
    except ValueError as error:
        message = str(error)
    else:
        raise AssertionError("Preço em DOUBLE deveria exigir reconstrução")

    assert "DECIMAL" in message
