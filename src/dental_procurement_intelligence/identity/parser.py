import re
from decimal import Decimal

from dental_procurement_intelligence.identity.models import (
    CanonicalProduct,
    NormalizationQuality,
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
        (
            "RESINA FLOW",
            "RES FLOW",
            "FLOWABLE",
            "RESINA FLUIDA",
            "RESINA COMPOSTA FLUIDA",
            "RESINA NATURAL FLOW",
        ),
    ),
    (
        ProductCategory.COMPOSITE_RESIN,
        (
            "RESINA COMPOSTA",
            "RES COMP",
            "RES FOTOP",
            "RESINA RESTAURADORA",
            "RESINA MICROHIBRIDA",
            "RESINA MICRO-HIBRIDA",
            "RESINA NANOHIBRIDA",
            "RESINA NANO-HIBRIDA",
        ),
    ),
    (
        ProductCategory.ADHESIVE,
        (
            "ADESIVO DENTAL",
            "SISTEMA ADESIVO",
            "ADESIVO ODONTOLOGICO",
            "ADESIVO FOTOPOLIMERIZAVEL",
            "ADESIVO UNIVERSAL",
        ),
    ),
    (
        ProductCategory.GLASS_IONOMER,
        ("IONOMERO DE VIDRO", "CIMENTO IONOMERO", "CIV RESTAURADOR"),
    ),
    (
        ProductCategory.PHOSPHORIC_ACID,
        ("ACIDO FOSFORICO", "CONDICIONADOR ACIDO", "ACIDO CONDICIONADOR"),
    ),
    (
        ProductCategory.ALGINATE,
        ("ALGINATO", "MATERIAL DE MOLDAGEM ALGINATO"),
    ),
    (
        ProductCategory.FLUORIDE_GEL,
        ("FLUOR GEL", "FLUOR EM GEL", "GEL FLUORETADO"),
    ),
    (
        ProductCategory.PROPHYLAXIS_PASTE,
        ("PASTA PROFILATICA", "PASTA DE PROFILAXIA"),
    ),
    (
        ProductCategory.CALCIUM_HYDROXIDE,
        ("HIDROXIDO DE CALCIO", "CIMENTO HIDROXIDO DE CALCIO"),
    ),
    (
        ProductCategory.ZINC_OXIDE,
        ("OXIDO DE ZINCO",),
    ),
    (
        ProductCategory.EUGENOL,
        ("EUGENOL",),
    ),
    (
        ProductCategory.RADIOGRAPHIC_FIXER,
        ("FIXADOR RADIOGRAFICO", "FIXADOR ODONTOLOGICO", "FIXADOR KODAK"),
    ),
    (
        ProductCategory.RADIOGRAPHIC_DEVELOPER,
        ("REVELADOR RADIOGRAFICO", "REVELADOR ODONTOLOGICO"),
    ),
    (
        ProductCategory.LOCAL_ANESTHETIC,
        (
            "ANESTESICO ODONTOLOGICO",
            "ANESTESICO LOCAL",
            "ANESTESICO TOPICO",
            "ANESTESICO ARTICAINE",
            "LIDOCAINA",
            "ARTICAINA",
            "ARTICAINE",
            "MEPIVACAINA",
        ),
    ),
)

_PRESENTATION_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("syringe", ("SERINGA",)),
    ("bottle", ("FRASCO",)),
    ("capsule", ("CAPSULA",)),
    ("tube", ("TUBO", "BISNAGA")),
    ("pot", ("POTE",)),
    ("sachet", ("SACHE", "ENVELOPE")),
    ("cartridge", ("TUBETE", "CARPULE", "AMPOLA")),
    ("kit", ("KIT",)),
)

_SHADE_PATTERN = re.compile(
    r"\b(?:COR\s*)?(?P<shade>[ABCD]-?[1-4](?:[.,]5)?|BL|TRANSLUCIDA)\b"
)
_CONCENTRATION_PATTERN = re.compile(r"\b(?P<value>\d+(?:[.,]\d+)?)\s*%")
_PACKAGE_PATTERNS = (
    re.compile(r"\bC\s*/\s*(?P<count>\d+)\b"),
    re.compile(
        r"\bCOM\s+(?P<count>\d+)\s+"
        r"(?:SERINGAS?|FRASCOS?|CAPSULAS?|UNIDADES?|TUBETES?|SACHES?|"
        r"ENVELOPES?|AMPOLAS?)\b"
    ),
    re.compile(
        r"\b(?P<count>\d+)\s+"
        r"(?:SERINGAS?|FRASCOS?|CAPSULAS?|TUBETES?|SACHES?|ENVELOPES?|"
        r"AMPOLAS?)\b"
    ),
)

_SHADE_CRITICAL = {
    ProductCategory.COMPOSITE_RESIN,
    ProductCategory.FLOWABLE_RESIN,
    ProductCategory.GLASS_IONOMER,
}

