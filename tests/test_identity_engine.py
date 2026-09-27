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


def test_parser_extracts_resin_technology_and_curing_mode() -> None:
    product = parse_product(
        "RESINA COMPOSTA NANOHIBRIDA A2 FOTOPOLIMERIZAVEL SERINGA 4G"
    )

    attrs = product.technical_attributes
    assert attrs.resin_technology == "nanohybrid"
    assert attrs.curing_mode == "light_cure"
    assert attrs.identified_count() == 2


def test_parser_extracts_category_specific_attributes() -> None:
    adhesive = parse_product(
        "ADESIVO DENTAL UNIVERSAL FOTOPOLIMERIZAVEL FRASCO 5ML"
    )
    ionomer = parse_product(
        "IONOMERO DE VIDRO RESTAURADOR AUTOPOLIMERIZAVEL FRASCO 10G"
    )
    fluoride = parse_product("FLUOR EM GEL NEUTRO FRASCO 200ML")
    anesthetic = parse_product(
        "LIDOCAINA 2% COM EPINEFRINA TUBETE 1.8ML"
    )

    assert adhesive.technical_attributes.adhesive_strategy == "universal"
    assert adhesive.technical_attributes.curing_mode == "light_cure"
    assert ionomer.technical_attributes.ionomer_use == "restorative"
    assert ionomer.technical_attributes.curing_mode == "self_cure"
    assert fluoride.technical_attributes.fluoride_formulation == "neutral"
    assert (
        anesthetic.technical_attributes.anesthetic_active_ingredient
        == "lidocaine"
    )
    assert (
        anesthetic.technical_attributes.anesthetic_vasoconstrictor
        == "epinephrine"
    )


def test_engine_rejects_different_resin_technologies() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA MICROHIBRIDA A2 SERINGA 4G",
        "RESINA COMPOSTA NANOHIBRIDA A2 SERINGA 4G",
    )

    assert result.decision == IdentityDecision.INCOMPATIBLE
    assert any(
        "resin technology differs" in conflict
        for conflict in result.conflicts
    )


def test_engine_reviews_when_technical_attribute_is_missing_on_one_side() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA NANOHIBRIDA A2 SERINGA 4G",
        "RESINA COMPOSTA A2 SERINGA 4G",
    )

    assert result.decision == IdentityDecision.REVIEW
    assert any(
        "resin technology missing for one item" in item
        for item in result.missing_evidence
    )


def test_engine_requires_anesthetic_active_ingredient() -> None:
    result = ProductIdentityEngine().compare(
        "ANESTESICO LOCAL 2% TUBETE 1.8ML",
        "ANESTESICO LOCAL 2% TUBETE 1.8ML",
    )

    assert result.decision == IdentityDecision.REVIEW
    assert any(
        "anesthetic active ingredient missing for both items" in item
        for item in result.missing_evidence
    )


def test_engine_rejects_different_anesthetic_active_ingredients() -> None:
    result = ProductIdentityEngine().compare(
        "LIDOCAINA 2% TUBETE 1.8ML",
        "MEPIVACAINA 2% TUBETE 1.8ML",
    )

    assert result.decision == IdentityDecision.INCOMPATIBLE
    assert any(
        "anesthetic active ingredient differs" in conflict
        for conflict in result.conflicts
    )


def test_engine_rejects_vasoconstrictor_conflict() -> None:
    result = ProductIdentityEngine().compare(
        "LIDOCAINA 2% COM EPINEFRINA TUBETE 1.8ML",
        "LIDOCAINA 2% SEM VASOCONSTRITOR TUBETE 1.8ML",
    )

    assert result.decision == IdentityDecision.INCOMPATIBLE
    assert any(
        "anesthetic vasoconstrictor differs" in conflict
        for conflict in result.conflicts
    )


def test_technical_attribute_work_does_not_tune_v5_category_failures() -> None:
    descriptions = (
        "IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL",
        "PASTA PROFIATICA",
        "FLUORETO DE SODIO 2% GEL NEUTRO",
    )

    for description in descriptions:
        assert parse_product(description).category == ProductCategory.UNKNOWN


