import hashlib
import json
import re
from decimal import Decimal
from typing import Any

from .models import PNCPContract, PNCPItemResult


_CONTROL_NUMBER_PATTERN = re.compile(
    r"^(?P<cnpj>\d{14})-\d+-(?P<sequence>\d+)/(?P<year>\d{4})$"
)


def normalize_cnpj(cnpj: str) -> str:
    normalized = "".join(character for character in cnpj if character.isdigit())
    if len(normalized) != 14:
        raise ValueError("CNPJ deve conter exatamente 14 dígitos")
    return normalized


def procurement_key(cnpj: str, year: int, sequence: int) -> str:
    if year < 1:
        raise ValueError("Ano da contratação deve ser positivo")
    if sequence < 1:
        raise ValueError("Sequencial da contratação deve ser positivo")
    return f"pncp:{normalize_cnpj(cnpj)}:{year}:{sequence}"


def procurement_key_from_contract(contract: PNCPContract) -> str | None:
    organization = contract.organization
    if (
        organization is not None
        and organization.cnpj
        and contract.purchase_year is not None
        and contract.sequence is not None
    ):
        return procurement_key(
            organization.cnpj,
            contract.purchase_year,
            contract.sequence,
        )

    if contract.control_number:
        control_number = contract.control_number.strip()
        match = _CONTROL_NUMBER_PATTERN.fullmatch(control_number)
        if match:
            return procurement_key(
                match.group("cnpj"),
                int(match.group("year")),
                int(match.group("sequence")),
            )
        if control_number:
            compact = "".join(control_number.split()).lower()
            return f"pncp-control:{compact}"

    return None


def _stable_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def award_key(
    procurement: str,
    result: PNCPItemResult,
) -> str:
    item_number = result.item_number

    if result.result_sequence is not None:
        return (
            f"{procurement}:item:{item_number}:"
            f"result:{result.result_sequence}"
        )

    payload = {
        "item_number": item_number,
        "supplier_document": result.supplier_document,
        "supplier_name": result.supplier_name,
        "brand": result.brand,
        "awarded_quantity": _stable_value(result.awarded_quantity),
        "awarded_unit_value": _stable_value(result.awarded_unit_value),
        "awarded_total_value": _stable_value(result.awarded_total_value),
        "result_date": _stable_value(result.result_date),
        "status_id": result.status_id,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    return f"{procurement}:item:{item_number}:result:sha256:{digest[:24]}"