_CONCENTRATION_CRITICAL = {
    ProductCategory.PHOSPHORIC_ACID,
    ProductCategory.FLUORIDE_GEL,
    ProductCategory.LOCAL_ANESTHETIC,
}

_COMPOSITE_CONTEXT_EXCLUSIONS = (
    re.compile(r"\b(?:KIT|PONTAS?)\b.*\b(?:ACABAMENTO|POLIMENTO)\b.*\bRESINA\b"),
    re.compile(r"\b(?:ACABAMENTO|POLIMENTO)\b.*\bDE\s+RESINA\b"),
)

_ADHESIVE_HINTS = (
    "ADESIVO",
    "PRIMER",
    "BOND",
)

_ANESTHETIC_ACTIVE_INGREDIENTS = (
    "LIDOCAINA",
    "ARTICAINA",
    "ARTICAINE",
    "MEPIVACAINA",
)


def _term_present(text: str, term: str) -> bool:
    pattern = rf"(?<![A-Z0-9]){re.escape(term)}(?![A-Z0-9])"
    return re.search(pattern, text) is not None


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(_term_present(text, term) for term in terms)


def _composite_context_excluded(text: str) -> bool:
    return any(pattern.search(text) for pattern in _COMPOSITE_CONTEXT_EXCLUSIONS)


def _classify_category(text: str) -> tuple[ProductCategory, tuple[str, ...]]:
    # Product head takes precedence over contextual mentions.
    if _has_any(text, _ANESTHETIC_ACTIVE_INGREDIENTS):
        matches = tuple(
            term for term in _ANESTHETIC_ACTIVE_INGREDIENTS if _term_present(text, term)
        )
        return ProductCategory.LOCAL_ANESTHETIC, matches

    if _term_present(text, "ADESIVO"):
        matches = tuple(term for term in _ADHESIVE_HINTS if _term_present(text, term))
        return ProductCategory.ADHESIVE, matches or ("ADESIVO",)

    for category, terms in _CATEGORY_RULES:
        matches = tuple(term for term in terms if _term_present(text, term))
        if not matches:
            continue
        if (
            category == ProductCategory.COMPOSITE_RESIN
            and _composite_context_excluded(text)
        ):
            continue
        return category, matches

    return ProductCategory.UNKNOWN, ()


def _presentation(text: str) -> str | None:
    for canonical, terms in _PRESENTATION_RULES:
        if any(_term_present(text, term) for term in terms):
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
        return Quantity(
            value=value / Decimal("1000"),
            unit="g",
            dimension=QuantityDimension.MASS,
        )
    if unit == "kg":
        return Quantity(
            value=value * Decimal("1000"),
            unit="g",
            dimension=QuantityDimension.MASS,
        )
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
    shade = None
    if shade_match:
        shade = shade_match.group("shade").replace("-", "").replace(",", ".")

    concentration_match = _CONCENTRATION_PATTERN.search(normalized)
    concentration = (
        Decimal(concentration_match.group("value").replace(",", "."))
        if concentration_match
        else None
    )

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
        concentration_percent=concentration,
        package_count=package_count,
        unit_quantity=unit_quantity,
        total_quantity=total_quantity,
        matched_terms=matched_terms,
    )


def assess_normalization_quality(product: CanonicalProduct) -> NormalizationQuality:
    category_ok = product.category != ProductCategory.UNKNOWN
    presentation_ok = product.presentation is not None
    measurement_ok = product.unit_quantity is not None

    critical_name = None
    critical_ok: bool | None = None

    if product.category in _SHADE_CRITICAL:
        critical_name = "shade"
        critical_ok = product.shade is not None
    elif product.category in _CONCENTRATION_CRITICAL:
        critical_name = "concentration_percent"
        critical_ok = product.concentration_percent is not None

    score = Decimal("0")
    denominator = Decimal("0.90")

    if category_ok:
        score += Decimal("0.45")
    if presentation_ok:
        score += Decimal("0.20")
    if measurement_ok:
        score += Decimal("0.25")

    missing: list[str] = []
    if not category_ok:
        missing.append("category")
    if not presentation_ok:
        missing.append("presentation")
    if not measurement_ok:
        missing.append("measurement")

    if critical_name is not None:
        denominator = Decimal("1.00")
        if critical_ok:
            score += Decimal("0.10")
        else:
            missing.append(critical_name)

    normalized_score = (score / denominator).quantize(Decimal("0.001"))

    fully_structured = (
        category_ok
        and presentation_ok
        and measurement_ok
        and (critical_ok is not False)
    )

    if normalized_score >= Decimal("0.80") and fully_structured:
        level = "high"
    elif normalized_score >= Decimal("0.55"):
        level = "medium"
    else:
        level = "low"

    return NormalizationQuality(
        score=normalized_score,
        level=level,
        fully_structured=fully_structured,
        category_identified=category_ok,
        presentation_identified=presentation_ok,
        measurement_identified=measurement_ok,
        critical_attribute_name=critical_name,
        critical_attribute_identified=critical_ok,
        missing_fields=tuple(missing),
    )
