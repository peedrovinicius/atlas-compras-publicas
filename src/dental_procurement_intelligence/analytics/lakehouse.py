import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import polars as pl

from dental_procurement_intelligence.analytics.numeric import (
    ANALYTIC_DECIMAL_DTYPE,
    analytic_decimal,
)
from dental_procurement_intelligence.identity import (
    ProductCategory,
    assess_normalization_quality,
    assess_price_normalization,
    parse_product,
)
from dental_procurement_intelligence.pncp import PNCPItem

ANALYTICAL_SCHEMA: dict[str, pl.DataType] = {
    "procurement_key": pl.String,
    "source_sha256": pl.String,
    "item_number": pl.Int64,
    "original_description": pl.String,
    "normalized_description": pl.String,
    "procurement_quantity_decimal": pl.String,
    "procurement_quantity": pl.Float64,
    "procurement_unit": pl.String,
    "estimated_unit_value_decimal": pl.String,
    "estimated_unit_value": ANALYTIC_DECIMAL_DTYPE,
    "total_value_decimal": pl.String,
    "total_value": ANALYTIC_DECIMAL_DTYPE,
    "product_category": pl.String,
    "identity_status": pl.String,
    "classification_method": pl.String,
    "matched_terms_count": pl.Int64,
    "presentation": pl.String,
    "shade": pl.String,
    "concentration_percent": pl.Float64,
    "technical_attribute_count": pl.Int64,
    "resin_technology": pl.String,
    "curing_mode": pl.String,
    "adhesive_strategy": pl.String,
    "ionomer_use": pl.String,
    "fluoride_formulation": pl.String,
    "anesthetic_active_ingredient": pl.String,
    "anesthetic_vasoconstrictor": pl.String,
    "package_count": pl.Int64,
    "measurement_candidate_count": pl.Int64,
    "measurement_resolution": pl.String,
    "unit_quantity_value": pl.Float64,
    "unit_quantity_unit": pl.String,
    "normalized_total_quantity_value": pl.Float64,
    "normalized_total_quantity_unit": pl.String,
    "normalized_price_per_base_unit": ANALYTIC_DECIMAL_DTYPE,
    "price_normalization_status": pl.String,
    "price_normalization_reason": pl.String,
    "category_identified": pl.Boolean,
    "presentation_identified": pl.Boolean,
    "measurement_identified": pl.Boolean,
    "critical_attribute_name": pl.String,
    "critical_attribute_identified": pl.Boolean,
    "normalization_quality_score": pl.Float64,
    "normalization_quality_level": pl.String,
    "fully_structured": pl.Boolean,
    "missing_fields": pl.String,
}


@dataclass(frozen=True, slots=True)
class AnalyticsBuildResult:
    source_sha256: str
    row_count: int
    identified_row_count: int
    priced_row_count: int
    fully_structured_row_count: int
    average_quality_score: float | None
    parquet_path: str
    database_path: str


def _decimal_to_text(value: Any) -> str | None:
    return format(value, "f") if value is not None else None


