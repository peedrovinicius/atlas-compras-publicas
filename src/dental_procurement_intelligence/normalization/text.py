import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal

_SPACE_PATTERN = re.compile(r"\s+")
_PUNCTUATION_PATTERN = re.compile(r"[^A-Z0-9.,/%\- ]+")
_MEASUREMENT_PATTERN = re.compile(
    r"(?P<value>\d+(?:[.,]\d+)?)\s*(?P<unit>MG|G|KG|ML|L)\b",
    flags=re.IGNORECASE,
)

_UNIT_ALIASES = {
    "MG": "mg",
    "G": "g",
    "KG": "kg",
    "ML": "ml",
    "L": "l",
}


@dataclass(frozen=True, slots=True)
class Measurement:
    value: Decimal
    unit: str
    source: str


def normalize_description(value: str) -> str:
    """Normaliza tipografia preservando símbolos semanticamente relevantes."""

    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    upper = without_accents.upper()
    cleaned = _PUNCTUATION_PATTERN.sub(" ", upper)
    return _SPACE_PATTERN.sub(" ", cleaned).strip()


def extract_measurements(value: str) -> list[Measurement]:
    """Extrai medidas explícitas de massa e volume da descrição."""

    normalized = normalize_description(value)
    measurements: list[Measurement] = []

    for match in _MEASUREMENT_PATTERN.finditer(normalized):
        number = Decimal(match.group("value").replace(",", "."))
        raw_unit = match.group("unit").upper()
        measurements.append(
            Measurement(
                value=number,
                unit=_UNIT_ALIASES[raw_unit],
                source=match.group(0),
            )
        )

    return measurements
