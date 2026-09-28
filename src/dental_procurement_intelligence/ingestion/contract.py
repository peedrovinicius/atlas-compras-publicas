import json
from dataclasses import dataclass

from dental_procurement_intelligence.ingestion.bundle import (
    build_contract_bundle,
    write_contract_bundle,
)
from dental_procurement_intelligence.ingestion.evidence import EvidenceRecord, EvidenceStore
from dental_procurement_intelligence.pncp import PNCPClient, PNCPItem


@dataclass(frozen=True, slots=True)
class ContractCaptureResult:
    procurement_key: str
    bundle_manifest_path: str
    item_count: int
    result_response_count: int
    result_count: int
    contract_evidence: EvidenceRecord
    item_evidence: EvidenceRecord
    result_evidence: tuple[EvidenceRecord, ...]
    item_page_evidence: tuple[EvidenceRecord, ...] = ()

    @property
    def all_item_evidence(self) -> tuple[EvidenceRecord, ...]:
        return (self.item_evidence, *self.item_page_evidence)


def _count_results(content: bytes) -> int:
    if not content.strip():
        return 0
    payload = json.loads(content)
    records = payload.get("listaResultados") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError("Resposta de resultados do PNCP em formato inesperado")
    return len(records)


def capture_contract(
    client: PNCPClient,
    store: EvidenceStore,
    *,
    cnpj: str,
    year: int,
    sequence: int,
) -> ContractCaptureResult:
    """Captura metadados, itens, resultados e manifesto estável da contratação."""

    raw_contract = client.get_contract_raw(cnpj, year, sequence)
    contract_evidence = store.capture(raw_contract)

    raw_item_pages = client.get_item_pages_raw(cnpj, year, sequence)
    if not raw_item_pages:
        raise ValueError("PNCP não retornou evidência para os itens")

    item_records = tuple(store.capture(raw) for raw in raw_item_pages)
    item_evidence = item_records[0]
    item_page_evidence = item_records[1:]

    items: list[PNCPItem] = []
    seen_item_numbers: set[int] = set()

    for raw_items in raw_item_pages:
        payload = json.loads(raw_items.content)
        if not isinstance(payload, list):
            raise ValueError("Resposta de itens do PNCP em formato inesperado")

        for record in payload:
            item = PNCPItem.model_validate(record)
            if item.item_number in seen_item_numbers:
                raise ValueError(
                    f"Item PNCP duplicado entre páginas: {item.item_number}"
                )
            seen_item_numbers.add(item.item_number)
            items.append(item)
    result_evidence: list[EvidenceRecord] = []
    result_count = 0

    for item in items:
        if item.has_result is False:
            continue

        raw_result = client.get_item_results_raw(
            cnpj,
            year,
            sequence,
            item.item_number,
        )
        result_count += _count_results(raw_result.content)
        result_evidence.append(store.capture(raw_result))

    bundle = build_contract_bundle(
        cnpj=cnpj,
        year=year,
        sequence=sequence,
        contract_evidence=contract_evidence,
        item_evidence=item_evidence,
        result_evidence=tuple(result_evidence),
        item_page_evidence=item_page_evidence,
    )
    bundle_path = write_contract_bundle(store, bundle)

    return ContractCaptureResult(
        procurement_key=bundle.procurement_key,
        bundle_manifest_path=bundle_path.as_posix(),
        item_count=len(items),
        result_response_count=len(result_evidence),
        result_count=result_count,
        contract_evidence=contract_evidence,
        item_evidence=item_evidence,
        result_evidence=tuple(result_evidence),
        item_page_evidence=item_page_evidence,
    )
