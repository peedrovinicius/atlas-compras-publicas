from decimal import Decimal

from dental_procurement_intelligence.identity import (
    IdentityDecision,
    ProductCategory,
    ProductIdentityEngine,
    assess_normalization_quality,
    parse_product,
)


def test_parser_structures_abbreviated_composite_resin() -> None:
    product = parse_product("RES FOTOP A2 C/2 SERINGAS 4G")

    assert product.category == ProductCategory.COMPOSITE_RESIN
    assert product.shade == "A2"
    assert product.presentation == "syringe"
    assert product.package_count == 2
    assert product.unit_quantity is not None
    assert product.unit_quantity.value == Decimal("4")
    assert product.unit_quantity.unit == "g"
    assert product.total_quantity is not None
    assert product.total_quantity.value == Decimal("8")


def test_microhybrid_resin_is_composite_resin() -> None:
    product = parse_product("RESINA MICROHIBRIDA A3,5 SERINGA C/ 4G")

    assert product.category == ProductCategory.COMPOSITE_RESIN
    assert product.shade == "A3.5"


def test_adhesive_takes_precedence_over_contextual_resin_mention() -> None:
    product = parse_product(
        "ADESIVO PARA RESTAURACOES DE RESINA COMPOSTA PRIMER E BOND UNIVERSAL"
    )

    assert product.category == ProductCategory.ADHESIVE


def test_polishing_kit_is_not_classified_as_composite_resin() -> None:
    product = parse_product(
        "KIT PONTAS PARA ACABAMENTO E POLIMENTO DE RESINA COMPOSTA"
    )

    assert product.category == ProductCategory.UNKNOWN


def test_local_anesthetic_is_recognized_by_active_ingredient() -> None:
    for description in (
        "LIDOCAINA CLORIDRATO DOSAGEM 3% INJETAVEL",
        "ARTICAINA ASSOCIADA COM EPINEFRINA CONCENTRACAO 4%",
        "MEPIVACAINA CLORIDRATO ASSOCIADA COM EPINEFRINA DOSAGEM 2%",
    ):
        product = parse_product(description)
        assert product.category == ProductCategory.LOCAL_ANESTHETIC


def test_parser_extracts_phosphoric_acid_concentration() -> None:
    product = parse_product(
        "ACIDO FOSFORICO 37% GEL SERINGA 2,5ML PACOTE COM 3 UNIDADES"
    )

    assert product.category == ProductCategory.PHOSPHORIC_ACID
    assert product.presentation == "syringe"
    assert product.concentration_percent == Decimal("37")
    assert product.unit_quantity is not None
    assert product.unit_quantity.value == Decimal("2.5")


def test_taxonomy_recognizes_additional_real_world_categories() -> None:
    cases = {
        "ALGINATO ODONTOLOGICO POTE 410G": ProductCategory.ALGINATE,
        "FLUOR EM GEL FRASCO 200ML": ProductCategory.FLUORIDE_GEL,
        "PASTA PROFILATICA TUBO 90G": ProductCategory.PROPHYLAXIS_PASTE,
        "OXIDO DE ZINCO PO FRASCO 50G": ProductCategory.ZINC_OXIDE,
        "FIXADOR RADIOGRAFICO ODONTOLOGICO 475ML": (
            ProductCategory.RADIOGRAPHIC_FIXER
        ),
    }

    for description, expected_category in cases.items():
        assert parse_product(description).category == expected_category


def test_quality_score_is_high_for_fully_structured_resin() -> None:
    product = parse_product("RESINA COMPOSTA A2 SERINGA 4G")
    quality = assess_normalization_quality(product)

    assert quality.score == Decimal("1.000")
    assert quality.level == "high"
    assert quality.fully_structured
    assert quality.missing_fields == ()


def test_quality_score_exposes_missing_critical_attribute() -> None:
    product = parse_product("ACIDO FOSFORICO GEL SERINGA 2,5ML")
    quality = assess_normalization_quality(product)

    assert quality.score == Decimal("0.900")
    assert quality.level == "medium"
    assert not quality.fully_structured
    assert quality.critical_attribute_name == "concentration_percent"
    assert quality.critical_attribute_identified is False
    assert "concentration_percent" in quality.missing_fields


def test_engine_rejects_different_concentrations() -> None:
    result = ProductIdentityEngine().compare(
        "ACIDO FOSFORICO 37% SERINGA 2,5ML",
        "ACIDO FOSFORICO 35% SERINGA 2,5ML",
    )

    assert result.decision == IdentityDecision.INCOMPATIBLE
    assert any(
        "concentration_percent differs" in conflict
        for conflict in result.conflicts
    )


def test_engine_requires_review_when_critical_attribute_is_missing() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA SERINGA 4G",
        "RESINA COMPOSTA SERINGA 4G",
    )

    assert result.decision == IdentityDecision.REVIEW
    assert any("shade missing" in item for item in result.missing_evidence)


def test_engine_matches_equivalent_descriptions_with_explanation() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA FOTOPOLIMERIZAVEL COR A2 SERINGA 4 G",
        "RES FOTOP A2 SERINGA 4G",
    )

    assert result.decision == IdentityDecision.MATCH
    assert result.score == Decimal("1.00")
    assert not result.conflicts
    assert "same shade: A2" in result.supporting_evidence


def test_engine_rejects_flowable_vs_composite_even_with_same_shade_and_mass() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA A2 SERINGA 2G",
        "RESINA FLOW A2 SERINGA 2G",
    )

    assert result.decision == IdentityDecision.INCOMPATIBLE
    assert any("category differs" in conflict for conflict in result.conflicts)


def test_engine_rejects_different_normalized_mass() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA A2 SERINGA 4G",
        "RESINA COMPOSTA A2 SERINGA 3.5G",
    )

    assert result.decision == IdentityDecision.INCOMPATIBLE
    assert any("unit quantity differs" in conflict for conflict in result.conflicts)
