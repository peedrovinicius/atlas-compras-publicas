import re
from decimal import Decimal

from dental_procurement_intelligence.identity.models import (
    CanonicalProduct,
    NormalizationQuality,
    ProductCategory,
    Quantity,
    QuantityDimension,
    TechnicalAttributes,
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
            "RESINAS FLUIDAS",
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
            "ADESIVOS",
        ),
    ),
    (
        ProductCategory.GLASS_IONOMER,
        (
            "IONOMERO DE VIDRO",
            "IONOMEROS DE VIDRO",
            "CIMENTO IONOMERO",
            "CIV RESTAURADOR",
        ),
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
        ("FLUOR GEL", "FLUOR EM GEL", "FLUOR ACIDO GEL", "GEL FLUORETADO"),
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
        ("OXIDO DE ZINCO", "OXIDO ZINCO"),
    ),
    (
        ProductCategory.EUGENOL,
        ("EUGENOL",),
    ),
    (
        ProductCategory.RADIOGRAPHIC_FIXER,
        (
            "FIXADOR RADIOGRAFICO",
            "FIXADOR RADIOLOGICO",
            "FIXADOR ODONTOLOGICO",
            "FIXADOR KODAK",
        ),
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
            "ANESTESICO",
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
    re.compile(
        r"\bC\s*/\s*(?P<count>\d+)\s+"
        r"(?:SERINGAS?|FRASCOS?|CAPSULAS?|UNIDADES?|TUBETES?|SACHES?|"
        r"ENVELOPES?|AMPOLAS?)\b"
    ),
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
    "ADESIVOS",
    "PRIMER",
    "BOND",
)

_ANESTHETIC_ACTIVE_INGREDIENTS = (
    "LIDOCAINA",
    "ARTICAINA",
    "ARTICAINE",
    "MEPIVACAINA",
)

_MIXED_KIT_FAMILY_TERMS: tuple[tuple[str, ...], ...] = (
    ("RESINA", "RESINAS"),
    ("ADESIVO", "ADESIVOS"),
    ("IONOMERO", "IONOMEROS"),
    ("ALGINATO", "ALGINATOS"),
    ("EUGENOL",),
    ("HIDROXIDO DE CALCIO",),
)


_RESIN_TECHNOLOGY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("bulk_fill", ("BULK FILL", "BULKFILL")),
    ("nanohybrid", ("NANOHIBRIDA", "NANO-HIBRIDA", "NANOHYBRID")),
    ("microhybrid", ("MICROHIBRIDA", "MICRO-HIBRIDA", "MICROHYBRID")),
)

_CURING_MODE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("dual_cure", ("CURA DUAL", "DUAL CURE")),
    (
        "light_cure",
        ("FOTOPOLIMERIZAVEL", "FOTOPOLIMERIZACAO", "LIGHT CURE"),
    ),
    (
        "self_cure",
        ("AUTOPOLIMERIZAVEL", "AUTOPOLIMERIZACAO", "SELF CURE"),
    ),
)

_ADHESIVE_STRATEGY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("universal", ("ADESIVO UNIVERSAL", "SISTEMA ADESIVO UNIVERSAL")),
    (
        "self_etch",
        ("AUTOCONDICIONANTE", "AUTO CONDICIONANTE", "SELF ETCH"),
    ),
    (
        "etch_and_rinse",
        ("CONDICIONAMENTO TOTAL", "TOTAL ETCH", "ETCH AND RINSE"),
    ),
)

_IONOMER_USE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("restorative", ("RESTAURADOR", "RESTAURATIVO")),
    ("luting", ("CIMENTACAO", "CIMENTANTE", "FIXACAO")),
    ("liner_base", ("FORRAMENTO", "FORRADOR", "BASE CAVITARIA")),
)

_FLUORIDE_FORMULATION_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("neutral", ("GEL NEUTRO", "FLUOR NEUTRO")),
    (
        "acidulated",
        ("GEL ACIDULADO", "FLUOR ACIDULADO", "FLUOR ACIDO"),
    ),
)

_ANESTHETIC_INGREDIENT_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("lidocaine", ("LIDOCAINA",)),
    ("articaine", ("ARTICAINA", "ARTICAINE")),
    ("mepivacaine", ("MEPIVACAINA",)),
)

_VASOCONSTRICTOR_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("epinephrine", ("EPINEFRINA", "ADRENALINA")),
    ("felypressin", ("FELIPRESSINA", "FELYPRESSIN")),
    ("norepinephrine", ("NOREPINEFRINA", "NORADRENALINA")),
)


