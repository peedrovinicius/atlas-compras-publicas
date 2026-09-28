from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

from dental_procurement_intelligence.api import service


def test_analytics_overview_uses_shared_analytics_layer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")

    monkeypatch.setattr(
        service.DuckDBWarehouse,
        "summary",
        lambda self: [{"product_category": "composite_resin", "item_count": 3}],
    )
    monkeypatch.setattr(
        service,
        "quality_summary",
        lambda path: {"total_items": 3, "category_identified_items": 3},
    )
    monkeypatch.setattr(
        service,
        "quality_by_category",
        lambda path: [{"product_category": "composite_resin"}],
    )
    monkeypatch.setattr(service, "award_summary", lambda path: [])
    monkeypatch.setattr(service, "anomaly_summary", lambda path: [])

    result = service.analytics_overview(database)

    assert result["database"] == "analytics.duckdb"
    assert result["quality"]["total_items"] == 3
    assert result["category_prices"][0]["item_count"] == 3
    assert any(domain["id"] == "dental" for domain in result["domains"])
    assert any(domain["id"] == "medications" for domain in result["domains"])


def test_analytics_overview_requires_existing_database(tmp_path: Path) -> None:
    missing = tmp_path / "missing.duckdb"

    with pytest.raises(FileNotFoundError, match="Banco analítico não encontrado"):
        service.analytics_overview(missing)


def test_categories_support_filter_and_pagination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")
    rows = [
        {"product_category": "composite_resin", "item_count": 8},
        {"product_category": "glass_ionomer", "item_count": 5},
        {"product_category": "fluoride_gel", "item_count": 3},
    ]
    monkeypatch.setattr(
        service.DuckDBWarehouse,
        "summary",
        lambda self: rows,
    )

    page = service.analytics_categories(
        database,
        category="glass_ionomer",
        limit=10,
        offset=0,
    )

    assert page == {
        "items": [{"product_category": "glass_ionomer", "item_count": 5}],
        "total": 1,
        "limit": 10,
        "offset": 0,
    }