def test_technical_tuning_recognizes_registered_baseline_variants() -> None:
    ionomer = parse_product(
        "IONOMERO DE VIDRO AUTOPOLIMERIZAVEL RESTAURACAO KIT"
    )
    fluoride_acidulated = parse_product(
        "FLUOR GEL ACIDULADO 1,23% FRASCO 200ML"
    )
    fluoride_neutral = parse_product(
        "FLUOR GEL NEUTRO 2% FRASCO 200ML"
    )
    adhesive = parse_product(
        "ADESIVO DENTINARIO UNIVERSAL FOTOPOLIMERIZADO FRASCO 5ML"
    )
    no_vaso = parse_product(
        "ANESTESICO MEPIVACAINA SEM VASO 3%"
    )
    phenylephrine = parse_product(
        "ANESTESICO LOCAL ARTICAINA + FENILEFRINA"
    )
    prilocaine = parse_product(
        "ANESTESICO ODONTOLOGICO PRILOCAINA 3% COM FELIPRESSINA"
    )

    assert ionomer.technical_attributes.ionomer_use == "restorative"
    assert (
        fluoride_acidulated.technical_attributes.fluoride_formulation
        == "acidulated"
    )
    assert (
        fluoride_neutral.technical_attributes.fluoride_formulation
        == "neutral"
    )
    assert adhesive.technical_attributes.adhesive_strategy == "universal"
    assert adhesive.technical_attributes.curing_mode == "light_cure"
    assert (
        no_vaso.technical_attributes.anesthetic_vasoconstrictor
        == "none"
    )
    assert (
        phenylephrine.technical_attributes.anesthetic_vasoconstrictor
        == "phenylephrine"
    )
    assert (
        prilocaine.technical_attributes.anesthetic_active_ingredient
        == "prilocaine"
    )


def test_broader_technical_terms_do_not_invent_missing_attributes() -> None:
    adhesive = parse_product(
        "ADESIVO MONOCOMPONENTE FOTOPOLIMERIZAVEL FRASCO 6ML"
    )
    fluoride = parse_product("FLUOR EM GEL FRASCO 200ML")
    ionomer = parse_product("IONOMERO DE VIDRO FRASCO 10G")
    anesthetic = parse_product("MEPIVACAINA 3% TUBETE 1.8ML")

    assert adhesive.technical_attributes.adhesive_strategy is None
    assert fluoride.technical_attributes.fluoride_formulation is None
    assert ionomer.technical_attributes.ionomer_use is None
    assert anesthetic.technical_attributes.anesthetic_vasoconstrictor is None


def test_prilocaine_attribute_does_not_expand_category_taxonomy() -> None:
    product = parse_product("PRILOCAINA 3% SOLUCAO INJETAVEL")

    assert product.category == ProductCategory.UNKNOWN
    assert product.technical_attributes.anesthetic_active_ingredient is None


def test_technical_v2_tuning_recognizes_registered_variants() -> None:
    chemically_activated = parse_product(
        "IONOMERO DE VIDRO QUIMICAMENTE ATIVADO PARA RESTAURACAO"
    )
    chemically_activated_second = parse_product(
        "IONOMERO DE VIDRO RESTAURADOR TIPO II QUIMICAMENTE ATIVADO"
    )
    acidulato = parse_product(
        "FLUOR EM GEL ACIDULATO TUTTI FRUTTI"
    )
    abbreviated_no_vaso = parse_product(
        "ANESTESICO MEPIVACAINA S/VASO 3%"
    )
    plural_luting = parse_product(
        "IONOMERO DE VIDRO REFORCADO PARA CIMENTACOES"
    )

    assert (
        chemically_activated.technical_attributes.curing_mode
        == "self_cure"
    )
    assert (
        chemically_activated_second.technical_attributes.curing_mode
        == "self_cure"
    )
    assert (
        acidulato.technical_attributes.fluoride_formulation
        == "acidulated"
    )
    assert (
        abbreviated_no_vaso.technical_attributes.anesthetic_vasoconstrictor
        == "none"
    )
    assert plural_luting.technical_attributes.ionomer_use == "luting"


