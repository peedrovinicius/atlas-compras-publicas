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
    r"^(?:(?:BR\d+|\d+(?:\.\d+)*)\s*(?:-\s*)?)+"
)
_STRENGTH = re.compile(
    r"(?P<value>(?:\d{1,3}(?:\.\d{3})+|\d+(?:[.,]\d+)?))\s*"
    r"(?P<unit>MCG|MG|G|UI)"
    r"(?:\s*/\s*(?:(?P<denom_value>\d+(?:[.,]\d+)?)\s*)?"
    r"(?P<denom_unit>ML|G|L))?"
)
_INGREDIENT_STOP = re.compile(
    r"\s+(?:DOSAGEM|CONCENTRACAO|COMPOSICAO|APRESENTACAO|"
    r"PRINCIPIO ATIVO|FORMA FARMACEUTICA|USO|APLICACAO|"
    r"TIPO MEDICAMENTO)\b"
)
_ASSOCIATED_INGREDIENT = re.compile(
    r"\bASSOCIAD[OA]\s+(?:(?:AO|A|COM)\s+|C/\s*)"
    r"(?P<ingredient>[A-Z][A-Z +/\-]*?)"
    r"(?=,|\s+(?:CONCENTRACAO|DOSAGEM|APRESENTACAO|"
    r"FORMA FARMACEUTICA|USO|COMPRIMIDO)\b|$)"
)
_PLUS_INGREDIENT = re.compile(
    r"\+\s*(?P<ingredient>[A-Z][A-Z -]*?)(?=\s+\d|,|$)"
)
_POST_STRENGTH_ADJUNCT = re.compile(
    r"(?:MCG|MG|G|UI)\s+"
    r"(?P<ingredient>FELIPRESSINA|EPINEFRINA|NOREPINEFRINA|FENILEFRINA)\b"
)
_BENZYLPENICILLIN_PRESENTATION = re.compile(
    r"\bAPRESENTACAO\s+"
    r"(?P<qualifier>BENZATINA|PROCAINA|POTASSICA|SODICA)\b"
)

_TEXT_REWRITES = (
    ("ACIDOFOLICO", "ACIDO FOLICO"),
    ("ACIDOACETICO", "ACIDO ACETICO"),
    ("SOLUCAOORAL", "SOLUCAO ORAL"),
    ("SOLUCAOINJETAVEL", "SOLUCAO INJETAVEL"),
    ("USOTOPICO", "USO TOPICO"),
    ("FOSFATODISSODICODEBETAMETASONA", "FOSFATO DISSODICO DE BETAMETASONA "),
    ("CONCETRACAO", "CONCENTRACAO"),
    ("VIADE ADMINISTRACAO", "VIA DE ADMINISTRACAO"),
)
_BRAND_ONLY_NAMES = {
    "BENESTARE",
}


def _prepare_text(description: str) -> str:
    protected = description.replace("+", " PLUS ")
    text = normalize_description(protected).replace(" PLUS ", " + ")
    for source, target in _TEXT_REWRITES:
        text = text.replace(source, target)
    return text


