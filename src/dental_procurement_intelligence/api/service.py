from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import duckdb

from dental_procurement_intelligence.analytics import (
    DuckDBWarehouse,
    anomaly_summary,
    award_summary,
    quality_by_category,
    quality_summary,
    unrecognized_items,
)
from dental_procurement_intelligence.identity import available_domains


def _require_database(database_path: str | Path) -> Path:
    path = Path(database_path)
    if not path.exists():
        raise FileNotFoundError(f"Banco analítico não encontrado: {path}")
    return path


def _optional_rows(
    query: Callable[[str | Path], list[dict[str, Any]]],
    database_path: str | Path,
) -> list[dict[str, Any]]:
    try:
        return query(database_path)
    except duckdb.CatalogException:
        return []


def analytics_overview(database_path: str | Path) -> dict[str, Any]:
    path = _require_database(database_path)
    categories = DuckDBWarehouse(path).summary()
    quality = quality_summary(path)

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "database": path.name,
        "domains": [
            {
                "id": descriptor.domain.value,
                "label": descriptor.label,
                "status": descriptor.status.value,
                "benchmark_required": descriptor.benchmark_required,
            }
            for descriptor in available_domains()
        ],
        "quality": quality,
        "quality_by_category": quality_by_category(path),
        "category_prices": categories,
        "awards": _optional_rows(award_summary, path),
        "anomalies": _optional_rows(anomaly_summary, path),
    }


def analytics_categories(database_path: str | Path) -> list[dict[str, Any]]:
    path = _require_database(database_path)
    return DuckDBWarehouse(path).summary()


def analytics_quality(database_path: str | Path) -> dict[str, Any]:
    path = _require_database(database_path)
    return {
        "summary": quality_summary(path),
        "by_category": quality_by_category(path),
    }


def analytics_awards(database_path: str | Path) -> list[dict[str, Any]]:
    path = _require_database(database_path)
    return _optional_rows(award_summary, path)


def analytics_anomalies(database_path: str | Path) -> list[dict[str, Any]]:
    path = _require_database(database_path)
    return _optional_rows(anomaly_summary, path)


def analytics_unrecognized(
    database_path: str | Path,
    *,
    limit: int = 50,
) -> list[dict[str, Any]]:
    path = _require_database(database_path)
    return unrecognized_items(path, limit=limit)
