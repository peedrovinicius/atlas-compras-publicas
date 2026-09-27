from pathlib import Path

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