def test_technical_v2_tuning_does_not_expand_unrelated_contexts() -> None:
    resin = parse_product(
        "RESINA COMPOSTA A2 QUIMICAMENTE ATIVADO SERINGA 4G"
    )
    fluoride = parse_product("FLUOR EM GEL FRASCO 200ML")
    ionomer = parse_product("IONOMERO DE VIDRO FRASCO 10G")
    anesthetic = parse_product("MEPIVACAINA 3% TUBETE 1.8ML")

    assert resin.category == ProductCategory.COMPOSITE_RESIN
    assert resin.technical_attributes.curing_mode == "self_cure"
    assert fluoride.technical_attributes.fluoride_formulation is None
    assert ionomer.technical_attributes.ionomer_use is None
    assert anesthetic.technical_attributes.anesthetic_vasoconstrictor is None


def test_technical_v2_tuning_keeps_taxonomy_holdout_unchanged() -> None:
    descriptions = (
        "IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL",
        "PASTA PROFIATICA",
        "FLUORETO DE SODIO 2% GEL NEUTRO",
    )

    for description in descriptions:
        assert parse_product(description).category == ProductCategory.UNKNOWN


def test_technical_v3_tuning_recognizes_registered_variants() -> None:
    abbreviated_no_vaso = parse_product(
        "ANESTESICO LOCAL MEPIVACAINA 3% S/VASOCONSTR."
    )
    misspelled_no_vaso = parse_product(
        "ANESTESICO LOCAL MEPIVACAINA 3% SEM VASOCONTRITOR"
    )
    photoactivated = parse_product(
        "IONOMERO DE VIDRO FOTOATIVADO"
    )
    plural_resin = parse_product(
        "RESINAS FOTOPOLIMERIZAVEIS A1 SERINGA 4G"
    )
    bulk_fill = parse_product(
        "RESINA BULK FILL SERINGA 4G"
    )
    fluoride = parse_product(
        "GEL DE FLUORETO DE SODIO A 1,23% BISNAGA 100G"
    )

    assert (
        abbreviated_no_vaso.technical_attributes.anesthetic_vasoconstrictor
        == "none"
    )
    assert (
        misspelled_no_vaso.technical_attributes.anesthetic_vasoconstrictor
        == "none"
    )
    assert photoactivated.category == ProductCategory.GLASS_IONOMER
    assert photoactivated.technical_attributes.curing_mode == "light_cure"
    assert plural_resin.category == ProductCategory.COMPOSITE_RESIN
    assert plural_resin.technical_attributes.curing_mode == "light_cure"
    assert bulk_fill.category == ProductCategory.COMPOSITE_RESIN
    assert bulk_fill.technical_attributes.resin_technology == "bulk_fill"
    assert fluoride.category == ProductCategory.FLUORIDE_GEL


def test_technical_v3_tuning_keeps_v5_holdout_failures_unchanged() -> None:
    descriptions = (
        "IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL",
        "PASTA PROFIATICA",
        "FLUORETO DE SODIO 2% GEL NEUTRO",
    )

    for description in descriptions:
        assert parse_product(description).category == ProductCategory.UNKNOWN


def test_technical_v3_category_rules_are_not_unbounded() -> None:
    unrelated = (
        "MATERIAL BULK FILL 4G",
        "GEL DE SODIO 100G",
        "FOTOPOLIMERIZAVEL A1 4G",
    )

    for description in unrelated:
        assert parse_product(description).category == ProductCategory.UNKNOWN


