import json
from dataclasses import dataclass

from dental_procurement_intelligence.ingestion.evidence import EvidenceRecord, EvidenceStore
from dental_procurement_intelligence.pncp import PNCPClient, PNCPItem


@dataclass(frozen=True, slots=True)
class ContractCaptureResult:
    item_count: int
    result_response_count: int
    result_count: int
    item_evidence: EvidenceRecord
    result_evidence: tuple[EvidenceRecord, ...]


def _count_results(content: bytes) -> int:
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
    """Captura itens e todas as respostas de resultados de uma contratação."""

    raw_items = client.get_items_raw(cnpj, year, sequence)
    item_evidence = store.capture(raw_items)
    payload = json.loads(raw_items.content)

    if not isinstance(payload, list):
        raise ValueError("Resposta de itens do PNCP em formato inesperado")

    items = [PNCPItem.model_validate(record) for record in payload]
    result_evidence: list[EvidenceRecord] = []
    result_count = 0

    for item in items:
        raw_result = client.get_item_results_raw(
            cnpj,
            year,
            sequence,
            item.item_number,
        )
        result_count += _count_results(raw_result.content)
        result_evidence.append(store.capture(raw_result))

    return ContractCaptureResult(
        item_count=len(items),
        result_response_count=len(result_evidence),
        result_count=result_count,
        item_evidence=item_evidence,
        result_evidence=tuple(result_evidence),
    )
