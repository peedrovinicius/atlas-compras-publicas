import hashlib
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import duckdb
import polars as pl

from dental_procurement_intelligence.analytics.numeric import (
    ANALYTIC_DECIMAL_DTYPE,
    analytic_decimal,
)
from dental_procurement_intelligence.identity import (
    assess_price_normalization,
    parse_product,
)
from dental_procurement_intelligence.ingestion.bundle import (
    ContractBundle,
    load_contract_bundle,
)
from dental_procurement_intelligence.normalization import macroregion_from_state
from dental_procurement_intelligence.pncp import (
    PNCPContract,
    PNCPItem,
    PNCPItemResult,
    procurement_key_from_contract,
)
from dental_procurement_intelligence.pncp import (
    award_key as stable_award_key,
)

AWARD_SCHEMA: dict[str, pl.DataType] = {
    "procurement_key": pl.String,
    "award_key": pl.String,
    "contract_source_sha256": pl.String,
    "item_source_sha256": pl.String,
    "result_source_sha256": pl.String,
    "item_number": pl.Int64,
    "result_sequence": pl.Int64,
    "original_description": pl.String,
    "product_category": pl.String,
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
    "procurement_unit": pl.String,
    "package_count": pl.Int64,
    "measurement_candidate_count": pl.Int64,
    "measurement_resolution": pl.String,
    "unit_quantity_value": pl.Float64,
    "unit_quantity_unit": pl.String,
    "supplier_name": pl.String,
    "supplier_document": pl.String,
    "brand": pl.String,
    "result_date": pl.Date,
    "publication_date": pl.Date,
    "analysis_date": pl.Date,
    "analysis_year": pl.Int64,
    "analysis_quarter": pl.String,
    "municipality_ibge": pl.String,
    "municipality_name": pl.String,
    "state_code": pl.String,
    "macroregion": pl.String,
    "government_sphere": pl.String,
    "modality": pl.String,
    "result_status_id": pl.Int64,
    "result_status_name": pl.String,
    "estimated_unit_value": ANALYTIC_DECIMAL_DTYPE,
    "awarded_unit_value": ANALYTIC_DECIMAL_DTYPE,
    "awarded_quantity": pl.Float64,
    "awarded_total_value": ANALYTIC_DECIMAL_DTYPE,
    "estimated_total_equivalent": ANALYTIC_DECIMAL_DTYPE,
    "economy_total": ANALYTIC_DECIMAL_DTYPE,
    "economy_percent": ANALYTIC_DECIMAL_DTYPE,
    "normalized_quantity_value": pl.Float64,
    "normalized_quantity_unit": pl.String,
    "estimated_price_per_base_unit": ANALYTIC_DECIMAL_DTYPE,
    "awarded_price_per_base_unit": ANALYTIC_DECIMAL_DTYPE,
    "price_normalization_status": pl.String,
    "price_normalization_reason": pl.String,
}


@dataclass(frozen=True, slots=True)
class AwardBuildResult:
    row_count: int
    active_result_count: int
    item_source_sha256: str
    contract_source_sha256: str | None
    result_source_count: int
    geolocated_row_count: int
    dated_row_count: int
    parquet_path: str
    database_path: str


@dataclass(frozen=True, slots=True)
class AwardDatasetBuildResult:
    row_count: int
    procurement_count: int
    manifest_count: int
    superseded_manifest_count: int
    geolocated_row_count: int
    dated_row_count: int
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


def load_raw_contract(path: str | Path) -> tuple[PNCPContract, str]:
    content = Path(path).read_bytes()
    payload = json.loads(content)
    if not isinstance(payload, dict):
        raise ValueError("O arquivo bruto da contratação deve conter um objeto JSON")
    return PNCPContract.model_validate(payload), _hash(content)


def load_raw_items(path: str | Path) -> tuple[list[PNCPItem], str]:
    content = Path(path).read_bytes()
    payload = json.loads(content)
    if not isinstance(payload, list):
        raise ValueError("O arquivo bruto de itens deve conter um array JSON")
    return [PNCPItem.model_validate(record) for record in payload], _hash(content)


def load_raw_results(path: str | Path) -> tuple[list[PNCPItemResult], str]:
    content = Path(path).read_bytes()
    if not content.strip():
        return [], _hash(content)
    payload = json.loads(content)
    records = _result_records(payload)
    return [PNCPItemResult.model_validate(record) for record in records], _hash(content)


