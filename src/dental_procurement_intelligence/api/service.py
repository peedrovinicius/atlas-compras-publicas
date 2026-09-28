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
from dental_procurement_intelligence.api.catalog import (
    normalize_product_search_text,
    parser_category_label,
    product_presentation_label,
    resolve_product_presentation_token,
    resolve_product_search_query,
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


def _table_columns(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
) -> set[str]:
    rows = connection.execute(
        f"PRAGMA table_info('{table_name}')"
    ).fetchall()
    return {str(row[1]) for row in rows}


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


def _award_filter_sql(
    *,
    identity: str | None = None,
    product_id: str | None = None,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> tuple[list[str], list[Any]]:
    clauses: list[str] = []
    parameters: list[Any] = []

    if identity is not None and product_id is not None:
        clauses.append(f"{identity} = ?")
        parameters.append(product_id)

    if state_code:
        clauses.append("UPPER(COALESCE(state_code, '')) = UPPER(?)")
        parameters.append(state_code.strip())

    if macroregion:
        clauses.append("LOWER(COALESCE(macroregion, '')) = LOWER(?)")
        parameters.append(macroregion.strip())

    if supplier:
        term = f"%{supplier.strip().casefold()}%"
        clauses.append(
            "("
            "LOWER(COALESCE(supplier_name, '')) LIKE ? "
            "OR LOWER(COALESCE(CAST(supplier_document AS VARCHAR), '')) LIKE ?"
            ")"
        )
        parameters.extend([term, term])

    if buyer:
        term = f"%{buyer.strip().casefold()}%"
        clauses.append(
            "("
            "LOWER(COALESCE(organization_name, '')) LIKE ? "
            "OR LOWER(COALESCE(CAST(organization_cnpj AS VARCHAR), '')) LIKE ? "
            "OR LOWER(COALESCE(buyer_unit_name, '')) LIKE ? "
            "OR LOWER(COALESCE(CAST(buyer_unit_code AS VARCHAR), '')) LIKE ?"
            ")"
        )
        parameters.extend([term, term, term, term])

    if start_date:
        clauses.append("analysis_date >= CAST(? AS DATE)")
        parameters.append(start_date)

    if end_date:
        clauses.append("analysis_date <= CAST(? AS DATE)")
        parameters.append(end_date)

    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date não pode ser posterior a end_date")

    return clauses, parameters


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


def analytics_product_discovery(
    database_path: str | Path,
) -> dict[str, Any]:
    path = _require_database(database_path)
    identity = _product_identity_expression()

    with duckdb.connect(str(path), read_only=True) as connection:
        cursor = connection.execute(
            f"""
            SELECT
                product_category,
                COUNT(DISTINCT {identity}) AS product_count,
                COUNT(*) AS award_count,
                COUNT(*) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS priced_observation_count
            FROM silver_awards
            WHERE product_category <> 'unknown'
            GROUP BY product_category
            ORDER BY priced_observation_count DESC, product_category
            """
        )
        columns = [column[0] for column in cursor.description]
        rows = [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]

    for row in rows:
        row["label"] = parser_category_label(row["product_category"])

    return {"items": rows}


def analytics_product_search(
    database_path: str | Path,
    *,
    query: str,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    sort: str = "relevance",
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
    if sort not in {"relevance", "coverage", "procurements", "latest", "name"}:
        raise ValueError("sort inválido")

    interpreted_category, residual_tokens, interpreted_label = (
        resolve_product_search_query(cleaned)
    )
    tokens = (
        residual_tokens
        if interpreted_category is not None
        else normalize_product_search_text(cleaned).split()
    )
    search_text = """
        LOWER(STRIP_ACCENTS(CONCAT_WS(
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
        )))
    """
    search_clauses = ["product_category <> 'unknown'"]
    search_parameters: list[Any] = []

    if interpreted_category is not None:
        search_clauses.append("product_category = ?")
        search_parameters.append(interpreted_category)

    presentation_tokens = {
        token: resolve_product_presentation_token(token)
        for token in tokens
    }

    for token in tokens:
        presentation = presentation_tokens[token]
        if presentation is not None:
            search_clauses.append(
                f"({search_text} LIKE ? OR presentation = ?)"
            )
            search_parameters.extend([f"%{token}%", presentation])
        else:
            search_clauses.append(f"{search_text} LIKE ?")
            search_parameters.append(f"%{token}%")

    identity = _product_identity_expression()
    filter_clauses, filter_parameters = _award_filter_sql(
        state_code=state_code,
        macroregion=macroregion,
        supplier=supplier,
        buyer=buyer,
        start_date=start_date,
        end_date=end_date,
    )
    search_clauses.extend(filter_clauses)
    search_where_sql = " AND ".join(search_clauses)

    base_sql = f"""
        FROM silver_awards
        WHERE {search_where_sql}
        GROUP BY {", ".join(_PRODUCT_IDENTITY_FIELDS)}
    """
    parameters = [
        *search_parameters,
        *filter_parameters,
    ]

    with duckdb.connect(str(path), read_only=True) as connection:
        available_columns = _table_columns(connection, "silver_awards")
        latest_date_expression = (
            "MAX(analysis_date)"
            if "analysis_date" in available_columns
            else "NULL"
        )

        normalized_cleaned = normalize_product_search_text(cleaned)
        relevance_parts = [
            (
                "MAX(CASE WHEN LOWER(STRIP_ACCENTS(original_description)) = ? "
                "THEN 100 ELSE 0 END)"
            )
        ]
        relevance_parameters: list[Any] = [normalized_cleaned]

        if interpreted_category is not None:
            relevance_parts.append(
                "CASE WHEN product_category = ? THEN 40 ELSE 0 END"
            )
            relevance_parameters.append(interpreted_category)

        for token in tokens:
            normalized_token = normalize_product_search_text(token)
            relevance_parts.append(
                "MAX(CASE WHEN LOWER(STRIP_ACCENTS(original_description)) LIKE ? "
                "THEN 10 ELSE 0 END)"
            )
            relevance_parameters.append(f"%{normalized_token}%")
            relevance_parts.append(
                "CASE WHEN LOWER(STRIP_ACCENTS(COALESCE(CAST(shade AS VARCHAR), ''))) = ? "
                "THEN 30 ELSE 0 END"
            )
            relevance_parameters.append(normalized_token)

            presentation = presentation_tokens[token]
            if presentation is not None:
                relevance_parts.append(
                    "CASE WHEN presentation = ? THEN 35 ELSE 0 END"
                )
                relevance_parameters.append(presentation)

        relevance_expression = " + ".join(relevance_parts)

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
                MIN(awarded_price_per_base_unit) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS min_price,
                QUANTILE_CONT(awarded_price_per_base_unit, 0.25) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS percentile_25,
                MEDIAN(awarded_price_per_base_unit) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS median_price,
                QUANTILE_CONT(awarded_price_per_base_unit, 0.75) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS percentile_75,
                MAX(awarded_price_per_base_unit) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS max_price,
                {latest_date_expression} AS latest_date,
                MIN(original_description) AS sample_description,
                {relevance_expression} AS relevance_score
            {base_sql}
            ORDER BY
                CASE WHEN ? = 'relevance' THEN relevance_score END DESC,
                CASE WHEN ? = 'relevance' THEN priced_observation_count END DESC,
                CASE WHEN ? = 'relevance' THEN procurement_count END DESC,
                CASE WHEN ? = 'coverage' THEN priced_observation_count END DESC,
                CASE WHEN ? = 'coverage' THEN procurement_count END DESC,
                CASE WHEN ? = 'procurements' THEN procurement_count END DESC,
                CASE WHEN ? = 'latest' THEN latest_date END DESC NULLS LAST,
                CASE WHEN ? = 'name' THEN product_category END ASC,
                CASE WHEN ? = 'name' THEN shade END ASC NULLS LAST,
                award_count DESC,
                product_category,
                shade
            LIMIT ? OFFSET ?
            """,
            [
                *relevance_parameters,
                *parameters,
                sort,
                sort,
                sort,
                sort,
                sort,
                sort,
                sort,
                sort,
                sort,
                limit,
                offset,
            ],
        )
        columns = [column[0] for column in cursor.description]
        rows = [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]

        facet_fields = (
            "shade",
            "presentation",
            "concentration_percent",
            "resin_technology",
            "curing_mode",
            "adhesive_strategy",
            "ionomer_use",
            "fluoride_formulation",
            "anesthetic_active_ingredient",
            "anesthetic_vasoconstrictor",
        )
        facets: dict[str, list[dict[str, Any]]] = {}
        for field in facet_fields:
            if field not in available_columns:
                continue

            facet_cursor = connection.execute(
                f"""
                SELECT
                    CAST({field} AS VARCHAR) AS value,
                    COUNT(DISTINCT {identity}) AS product_count
                FROM silver_awards
                WHERE {search_where_sql}
                  AND {field} IS NOT NULL
                  AND TRIM(CAST({field} AS VARCHAR)) <> ''
                GROUP BY {field}
                ORDER BY product_count DESC, value
                LIMIT 8
                """,
                parameters,
            )
            facets[field] = [
                {
                    "value": value,
                    "product_count": int(product_count),
                }
                for value, product_count in facet_cursor.fetchall()
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

        reasons: list[str] = []
        if interpreted_label:
            reasons.append(f"Categoria: {interpreted_label}")

        normalized_shade = normalize_product_search_text(
            str(row.get("shade") or "")
        )
        if normalized_shade and any(
            normalize_product_search_text(token) == normalized_shade
            for token in tokens
        ):
            reasons.append(f"Cor {row['shade']}")

        for token in tokens:
            presentation = presentation_tokens[token]
            if presentation and presentation == row.get("presentation"):
                reasons.append(
                    f"Apresentação: {product_presentation_label(presentation)}"
                )
                break

        if not reasons:
            reasons.append("Descrição compatível")

        row["match_reasons"] = reasons[:3]

    return {
        "query": cleaned,
        "sort": sort,
        "interpreted_category": interpreted_category,
        "interpreted_label": interpreted_label,
        "filters": {
            "state_code": state_code,
            "macroregion": macroregion,
            "supplier": supplier,
            "buyer": buyer,
            "start_date": start_date,
            "end_date": end_date,
        },
        "items": rows,
        "facets": facets,
        "total": total,
        "limit": limit,
        "offset": offset,
    }



def analytics_product_summary(
    database_path: str | Path,
    *,
    product_id: str,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    minimum_sample_size: int = 5,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")
    if minimum_sample_size < 1:
        raise ValueError("minimum_sample_size deve ser positivo")

    identity = _product_identity_expression()
    identity_fields = ", ".join(_PRODUCT_IDENTITY_FIELDS)
    filter_clauses, parameters = _award_filter_sql(
        identity=identity,
        product_id=product_id,
        state_code=state_code,
        macroregion=macroregion,
        supplier=supplier,
        buyer=buyer,
        start_date=start_date,
        end_date=end_date,
    )
    where_sql = " AND ".join(filter_clauses)

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
            WHERE {where_sql}
            GROUP BY {identity_fields}
            """,
            parameters,
        )
        row = cursor.fetchone()
        if row is None:
            raise LookupError("Produto não encontrado para os filtros informados")
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
            WHERE {where_sql}
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
            """,
            parameters,
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

def analytics_product_distribution(
    database_path: str | Path,
    *,
    product_id: str,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    bin_count: int = 10,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")
    if bin_count < 5 or bin_count > 40:
        raise ValueError("bin_count deve estar entre 5 e 40")

    identity = _product_identity_expression()
    filter_clauses, parameters = _award_filter_sql(
        identity=identity,
        product_id=product_id,
        state_code=state_code,
        macroregion=macroregion,
        supplier=supplier,
        buyer=buyer,
        start_date=start_date,
        end_date=end_date,
    )
    where_sql = " AND ".join(filter_clauses)

    with duckdb.connect(str(path), read_only=True) as connection:
        exists = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM silver_awards
            WHERE {where_sql}
            """,
            parameters,
        ).fetchone()[0]
        if not exists:
            raise LookupError("Produto não encontrado para os filtros informados")

        row = connection.execute(
            f"""
            SELECT
                COUNT(*) AS observations,
                MIN(CAST(awarded_price_per_base_unit AS DOUBLE)) AS min_price,
                MAX(CAST(awarded_price_per_base_unit AS DOUBLE)) AS max_price
            FROM silver_awards
            WHERE {where_sql}
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
            """,
            parameters,
        ).fetchone()

        observations = int(row[0])
        min_price = row[1]
        max_price = row[2]

        if observations == 0 or min_price is None or max_price is None:
            return {
                "product_id": product_id,
                "observations": 0,
                "bin_count": bin_count,
                "min_price": None,
                "max_price": None,
                "bins": [],
            }

        if min_price == max_price:
            return {
                "product_id": product_id,
                "observations": observations,
                "bin_count": 1,
                "min_price": min_price,
                "max_price": max_price,
                "bins": [
                    {
                        "index": 0,
                        "lower": min_price,
                        "upper": max_price,
                        "count": observations,
                    }
                ],
            }

        cursor = connection.execute(
            f"""
            SELECT
                LEAST(
                    ?,
                    CAST(
                        FLOOR(
                            (
                                CAST(awarded_price_per_base_unit AS DOUBLE) - ?
                            ) / (? - ?) * ?
                        ) AS INTEGER
                    )
                ) AS bucket_index,
                COUNT(*) AS bucket_count
            FROM silver_awards
            WHERE {where_sql}
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
            GROUP BY 1
            ORDER BY 1
            """,
            [
                bin_count - 1,
                min_price,
                max_price,
                min_price,
                bin_count,
                *parameters,
            ],
        )
        counts = {
            int(bucket_index): int(bucket_count)
            for bucket_index, bucket_count in cursor.fetchall()
        }

    width = (max_price - min_price) / bin_count
    bins = []
    for index in range(bin_count):
        lower = min_price + width * index
        upper = max_price if index == bin_count - 1 else min_price + width * (index + 1)
        bins.append(
            {
                "index": index,
                "lower": lower,
                "upper": upper,
                "count": counts.get(index, 0),
            }
        )

    return {
        "product_id": product_id,
        "observations": observations,
        "bin_count": bin_count,
        "min_price": min_price,
        "max_price": max_price,
        "bins": bins,
    }

def analytics_product_history(
    database_path: str | Path,
    *,
    product_id: str,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")

    identity = _product_identity_expression()
    filter_clauses, parameters = _award_filter_sql(
        identity=identity,
        product_id=product_id,
        state_code=state_code,
        macroregion=macroregion,
        supplier=supplier,
        buyer=buyer,
        start_date=start_date,
        end_date=end_date,
    )
    where_sql = " AND ".join(filter_clauses)

    with duckdb.connect(str(path), read_only=True) as connection:
        exists = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM silver_awards
            WHERE {where_sql}
            """,
            parameters,
        ).fetchone()[0]
        if not exists:
            raise LookupError("Produto não encontrado para os filtros informados")

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
            WHERE {where_sql}
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
              AND analysis_date IS NOT NULL
            GROUP BY 1
            ORDER BY month
            """,
            parameters,
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
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")

    identity = _product_identity_expression()
    filter_clauses, parameters = _award_filter_sql(
        identity=identity,
        product_id=product_id,
        state_code=state_code,
        macroregion=macroregion,
        supplier=supplier,
        buyer=buyer,
        start_date=start_date,
        end_date=end_date,
    )
    where_sql = " AND ".join(filter_clauses)

    with duckdb.connect(str(path), read_only=True) as connection:
        exists = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM silver_awards
            WHERE {where_sql}
            """,
            parameters,
        ).fetchone()[0]
        if not exists:
            raise LookupError("Produto não encontrado para os filtros informados")

        national = connection.execute(
            f"""
            SELECT
                COUNT(*) AS observations,
                COUNT(DISTINCT procurement_key) AS procurement_count,
                COUNT(DISTINCT state_code) AS state_count,
                MEDIAN(awarded_price_per_base_unit) AS median_price
            FROM silver_awards
            WHERE {where_sql}
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
            """,
            parameters,
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
                WHERE {where_sql}
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
                *parameters,
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
            WHERE {where_sql}
              AND price_normalization_status = 'defensible'
              AND awarded_price_per_base_unit IS NOT NULL
              AND awarded_price_per_base_unit > 0
              AND macroregion IS NOT NULL
            GROUP BY macroregion
            ORDER BY observations DESC, macroregion
            """,
            parameters,
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

def analytics_product_suppliers(
    database_path: str | Path,
    *,
    product_id: str,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")
    if limit < 1 or limit > 100:
        raise ValueError("limit deve estar entre 1 e 100")
    if offset < 0:
        raise ValueError("offset não pode ser negativo")

    identity = _product_identity_expression()
    filter_clauses, parameters = _award_filter_sql(
        identity=identity,
        product_id=product_id,
        state_code=state_code,
        macroregion=macroregion,
        supplier=supplier,
        buyer=buyer,
        start_date=start_date,
        end_date=end_date,
    )
    where_sql = " AND ".join(filter_clauses)

    with duckdb.connect(str(path), read_only=True) as connection:
        total_awards = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM silver_awards
            WHERE {where_sql}
            """,
            parameters,
        ).fetchone()[0]
        if not total_awards:
            raise LookupError("Produto não encontrado para os filtros informados")

        total_suppliers = connection.execute(
            f"""
            SELECT COUNT(DISTINCT supplier_document)
            FROM silver_awards
            WHERE {where_sql}
              AND supplier_document IS NOT NULL
            """,
            parameters,
        ).fetchone()[0]

        cursor = connection.execute(
            f"""
            SELECT
                supplier_document,
                MIN(supplier_name) AS supplier_name,
                COUNT(*) AS award_count,
                COUNT(DISTINCT procurement_key) AS procurement_count,
                MEDIAN(
                    awarded_price_per_base_unit
                ) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS median_price,
                COUNT(*) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS priced_observation_count,
                ROUND(
                    100.0 * COUNT(*) / ?,
                    2
                ) AS sample_share_percent
            FROM silver_awards
            WHERE {where_sql}
              AND supplier_document IS NOT NULL
            GROUP BY supplier_document
            ORDER BY award_count DESC, supplier_name
            LIMIT ? OFFSET ?
            """,
            [total_awards, *parameters, limit, offset],
        )
        columns = [column[0] for column in cursor.description]
        rows = [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]

    return {
        "product_id": product_id,
        "items": rows,
        "total": total_suppliers,
        "limit": limit,
        "offset": offset,
    }

def analytics_product_buyers(
    database_path: str | Path,
    *,
    product_id: str,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")
    if limit < 1 or limit > 100:
        raise ValueError("limit deve estar entre 1 e 100")
    if offset < 0:
        raise ValueError("offset não pode ser negativo")

    identity = _product_identity_expression()
    filter_clauses, parameters = _award_filter_sql(
        identity=identity,
        product_id=product_id,
        state_code=state_code,
        macroregion=macroregion,
        supplier=supplier,
        buyer=buyer,
        start_date=start_date,
        end_date=end_date,
    )
    where_sql = " AND ".join(filter_clauses)

    with duckdb.connect(str(path), read_only=True) as connection:
        exists = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM silver_awards
            WHERE {where_sql}
            """,
            parameters,
        ).fetchone()[0]
        if not exists:
            raise LookupError("Produto não encontrado para os filtros informados")

        total_buyers = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT
                    organization_cnpj,
                    buyer_unit_code
                FROM silver_awards
                WHERE {where_sql}
                  AND (
                      organization_cnpj IS NOT NULL
                      OR buyer_unit_code IS NOT NULL
                  )
                GROUP BY organization_cnpj, buyer_unit_code
            )
            """,
            parameters,
        ).fetchone()[0]

        cursor = connection.execute(
            f"""
            SELECT
                organization_cnpj,
                MIN(organization_name) AS organization_name,
                buyer_unit_code,
                MIN(buyer_unit_name) AS buyer_unit_name,
                MIN(state_code) AS state_code,
                MIN(macroregion) AS macroregion,
                COUNT(*) AS award_count,
                COUNT(DISTINCT procurement_key) AS procurement_count,
                SUM(awarded_total_value) AS awarded_total_value,
                MEDIAN(
                    awarded_price_per_base_unit
                ) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS median_price,
                COUNT(*) FILTER (
                    WHERE price_normalization_status = 'defensible'
                      AND awarded_price_per_base_unit IS NOT NULL
                      AND awarded_price_per_base_unit > 0
                ) AS priced_observation_count
            FROM silver_awards
            WHERE {where_sql}
              AND (
                  organization_cnpj IS NOT NULL
                  OR buyer_unit_code IS NOT NULL
              )
            GROUP BY organization_cnpj, buyer_unit_code
            ORDER BY procurement_count DESC, award_count DESC, organization_name
            LIMIT ? OFFSET ?
            """,
            [*parameters, limit, offset],
        )
        columns = [column[0] for column in cursor.description]
        rows = [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]

    return {
        "product_id": product_id,
        "items": rows,
        "total": total_buyers,
        "limit": limit,
        "offset": offset,
    }

def _pncp_procurement_url(procurement_key: str | None) -> str | None:
    if not procurement_key or not procurement_key.startswith("pncp:"):
        return None
    parts = procurement_key.split(":")
    if len(parts) != 4:
        return None
    _, cnpj, year, sequence = parts
    return (
        "https://pncp.gov.br/app/editais/"
        f"{cnpj}/{year}/{sequence}"
    )


_SIGNAL_DISCLAIMER = (
    "Um sinal estatístico indica apenas que o preço está distante da "
    "distribuição observada para produtos comparáveis. Isso não constitui "
    "prova de irregularidade."
)


def analytics_product_signals(
    database_path: str | Path,
    *,
    product_id: str,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")
    if limit < 1 or limit > 100:
        raise ValueError("limit deve estar entre 1 e 100")
    if offset < 0:
        raise ValueError("offset não pode ser negativo")

    identity = _product_identity_expression()
    filter_clauses, parameters = _award_filter_sql(
        identity=identity,
        product_id=product_id,
        state_code=state_code,
        macroregion=macroregion,
        supplier=supplier,
        buyer=buyer,
        start_date=start_date,
        end_date=end_date,
    )
    where_sql = " AND ".join(filter_clauses)

    with duckdb.connect(str(path), read_only=True) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'main'
                """
            ).fetchall()
        }
        if "gold_price_signals" not in tables:
            return {
                "product_id": product_id,
                "items": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "disclaimer": _SIGNAL_DISCLAIMER,
            }

        exists = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM silver_awards
            WHERE {where_sql}
            """,
            parameters,
        ).fetchone()[0]
        if not exists:
            raise LookupError("Produto não encontrado para os filtros informados")

        total = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM gold_price_signals
            WHERE {where_sql}
              AND is_price_signal
            """,
            parameters,
        ).fetchone()[0]

        cursor = connection.execute(
            f"""
            SELECT
                award_key,
                procurement_key,
                item_number,
                original_description,
                supplier_name,
                supplier_document,
                organization_name,
                state_code,
                analysis_date,
                awarded_price_per_base_unit,
                comparison_scope,
                comparison_geography,
                comparison_period,
                scope_group_key,
                group_size,
                median_price,
                q1_price,
                q3_price,
                mad_price,
                modified_z_score,
                detection_method,
                is_price_signal,
                contract_source_sha256,
                item_source_sha256,
                result_source_sha256
            FROM gold_price_signals
            WHERE {where_sql}
              AND is_price_signal
            ORDER BY
                ABS(COALESCE(modified_z_score, 0)) DESC,
                analysis_date DESC NULLS LAST,
                award_key
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
        row["pncp_url"] = _pncp_procurement_url(row.get("procurement_key"))

    return {
        "product_id": product_id,
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
        "disclaimer": _SIGNAL_DISCLAIMER,
    }

def analytics_product_records(
    database_path: str | Path,
    *,
    product_id: str,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    path = _require_database(database_path)
    if len(product_id) != 32:
        raise ValueError("product_id inválido")
    if limit < 1 or limit > 100:
        raise ValueError("limit deve estar entre 1 e 100")
    if offset < 0:
        raise ValueError("offset não pode ser negativo")

    identity = _product_identity_expression()
    filter_clauses, parameters = _award_filter_sql(
        identity=identity,
        product_id=product_id,
        state_code=state_code,
        macroregion=macroregion,
        supplier=supplier,
        buyer=buyer,
        start_date=start_date,
        end_date=end_date,
    )
    where_sql = " AND ".join(filter_clauses)

    with duckdb.connect(str(path), read_only=True) as connection:
        total = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM silver_awards
            WHERE {where_sql}
            """,
            parameters,
        ).fetchone()[0]
        if not total:
            raise LookupError("Produto não encontrado para os filtros informados")

        cursor = connection.execute(
            f"""
            SELECT
                award_key,
                procurement_key,
                item_number,
                result_sequence,
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
                procurement_unit,
                package_count,
                unit_quantity_value,
                unit_quantity_unit,
                normalized_quantity_value,
                normalized_quantity_unit,
                supplier_name,
                supplier_document,
                brand,
                organization_cnpj,
                organization_name,
                buyer_unit_code,
                buyer_unit_name,
                municipality_name,
                state_code,
                macroregion,
                modality,
                analysis_date,
                awarded_unit_value,
                awarded_quantity,
                awarded_total_value,
                awarded_price_per_base_unit,
                price_normalization_status,
                price_normalization_reason,
                contract_source_sha256,
                item_source_sha256,
                result_source_sha256
            FROM silver_awards
            WHERE {where_sql}
            ORDER BY
                analysis_date DESC NULLS LAST,
                procurement_key,
                item_number,
                award_key
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
        row["pncp_url"] = _pncp_procurement_url(row.get("procurement_key"))

    return {
        "product_id": product_id,
        "items": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

def analytics_product_records_export(
    database_path: str | Path,
    *,
    product_id: str,
    state_code: str | None = None,
    macroregion: str | None = None,
    supplier: str | None = None,
    buyer: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    offset = 0

    while True:
        page = analytics_product_records(
            database_path,
            product_id=product_id,
            state_code=state_code,
            macroregion=macroregion,
            supplier=supplier,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date,
            limit=100,
            offset=offset,
        )
        page_items = page["items"]
        items.extend(page_items)

        if len(items) >= page["total"] or not page_items:
            break
        offset += len(page_items)

    return items