def test_awards_support_combined_filters(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")
    rows = [
        {
            "product_category": "composite_resin",
            "macroregion": "Nordeste",
            "analysis_year": 2026,
        },
        {
            "product_category": "composite_resin",
            "macroregion": "Sudeste",
            "analysis_year": 2026,
        },
    ]
    monkeypatch.setattr(service, "award_summary", lambda path: rows)

    page = service.analytics_awards(
        database,
        category="composite_resin",
        macroregion="Nordeste",
        year=2026,
        limit=20,
        offset=0,
    )

    assert page["total"] == 1
    assert page["items"][0]["macroregion"] == "Nordeste"


def test_anomalies_support_scope_filter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")
    rows = [
        {
            "comparison_scope": "state",
            "product_category": "glass_ionomer",
        },
        {
            "comparison_scope": "national",
            "product_category": "glass_ionomer",
        },
    ]
    monkeypatch.setattr(service, "anomaly_summary", lambda path: rows)

    page = service.analytics_anomalies(
        database,
        category="glass_ionomer",
        scope="state",
        limit=20,
        offset=0,
    )

    assert page["total"] == 1
    assert page["items"][0]["comparison_scope"] == "state"


def test_unrecognized_pagination_uses_total_count(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")

    monkeypatch.setattr(
        service,
        "unrecognized_items",
        lambda path, limit, offset: [{"item_number": offset + 1}],
    )
    monkeypatch.setattr(service, "unrecognized_count", lambda path: 37)

    page = service.analytics_unrecognized(
        database,
        limit=10,
        offset=20,
    )

    assert page == {
        "items": [{"item_number": 21}],
        "total": 37,
        "limit": 10,
        "offset": 20,
    }


def test_pagination_rejects_invalid_bounds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "analytics.duckdb"
    database.write_bytes(b"duckdb-placeholder")
    monkeypatch.setattr(service.DuckDBWarehouse, "summary", lambda self: [])

    with pytest.raises(ValueError, match="limit"):
        service.analytics_categories(database, limit=0)

    with pytest.raises(ValueError, match="offset"):
        service.analytics_categories(database, offset=-1)



def test_product_search_groups_awards_by_technical_identity(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'a1', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'CE', DATE '2026-05-10', 10.0,
                        'defensible', 10.00
                    ),
                    (
                        'p2', 'a2', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '222', 'MG', DATE '2026-06-10', 20.0,
                        'defensible', 12.00
                    ),
                    (
                        'p3', 'a3', 2, 'IONOMERO DE VIDRO 10G',
                        'glass_ionomer', 'powder', NULL, NULL,
                        NULL, NULL, NULL, NULL, NULL,
                        NULL, NULL, 1, 10.0, 'g', NULL, NULL,
                        '333', 'PR', DATE '2026-06-11', 5.0,
                        'review', NULL
                    )
            ) AS t(
                procurement_key,
                award_key,
                item_number,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_document,
                state_code,
                analysis_date,
                awarded_quantity,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    result = service.analytics_product_search(
        database,
        query="resina composta A2",
        limit=20,
        offset=0,
    )

    assert result["query"] == "resina composta A2"
    assert result["total"] == 1
    item = result["items"][0]
    assert item["product_category"] == "composite_resin"
    assert item["display_name"].startswith("Resina composta")
    assert item["award_count"] == 2
    assert item["procurement_count"] == 2
    assert item["supplier_count"] == 2
    assert item["state_count"] == 2
    assert item["priced_observation_count"] == 2


def test_product_search_rejects_short_query(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    database.touch()

    with pytest.raises(ValueError, match="pelo menos 2"):
        service.analytics_product_search(database, query="a")



def test_product_summary_prioritizes_median_and_marks_small_sample(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'a1', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '111', 'CE', DATE '2026-05-10', 10.0,
                        'defensible', 10.00
                    ),
                    (
                        'p2', 'a2', 1, 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        '222', 'MG', DATE '2026-06-10', 20.0,
                        'defensible', 12.00
                    )
            ) AS t(
                procurement_key,
                award_key,
                item_number,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_document,
                state_code,
                analysis_date,
                awarded_quantity,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    summary = service.analytics_product_summary(
        database,
        product_id=product_id,
    )

    assert summary["display_name"].startswith("Resina composta")
    assert summary["award_count"] == 2
    assert summary["procurement_count"] == 2
    assert summary["item_count"] == 2
    assert summary["supplier_count"] == 2
    assert summary["state_count"] == 2
    assert summary["price_sample_count"] == 2
    assert summary["minimum_sample_size"] == 5
    assert summary["sample_sufficient"] is False
    assert summary["price_unit"] == "R$/g"
    assert summary["price_stats"]["median_price"] == Decimal("11.000")
    assert summary["price_stats"]["min_price"] == Decimal("10.000")
    assert summary["price_stats"]["max_price"] == Decimal("12.000")
    assert float(summary["price_stats"]["total_physical_quantity"]) == 120.0


def test_product_summary_rejects_unknown_product(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards (
                product_category VARCHAR,
                presentation VARCHAR,
                shade VARCHAR,
                concentration_percent DOUBLE,
                resin_technology VARCHAR,
                curing_mode VARCHAR,
                adhesive_strategy VARCHAR,
                ionomer_use VARCHAR,
                fluoride_formulation VARCHAR,
                anesthetic_active_ingredient VARCHAR,
                anesthetic_vasoconstrictor VARCHAR,
                package_count BIGINT,
                unit_quantity_value DOUBLE,
                unit_quantity_unit VARCHAR,
                normalized_quantity_value DOUBLE,
                normalized_quantity_unit VARCHAR,
                procurement_key VARCHAR,
                item_number BIGINT,
                supplier_document VARCHAR,
                state_code VARCHAR,
                analysis_date DATE,
                original_description VARCHAR,
                awarded_quantity DOUBLE,
                price_normalization_status VARCHAR,
                awarded_price_per_base_unit DECIMAL(38,12)
            )
            """
        )

    with pytest.raises(LookupError, match="não encontrado"):
        service.analytics_product_summary(
            database,
            product_id="0" * 32,
        )



def test_product_history_aggregates_monthly_prices(tmp_path: Path) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        'CE', DATE '2026-05-10', 'defensible', 10.00
                    ),
                    (
                        'p2', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        'MG', DATE '2026-05-20', 'defensible', 14.00
                    ),
                    (
                        'p3', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        'PR', DATE '2026-06-05', 'defensible', 12.00
                    )
            ) AS t(
                procurement_key,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                state_code,
                analysis_date,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    history = service.analytics_product_history(
        database,
        product_id=product_id,
    )

    assert history["total_observations"] == 3
    assert len(history["points"]) == 2
    may = history["points"][0]
    assert may["observations"] == 2
    assert float(may["median_price"]) == 12.0
    assert float(may["percentile_25"]) == 11.0
    assert float(may["percentile_75"]) == 13.0
    june = history["points"][1]
    assert june["observations"] == 1
    assert float(june["median_price"]) == 12.0



def test_product_regions_compare_states_to_national_median(
    tmp_path: Path,
) -> None:
    database = tmp_path / "analytics.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute(
            """
            CREATE TABLE silver_awards AS
            SELECT * FROM (
                VALUES
                    (
                        'p1', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        'CE', 'Nordeste', 'defensible', 10.00
                    ),
                    (
                        'p2', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        'MG', 'Sudeste', 'defensible', 20.00
                    ),
                    (
                        'p3', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g', 4.0, 'g',
                        'MG', 'Sudeste', 'defensible', 30.00
                    )
            ) AS t(
                procurement_key,
                original_description,
                product_category,
                presentation,
                shade,
                concentration_percent,
                resin_technology,
                curing_mode,
                adhesive_strategy,
                ionomer_use,
                fluoride_formulation,
                anesthetic_active_ingredient,
                anesthetic_vasoconstrictor,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                state_code,
                macroregion,
                price_normalization_status,
                awarded_price_per_base_unit
            )
            """
        )

    search = service.analytics_product_search(
        database,
        query="resina composta A2",
    )
    product_id = search["items"][0]["product_id"]

    result = service.analytics_product_regions(
        database,
        product_id=product_id,
    )

    assert result["national"]["observations"] == 3
    assert float(result["national"]["median_price"]) == 20.0
    assert len(result["regions"]) == 2
    states = {row["state_code"]: row for row in result["states"]}
    assert states["CE"]["observations"] == 1
    assert states["CE"]["difference_from_national_percent"] == -50.0
    assert states["MG"]["observations"] == 2
    assert states["MG"]["difference_from_national_percent"] == 25.0