def _quarter(value: date | None) -> str | None:
    if value is None:
        return None
    quarter = ((value.month - 1) // 3) + 1
    return f"{value.year}-T{quarter}"


def build_award_frame(
    items: list[PNCPItem],
    item_source_sha256: str,
    result_sources: list[tuple[list[PNCPItemResult], str]],
    *,
    item_source_sha256_by_number: dict[int, str] | None = None,
    contract: PNCPContract | None = None,
    contract_source_sha256: str | None = None,
    procurement_key: str | None = None,
) -> pl.DataFrame:
    item_by_number = {item.item_number: item for item in items}
    rows: list[dict[str, Any]] = []

    resolved_procurement_key = procurement_key
    if resolved_procurement_key is None and contract is not None:
        resolved_procurement_key = procurement_key_from_contract(contract)

    unit = contract.organization_unit if contract is not None else None
    organization = contract.organization if contract is not None else None
    publication_date = contract.publication_date if contract is not None else None
    state_code = unit.state_code if unit is not None else None

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
            price_assessment = assess_price_normalization(product, item.unit)
            basis = price_assessment.basis
            analysis_date = result.result_date or publication_date
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

            result_key = (
                stable_award_key(resolved_procurement_key, result)
                if resolved_procurement_key is not None
                else None
            )

            rows.append(
                {
                    "procurement_key": resolved_procurement_key,
                    "award_key": result_key,
                    "contract_source_sha256": contract_source_sha256,
                    "item_source_sha256": (
                        item_source_sha256_by_number.get(
                            item.item_number,
                            item_source_sha256,
                        )
                        if item_source_sha256_by_number is not None
                        else item_source_sha256
                    ),
                    "result_source_sha256": result_sha256,
                    "item_number": item.item_number,
                    "result_sequence": result.result_sequence,
                    "original_description": item.description,
                    "product_category": product.category.value,
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
                    "procurement_unit": item.unit,
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
                    "supplier_name": result.supplier_name,
                    "supplier_document": result.supplier_document,
                    "brand": result.brand,
                    "result_date": result.result_date,
                    "publication_date": publication_date,
                    "analysis_date": analysis_date,
                    "analysis_year": analysis_date.year if analysis_date else None,
                    "analysis_quarter": _quarter(analysis_date),
                    "municipality_ibge": (
                        str(unit.municipality_id)
                        if unit is not None and unit.municipality_id is not None
                        else None
                    ),
                    "municipality_name": unit.municipality_name if unit else None,
                    "state_code": state_code,
                    "macroregion": macroregion_from_state(state_code),
                    "government_sphere": organization.sphere if organization else None,
                    "modality": contract.modality_name if contract else None,
                    "result_status_id": result.status_id,
                    "result_status_name": result.status_name,
                    "estimated_unit_value": analytic_decimal(item.estimated_unit_value),
                    "awarded_unit_value": analytic_decimal(result.awarded_unit_value),
                    "awarded_quantity": (
                        float(result.awarded_quantity)
                        if result.awarded_quantity is not None
                        else None
                    ),
                    "awarded_total_value": analytic_decimal(awarded_total),
                    "estimated_total_equivalent": analytic_decimal(
                        estimated_total_equivalent
                    ),
                    "economy_total": analytic_decimal(economy_total),
                    "economy_percent": analytic_decimal(economy_percent),
                    "normalized_quantity_value": (
                        float(basis.value) if basis is not None else None
                    ),
                    "normalized_quantity_unit": (
                        basis.unit if basis is not None else None
                    ),
                    "estimated_price_per_base_unit": analytic_decimal(
                        estimated_normalized
                    ),
                    "awarded_price_per_base_unit": analytic_decimal(
                        awarded_normalized
                    ),
                    "price_normalization_status": price_assessment.status.value,
                    "price_normalization_reason": price_assessment.reason,
                }
            )

    return pl.DataFrame(rows, schema=AWARD_SCHEMA)


def _create_award_views(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute("DROP VIEW IF EXISTS award_savings_summary")
    connection.execute(
        """
        CREATE VIEW award_savings_summary AS
        SELECT
            product_category,
            macroregion,
            analysis_year,
            COUNT(*) AS result_count,
            COUNT(DISTINCT procurement_key) AS procurement_count,
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
        GROUP BY product_category, macroregion, analysis_year
        ORDER BY analysis_year DESC, product_category, macroregion
        """
    )


def _publish_award_frame(
    frame: pl.DataFrame,
    parquet_path: str | Path,
    database_path: str | Path,
) -> tuple[Path, Path]:
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
        _create_award_views(connection)

    return parquet, database


def build_awards(
    items_raw_path: str | Path,
    results_raw_paths: list[str | Path],
    parquet_path: str | Path,
    database_path: str | Path,
    *,
    contract_raw_path: str | Path | None = None,
) -> AwardBuildResult:
    items, item_sha256 = load_raw_items(items_raw_path)
    sources = [load_raw_results(path) for path in results_raw_paths]

    contract = None
    contract_sha256 = None
    if contract_raw_path is not None:
        contract, contract_sha256 = load_raw_contract(contract_raw_path)

    frame = build_award_frame(
        items,
        item_sha256,
        sources,
        contract=contract,
        contract_source_sha256=contract_sha256,
    )

    parquet, database = _publish_award_frame(
        frame,
        parquet_path,
        database_path,
    )

    geolocated = frame.filter(pl.col("state_code").is_not_null()).height
    dated = frame.filter(pl.col("analysis_date").is_not_null()).height

    return AwardBuildResult(
        row_count=frame.height,
        active_result_count=frame.height,
        item_source_sha256=item_sha256,
        contract_source_sha256=contract_sha256,
        result_source_count=len(sources),
        geolocated_row_count=geolocated,
        dated_row_count=dated,
        parquet_path=parquet.as_posix(),
        database_path=database.as_posix(),
    )


def _verify_evidence(path: str, expected_sha256: str) -> None:
    content = Path(path).read_bytes()
    actual = _hash(content)
    if actual != expected_sha256:
        raise ValueError(
            f"Evidência alterada: esperado {expected_sha256}, obtido {actual}"
        )


def _bundle_frame(bundle: ContractBundle) -> pl.DataFrame:
    _verify_evidence(
        bundle.contract_evidence.object_path,
        bundle.contract_evidence.sha256,
    )
    for evidence in bundle.all_item_evidence:
        _verify_evidence(
            evidence.object_path,
            evidence.sha256,
        )
    for evidence in bundle.result_evidence:
        _verify_evidence(evidence.object_path, evidence.sha256)

    contract, contract_sha256 = load_raw_contract(
        bundle.contract_evidence.object_path
    )
    items: list[PNCPItem] = []
    item_sha256_by_number: dict[int, str] = {}

    for evidence in bundle.all_item_evidence:
        page_items, page_sha256 = load_raw_items(evidence.object_path)
        for item in page_items:
            if item.item_number in item_sha256_by_number:
                raise ValueError(
                    f"Item duplicado entre evidências: {item.item_number}"
                )
            items.append(item)
            item_sha256_by_number[item.item_number] = page_sha256

    item_sha256 = bundle.item_evidence.sha256
    result_sources = [
        load_raw_results(evidence.object_path)
        for evidence in bundle.result_evidence
    ]

    contract_key = procurement_key_from_contract(contract)
    if (
        contract_key is not None
        and contract_key.startswith("pncp:")
        and contract_key != bundle.procurement_key
    ):
        raise ValueError(
            "Manifesto e contratação bruta possuem identidades PNCP diferentes"
        )

    return build_award_frame(
        items,
        item_sha256,
        result_sources,
        item_source_sha256_by_number=item_sha256_by_number,
        contract=contract,
        contract_source_sha256=contract_sha256,
        procurement_key=bundle.procurement_key,
    )


def _select_latest_bundles(
    manifest_paths: list[str | Path],
) -> tuple[list[ContractBundle], int]:
    selected: dict[str, ContractBundle] = {}
    superseded = 0

    for path in sorted(Path(path) for path in manifest_paths):
        bundle = load_contract_bundle(path)
        current = selected.get(bundle.procurement_key)

        if current is None:
            selected[bundle.procurement_key] = bundle
            continue

        superseded += 1
        if bundle.captured_at_utc > current.captured_at_utc:
            selected[bundle.procurement_key] = bundle
        elif (
            bundle.captured_at_utc == current.captured_at_utc
            and bundle != current
        ):
            raise ValueError(
                "Dois manifestos diferentes possuem a mesma chave e timestamp"
            )

    bundles = [selected[key] for key in sorted(selected)]
    return bundles, superseded


def build_award_dataset(
    bundle_manifest_paths: list[str | Path],
    parquet_path: str | Path,
    database_path: str | Path,
) -> AwardDatasetBuildResult:
    if not bundle_manifest_paths:
        raise ValueError("Nenhum manifesto de contratação foi informado")

    bundles, superseded = _select_latest_bundles(bundle_manifest_paths)
    frames = [_bundle_frame(bundle) for bundle in bundles]

    frame = pl.concat(frames, how="vertical") if frames else pl.DataFrame(schema=AWARD_SCHEMA)

    if frame.height:
        if frame.filter(pl.col("award_key").is_null()).height:
            raise ValueError("Dataset consolidado exige award_key em todas as linhas")
        frame = frame.unique(
            subset=["award_key"],
            keep="last",
            maintain_order=True,
        ).sort(["procurement_key", "item_number", "award_key"])

    parquet, database = _publish_award_frame(
        frame,
        parquet_path,
        database_path,
    )

    geolocated = frame.filter(pl.col("state_code").is_not_null()).height
    dated = frame.filter(pl.col("analysis_date").is_not_null()).height

    return AwardDatasetBuildResult(
        row_count=frame.height,
        procurement_count=len(bundles),
        manifest_count=len(bundle_manifest_paths),
        superseded_manifest_count=superseded,
        geolocated_row_count=geolocated,
        dated_row_count=dated,
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
