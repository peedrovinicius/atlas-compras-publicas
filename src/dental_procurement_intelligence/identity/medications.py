import re
from dataclasses import dataclass
from enum import StrEnum

from dental_procurement_intelligence.normalization import normalize_description


class MedicationDosageForm(StrEnum):
    TABLET = "tablet"
    CAPSULE = "capsule"
    ORAL_LIQUID = "oral_liquid"
    INJECTABLE = "injectable"
    OPHTHALMIC = "ophthalmic"
    TOPICAL = "topical"
    OTHER = "other"
    UNKNOWN = "unknown"


class MedicationRoute(StrEnum):
    ORAL = "oral"
    INJECTABLE = "injectable"
    OPHTHALMIC = "ophthalmic"
    TOPICAL = "topical"
    SUBLINGUAL = "sublingual"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class MedicationIdentity:
    original_description: str
    normalized_description: str
    active_ingredient: str | None
    strength: str | None
    dosage_form: MedicationDosageForm
    route: MedicationRoute


_LEADING_CODE = re.compile(
    r"^(?:\(BR\d+\)\s*|\d+\s*-\s*)+"
)
_STRENGTH = re.compile(
    r"(?<![A-Z0-9])(?P<value>\d+(?:[.,]\d+)?)\s*"
    r"(?P<unit>MCG|MG|G|UI)(?:\s*/\s*(?P<denom>ML|G))?"
)
_INGREDIENT_STOP = re.compile(
    r"\s+(?:DOSAGEM|CONCENTRACAO|COMPOSICAO|APRESENTACAO|"
    r"FORMA FARMACEUTICA|FORMA FARMACEUTICA|USO|APLICACAO|"
    r"TIPO MEDICAMENTO)\s*:"
)


def _clean_active_ingredient(text: str) -> str | None:
    cleaned = _LEADING_CODE.sub("", text).strip()
    cleaned = _INGREDIENT_STOP.split(cleaned, maxsplit=1)[0].strip(" ,-")

    strength_match = _STRENGTH.search(cleaned)
    if strength_match:
        cleaned = cleaned[: strength_match.start()].strip(" ,-")

    form_markers = (
        " COMPRIMIDO",
        " CAPSULA",
        " AMPOLA",
        " FRASCO-AMPOLA",
        " FRASCO AMPOLA",
        " SOLUCAO ORAL",
        " SOLUCAO INJETAVEL",
        " INJETAVEL",
        " COLIRIO",
        " XAROPE",
        " POMADA",
        " CREME",
    )
    positions = [
        cleaned.find(marker)
        for marker in form_markers
        if cleaned.find(marker) >= 0
    ]
    if positions:
        cleaned = cleaned[: min(positions)].strip(" ,-")

    generic_noise = {
        "",
        "MEDICAMENTO",
        "SOLUCAO",
        "COMPRIMIDO",
        "CAPSULA",
    }
    if cleaned in generic_noise:
        return None
    return cleaned or None


def _extract_strength(text: str) -> str | None:
    match = _STRENGTH.search(text)
    if not match:
        return None
    value = match.group("value").replace(",", ".")
    unit = match.group("unit").lower()
    denom = match.group("denom")
    if denom:
        return f"{value} {unit}/{denom.lower()}"
    return f"{value} {unit}"


def _dosage_form(text: str) -> MedicationDosageForm:
    if "COLIRIO" in text or "OFTALM" in text:
        return MedicationDosageForm.OPHTHALMIC
    if (
        "INJETAVEL" in text
        or "FRASCO-AMPOLA" in text
        or "FRASCO AMPOLA" in text
        or re.search(r"\bAMPOLA\b", text)
        or "PO LIOFILO" in text
        or "PO LIOFILIZADO" in text
    ):
        return MedicationDosageForm.INJECTABLE
    if (
        "SOLUCAO ORAL" in text
        or "XAROPE" in text
        or "GOTAS" in text
        or re.search(r"\bXPE\b", text)
    ):
        return MedicationDosageForm.ORAL_LIQUID
    if "COMPRIMIDO" in text or re.search(r"\b(?:CPR|COMP)\b", text):
        return MedicationDosageForm.TABLET
    if "CAPSULA" in text:
        return MedicationDosageForm.CAPSULE
    if "POMADA" in text or "CREME" in text:
        return MedicationDosageForm.TOPICAL
    return MedicationDosageForm.UNKNOWN


def _route(
    text: str,
    dosage_form: MedicationDosageForm,
) -> MedicationRoute:
    if "SUBLINGUAL" in text:
        return MedicationRoute.SUBLINGUAL
    if dosage_form == MedicationDosageForm.INJECTABLE:
        return MedicationRoute.INJECTABLE
    if dosage_form == MedicationDosageForm.OPHTHALMIC:
        return MedicationRoute.OPHTHALMIC
    if dosage_form == MedicationDosageForm.TOPICAL:
        return MedicationRoute.TOPICAL
    if dosage_form in (
        MedicationDosageForm.TABLET,
        MedicationDosageForm.CAPSULE,
        MedicationDosageForm.ORAL_LIQUID,
    ):
        return MedicationRoute.ORAL
    if re.search(r"\bVO\b", text):
        return MedicationRoute.ORAL
    return MedicationRoute.UNKNOWN


def parse_medication(description: str) -> MedicationIdentity:
    text = normalize_description(description)
    dosage_form = _dosage_form(text)

    return MedicationIdentity(
        original_description=description,
        normalized_description=text,
        active_ingredient=_clean_active_ingredient(text),
        strength=_extract_strength(text),
        dosage_form=dosage_form,
        route=_route(text, dosage_form),
    )
