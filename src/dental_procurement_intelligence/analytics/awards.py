import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import duckdb
import polars as pl

from dental_procurement_intelligence.identity import parse_product
from dental_procurement_intelligence.pncp import PNCPItem, PNCPItemResult


AWARD_SCHEMA: dict[str, pl.DataType] = {
    "item_source_sha256": pl.String,
    "result_source_sha256": pl.String,
    "item_number": pl.Int64,
    "result_sequence": pl.Int64,
    "original_description": pl.String,
    "product_category": pl.String,
    "presentation": pl.String,
    "shade": pl.String,
    "supplier_name": pl.String,
    "supplier_document": pl.String,
    "brand": pl.String,
    "result_date": pl.Date,
    "result_status_id": pl.Int64,
    "result_status_name": pl.String,
    "estimated_unit_value": pl.Float64,
    "awarded_unit_value": pl.Float64,
    "awarded_quantity": pl.Float64,
    "awarded_total_value": pl.Float64,
    "estimated_total_equivalent": pl.Float64,
    "economy_total": pl.Float64,
    "economy_percent": pl.Float64,
    "normalized_quantity_value": pl.Float64,
    "normalized_quantity_unit": pl.String,
    "estimated_price_per_base_unit": pl.Float64,
    "awarded_price_per_base_unit": pl.Float64,
}


@dataclass(frozen=True, slots=True)
class AwardBuildResult:
    row_count: int
    active_result_count: int
    item_source_sha256: str
    result_source_count: int
    parquet_path: str
    database_path: str


def _hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _result_records(payload: Any) -> list[dict[str, Any]]:
    records = payload.get("listaResultados") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError("O arquivo bruto de resultados deve conter uma lista de resultados")
    if not all(isinstance(record, dict) for record in records):
        raise ValueError("Todos os resultados do PNCP devem ser objetos JSON")
    return records


def load_raw_items(path: str | Path) -> tuple[list[PNCPItem], str]:
    content = Path(path).read_bytes()
    payload = json.loads(content)
    if not isinstance(payload, list):
        raise ValueError("O arquivo bruto de itens deve conter um array JSON")
    return [PNCPItem.model_validate(record) for record in payload], _hash(content)


def load_raw_results(path: str | Path) -> tuple[list[PNCPItemResult], str]:
    content = Path(path).read_bytes()
    payload = json.loads(content)
    records = _result_records(payload)
    return [PNCPItemResult.model_validate(record) for record in records], _hash(content)


