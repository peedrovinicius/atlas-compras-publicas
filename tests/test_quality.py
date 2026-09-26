from pathlib import Path

import duckdb

from dental_procurement_intelligence.analytics.quality import (
    quality_by_category,
    quality_summary,
    unrecognized_items,
)


def _create_silver_items(database: Path) -> None:
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_items (
                item_number BIGINT,
                original_description VARCHAR,
                procurement_unit VARCHAR,
                estimated_unit_value DOUBLE,
                product_category VARCHAR,
                category_identified BOOLEAN,
                presentation_identified BOOLEAN,
                measurement_identified BOOLEAN,
                normalization_quality_score DOUBLE,
                normalization_quality_level VARCHAR,
                fully_structured BOOLEAN,
                normalized_price_per_base_unit DOUBLE,
                missing_fields VARCHAR,
                source_sha256 VARCHAR
            )
            """
        )
        connection.execute(
            """
            INSERT INTO silver_items VALUES
            (
                1, 'RESINA COMPOSTA A2 SERINGA 4G', 'UNIDADE', 40,
                'composite_resin', TRUE, TRUE, TRUE, 1.0, 'high',
                TRUE, 10.0, '', 'hash1'
            ),
            (
                2, 'ITEM SEM CATEGORIA 10G', 'UNIDADE', 20,
                'unknown', FALSE, FALSE, TRUE, 0.278, 'low',
                FALSE, 2.0, 'category,presentation', 'hash2'
            )
            """
        )


def test_quality_summary_exposes_coverage_rates(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    _create_silver_items(database)

    summary = quality_summary(database)

    assert summary["total_items"] == 2
    assert summary["category_coverage_percent"] == 50.0
    assert summary["fully_structured_percent"] == 50.0
    assert summary["price_normalizable_percent"] == 100.0


def test_quality_by_category_and_unknown_queue(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    _create_silver_items(database)

    categories = quality_by_category(database)
    unknown = unrecognized_items(database, limit=10)

    assert {row["product_category"] for row in categories} == {
        "composite_resin",
        "unknown",
    }
    assert len(unknown) == 1
    assert unknown[0]["item_number"] == 2
