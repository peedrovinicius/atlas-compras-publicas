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
