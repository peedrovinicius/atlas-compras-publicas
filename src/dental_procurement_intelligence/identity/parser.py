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
from dental_procurement_intelligence.identity.rules import (
    DENTAL_CATEGORY_SPECS,
    compile_category_rules,
)
from dental_procurement_intelligence.identity.rules.dental import (
    ADHESIVE_HINTS as _ADHESIVE_HINTS,
    ADHESIVE_STRATEGY_RULES as _ADHESIVE_STRATEGY_RULES,
    ANESTHETIC_ACTIVE_INGREDIENTS as _ANESTHETIC_ACTIVE_INGREDIENTS,
    ANESTHETIC_INGREDIENT_RULES as _ANESTHETIC_INGREDIENT_RULES,
    CURING_MODE_RULES as _CURING_MODE_RULES,
    FLUID_RESIN_TERMS as _FLUID_RESIN_TERMS,
    FLUORIDE_FORMULATION_RULES as _FLUORIDE_FORMULATION_RULES,
    IONOMER_USE_RULES as _IONOMER_USE_RULES,
    MIXED_KIT_FAMILY_TERMS as _MIXED_KIT_FAMILY_TERMS,
    RESIN_HEAD_TERMS as _RESIN_HEAD_TERMS,
    RESIN_TECHNOLOGY_RULES as _RESIN_TECHNOLOGY_RULES,
    VASOCONSTRICTOR_RULES as _VASOCONSTRICTOR_RULES,
)
from dental_procurement_intelligence.normalization import (
    extract_measurements,
    normalize_description,
)

_CATEGORY_RULES = compile_category_rules(DENTAL_CATEGORY_SPECS)

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
    re.compile(r"\bSELANTE\b.*\bRESINA\b"),
    re.compile(r"\bIONOMERO(?:\s+-)?\s+DE\s+VIDRO\b.*\bRESINA\b"),
)

_ADHESIVE_CONTEXT_EXCLUSIONS = (
    re.compile(r"\bAPLICADOR(?:ES)?\s+DE\s+ADESIVO\b"),
    re.compile(r"\bADESIVO\s+PARA\s+MOLDEIRAS?\b"),
    re.compile(r"\bSELANTE\b.*\bADESIVO\b"),
    re.compile(r"\bCIMENTO ODONTOLOGICO\b.*\bADESIVO RESINOSO\b"),
)

_GLASS_IONOMER_CONTEXT_EXCLUSIONS = (
    re.compile(r"\bSELANTE\b.*\bIONOMERO\s+DE\s+VIDRO\b"),
)

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
        rf"\bDISPENSA(?:\s+O)?\s+USO\s+DE\s+{escaped}\b",
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


def _adhesive_context_excluded(text: str) -> bool:
    return any(pattern.search(text) for pattern in _ADHESIVE_CONTEXT_EXCLUSIONS)


def _glass_ionomer_context_excluded(text: str) -> bool:
    return any(
        pattern.search(text) for pattern in _GLASS_IONOMER_CONTEXT_EXCLUSIONS
    )


def _zinc_oxide_context_excluded(text: str) -> bool:
    has_zinc_oxide = (
        _term_present(text, "OXIDO DE ZINCO")
        or _term_present(text, "OXIDO ZINCO")
    )
    if not has_zinc_oxide:
        return False

    if _term_present(text, "CIMENTO ODONTOLOGICO") or _term_present(text, "CIMENTO"):
        return True

    if _term_present(text, "RESTAURADOR TEMPORARIO"):
        return True

    return (
        _term_present(text, "COMPOSICAO BASE")
        and _term_present(text, "FOSFATO CALCIO")
    )


