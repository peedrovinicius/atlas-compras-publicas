from decimal import Decimal

from dental_procurement_intelligence.normalization import extract_measurements, normalize_description


def test_normalize_description_removes_accents_and_collapses_noise() -> None:
    value = "  Resina composta fotopolimerizável — A2 / seringa 4 g  "

    assert normalize_description(value) == "RESINA COMPOSTA FOTOPOLIMERIZAVEL A2 / SERINGA 4 G"


def test_extract_measurements_handles_decimal_comma_and_multiple_units() -> None:
    measurements = extract_measurements("Kit com 2 seringas de 3,5 g e frasco de 5 ml")

    assert [(item.value, item.unit) for item in measurements] == [
        (Decimal("3.5"), "g"),
        (Decimal("5"), "ml"),
    ]
