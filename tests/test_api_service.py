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
                        'p1', 'a1', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g',
                        '111', 'CE', DATE '2026-05-10',
                        'defensible', 10.00
                    ),
                    (
                        'p2', 'a2', 'RESINA COMPOSTA A2 SERINGA 4G',
                        'composite_resin', 'syringe', 'A2', NULL,
                        'nanohybrid', 'light_cure', NULL, NULL, NULL,
                        NULL, NULL, 1, 4.0, 'g',
                        '222', 'MG', DATE '2026-06-10',
                        'defensible', 12.00
                    ),
                    (
                        'p3', 'a3', 'IONOMERO DE VIDRO 10G',
                        'glass_ionomer', 'powder', NULL, NULL,
                        NULL, NULL, NULL, NULL, NULL,
                        NULL, NULL, 1, 10.0, 'g',
                        '333', 'PR', DATE '2026-06-11',
                        'review', NULL
                    )
            ) AS t(
                procurement_key,
                award_key,
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
                supplier_document,
                state_code,
                analysis_date,
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