def _eugenol_context_excluded(text: str) -> bool:
    return (
        (
            _term_present(text, "CIMENTO ODONTOLOGICO")
            or _term_present(text, "CIMENTO")
            or _term_present(text, "RESTAURADOR TEMPORARIO")
        )
        and _term_present(text, "EUGENOL")
    )


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
    if _term_present(text, "A BASE HIDROXIDO DE CALCIO"):
        return ProductCategory.CALCIUM_HYDROXIDE, ("A BASE HIDROXIDO DE CALCIO",)

    if _is_mixed_kit(text):
        return ProductCategory.UNKNOWN, ("MIXED_KIT",)

    if (
        _term_present(text, "PRILOCAINA")
        and _term_present(text, "FELIPRESSINA")
    ):
        return ProductCategory.LOCAL_ANESTHETIC, ("PRILOCAINA", "FELIPRESSINA")

    if (
        _term_present(text, "FLUORETO DE SODIO")
        and _term_present(text, "FORMA FARMACEUTICA")
        and _term_present(text, "GEL")
    ):
        return ProductCategory.FLUORIDE_GEL, ("FLUORETO DE SODIO", "GEL")

    if _has_any(text, _ANESTHETIC_ACTIVE_INGREDIENTS):
        matches = tuple(
            term for term in _ANESTHETIC_ACTIVE_INGREDIENTS if _term_present(text, term)
        )
        return ProductCategory.LOCAL_ANESTHETIC, matches

    if (
        _has_any(text, ("ADESIVO", "ADESIVOS"))
        and not _adhesive_context_excluded(text)
    ):
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
        if (
            category == ProductCategory.GLASS_IONOMER
            and _glass_ionomer_context_excluded(text)
        ):
            continue
        if (
            category == ProductCategory.ZINC_OXIDE
            and _zinc_oxide_context_excluded(text)
        ):
            continue
        if (
            category == ProductCategory.EUGENOL
            and _eugenol_context_excluded(text)
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


def _single_attribute_match(
    text: str,
    rules: tuple[tuple[str, tuple[str, ...]], ...],
) -> str | None:
    matches = {
        canonical
        for canonical, terms in rules
        if any(_term_present(text, term) for term in terms)
    }
    if len(matches) == 1:
        return next(iter(matches))
    return None


def _anesthetic_vasoconstrictor(text: str) -> str | None:
    if re.search(
        r"(?:\bSEM\s+(?:VASO(?:CONSTRITOR)?|VASO-CONSTRITOR|VASOCONTRITOR|VASOCONSTRICTOR)\b"
        r"|\bS\s*/\s*VASO(?:CONSTR(?:ITOR)?)?\b)",
        text,
    ):
        return "none"

    return _single_attribute_match(text, _VASOCONSTRICTOR_RULES)


def _resin_technology(text: str) -> str | None:
    ambiguous_nanoparticle = (
        re.search(
            r"\b(?:NANOHIBRIDA|NANO-HIBRIDA)\s+OU\s+NANOPARTICULADA\b",
            text,
        )
        or re.search(
            r"\bNANOPARTICULADA\s+OU\s+(?:NANOHIBRIDA|NANO-HIBRIDA)\b",
            text,
        )
    )
    if ambiguous_nanoparticle:
        return None
    return _single_attribute_match(text, _RESIN_TECHNOLOGY_RULES)


def _resin_curing_mode(text: str) -> str | None:
    if re.search(r"\bRESINA(?:S)?\s+FOTO\b", text):
        return "light_cure"
    return _first_attribute_match(text, _CURING_MODE_RULES)


def _adhesive_strategy(text: str) -> str | None:
    context = text
    if _term_present(text, "MARCA DE REFERENCIA"):
        context = text.split("MARCA DE REFERENCIA", 1)[0]
    return _first_attribute_match(context, _ADHESIVE_STRATEGY_RULES)


def _fluoride_formulation(text: str) -> str | None:
    if (
        _term_present(text, "OU")
        and _term_present(text, "NEUTRO")
        and _term_present(text, "ACIDULADO")
    ):
        return None
    return _first_attribute_match(text, _FLUORIDE_FORMULATION_RULES)


def _adhesive_curing_mode(text: str) -> str | None:
    if _term_present(text, "ATIVACAO DUAL"):
        return "dual_cure"

    if re.search(r"\bADESIVO\s+FOTO\b", text):
        return "light_cure"

    context = re.sub(
        r"\bRESINA\s+(?:FOTOPOLIMERIZAVEL|FOTOPOLIMERIZAVEIS)\b",
        "RESINA",
        text,
    )
    return _first_attribute_match(context, _CURING_MODE_RULES)


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
        resin_technology = _resin_technology(text)
        curing_mode = _resin_curing_mode(text)

    elif category == ProductCategory.ADHESIVE:
        adhesive_strategy = _adhesive_strategy(text)
        curing_mode = _adhesive_curing_mode(text)

    elif category == ProductCategory.GLASS_IONOMER:
        ionomer_use = _first_attribute_match(text, _IONOMER_USE_RULES)
        curing_mode = _first_attribute_match(text, _CURING_MODE_RULES)

    elif category == ProductCategory.FLUORIDE_GEL:
        fluoride_formulation = _fluoride_formulation(text)

    elif category == ProductCategory.LOCAL_ANESTHETIC:
        anesthetic_active_ingredient = _first_attribute_match(
            text,
            _ANESTHETIC_INGREDIENT_RULES,
        )
        anesthetic_vasoconstrictor = _anesthetic_vasoconstrictor(text)

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
