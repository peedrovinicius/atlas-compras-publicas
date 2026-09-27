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
    r"^(?:(?:BR\d+|\d+)\s*(?:-\s*)?)+"
)
_STRENGTH = re.compile(
    r"(?P<value>(?:\d{1,3}(?:\.\d{3})+|\d+(?:[.,]\d+)?))\s*"
    r"(?P<unit>MCG|MG|G|UI)"
    r"(?:\s*/\s*(?:(?P<denom_value>\d+(?:[.,]\d+)?)\s*)?"
    r"(?P<denom_unit>ML|G|L))?"
)
_INGREDIENT_STOP = re.compile(
    r"\s+(?:DOSAGEM|CONCENTRACAO|COMPOSICAO|APRESENTACAO|"
    r"FORMA FARMACEUTICA|USO|APLICACAO|TIPO MEDICAMENTO)\b"
)
_ASSOCIATED_INGREDIENT = re.compile(
    r"\bASSOCIAD[OA]\s+(?:AO|A)\s+"
    r"(?P<ingredient>[A-Z][A-Z -]*?)"
    r"(?=,|\s+(?:CONCENTRACAO|DOSAGEM|APRESENTACAO|"
    r"FORMA FARMACEUTICA|USO|COMPRIMIDO)\b|$)"
)
_PLUS_INGREDIENT = re.compile(
    r"\+\s*(?P<ingredient>[A-Z][A-Z -]*?)(?=\s+\d|,|$)"
)
_POST_STRENGTH_ADJUNCT = re.compile(
    r"\b(?:MCG|MG|G|UI)\s+"
    r"(?P<ingredient>FELIPRESSINA|EPINEFRINA|NOREPINEFRINA|FENILEFRINA)\b"
)
_BENZYLPENICILLIN_PRESENTATION = re.compile(
    r"\bAPRESENTACAO\s+"
    r"(?P<qualifier>BENZATINA|PROCAINA|POTASSICA|SODICA)\b"
)

_TEXT_REWRITES = (
    ("ACIDOFOLICO", "ACIDO FOLICO"),
)
_BRAND_ONLY_NAMES = {
    "BENESTARE",
}


def _prepare_text(description: str) -> str:
    text = normalize_description(description)
    for source, target in _TEXT_REWRITES:
        text = text.replace(source, target)
    return text


def _clean_active_ingredient(text: str) -> str | None:
    without_code = _LEADING_CODE.sub("", text).strip()
    cleaned = _INGREDIENT_STOP.split(without_code, maxsplit=1)[0].strip(" ,-")

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
        " TUBETE",
    )
    positions = [
        cleaned.find(marker)
        for marker in form_markers
        if cleaned.find(marker) >= 0
    ]
    if positions:
        cleaned = cleaned[: min(positions)].strip(" ,-")

    associated = _ASSOCIATED_INGREDIENT.search(without_code)
    if associated:
        associated_name = associated.group("ingredient").strip(" ,-")
        if associated_name and associated_name not in cleaned:
            cleaned = f"{cleaned} + {associated_name}".strip(" +")

    plus_match = _PLUS_INGREDIENT.search(without_code)
    if plus_match:
        plus_name = plus_match.group("ingredient").strip(" ,-")
        if plus_name and plus_name not in cleaned:
            cleaned = f"{cleaned} + {plus_name}".strip(" +")

    adjunct = _POST_STRENGTH_ADJUNCT.search(without_code)
    if adjunct:
        adjunct_name = adjunct.group("ingredient")
        if adjunct_name not in cleaned:
            cleaned = f"{cleaned} + {adjunct_name}".strip(" +")

    if cleaned == "BENZILPENICILINA":
        qualifier = _BENZYLPENICILLIN_PRESENTATION.search(without_code)
        if qualifier:
            cleaned = f"{cleaned} {qualifier.group('qualifier')}"

    generic_noise = {
        "",
        "MEDICAMENTO",
        "SOLUCAO",
        "COMPRIMIDO",
        "CAPSULA",
    }
    if cleaned in generic_noise or cleaned in _BRAND_ONLY_NAMES:
        return None
    return cleaned or None


def _normalize_number(value: str) -> str:
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", value):
        return value.replace(".", "")
    return value.replace(",", ".")


def _extract_strength(
    text: str,
    dosage_form: MedicationDosageForm,
) -> str | None:
    match = _STRENGTH.search(text)
    if not match:
        return None

    value = _normalize_number(match.group("value"))
    unit = match.group("unit").lower()
    denom_value = match.group("denom_value")
    denom_unit = match.group("denom_unit")

    if (
        denom_value
        and dosage_form
        not in (
            MedicationDosageForm.INJECTABLE,
            MedicationDosageForm.ORAL_LIQUID,
        )
    ):
        return f"{value} {unit}"

    if denom_unit:
        denominator = denom_unit.lower()
        if denom_value:
            denominator = f"{_normalize_number(denom_value)} {denominator}"
        return f"{value} {unit}/{denominator}"

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
    if "TUBETE" in text:
        return MedicationDosageForm.OTHER
    return MedicationDosageForm.UNKNOWN


def _route(
    text: str,
    dosage_form: MedicationDosageForm,
) -> MedicationRoute:
    if "SUBLINGUAL" in text:
        return MedicationRoute.SUBLINGUAL
    if (
        dosage_form == MedicationDosageForm.INJECTABLE
        or "INTRAVENOSO" in text
        or "ENDOVENOSO" in text
        or re.search(r"\bIV\b", text)
    ):
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
    text = _prepare_text(description)
    dosage_form = _dosage_form(text)

    return MedicationIdentity(
        original_description=description,
        normalized_description=text,
        active_ingredient=_clean_active_ingredient(text),
        strength=_extract_strength(text, dosage_form),
        dosage_form=dosage_form,
        route=_route(text, dosage_form),
    )