def build_item_frame(
    items: list[PNCPItem],
    *,
    source_sha256: str,
    procurement_key: str | None = None,
) -> pl.DataFrame:
    """Constrói a representação analítica silver dos itens de contratação."""

    rows: list[dict[str, Any]] = []

    for item in items:
        product = parse_product(item.description)
        quality = assess_normalization_quality(product)
        price_assessment = assess_price_normalization(product, item.unit)
        price_basis = price_assessment.basis
        normalized_price = None

        if (
            item.estimated_unit_value is not None
            and price_basis is not None
            and price_basis.value > 0
        ):
            normalized_price = analytic_decimal(
                item.estimated_unit_value / price_basis.value
            )

        rows.append(
            {
                "procurement_key": procurement_key,
                "source_sha256": source_sha256,
                "item_number": item.item_number,
                "original_description": item.description,
                "normalized_description": product.normalized_description,
                "procurement_quantity_decimal": _decimal_to_text(item.quantity),
                "procurement_quantity": (
                    float(item.quantity) if item.quantity is not None else None
                ),
                "procurement_unit": item.unit,
                "estimated_unit_value_decimal": _decimal_to_text(
                    item.estimated_unit_value
                ),
                "estimated_unit_value": analytic_decimal(item.estimated_unit_value),
                "total_value_decimal": _decimal_to_text(item.total_value),
                "total_value": analytic_decimal(item.total_value),
                "product_category": product.category.value,
                "identity_status": (
                    "identified"
                    if product.category != ProductCategory.UNKNOWN
                    else "unknown"
                ),
                "classification_method": "deterministic_rule",
                "matched_terms_count": len(product.matched_terms),
                "presentation": product.presentation,
                "shade": product.shade,
                "concentration_percent": (
                    float(product.concentration_percent)
                    if product.concentration_percent is not None
                    else None
                ),
                "technical_attribute_count": (
                    product.technical_attributes.identified_count()
                ),
                "resin_technology": (
                    product.technical_attributes.resin_technology
                ),
                "curing_mode": product.technical_attributes.curing_mode,
                "adhesive_strategy": (
                    product.technical_attributes.adhesive_strategy
                ),
                "ionomer_use": product.technical_attributes.ionomer_use,
                "fluoride_formulation": (
                    product.technical_attributes.fluoride_formulation
                ),
                "anesthetic_active_ingredient": (
                    product.technical_attributes.anesthetic_active_ingredient
                ),
                "anesthetic_vasoconstrictor": (
                    product.technical_attributes.anesthetic_vasoconstrictor
                ),
                "package_count": product.package_count,
                "measurement_candidate_count": len(product.measurement_candidates),
                "measurement_resolution": product.measurement_resolution,
                "unit_quantity_value": (
                    float(product.unit_quantity.value)
                    if product.unit_quantity is not None
                    else None
                ),
                "unit_quantity_unit": (
                    product.unit_quantity.unit
                    if product.unit_quantity is not None
                    else None
                ),
                "normalized_total_quantity_value": (
                    float(price_basis.value) if price_basis is not None else None
                ),
                "normalized_total_quantity_unit": (
                    price_basis.unit if price_basis is not None else None
                ),
                "normalized_price_per_base_unit": normalized_price,
                "price_normalization_status": price_assessment.status.value,
                "price_normalization_reason": price_assessment.reason,
                "category_identified": quality.category_identified,
                "presentation_identified": quality.presentation_identified,
                "measurement_identified": quality.measurement_identified,
                "critical_attribute_name": quality.critical_attribute_name,
                "critical_attribute_identified": (
                    quality.critical_attribute_identified
                ),
                "normalization_quality_score": float(quality.score),
                "normalization_quality_level": quality.level,
                "fully_structured": quality.fully_structured,
                "missing_fields": ",".join(quality.missing_fields),
            }
        )

    return pl.DataFrame(rows, schema=ANALYTICAL_SCHEMA)


def load_raw_items(path: str | Path) -> tuple[list[PNCPItem], str]:
    """Carrega um JSON bruto do PNCP e calcula o SHA-256 usado na rastreabilidade."""

    raw_path = Path(path)
    content = raw_path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    payload = json.loads(content)

    if not isinstance(payload, list):
        raise ValueError("O arquivo bruto de itens do PNCP deve conter um array JSON")

    return [PNCPItem.model_validate(record) for record in payload], digest