def _clean_active_ingredient(text: str) -> str | None:
    without_code = _LEADING_CODE.sub("", text).strip()

    structured_salts = (
        (
            r"^AMBROXOL\s+COMPOSICAO\s+SAL\s+CLORIDRATO\b",
            "AMBROXOL CLORIDRATO",
        ),
        (
            r"^FENTANILA\s+APRESENTACAO\s+SAL\s+CITRATO\b",
            "FENTANILA CITRATO",
        ),
    )
    for pattern, ingredient in structured_salts:
        if re.search(pattern, without_code):
            return ingredient

    ingredient_text = _INGREDIENT_STOP.split(
        without_code, maxsplit=1
    )[0].strip(" ,-")

    strength_matches = list(_STRENGTH.finditer(ingredient_text))
    if strength_matches:
        first_strength = strength_matches[0]
        first = ingredient_text[: first_strength.start()].strip(" ,-")
    else:
        first = ingredient_text

    first = re.sub(
        r",\s*(FOSFATO|CLORIDRATO|LACTATO|SULFATO)\b",
        r" \1",
        first,
    )
    first = re.sub(r"\s+", " ", first).strip(" ,-")
    first = re.sub(r"\s*\+\s*", " + ", first)

    if re.search(r"\b(?:FRASCO/AMPOLA|FRASCO|AMPOLA)\b", first):
        first = re.split(
            r"\b(?:FRASCO/AMPOLA|FRASCO|AMPOLA)\b",
            first,
            maxsplit=1,
        )[0].strip(" ,-")

    first = re.sub(r",?\s*\d+(?:[.,]\d+)?%$", "", first).strip(" ,-")
    components = [first] if first else []

    qualifier = re.search(
        r"\b(?:PRINCIPIO ATIVO|COMPOSICAO)\s+(?:SAL\s+)?"
        r"(?P<qualifier>ACETATO|CLORIDRATO|SUCCINATO|DINITRATO|"
        r"FOSFATO|LACTATO|SULFATO|BENZATINA|POTASSICA|SODICA)\b",
        without_code,
    )
    if components and qualifier:
        value = qualifier.group("qualifier")
        if value not in components[0]:
            components[0] = f"{components[0]} {value}"

    association_text = re.split(
        r"\b(?:SOL INJ|SOLUCAO INJETAVEL|INJETAVEL|AMPOLA|POMADA|CREME)\b",
        ingredient_text,
        maxsplit=1,
    )[0]
    strength_matches = list(_STRENGTH.finditer(association_text))

    for index in range(1, len(strength_matches)):
        previous = strength_matches[index - 1]
        current = strength_matches[index]
        between = ingredient_text[previous.end() : current.start()]
        if "+" not in between:
            continue
        candidate = between.split("+", 1)[1].strip(" ,-")
        candidate = re.sub(
            r"^(?:PO|DILUENTE|BISNAGA(?:\s+COM)?)\s+",
            "",
            candidate,
        ).strip(" ,-")
        if candidate and candidate not in components:
            components.append(candidate)

    associated = _ASSOCIATED_INGREDIENT.search(without_code)
    if associated:
        candidate = associated.group("ingredient").strip(" ,-")
        if candidate and candidate not in components:
            components.append(candidate)

    adjunct = _POST_STRENGTH_ADJUNCT.search(without_code)
    if adjunct:
        candidate = adjunct.group("ingredient")
        if candidate and candidate not in components:
            components.append(candidate)

    if components == ["BENZILPENICILINA"]:
        qualifier = _BENZYLPENICILLIN_PRESENTATION.search(without_code)
        if qualifier:
            components[0] = (
                f"BENZILPENICILINA {qualifier.group('qualifier')}"
            )

    cleaned = " + ".join(components).strip(" +")

    form_markers = (
        " COMPRIMIDO",
        " CAPSULA",
        " CAPS",
        " AMPOLA",
        " FRASCO-AMPOLA",
        " FRASCO AMPOLA",
        " SOLUCAO ORAL",
        " SUSPENSAO ORAL",
        " SOLUCAO INJETAVEL",
        " INJETAVEL",
        " COLIRIO",
        " SOL. OFTALMICA",
        " SOLUCAO OFTALMICA",
        " SOL INJ",
        " PO PARA SOL INJ",
        " XAROPE",
        " ELIXIR",
        " POMADA",
        " CREME",
        " GEL",
        " GELEIA",
        " GEL VAGINAL",
        " TUBETE",
        " USO TOPICO",
    )
    positions = [
        cleaned.find(marker)
        for marker in form_markers
        if cleaned.find(marker) >= 0
    ]
    if positions:
        cleaned = cleaned[: min(positions)].strip(" ,-")

    cleaned = re.sub(
        r"(?<=[A-Z])(?=\d+(?:[.,]\d+)?%)",
        " ",
        cleaned,
    )
    cleaned = re.sub(r"\s*\d+(?:[.,]\d+)?%.*$", "", cleaned).strip(" ,-")

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
        or re.search(r"\b(?:IV|EV)/IM\b", text)
        or "PO PARA SOL INJ" in text
        or "SOL INJ" in text
    ):
        return MedicationDosageForm.INJECTABLE
    if (
        "SOLUCAO ORAL" in text
        or "SUSPENSAO ORAL" in text
        or "PO PARA SUSPENSAO" in text
        or "EM PO PARA SUSPENSAO" in text
        or "XAROPE" in text
        or "ELIXIR" in text
        or "GOTAS" in text
        or re.search(r"\bXPE\b", text)
    ):
        return MedicationDosageForm.ORAL_LIQUID
    if "COMPRIMIDO" in text or re.search(r"\b(?:CPR|COMP)\b", text):
        return MedicationDosageForm.TABLET
    if "CAPSULA" in text or re.search(r"\bCAPS\b", text):
        return MedicationDosageForm.CAPSULE
    if (
        "POMADA" in text
        or "CREME" in text
        or "GEL VAGINAL" in text
        or re.search(r"\bGEL\b", text)
        or "GELEIA" in text
        or "LOCAO OLEOSA" in text
    ):
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
        or re.search(r"\bEV\b", text)
    ):
        return MedicationRoute.INJECTABLE
    if dosage_form == MedicationDosageForm.OPHTHALMIC:
        return MedicationRoute.OPHTHALMIC
    if (
        dosage_form == MedicationDosageForm.TOPICAL
        or "USO TOPICO" in text
        or "ADMINISTRACAO TOPICA" in text
    ):
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