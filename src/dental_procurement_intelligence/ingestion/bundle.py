import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from dental_procurement_intelligence.ingestion.evidence import (
    EvidenceRecord,
    EvidenceStore,
)
from dental_procurement_intelligence.pncp import procurement_key


@dataclass(frozen=True, slots=True)
class ContractBundle:
    schema_version: int
    procurement_key: str
    cnpj: str
    year: int
    sequence: int
    captured_at_utc: str
    contract_evidence: EvidenceRecord
    item_evidence: EvidenceRecord
    result_evidence: tuple[EvidenceRecord, ...]
    item_page_evidence: tuple[EvidenceRecord, ...] = ()

    @property
    def all_item_evidence(self) -> tuple[EvidenceRecord, ...]:
        return (self.item_evidence, *self.item_page_evidence)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ContractBundle":
        result_records = payload.get("result_evidence", [])
        page_records = payload.get("item_page_evidence", [])
        if not isinstance(result_records, list):
            raise ValueError("result_evidence deve ser uma lista")
        if not isinstance(page_records, list):
            raise ValueError("item_page_evidence deve ser uma lista")

        return cls(
            schema_version=int(payload["schema_version"]),
            procurement_key=str(payload["procurement_key"]),
            cnpj=str(payload["cnpj"]),
            year=int(payload["year"]),
            sequence=int(payload["sequence"]),
            captured_at_utc=str(payload["captured_at_utc"]),
            contract_evidence=EvidenceRecord(**payload["contract_evidence"]),
            item_evidence=EvidenceRecord(**payload["item_evidence"]),
            result_evidence=tuple(
                EvidenceRecord(**record) for record in result_records
            ),
            item_page_evidence=tuple(
                EvidenceRecord(**record) for record in page_records
            ),
        )


def build_contract_bundle(
    *,
    cnpj: str,
    year: int,
    sequence: int,
    contract_evidence: EvidenceRecord,
    item_evidence: EvidenceRecord,
    result_evidence: tuple[EvidenceRecord, ...],
    item_page_evidence: tuple[EvidenceRecord, ...] = (),
) -> ContractBundle:
    evidence = (
        contract_evidence,
        item_evidence,
        *item_page_evidence,
        *result_evidence,
    )
    captured_at = max(record.retrieved_at_utc for record in evidence)

    return ContractBundle(
        schema_version=2,
        procurement_key=procurement_key(cnpj, year, sequence),
        cnpj=cnpj,
        year=year,
        sequence=sequence,
        captured_at_utc=captured_at,
        contract_evidence=contract_evidence,
        item_evidence=item_evidence,
        result_evidence=result_evidence,
        item_page_evidence=item_page_evidence,
    )


def contract_bundle_relative_path(bundle: ContractBundle) -> Path:
    normalized_cnpj = bundle.procurement_key.split(":")[1]
    return (
        Path("contracts")
        / normalized_cnpj
        / str(bundle.year)
        / f"{bundle.sequence}.json"
    )


def write_contract_bundle(
    store: EvidenceStore,
    bundle: ContractBundle,
) -> Path:
    path = store.root / contract_bundle_relative_path(bundle)
    content = (
        json.dumps(
            bundle.to_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )
    store.write_metadata(path, content)
    return path


def load_contract_bundle(path: str | Path) -> ContractBundle:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Manifesto de contratação deve conter um objeto JSON")

    bundle = ContractBundle.from_dict(payload)
    expected_key = procurement_key(bundle.cnpj, bundle.year, bundle.sequence)
    if bundle.procurement_key != expected_key:
        raise ValueError(
            "Chave da contratação diverge dos campos CNPJ, ano e sequencial"
        )
    return bundle


def discover_contract_bundles(root: str | Path) -> list[Path]:
    directory = Path(root)
    if not directory.exists():
        return []
    return sorted(path for path in directory.rglob("*.json") if path.is_file())