def write_parquet(frame: pl.DataFrame, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(output, compression="zstd", statistics=True)
    return output


class DuckDBWarehouse:
    """Catálogo analítico local baseado em DuckDB."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    @staticmethod
    def _sql_literal(value: str | Path) -> str:
        return str(value).replace("'", "''")

    def ingest_parquet(self, parquet_path: str | Path) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        source = self._sql_literal(Path(parquet_path).resolve())

        with duckdb.connect(str(self.path)) as connection:
            connection.execute("DROP VIEW IF EXISTS category_price_summary")
            connection.execute("DROP TABLE IF EXISTS silver_items")
            connection.execute(
                f"CREATE TABLE silver_items AS "
                f"SELECT * FROM read_parquet('{source}')"
            )
            connection.execute(
                """
                CREATE VIEW category_price_summary AS
                SELECT
                    product_category,
                    COUNT(*) AS item_count,
                    COUNT(normalized_price_per_base_unit) AS priced_item_count,
                    MEDIAN(normalized_price_per_base_unit) AS median_normalized_price,
                    MIN(normalized_price_per_base_unit) AS min_normalized_price,
                    MAX(normalized_price_per_base_unit) AS max_normalized_price
                FROM silver_items
                GROUP BY product_category
                ORDER BY item_count DESC, product_category
                """
            )

    def summary(self) -> list[dict[str, Any]]:
        with duckdb.connect(str(self.path), read_only=True) as connection:
            column_types = {
                row[1]: str(row[2]).upper()
                for row in connection.execute(
                    "PRAGMA table_info('silver_items')"
                ).fetchall()
            }
            price_type = column_types.get("normalized_price_per_base_unit", "")
            if not price_type.startswith("DECIMAL("):
                raise ValueError(
                    "silver_items precisa ser reconstruída com precisão decimal."
                )

            cursor = connection.execute("SELECT * FROM category_price_summary")
            columns = [column[0] for column in cursor.description]
            return [
                dict(zip(columns, row, strict=True))
                for row in cursor.fetchall()
            ]


def _publish_analytics_frame(
    frame: pl.DataFrame,
    source_sha256: str,
    parquet_path: str | Path,
    database_path: str | Path,
) -> AnalyticsBuildResult:
    parquet = write_parquet(frame, parquet_path)

    warehouse = DuckDBWarehouse(database_path)
    warehouse.ingest_parquet(parquet)

    identified = frame.filter(pl.col("identity_status") == "identified").height
    priced = frame.filter(
        pl.col("normalized_price_per_base_unit").is_not_null()
    ).height
    fully_structured = frame.filter(pl.col("fully_structured")).height
    average_quality = (
        frame.select(pl.col("normalization_quality_score").mean()).item()
        if frame.height
        else None
    )

    return AnalyticsBuildResult(
        source_sha256=source_sha256,
        row_count=frame.height,
        identified_row_count=identified,
        priced_row_count=priced,
        fully_structured_row_count=fully_structured,
        average_quality_score=average_quality,
        parquet_path=parquet.as_posix(),
        database_path=Path(database_path).as_posix(),
    )


def build_analytics_dataset(
    raw_paths: list[str | Path],
    parquet_path: str | Path,
    database_path: str | Path,
    *,
    procurement_key_by_path: dict[str, str] | None = None,
) -> AnalyticsBuildResult:
    if not raw_paths:
        raise ValueError("Nenhuma página bruta de itens foi informada")

    frames: list[pl.DataFrame] = []
    source_hashes: list[str] = []

    for raw_path in raw_paths:
        items, source_sha256 = load_raw_items(raw_path)
        source_hashes.append(source_sha256)
        resolved_path = Path(raw_path).as_posix()
        procurement_key = (
            procurement_key_by_path.get(resolved_path)
            if procurement_key_by_path is not None
            else None
        )
        frames.append(
            build_item_frame(
                items,
                source_sha256=source_sha256,
                procurement_key=procurement_key,
            )
        )

    frame = pl.concat(frames, how="vertical")
    if frame.height:
        keyed = frame.filter(pl.col("procurement_key").is_not_null())
        unkeyed = frame.filter(pl.col("procurement_key").is_null())

        if keyed.height:
            unique_keyed_items = keyed.select(
                pl.struct(["procurement_key", "item_number"]).n_unique()
            ).item()
            if unique_keyed_items != keyed.height:
                raise ValueError(
                    "Dataset de itens contém chave "
                    "(procurement_key, item_number) duplicada"
                )

        if unkeyed.height:
            unique_unkeyed_items = unkeyed.select(
                pl.col("item_number").n_unique()
            ).item()
            if unique_unkeyed_items != unkeyed.height:
                raise ValueError(
                    "Dataset legado sem procurement_key contém "
                    "item_number duplicado"
                )

    frame = frame.sort(["procurement_key", "item_number"], nulls_last=True)
    dataset_sha256 = hashlib.sha256(
        "".join(source_hashes).encode("ascii")
    ).hexdigest()

    return _publish_analytics_frame(
        frame,
        dataset_sha256,
        parquet_path,
        database_path,
    )


def build_analytics(
    raw_path: str | Path,
    parquet_path: str | Path,
    database_path: str | Path,
) -> AnalyticsBuildResult:
    return build_analytics_dataset(
        [raw_path],
        parquet_path,
        database_path,
    )
