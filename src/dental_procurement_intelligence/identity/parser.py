import re
from decimal import Decimal

from dental_procurement_intelligence.identity.models import (
    CanonicalProduct,
    ProductCategory,
    Quantity,
    QuantityDimension,
)
from dental_procurement_intelligence.normalization import (
    extract_measurements,
    normalize_description,
)

_CATEGORY_RULES: tuple[tuple[ProductCategory, tuple[str, ...]], ...] = (
    (
        ProductCategory.FLOWABLE_RESIN,
        ("RESINA FLOW", "RES FLOW", "FLOWABLE", "RESINA FLUIDA"),
    ),
    (
        ProductCategory.COMPOSITE_RESIN,
        ("RESINA COMPOSTA", "RES COMP", "RES FOTOP", "RESINA RESTAURADORA"),
    ),
    (
        ProductCategory.ADHESIVE,
        ("ADESIVO DENTAL", "SISTEMA ADESIVO", "ADESIVO ODONTOLOGICO"),
    ),
    (
        ProductCategory.GLASS_IONOMER,
        ("IONOMERO DE VIDRO", "CIMENTO IONOMERO", "CIV"),
    ),
)

_PRESENTATION_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("syringe", ("SERINGA", "SER ")),
    ("bottle", ("FRASCO", "FR ")),
    ("capsule", ("CAPSULA", "CAP ")),
    ("kit", ("KIT",)),
)

_SHADE_PATTERN = re.compile(r"\b(?:COR\s*)?(?P<shade>[ABCD][1-4](?:\.5)?|BL|TRANSLUCIDA)\b")
_PACKAGE_PATTERNS = (
    re.compile(r"\bC\s*/\s*(?P<count>\d+)\b"),
    re.compile(r"\bCOM\s+(?P<count>\d+)\s+(?:SERINGAS?|FRASCOS?|CAPSULAS?|UNIDADES?)\b"),
    re.compile(r"\b(?P<count>\d+)\s+(?:SERINGAS?|FRASCOS?|CAPSULAS?)\b"),
)


def _classify_category(text: str) -> tuple[ProductCategory, tuple[str, ...]]:
    for category, terms in _CATEGORY_RULES:
        matches = tuple(term for term in terms if term in text)
        if matches:
            return category, matches
    return ProductCategory.UNKNOWN, ()


def _presentation(text: str) -> str | None:
    for canonical, terms in _PRESENTATION_RULES:
        if any(term in text for term in terms):
            return canonical
    return None


def _package_count(text: str) -> int | None:
    for pattern in _PACKAGE_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group("count"))
    return None


def _to_base_quantity(value: Decimal, unit: str) -> Quantity:
    if unit == "mg":
        return Quantity(value=value / Decimal("1000"), unit="g", dimension=QuantityDimension.MASS)
    if unit == "kg":
        return Quantity(value=value * Decimal("1000"), unit="g", dimension=QuantityDimension.MASS)
    if unit == "g":
        return Quantity(value=value, unit="g", dimension=QuantityDimension.MASS)
    if unit == "l":
        return Quantity(
            value=value * Decimal("1000"),
            unit="ml",
            dimension=QuantityDimension.VOLUME,
        )
    return Quantity(value=value, unit="ml", dimension=QuantityDimension.VOLUME)


def parse_product(description: str) -> CanonicalProduct:
    normalized = normalize_description(description)
    category, matched_terms = _classify_category(normalized)
    shade_match = _SHADE_PATTERN.search(normalized)
    shade = shade_match.group("shade") if shade_match else None
    package_count = _package_count(normalized)

    measurements = extract_measurements(normalized)
    unit_quantity = (
        _to_base_quantity(measurements[0].value, measurements[0].unit)
        if measurements
        else None
    )
    total_quantity = None
    if unit_quantity is not None and package_count is not None:
        total_quantity = Quantity(
            value=unit_quantity.value * package_count,
            unit=unit_quantity.unit,
            dimension=unit_quantity.dimension,
        )

    return CanonicalProduct(
        original_description=description,
        normalized_description=normalized,
        category=category,
        presentation=_presentation(normalized),
        shade=shade,
        package_count=package_count,
        unit_quantity=unit_quantity,
        total_quantity=total_quantity,
        matched_terms=matched_terms,
    )