def test_technical_v4_tuning_recognizes_registered_variants() -> None:
    adhesive_photo = parse_product(
        "AGENTE DE UNIAO MULTI-USO ADESIVO FOTO"
    )
    apinephrine = parse_product(
        "ANESTESICO ARTICAINA COM APINEFRINA"
    )
    total_etch = parse_product(
        "ADESIVO FOTOPOLIMERIZAVEL COMPATIVEL COM "
        "CONDICIONAMENTO ACIDO TOTAL"
    )
    photo_resin = parse_product(
        "RESINA FOTOPOLIMERIZAVEL COR A2 MICROHIBRIDA SERINGA 4G"
    )

    assert adhesive_photo.category == ProductCategory.ADHESIVE
    assert adhesive_photo.technical_attributes.curing_mode == "light_cure"
    assert (
        apinephrine.technical_attributes.anesthetic_vasoconstrictor
        == "epinephrine"
    )
    assert (
        total_etch.technical_attributes.adhesive_strategy
        == "etch_and_rinse"
    )
    assert total_etch.technical_attributes.curing_mode == "light_cure"
    assert photo_resin.category == ProductCategory.COMPOSITE_RESIN
    assert photo_resin.technical_attributes.resin_technology == "microhybrid"
    assert photo_resin.technical_attributes.curing_mode == "light_cure"


def test_adhesive_curing_mode_ignores_resin_context() -> None:
    product = parse_product(
        "ADESIVO PARA RESINA FOTOPOLIMERIZAVEL FRASCO UNICO 5ML"
    )

    assert product.category == ProductCategory.ADHESIVE
    assert product.technical_attributes.curing_mode is None


def test_adhesive_curing_mode_keeps_direct_adhesive_evidence() -> None:
    product = parse_product(
        "ADESIVO FOTOPOLIMERIZAVEL PARA RESINA COMPOSTA FRASCO 5ML"
    )

    assert product.category == ProductCategory.ADHESIVE
    assert product.technical_attributes.curing_mode == "light_cure"


def test_technical_v4_tuning_keeps_v5_holdout_failures_unchanged() -> None:
    descriptions = (
        "IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL",
        "PASTA PROFIATICA",
        "FLUORETO DE SODIO 2% GEL NEUTRO",
    )

    for description in descriptions:
        assert parse_product(description).category == ProductCategory.UNKNOWN


def test_technical_v4_category_rules_remain_bounded() -> None:
    unrelated = (
        "MATERIAL FOTOPOLIMERIZAVEL A2",
        "PRODUTO MICROHIBRIDO 4G",
        "GEL DE SODIO 100G",
    )

    for description in unrelated:
        assert parse_product(description).category == ProductCategory.UNKNOWN


def test_technical_v5_context_keeps_primary_product_category() -> None:
    ionomer = parse_product(
        "CIMENTO DE IONOMERO DE VIDRO DE ALTA VISCOSIDADE "
        "DISPENSA O USO DE ADESIVO"
    )
    applicator = parse_product(
        "APLICADOR DE ADESIVO DESCARTAVEL CAIXA COM 100 UNIDADES"
    )
    sealant = parse_product(
        "SELANTE PARA FOSSULAS E FISSURAS FOTOPOLIMERIZAVEL "
        "COMPOSTO POR RESINA FOTOPOLIMERIZAVEL DE ALTA FLUIDEZ"
    )

    assert ionomer.category == ProductCategory.GLASS_IONOMER
    assert applicator.category == ProductCategory.UNKNOWN
    assert sealant.category == ProductCategory.UNKNOWN
    assert sealant.technical_attributes.curing_mode is None


def test_technical_v5_recognizes_registered_spelling_variants() -> None:
    resin_typo = parse_product(
        "RESINA COMPOSTA A1 FOTOPOLIMERIZALVEL SERINGA 4G"
    )
    ionomer_typo = parse_product(
        "CIMENTO DE IONOMERO DE VIDRO FOTOPOLIMERIXAVE"
    )
    microhybrid_typo = parse_product(
        "RESINA COMPOSTA MICROHIDRIDA A2 SERINGA 4G"
    )

    assert resin_typo.technical_attributes.curing_mode == "light_cure"
    assert ionomer_typo.technical_attributes.curing_mode == "light_cure"
    assert (
        microhybrid_typo.technical_attributes.resin_technology
        == "microhybrid"
    )