_RESIN_HEAD_TERMS = ("RESINA", "RESINAS")
_FLUID_RESIN_TERMS = ("FLUIDA", "FLUIDAS", "FLOW", "FLOWABLE")


def _term_present(text: str, term: str) -> bool:
    pattern = rf"(?<![A-Z0-9]){re.escape(term)}(?![A-Z0-9])"
    return re.search(pattern, text) is not None


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(_term_present(text, term) for term in terms)


def _term_negated(text: str, term: str) -> bool:
    escaped = re.escape(term)
    patterns = (
        rf"\bSEM\s+{escaped}\b",
        rf"\bISENTO(?:\s+DE)?\s+{escaped}\b",
        rf"\bLIVRE\s+DE\s+{escaped}\b",
        rf"\bNAO\s+CONTEM\s+{escaped}\b",
        rf"\bNAO\s+{escaped}\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _is_mixed_kit(text: str) -> bool:
    if not _term_present(text, "KIT"):
        return False

    family_count = sum(
        1
        for terms in _MIXED_KIT_FAMILY_TERMS
        if _has_any(text, terms)
    )
    return family_count >= 2


def _composite_context_excluded(text: str) -> bool:
    return any(pattern.search(text) for pattern in _COMPOSITE_CONTEXT_EXCLUSIONS)


def _looks_like_flowable_resin(text: str) -> bool:
    if not _has_any(text, _RESIN_HEAD_TERMS):
        return False

    return any(
        _term_present(text, term) and not _term_negated(text, term)
        for term in _FLUID_RESIN_TERMS
    )


def _alginate_context_excluded(text: str) -> bool:
    if not _term_present(text, "ISOLANTE"):
        return False
    if not _term_present(text, "ALGINATO"):
        return False

    return (
        _term_present(text, "COMPOSICAO")
        or re.search(r"\bA\s+BASE\s+DE\b", text) is not None
    )


def _classify_category(text: str) -> tuple[ProductCategory, tuple[str, ...]]:
    if _is_mixed_kit(text):
        return ProductCategory.UNKNOWN, ("MIXED_KIT",)

    if _has_any(text, _ANESTHETIC_ACTIVE_INGREDIENTS):
        matches = tuple(
            term for term in _ANESTHETIC_ACTIVE_INGREDIENTS if _term_present(text, term)
        )
        return ProductCategory.LOCAL_ANESTHETIC, matches

    if _has_any(text, ("ADESIVO", "ADESIVOS")):
        matches = tuple(
            term
            for term in _ADHESIVE_HINTS
            if _term_present(text, term) and not _term_negated(text, term)
        )
        if matches:
            return ProductCategory.ADHESIVE, matches

    if _term_present(text, "ANESTESICO") and not _term_negated(text, "ANESTESICO"):
        return ProductCategory.LOCAL_ANESTHETIC, ("ANESTESICO",)

    if _looks_like_flowable_resin(text):
        matches = tuple(
            term
            for term in (*_RESIN_HEAD_TERMS, *_FLUID_RESIN_TERMS)
            if _term_present(text, term)
        )
        return ProductCategory.FLOWABLE_RESIN, matches

    for category, terms in _CATEGORY_RULES:
        matches = tuple(
            term
            for term in terms
            if _term_present(text, term) and not _term_negated(text, term)
        )
        if not matches:
            continue
        if (
            category == ProductCategory.COMPOSITE_RESIN
            and _composite_context_excluded(text)
        ):
            continue
        if category == ProductCategory.ALGINATE and _alginate_context_excluded(text):
            continue
        return category, matches

    return ProductCategory.UNKNOWN, ()


def _first_attribute_match(
    text: str,
    rules: tuple[tuple[str, tuple[str, ...]], ...],
) -> str | None:
    for canonical, terms in rules:
        if any(_term_present(text, term) for term in terms):
            return canonical
    return None


def _technical_attributes(
    text: str,
    category: ProductCategory,
) -> TechnicalAttributes:
    resin_technology = None
    curing_mode = None
    adhesive_strategy = None
    ionomer_use = None
    fluoride_formulation = None
    anesthetic_active_ingredient = None
    anesthetic_vasoconstrictor = None

    if category in (ProductCategory.COMPOSITE_RESIN, ProductCategory.FLOWABLE_RESIN):
        resin_technology = _first_attribute_match(text, _RESIN_TECHNOLOGY_RULES)
        curing_mode = _first_attribute_match(text, _CURING_MODE_RULES)

    elif category == ProductCategory.ADHESIVE:
        adhesive_strategy = _first_attribute_match(text, _ADHESIVE_STRATEGY_RULES)
        curing_mode = _first_attribute_match(text, _CURING_MODE_RULES)

    elif category == ProductCategory.GLASS_IONOMER:
        ionomer_use = _first_attribute_match(text, _IONOMER_USE_RULES)
        curing_mode = _first_attribute_match(text, _CURING_MODE_RULES)

    elif category == ProductCategory.FLUORIDE_GEL:
        fluoride_formulation = _first_attribute_match(
            text,
            _FLUORIDE_FORMULATION_RULES,
        )

    elif category == ProductCategory.LOCAL_ANESTHETIC:
        anesthetic_active_ingredient = _first_attribute_match(
            text,
            _ANESTHETIC_INGREDIENT_RULES,
        )
        if re.search(r"\bSEM\s+VASOCONSTRITOR\b", text):
            anesthetic_vasoconstrictor = "none"
        else:
            anesthetic_vasoconstrictor = _first_attribute_match(
                text,
                _VASOCONSTRICTOR_RULES,
            )

    return TechnicalAttributes(
        resin_technology=resin_technology,
        curing_mode=curing_mode,
        adhesive_strategy=adhesive_strategy,
        ionomer_use=ionomer_use,
        fluoride_formulation=fluoride_formulation,
        anesthetic_active_ingredient=anesthetic_active_ingredient,
        anesthetic_vasoconstrictor=anesthetic_vasoconstrictor,
    )


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


def _measurement_candidates(description: str) -> tuple[Quantity, ...]:
    candidates: list[Quantity] = []
    seen: set[tuple[QuantityDimension, Decimal]] = set()

    for measurement in extract_measurements(description):
        quantity = _to_base_quantity(measurement.value, measurement.unit)
        key = (quantity.dimension, quantity.value)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(quantity)

    return tuple(candidates)


def _resolve_measurements(
    candidates: tuple[Quantity, ...],
    package_count: int | None,
) -> tuple[Quantity | None, Quantity | None, str]:
    if not candidates:
        return None, None, "missing"

    if len(candidates) == 1:
        unit_quantity = candidates[0]
        if package_count is None:
            return unit_quantity, None, "single"

        total_quantity = Quantity(
            value=unit_quantity.value * package_count,
            unit=unit_quantity.unit,
            dimension=unit_quantity.dimension,
        )
        return unit_quantity, total_quantity, "package_derived"

    if package_count is not None and len(candidates) == 2:
        matches: list[tuple[Quantity, Quantity]] = []
        for unit_quantity in candidates:
            for total_quantity in candidates:
                if unit_quantity is total_quantity:
                    continue
                if unit_quantity.dimension != total_quantity.dimension:
                    continue
                if total_quantity.value == unit_quantity.value * package_count:
                    matches.append((unit_quantity, total_quantity))

        if len(matches) == 1:
            unit_quantity, total_quantity = matches[0]
            return unit_quantity, total_quantity, "package_total_confirmed"

    return None, None, "ambiguous"


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

    technical_attributes = _technical_attributes(normalized, category)
    package_count = _package_count(normalized)
    measurement_candidates = _measurement_candidates(normalized)
    unit_quantity, total_quantity, measurement_resolution = _resolve_measurements(
        measurement_candidates,
        package_count,
    )

    return CanonicalProduct(
        original_description=description,
        normalized_description=normalized,
        category=category,
        presentation=_presentation(normalized),
        shade=shade,
        concentration_percent=concentration,
        technical_attributes=technical_attributes,
        package_count=package_count,
        measurement_candidates=measurement_candidates,
        measurement_resolution=measurement_resolution,
        unit_quantity=unit_quantity,
        total_quantity=total_quantity,
        matched_terms=matched_terms,
    )


def assess_normalization_quality(product: CanonicalProduct) -> NormalizationQuality:
    category_ok = product.category != ProductCategory.UNKNOWN
    presentation_ok = product.presentation is not None
    measurement_ok = product.unit_quantity is not None
    measurement_ambiguous = product.measurement_resolution == "ambiguous"

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
        missing.append(
            "measurement_ambiguous" if measurement_ambiguous else "measurement"
        )

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
