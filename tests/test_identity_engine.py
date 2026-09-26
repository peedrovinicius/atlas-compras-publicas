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


def test_plural_domain_terms_are_recognized() -> None:
    cases = {
        "MATERIAL ODONTOLOGICO RESINAS FLUIDAS": ProductCategory.FLOWABLE_RESIN,
        "MATERIAL ODONTOLOGICO ADESIVOS": ProductCategory.ADHESIVE,
        "IONOMEROS DE VIDRO RESTAURADOR": ProductCategory.GLASS_IONOMER,
    }

    for description, expected in cases.items():
        assert parse_product(description).category == expected


def test_bulk_fill_fluid_resin_has_flowable_precedence() -> None:
    product = parse_product(
        "RESINA COMPOSTA TIPO BULK FILL ASPECTO FISICO FLUIDA "
        "BAIXA VISCOSIDADE SERINGA 2G"
    )

    assert product.category == ProductCategory.FLOWABLE_RESIN


def test_generic_anesthetic_product_is_recognized() -> None:
    product = parse_product("CAIXAS DE ANESTESICO SS.WHITI100")

    assert product.category == ProductCategory.LOCAL_ANESTHETIC


def test_fluoride_gel_accepts_acid_word_order() -> None:
    product = parse_product("FLUOR ACIDO GEL")

    assert product.category == ProductCategory.FLUORIDE_GEL


def test_alginate_in_isolator_composition_is_not_product_identity() -> None:
    product = parse_product(
        "ISOLANTE USO ODONTOLOGICO COMPOSICAO BASICA "
        "ALGINATO DE SODIO E AGUA"
    )

    assert product.category == ProductCategory.UNKNOWN


def test_real_alginate_product_remains_recognized() -> None:
    product = parse_product("ALGINATO USO ODONTOLOGICO PRESA RAPIDA 453G")

    assert product.category == ProductCategory.ALGINATE


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


def test_mixed_kit_is_not_reduced_to_one_product_category() -> None:
    product = parse_product(
        "KIT 3 RESINAS MAIS ADESIVO UNIVERSAL RESINA COM NANOPARTICULAS"
    )

    assert product.category == ProductCategory.UNKNOWN
    assert "MIXED_KIT" in product.matched_terms


def test_negated_eugenol_is_not_classified_as_eugenol() -> None:
    product = parse_product(
        "CIMENTO ODONTOLOGICO ENDODONTICO SEM EUGENOL ASPECTO FISICO PASTA"
    )

    assert product.category == ProductCategory.UNKNOWN


def test_positive_eugenol_remains_supported() -> None:
    product = parse_product("EUGENOL FRASCO 20ML")

    assert product.category == ProductCategory.EUGENOL


def test_zinc_oxide_without_preposition_is_recognized() -> None:
    product = parse_product("OXIDO ZINCO PO FRASCO 50G")

    assert product.category == ProductCategory.ZINC_OXIDE


def test_radiological_fixer_variant_is_recognized() -> None:
    product = parse_product("FIXADOR RADIOLOGICO PARA PROCESSAMENTO MANUAL 500ML")

    assert product.category == ProductCategory.RADIOGRAPHIC_FIXER


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


def test_engine_rejects_different_package_counts() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA A2 C/1 SERINGA 4G",
        "RESINA COMPOSTA A2 C/2 SERINGAS 4G",
    )

    assert result.decision == IdentityDecision.INCOMPATIBLE
    assert any("package count differs" in conflict for conflict in result.conflicts)


def test_engine_requires_review_when_package_count_is_missing_on_one_side() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA A2 SERINGA 4G",
        "RESINA COMPOSTA A2 C/2 SERINGAS 4G",
    )

    assert result.decision == IdentityDecision.REVIEW
    assert any("package count missing" in item for item in result.missing_evidence)


def test_engine_matches_same_explicit_package_configuration() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA A2 C/2 SERINGAS 4G",
        "RES FOTOP A2 COM 2 SERINGAS 4G",
    )

    assert result.decision == IdentityDecision.MATCH
    assert "same package count: 2" in result.supporting_evidence
    assert "same total package quantity: 8 g" in result.supporting_evidence


def test_c_slash_mass_is_not_interpreted_as_package_count() -> None:
    product = parse_product("RESINA MICROHIBRIDA A3,5 SERINGA C/ 4G")

    assert product.package_count is None
    assert product.measurement_resolution == "single"
    assert product.unit_quantity is not None
    assert product.unit_quantity.value == Decimal("4")
    assert product.total_quantity is None


def test_parser_confirms_explicit_unit_and_total_package_measurements() -> None:
    product = parse_product(
        "RESINA COMPOSTA A2 C/2 SERINGAS 4G CONTEUDO TOTAL 8G"
    )

    assert product.package_count == 2
    assert product.measurement_resolution == "package_total_confirmed"
    assert len(product.measurement_candidates) == 2
    assert product.unit_quantity is not None
    assert product.unit_quantity.value == Decimal("4")
    assert product.total_quantity is not None
    assert product.total_quantity.value == Decimal("8")


def test_equivalent_measurements_are_deduplicated_after_unit_conversion() -> None:
    product = parse_product(
        "RESINA COMPOSTA A2 SERINGA 4G EQUIVALENTE A 4000MG"
    )

    assert len(product.measurement_candidates) == 1
    assert product.measurement_resolution == "single"
    assert product.unit_quantity is not None
    assert product.unit_quantity.value == Decimal("4")


def test_mixed_mass_and_volume_measurements_are_ambiguous() -> None:
    product = parse_product(
        "KIT RESINA COMPOSTA A2 SERINGA 4G MAIS ADESIVO FRASCO 5ML"
    )
    quality = assess_normalization_quality(product)

    assert product.category == ProductCategory.UNKNOWN
    assert product.measurement_resolution == "ambiguous"
    assert len(product.measurement_candidates) == 2
    assert product.unit_quantity is None
    assert product.total_quantity is None
    assert not quality.measurement_identified
    assert "measurement_ambiguous" in quality.missing_fields


def test_same_dimension_heterogeneous_kit_is_ambiguous() -> None:
    product = parse_product(
        "KIT RESINA COMPOSTA A2 COM 1 SERINGA 4G E 1 SERINGA 2G"
    )

    assert product.measurement_resolution == "ambiguous"
    assert product.unit_quantity is None
    assert product.total_quantity is None