def test_technical_v5_recognizes_new_explicit_product_forms() -> None:
    dental_resin = parse_product(
        "RESINA ODONTOLOGICA FOTOPOLIMERIZAVEL COR A2"
    )
    form_resin = parse_product(
        "RESINA FORMA NANOHIBRIDA 4G COR A1B"
    )
    neutral_fluoride = parse_product(
        "FLUOR NEUTRO FRASCO 200ML"
    )
    acidulated_fluoride = parse_product(
        "FLUOR ACIDULADO FRASCO 200ML"
    )
    photo_resin = parse_product(
        "RESINA FOTO B1 CHARISMA 4G"
    )
    photo_flow = parse_product(
        "RESINA FOTO A1 OPALLIS FLOW 2G"
    )

    assert dental_resin.category == ProductCategory.COMPOSITE_RESIN
    assert dental_resin.technical_attributes.curing_mode == "light_cure"
    assert form_resin.category == ProductCategory.COMPOSITE_RESIN
    assert form_resin.technical_attributes.resin_technology == "nanohybrid"
    assert neutral_fluoride.category == ProductCategory.FLUORIDE_GEL
    assert (
        neutral_fluoride.technical_attributes.fluoride_formulation
        == "neutral"
    )
    assert acidulated_fluoride.category == ProductCategory.FLUORIDE_GEL
    assert (
        acidulated_fluoride.technical_attributes.fluoride_formulation
        == "acidulated"
    )
    assert photo_resin.category == ProductCategory.COMPOSITE_RESIN
    assert photo_resin.technical_attributes.curing_mode == "light_cure"
    assert photo_flow.category == ProductCategory.FLOWABLE_RESIN
    assert photo_flow.technical_attributes.curing_mode == "light_cure"


def test_technical_v5_explicit_alternative_has_no_single_resin_technology() -> None:
    product = parse_product(
        "RESINA COMPOSTA FOTOPOLIMERIZAVEL "
        "MICRO-HIBRIDA OU NANO-HIBRIDA COR A1"
    )

    assert product.category == ProductCategory.COMPOSITE_RESIN
    assert product.technical_attributes.resin_technology is None
    assert product.technical_attributes.curing_mode == "light_cure"


def test_technical_v5_tuning_keeps_taxonomy_holdout_unchanged() -> None:
    descriptions = (
        "IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL",
        "PASTA PROFIATICA",
        "FLUORETO DE SODIO 2% GEL NEUTRO",
    )

    for description in descriptions:
        assert parse_product(description).category == ProductCategory.UNKNOWN


def test_technical_v5_category_rules_remain_bounded() -> None:
    unrelated = (
        "APLICADOR UNIVERSAL DESCARTAVEL",
        "MATERIAL FOTO A2 4G",
        "PRODUTO ODONTOLOGICO NANOHIBRIDO",
    )

    for description in unrelated:
        assert parse_product(description).category == ProductCategory.UNKNOWN


def test_technical_v6_tuning_recognizes_bounded_variants() -> None:
    prilocaine = parse_product(
        "PRILOCAINA COMPOSICAO ASSOCIADA COM FELIPRESSINA"
    )
    fluoride_acidulated = parse_product(
        "FLUORETO DE SODIO CONCENTRACAO 2% "
        "FORMA FARMACEUTICA GEL TIXOTROPICO "
        "CARACTERISTICA ADICIONAL ACIDULADO"
    )
    fluoride_neutral = parse_product(
        "FLUORETO DE SODIO CONCENTRACAO 2% "
        "FORMA FARMACEUTICA GEL TIXOTROPICO "
        "CARACTERISTICA ADICIONAL NEUTRO"
    )
    adhesive = parse_product(
        "ADESIVO DENTAL TIPO ATIVACAO DUAL "
        "COMPONENTES AUTOCONDICIONANTE"
    )

    assert prilocaine.category == ProductCategory.LOCAL_ANESTHETIC
    assert (
        prilocaine.technical_attributes.anesthetic_active_ingredient
        == "prilocaine"
    )
    assert (
        prilocaine.technical_attributes.anesthetic_vasoconstrictor
        == "felypressin"
    )
    assert fluoride_acidulated.category == ProductCategory.FLUORIDE_GEL
    assert (
        fluoride_acidulated.technical_attributes.fluoride_formulation
        == "acidulated"
    )
    assert fluoride_neutral.category == ProductCategory.FLUORIDE_GEL
    assert (
        fluoride_neutral.technical_attributes.fluoride_formulation
        == "neutral"
    )
    assert adhesive.category == ProductCategory.ADHESIVE
    assert adhesive.technical_attributes.adhesive_strategy == "self_etch"
    assert adhesive.technical_attributes.curing_mode == "dual_cure"


