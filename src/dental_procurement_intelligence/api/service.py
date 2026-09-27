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
    unrecognized_count,
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


def _matches(value: Any, expected: Any) -> bool:
    if expected is None:
        return True
    if isinstance(value, str) and isinstance(expected, str):
        return value.casefold() == expected.casefold()
    return value == expected


def _paginate(
    rows: list[dict[str, Any]],
    *,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    if limit < 1 or limit > 500:
        raise ValueError("limit deve estar entre 1 e 500")
    if offset < 0:
        raise ValueError("offset não pode ser negativo")

    return {
        "items": rows[offset : offset + limit],
        "total": len(rows),
        "limit": limit,
        "offset": offset,
    }


def analytics_categories(
    database_path: str | Path,
    *,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    path = _require_database(database_path)
    rows = DuckDBWarehouse(path).summary()
    filtered = [
        row
        for row in rows
        if _matches(row.get("product_category"), category)
    ]
    return _paginate(filtered, limit=limit, offset=offset)


def analytics_quality(database_path: str | Path) -> dict[str, Any]:
    path = _require_database(database_path)
    return {
        "summary": quality_summary(path),
        "by_category": quality_by_category(path),
    }


def analytics_awards(
    database_path: str | Path,
    *,
    category: str | None = None,
    macroregion: str | None = None,
    year: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    path = _require_database(database_path)
    rows = _optional_rows(award_summary, path)
    filtered = [
        row
        for row in rows
        if _matches(row.get("product_category"), category)
        and _matches(row.get("macroregion"), macroregion)
        and _matches(row.get("analysis_year"), year)
    ]
    return _paginate(filtered, limit=limit, offset=offset)


def analytics_anomalies(
    database_path: str | Path,
    *,
    category: str | None = None,
    scope: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    path = _require_database(database_path)
    rows = _optional_rows(anomaly_summary, path)
    filtered = [
        row
        for row in rows
        if _matches(row.get("product_category"), category)
        and _matches(row.get("comparison_scope"), scope)
    ]
    return _paginate(filtered, limit=limit, offset=offset)


def analytics_unrecognized(
    database_path: str | Path,
    *,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if limit < 1 or limit > 500:
        raise ValueError("limit deve estar entre 1 e 500")
    if offset < 0:
        raise ValueError("offset não pode ser negativo")

    return {
        "items": unrecognized_items(
            path,
            limit=limit,
            offset=offset,
        ),
        "total": unrecognized_count(path),
        "limit": limit,
        "offset": offset,
    }
