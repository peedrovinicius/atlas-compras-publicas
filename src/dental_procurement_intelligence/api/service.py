from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb

from dental_procurement_intelligence.api.catalog import parser_category_label
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


_PRODUCT_IDENTITY_FIELDS = (
    "product_category",
    "presentation",
    "shade",
    "concentration_percent",
    "resin_technology",
    "curing_mode",
    "adhesive_strategy",
    "ionomer_use",
    "fluoride_formulation",
    "anesthetic_active_ingredient",
    "anesthetic_vasoconstrictor",
    "package_count",
    "unit_quantity_value",
    "unit_quantity_unit",
)


def _product_identity_expression() -> str:
    parts = ", ".join(
        f"COALESCE(CAST({field} AS VARCHAR), '∅')"
        for field in _PRODUCT_IDENTITY_FIELDS
    )
    return f"MD5(CONCAT_WS('|', {parts}))"


def analytics_product_search(
    database_path: str | Path,
    *,
    query: str,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    path = _require_database(database_path)
    cleaned = " ".join(query.split())
    if len(cleaned) < 2:
        raise ValueError("query deve ter pelo menos 2 caracteres")
    if limit < 1 or limit > 100:
        raise ValueError("limit deve estar entre 1 e 100")
    if offset < 0:
        raise ValueError("offset não pode ser negativo")

    tokens = [token.casefold() for token in cleaned.split()]
    search_text = """
        LOWER(CONCAT_WS(
            ' ',
            original_description,
            product_category,
            presentation,
            shade,
            CAST(concentration_percent AS VARCHAR),
            resin_technology,
            curing_mode,
            adhesive_strategy,
            ionomer_use,
            fluoride_formulation,
            anesthetic_active_ingredient,
            anesthetic_vasoconstrictor
        ))
    """
    where_tokens = " AND ".join(
        f"{search_text} LIKE ?" for _ in tokens
    )
    identity = _product_identity_expression()

    base_sql = f"""
        FROM silver_awards
        WHERE product_category <> 'unknown'
          AND {where_tokens}
        GROUP BY {", ".join(_PRODUCT_IDENTITY_FIELDS)}
    """
    parameters = [f"%{token}%" for token in tokens]

    with duckdb.connect(str(path), read_only=True) as connection:
        total = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT 1
                {base_sql}
            )
            """,
            parameters,
        ).fetchone()[0]

        cursor = connection.execute(
            f"""
            SELECT
                {identity} AS product_id,
                {", ".join(_PRODUCT_IDENTITY_FIELDS)},
                COUNT(*) AS award_count,
                COUNT(DISTINCT procurement_key) AS procurement_count,
                COUNT(DISTINCT supplier_document) AS supplier_count,
                COUNT(DISTINCT state_code) AS state_count,
                COUNT(*) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS priced_observation_count,
                MAX(analysis_date) AS latest_date,
                MIN(original_description) AS sample_description
            {base_sql}
            ORDER BY
                priced_observation_count DESC,
                procurement_count DESC,
                award_count DESC,
                product_category,
                shade
            LIMIT ? OFFSET ?
            """,
            [*parameters, limit, offset],
        )
        columns = [column[0] for column in cursor.description]
        rows = [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]

    for row in rows:
        category_label = parser_category_label(row["product_category"])
        details = [
            category_label,
            row.get("shade"),
            row.get("presentation"),
        ]
        row["display_name"] = " · ".join(
            str(value) for value in details if value
        )

    return {
        "query": cleaned,
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