def test_technical_v6_tuning_preserves_previous_holdout_boundaries() -> None:
    old_prilocaine = parse_product("PRILOCAINA 3% SOLUCAO INJETAVEL")
    old_fluoride = parse_product("FLUORETO DE SODIO 2% GEL NEUTRO")
    resin = parse_product("RESINA COMPOSTA ATIVACAO DUAL A2")

    assert old_prilocaine.category == ProductCategory.UNKNOWN
    assert old_fluoride.category == ProductCategory.UNKNOWN
    assert resin.category == ProductCategory.COMPOSITE_RESIN
    assert resin.technical_attributes.curing_mode is None


def test_technical_v7_tuning_recognizes_bounded_variants() -> None:
    benzocaine = parse_product("ANESTESICO TOPICO GEL BENZOCAINA 20%")
    mold_adhesive = parse_product(
        "ADESIVO PARA MOLDEIRAS USO UNIVERSAL ASPECTO FISICO LIQUIDO"
    )
    total_etch = parse_product(
        "ADESIVO FOTOPOLIMERIZAVEL PRIMER DECAPAGEM TOTAL"
    )
    typo_ionomer = parse_product("LONOMERO DE VIDRO PO E LIQUIDO")
    developer = parse_product(
        "REVELADORREVELADOR INDICADO PARA REVELACAO DA IMAGEM DO FILME"
    )
    liner = parse_product(
        "CIMENTO DE IONOMERO DE VIDRO TIPO FORRACAO AUTOPOLIMERIZAVEL"
    )
    restorative = parse_product(
        "CIMENTO DE IONOMERO DE VIDRO PARA NUCLEOS E RESTAURACOES"
    )
    sealant = parse_product(
        "SELANTE PARA SUPERFICIES DE RESTAURACOES DE IONOMERO DE VIDRO"
    )
    z250 = parse_product("RESINA FILTEK Z250 XT A1")

    assert benzocaine.category == ProductCategory.LOCAL_ANESTHETIC
    assert (
        benzocaine.technical_attributes.anesthetic_active_ingredient
        == "benzocaine"
    )
    assert mold_adhesive.category == ProductCategory.UNKNOWN
    assert total_etch.category == ProductCategory.ADHESIVE
    assert total_etch.technical_attributes.adhesive_strategy == "etch_and_rinse"
    assert typo_ionomer.category == ProductCategory.GLASS_IONOMER
    assert developer.category == ProductCategory.RADIOGRAPHIC_DEVELOPER
    assert liner.category == ProductCategory.GLASS_IONOMER
    assert liner.technical_attributes.ionomer_use == "liner_base"
    assert restorative.category == ProductCategory.GLASS_IONOMER
    assert restorative.technical_attributes.ionomer_use == "restorative"
    assert sealant.category == ProductCategory.UNKNOWN
    assert z250.category == ProductCategory.COMPOSITE_RESIN


def test_technical_v7_tuning_keeps_new_rules_bounded() -> None:
    benzocaine_only = parse_product("BENZOCAINA 20% GEL")
    generic_developer = parse_product("REVELADOR DE PLACA BACTERIANA")
    universal_adhesive = parse_product("ADESIVO DENTAL UNIVERSAL")
    bulk_flow = parse_product("RESINA FILTEK BULK FILL FLOW A2")

    assert benzocaine_only.category == ProductCategory.UNKNOWN
    assert generic_developer.category == ProductCategory.UNKNOWN
    assert universal_adhesive.category == ProductCategory.ADHESIVE
    assert (
        universal_adhesive.technical_attributes.adhesive_strategy
        == "universal"
    )
    assert bulk_flow.category == ProductCategory.FLOWABLE_RESIN
    assert bulk_flow.technical_attributes.resin_technology == "bulk_fill"