def _decimal_float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def build_award_frame(
    items: list[PNCPItem],
    item_source_sha256: str,
    result_sources: list[tuple[list[PNCPItemResult], str]],
) -> pl.DataFrame:
    item_by_number = {item.item_number: item for item in items}
    rows: list[dict[str, Any]] = []

    for results, result_sha256 in result_sources:
        for result in results:
            if result.status_id == 2:
                continue

            item = item_by_number.get(result.item_number)
            if item is None:
                raise ValueError(
                    f"Resultado referencia item inexistente: {result.item_number}"
                )

            product = parse_product(item.description)
            basis = product.total_quantity or product.unit_quantity
            awarded_total = result.awarded_total_value
            if (
                awarded_total is None
                and result.awarded_unit_value is not None
                and result.awarded_quantity is not None
            ):
                awarded_total = result.awarded_unit_value * result.awarded_quantity

            estimated_total_equivalent = None
            economy_total = None
            economy_percent = None
            if (
                item.estimated_unit_value is not None
                and result.awarded_quantity is not None
            ):
                estimated_total_equivalent = (
                    item.estimated_unit_value * result.awarded_quantity
                )
                if awarded_total is not None:
                    economy_total = estimated_total_equivalent - awarded_total
                    if estimated_total_equivalent != 0:
                        economy_percent = (
                            economy_total / estimated_total_equivalent
                        ) * Decimal("100")

            estimated_normalized = None
            awarded_normalized = None
            if basis is not None and basis.value > 0:
                if item.estimated_unit_value is not None:
                    estimated_normalized = item.estimated_unit_value / basis.value
                if result.awarded_unit_value is not None:
                    awarded_normalized = result.awarded_unit_value / basis.value

            rows.append(
                {
                    "item_source_sha256": item_source_sha256,
                    "result_source_sha256": result_sha256,
                    "item_number": item.item_number,
                    "result_sequence": result.result_sequence,
                    "original_description": item.description,
                    "product_category": product.category.value,
                    "presentation": product.presentation,
                    "shade": product.shade,
                    "supplier_name": result.supplier_name,
                    "supplier_document": result.supplier_document,
                    "brand": result.brand,
                    "result_date": result.result_date,
                    "result_status_id": result.status_id,
                    "result_status_name": result.status_name,
                    "estimated_unit_value": _decimal_float(item.estimated_unit_value),
                    "awarded_unit_value": _decimal_float(result.awarded_unit_value),
                    "awarded_quantity": _decimal_float(result.awarded_quantity),
                    "awarded_total_value": _decimal_float(awarded_total),
                    "estimated_total_equivalent": _decimal_float(
                        estimated_total_equivalent
                    ),
                    "economy_total": _decimal_float(economy_total),
                    "economy_percent": _decimal_float(economy_percent),
                    "normalized_quantity_value": (
                        float(basis.value) if basis is not None else None
                    ),
                    "normalized_quantity_unit": (
                        basis.unit if basis is not None else None
                    ),
                    "estimated_price_per_base_unit": _decimal_float(
                        estimated_normalized
                    ),
                    "awarded_price_per_base_unit": _decimal_float(
                        awarded_normalized
                    ),
                }
            )

    return pl.DataFrame(rows, schema=AWARD_SCHEMA)


def build_awards(
    items_raw_path: str | Path,
    results_raw_paths: list[str | Path],
    parquet_path: str | Path,
    database_path: str | Path,
) -> AwardBuildResult:
    items, item_sha256 = load_raw_items(items_raw_path)
    sources = [load_raw_results(path) for path in results_raw_paths]
    frame = build_award_frame(items, item_sha256, sources)

    parquet = Path(parquet_path)
    parquet.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(parquet, compression="zstd", statistics=True)

    database = Path(database_path)
    database.parent.mkdir(parents=True, exist_ok=True)
    source = str(parquet.resolve()).replace("'", "''")

    with duckdb.connect(str(database)) as connection:
        connection.execute("DROP VIEW IF EXISTS award_savings_summary")
        connection.execute("DROP TABLE IF EXISTS silver_awards")
        connection.execute(
            f"CREATE TABLE silver_awards AS SELECT * FROM read_parquet('{source}')"
        )
        connection.execute(
            """
            CREATE VIEW award_savings_summary AS
            SELECT
                product_category,
                COUNT(*) AS result_count,
                SUM(estimated_total_equivalent) AS estimated_total_equivalent,
                SUM(awarded_total_value) AS awarded_total_value,
                SUM(economy_total) AS economy_total,
                CASE
                    WHEN SUM(estimated_total_equivalent) = 0 THEN NULL
                    ELSE
                        100.0 * SUM(economy_total)
                        / SUM(estimated_total_equivalent)
                END AS economy_percent
            FROM silver_awards
            GROUP BY product_category
            ORDER BY ABS(COALESCE(SUM(economy_total), 0)) DESC
            """
        )

    return AwardBuildResult(
        row_count=frame.height,
        active_result_count=frame.height,
        item_source_sha256=item_sha256,
        result_source_count=len(sources),
        parquet_path=parquet.as_posix(),
        database_path=database.as_posix(),
    )


def award_summary(database_path: str | Path) -> list[dict[str, Any]]:
    with duckdb.connect(str(database_path), read_only=True) as connection:
        cursor = connection.execute("SELECT * FROM award_savings_summary")
        columns = [column[0] for column in cursor.description]
        return [
            dict(zip(columns, row, strict=True))
            for row in cursor.fetchall()
        ]
