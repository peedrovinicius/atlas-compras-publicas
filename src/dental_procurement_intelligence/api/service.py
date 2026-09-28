from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
from dental_procurement_intelligence.api.catalog import parser_category_label
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
    "normalized_quantity_value",
    "normalized_quantity_unit",
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



def analytics_product_summary(
    database_path: str | Path,
    *,
    product_id: str,
    minimum_sample_size: int = 5,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")
    if minimum_sample_size < 1:
        raise ValueError("minimum_sample_size deve ser positivo")

    identity = _product_identity_expression()
    identity_fields = ", ".join(_PRODUCT_IDENTITY_FIELDS)

    with duckdb.connect(str(path), read_only=True) as connection:
        cursor = connection.execute(
            f"""
            SELECT
                {identity} AS product_id,
                {identity_fields},
                COUNT(*) AS award_count,
                COUNT(DISTINCT procurement_key) AS procurement_count,
                COUNT(
                    DISTINCT CONCAT(
                        procurement_key,
                        '|',
                        CAST(item_number AS VARCHAR)
                    )
                ) AS item_count,
                COUNT(DISTINCT supplier_document) AS supplier_count,
                COUNT(DISTINCT state_code) AS state_count,
                MIN(analysis_date) AS period_start,
                MAX(analysis_date) AS period_end,
                MAX(analysis_date) AS latest_update,
                MIN(original_description) AS sample_description,
                COUNT(*) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS price_sample_count
            FROM silver_awards
            WHERE {identity} = ?
            GROUP BY {identity_fields}
            """,
            [product_id],
        )
        row = cursor.fetchone()
        if row is None:
            raise LookupError("Produto não encontrado na base analítica")
        columns = [column[0] for column in cursor.description]
        summary = dict(zip(columns, row, strict=True))

        price_cursor = connection.execute(
            f"""
            SELECT
                MEDIAN(awarded_price_per_base_unit) AS median_price,
                AVG(awarded_price_per_base_unit) AS average_price,
                MIN(awarded_price_per_base_unit) AS min_price,
                MAX(awarded_price_per_base_unit) AS max_price,
                QUANTILE_CONT(
                    awarded_price_per_base_unit,
                    0.25
                ) AS percentile_25,
                QUANTILE_CONT(
                    awarded_price_per_base_unit,
                    0.75
                ) AS percentile_75,
                STDDEV_POP(
                    awarded_price_per_base_unit
                ) AS standard_deviation,
                SUM(
                    awarded_quantity * normalized_quantity_value
                ) AS total_physical_quantity
            FROM silver_awards
            WHERE {identity} = ?
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
            """,
            [product_id],
        )
        price_row = price_cursor.fetchone()
        price_columns = [column[0] for column in price_cursor.description]
        price_stats = dict(zip(price_columns, price_row, strict=True))

    price_sample_count = summary["price_sample_count"]
    category_label = parser_category_label(summary["product_category"])
    details = [
        category_label,
        summary.get("shade"),
        summary.get("presentation"),
    ]

    return {
        **summary,
        "display_name": " · ".join(
            str(value) for value in details if value
        ),
        "minimum_sample_size": minimum_sample_size,
        "sample_sufficient": price_sample_count >= minimum_sample_size,
        "price_unit": (
            f"R$/{summary['normalized_quantity_unit']}"
            if summary.get("normalized_quantity_unit")
            else None
        ),
        "price_stats": price_stats,
    }



def analytics_product_history(
    database_path: str | Path,
    *,
    product_id: str,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")

    identity = _product_identity_expression()

    with duckdb.connect(str(path), read_only=True) as connection:
        exists = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM silver_awards
            WHERE {identity} = ?
            """,
            [product_id],
        ).fetchone()[0]
        if not exists:
            raise LookupError("Produto não encontrado na base analítica")

        cursor = connection.execute(
            f"""
            SELECT
                DATE_TRUNC('month', analysis_date) AS month,
                COUNT(*) AS observations,
                COUNT(DISTINCT procurement_key) AS procurement_count,
                COUNT(DISTINCT state_code) AS state_count,
                MEDIAN(awarded_price_per_base_unit) AS median_price,
                AVG(awarded_price_per_base_unit) AS average_price,
                QUANTILE_CONT(
                    awarded_price_per_base_unit,
                    0.25
                ) AS percentile_25,
                QUANTILE_CONT(
                    awarded_price_per_base_unit,
                    0.75
                ) AS percentile_75,
                MIN(awarded_price_per_base_unit) AS min_price,
                MAX(awarded_price_per_base_unit) AS max_price
            FROM silver_awards
            WHERE {identity} = ?
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
              AND analysis_date IS NOT NULL
            GROUP BY 1
            ORDER BY month
            """,
            [product_id],
        )
        columns = [column[0] for column in cursor.description]
        rows = [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]

    return {
        "product_id": product_id,
        "points": rows,
        "total_observations": sum(row["observations"] for row in rows),
    }



def analytics_product_regions(
    database_path: str | Path,
    *,
    product_id: str,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")

    identity = _product_identity_expression()

    with duckdb.connect(str(path), read_only=True) as connection:
        exists = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM silver_awards
            WHERE {identity} = ?
            """,
            [product_id],
        ).fetchone()[0]
        if not exists:
            raise LookupError("Produto não encontrado na base analítica")

        national = connection.execute(
            f"""
            SELECT
                COUNT(*) AS observations,
                COUNT(DISTINCT procurement_key) AS procurement_count,
                COUNT(DISTINCT state_code) AS state_count,
                MEDIAN(awarded_price_per_base_unit) AS median_price
            FROM silver_awards
            WHERE {identity} = ?
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
            """,
            [product_id],
        ).fetchone()

        national_columns = [
            "observations",
            "procurement_count",
            "state_count",
            "median_price",
        ]
        national_summary = dict(
            zip(national_columns, national, strict=True)
        )

        cursor = connection.execute(
            f"""
            WITH state_stats AS (
                SELECT
                    state_code,
                    macroregion,
                    COUNT(*) AS observations,
                    COUNT(DISTINCT procurement_key) AS procurement_count,
                    MEDIAN(awarded_price_per_base_unit) AS median_price
                FROM silver_awards
                WHERE {identity} = ?
                  AND price_normalization_status = 'defensible'
                  AND awarded_price_per_base_unit IS NOT NULL
                  AND awarded_price_per_base_unit > 0
                  AND state_code IS NOT NULL
                GROUP BY state_code, macroregion
            )
            SELECT
                state_code,
                macroregion,
                observations,
                procurement_count,
                median_price,
                CASE
                    WHEN ? IS NULL OR ? = 0 THEN NULL
                    ELSE ROUND(
                        100 * (
                            CAST(median_price AS DOUBLE)
                            / CAST(? AS DOUBLE)
                            - 1
                        ),
                        2
                    )
                END AS difference_from_national_percent
            FROM state_stats
            ORDER BY observations DESC, state_code
            """,
            [
                product_id,
                national_summary["median_price"],
                national_summary["median_price"],
                national_summary["median_price"],
            ],
        )
        columns = [column[0] for column in cursor.description]
        states = [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]

        region_cursor = connection.execute(
            f"""
            SELECT
                macroregion,
                COUNT(*) AS observations,
                COUNT(DISTINCT procurement_key) AS procurement_count,
                COUNT(DISTINCT state_code) AS state_count,
                MEDIAN(awarded_price_per_base_unit) AS median_price
            FROM silver_awards
            WHERE {identity} = ?
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
              AND macroregion IS NOT NULL
            GROUP BY macroregion
            ORDER BY observations DESC, macroregion
            """,
            [product_id],
        )
        region_columns = [
            column[0] for column in region_cursor.description
        ]
        regions = [
            dict(zip(region_columns, row, strict=True))
            for row in region_cursor.fetchall()
        ]

    return {
        "product_id": product_id,
        "national": national_summary,
        "regions": regions,
        "states": states,
    }
