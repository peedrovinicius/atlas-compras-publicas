from pathlib import Path
from typing import Any

import duckdb


def build_quality_views(database_path: str | Path) -> None:
    """Cria visões auditáveis de cobertura e qualidade do normalizador."""

    with duckdb.connect(str(database_path)) as connection:
        exists = connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'silver_items'
            """
        ).fetchone()[0]

        if not exists:
            raise ValueError(
                "A tabela silver_items não existe. Execute build-analytics primeiro."
            )

        column_types = {
            row[1]: str(row[2]).upper()
            for row in connection.execute(
                "PRAGMA table_info('silver_items')"
            ).fetchall()
        }
        price_type = column_types.get("normalized_price_per_base_unit", "")
        estimated_type = column_types.get("estimated_unit_value", "")
        if not price_type.startswith("DECIMAL(") or not estimated_type.startswith(
            "DECIMAL("
        ):
            raise ValueError(
                "silver_items precisa ser reconstruída com precisão decimal."
            )

        connection.execute("DROP VIEW IF EXISTS normalization_quality_summary")
        connection.execute("DROP VIEW IF EXISTS normalization_quality_by_category")
        connection.execute("DROP VIEW IF EXISTS unrecognized_items")

        connection.execute(
            """
            CREATE VIEW normalization_quality_summary AS
            SELECT
                COUNT(*) AS total_items,
                SUM(CASE WHEN category_identified THEN 1 ELSE 0 END)
                    AS category_identified_items,
                ROUND(
                    100.0 * SUM(CASE WHEN category_identified THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS category_coverage_percent,
                SUM(CASE WHEN presentation_identified THEN 1 ELSE 0 END)
                    AS presentation_identified_items,
                ROUND(
                    100.0 * SUM(CASE WHEN presentation_identified THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS presentation_coverage_percent,
                SUM(CASE WHEN measurement_identified THEN 1 ELSE 0 END)
                    AS measurement_identified_items,
                ROUND(
                    100.0 * SUM(CASE WHEN measurement_identified THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS measurement_coverage_percent,
                SUM(CASE WHEN fully_structured THEN 1 ELSE 0 END)
                    AS fully_structured_items,
                ROUND(
                    100.0 * SUM(CASE WHEN fully_structured THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS fully_structured_percent,
                COUNT(normalized_price_per_base_unit) AS price_normalizable_items,
                ROUND(
                    100.0 * COUNT(normalized_price_per_base_unit)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS price_normalizable_percent,
                SUM(
                    CASE WHEN price_normalization_status = 'defensible'
                    THEN 1 ELSE 0 END
                ) AS price_basis_defensible_items,
                SUM(
                    CASE WHEN price_normalization_status = 'review'
                    THEN 1 ELSE 0 END
                ) AS price_basis_review_items,
                SUM(
                    CASE WHEN price_normalization_status = 'unavailable'
                    THEN 1 ELSE 0 END
                ) AS price_basis_unavailable_items,
                ROUND(AVG(normalization_quality_score), 3)
                    AS average_quality_score
            FROM silver_items
            """
        )

        connection.execute(
            """
            CREATE VIEW normalization_quality_by_category AS
            SELECT
                product_category,
                COUNT(*) AS item_count,
                ROUND(AVG(normalization_quality_score), 3)
                    AS average_quality_score,
                SUM(CASE WHEN fully_structured THEN 1 ELSE 0 END)
                    AS fully_structured_items,
                ROUND(
                    100.0 * SUM(CASE WHEN fully_structured THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS fully_structured_percent,
                COUNT(normalized_price_per_base_unit) AS price_normalizable_items,
                SUM(
                    CASE WHEN price_normalization_status = 'defensible'
                    THEN 1 ELSE 0 END
                ) AS price_basis_defensible_items,
                SUM(
                    CASE WHEN price_normalization_status = 'review'
                    THEN 1 ELSE 0 END
                ) AS price_basis_review_items,
                SUM(
                    CASE WHEN price_normalization_status = 'unavailable'
                    THEN 1 ELSE 0 END
                ) AS price_basis_unavailable_items
            FROM silver_items
            GROUP BY product_category
            ORDER BY item_count DESC, product_category
            """
        )

        connection.execute(
            """
            CREATE VIEW unrecognized_items AS
            SELECT
                item_number,
                original_description,
                procurement_unit,
                estimated_unit_value,
                normalization_quality_score,
                missing_fields,
                source_sha256
            FROM silver_items
            WHERE NOT category_identified
            ORDER BY
                estimated_unit_value DESC NULLS LAST,
                item_number
            """
        )


def quality_summary(database_path: str | Path) -> dict[str, Any]:
    build_quality_views(database_path)

    with duckdb.connect(str(database_path), read_only=True) as connection:
        cursor = connection.execute("SELECT * FROM normalization_quality_summary")
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()

    return dict(zip(columns, row, strict=True))


def quality_by_category(database_path: str | Path) -> list[dict[str, Any]]:
    build_quality_views(database_path)

    with duckdb.connect(str(database_path), read_only=True) as connection:
        cursor = connection.execute(
            "SELECT * FROM normalization_quality_by_category"
        )
        columns = [column[0] for column in cursor.description]
        return [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]


def unrecognized_items(
    database_path: str | Path,
    *,
    limit: int = 50,
) -> list[dict[str, Any]]:
    if limit < 1:
        raise ValueError("limit deve ser pelo menos 1")

    build_quality_views(database_path)

    with duckdb.connect(str(database_path), read_only=True) as connection:
        cursor = connection.execute(
            "SELECT * FROM unrecognized_items LIMIT ?",
            [limit],
        )
        columns = [column[0] for column in cursor.description]
        return [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]
