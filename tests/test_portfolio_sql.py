from pathlib import Path

import duckdb
import pytest


SQL_DIR = Path("sql")


@pytest.fixture
def portfolio_database(tmp_path: Path) -> Path:
    database = tmp_path / "portfolio.duckdb"

    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards (
                product_category VARCHAR,
                macroregion VARCHAR,
                analysis_date DATE,
                awarded_price_per_base_unit DECIMAL(18, 6),
                price_normalization_status VARCHAR
            )
            """
        )
        connection.execute(
            """
            INSERT INTO silver_awards VALUES
                ('composite_resin', 'Nordeste', DATE '2026-01-10', 10.000000, 'defensible'),
                ('composite_resin', 'Nordeste', DATE '2026-02-10', 12.000000, 'defensible'),
                ('composite_resin', 'Sudeste', DATE '2026-01-15', 20.000000, 'defensible'),
                ('composite_resin', 'Sudeste', DATE '2026-02-15', 22.000000, 'defensible'),
                ('glass_ionomer', 'Nordeste', DATE '2026-01-20', 8.000000, 'defensible')
            """
        )

        connection.execute(
            """
            CREATE TABLE silver_items (
                product_category VARCHAR,
                category_identified BOOLEAN,
                presentation_identified BOOLEAN,
                measurement_identified BOOLEAN,
                fully_structured BOOLEAN,
                normalization_quality_score DOUBLE
            )
            """
        )
        connection.execute(
            """
            INSERT INTO silver_items VALUES
                ('composite_resin', TRUE, TRUE, TRUE, TRUE, 1.0),
                ('composite_resin', TRUE, TRUE, FALSE, FALSE, 0.75),
                ('glass_ionomer', TRUE, TRUE, TRUE, TRUE, 1.0)
            """
        )

        connection.execute(
            """
            CREATE TABLE gold_price_signals (
                product_key VARCHAR,
                comparison_scope VARCHAR,
                awarded_price_per_base_unit DECIMAL(18, 6),
                award_key VARCHAR,
                procurement_key VARCHAR,
                item_number BIGINT,
                original_description VARCHAR,
                product_category VARCHAR,
                comparison_geography VARCHAR,
                comparison_period VARCHAR,
                scope_group_key VARCHAR,
                group_size BIGINT,
                median_price DECIMAL(18, 6),
                q1_price DECIMAL(18, 6),
                q3_price DECIMAL(18, 6),
                mad_price DECIMAL(18, 6),
                modified_z_score DOUBLE,
                detection_method VARCHAR,
                is_price_signal BOOLEAN,
                contract_source_sha256 VARCHAR,
                item_source_sha256 VARCHAR,
                result_source_sha256 VARCHAR
            )
            """
        )

        rows = [
            (
                "product-a",
                "brasil_ano",
                float(price),
                f"award-{index}",
                "pncp:test",
                index,
                "RESINA COMPOSTA A2 SERINGA 4G",
                "composite_resin",
                "Brasil",
                "2026",
                "group-a",
                5,
                12.0,
                10.0,
                14.0,
                1.0,
                float(index - 3),
                "modified_z_score",
                index == 5,
                "a" * 64,
                "b" * 64,
                "c" * 64,
            )
            for index, price in enumerate([10, 11, 12, 13, 20], start=1)
        ]
        connection.executemany(
            """
            INSERT INTO gold_price_signals VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            rows,
        )

    return database


@pytest.mark.parametrize(
    "filename",
    [
        "01_price_evolution.sql",
        "02_group_dispersion.sql",
        "03_regional_gap.sql",
        "04_normalization_coverage.sql",
    ],
)
def test_portfolio_sql_executes(filename: str, portfolio_database: Path) -> None:
    sql = (SQL_DIR / filename).read_text(encoding="utf-8")

    with duckdb.connect(str(portfolio_database), read_only=True) as connection:
        rows = connection.execute(sql).fetchall()

    assert rows


def test_signal_trace_sql_is_parameterized(portfolio_database: Path) -> None:
    sql = (SQL_DIR / "05_signal_trace.sql").read_text(encoding="utf-8")

    with duckdb.connect(str(portfolio_database), read_only=True) as connection:
        row = connection.execute(sql, ["award-5"]).fetchone()

    assert row is not None
    assert row[0] == "award-5"
    assert row[-1] == "c" * 64
