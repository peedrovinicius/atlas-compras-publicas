from dental_procurement_intelligence.identity.medications import (
    MedicationDosageForm,
    MedicationRoute,
    parse_medication,
)


def test_parse_medication_tablet() -> None:
    result = parse_medication("Amiodarona 200mg - Comprimido")

    assert result.active_ingredient == "AMIODARONA"
    assert result.strength == "200 mg"
    assert result.dosage_form == MedicationDosageForm.TABLET
    assert result.route == MedicationRoute.ORAL


def test_parse_medication_injectable_with_br_code() -> None:
    result = parse_medication(
        "(BR0268228) CEFALOTINA SÓDICA, CONCENTRAÇÃO: 1 G, "
        "FRASCO-AMPOLA"
    )

    assert result.active_ingredient == "CEFALOTINA SODICA"
    assert result.strength == "1 g"
    assert result.dosage_form == MedicationDosageForm.INJECTABLE
    assert result.route == MedicationRoute.INJECTABLE


def test_parse_medication_oral_liquid() -> None:
    result = parse_medication(
        "CLONAZEPAM, DOSAGEM: 2,5 MG/ML, APRESENTACAO: "
        "SOLUÇÃO ORAL - GOTAS"
    )

    assert result.active_ingredient == "CLONAZEPAM"
    assert result.strength == "2.5 mg/ml"
    assert result.dosage_form == MedicationDosageForm.ORAL_LIQUID
    assert result.route == MedicationRoute.ORAL


def test_parse_medication_ophthalmic() -> None:
    result = parse_medication("CLORANFENICOL COLIRIO 32MG/8 ML")

    assert result.active_ingredient == "CLORANFENICOL"
    assert result.dosage_form == MedicationDosageForm.OPHTHALMIC
    assert result.route == MedicationRoute.OPHTHALMIC


def test_medication_v1_tuning_covers_bounded_variants() -> None:
    brand_only = parse_medication("BENESTARE 625 MG CPR")
    association = parse_medication(
        "Ceftazidima composição: associado ao avibactam, "
        "concentração: 2000 mg + 500, forma farmaceutica: injetável"
    )
    adjunct = parse_medication(
        "PRILOCAINA (CLORIDRATO) 30MG + FELIPRESSINA 0,03 UI "
        "- TUBETE 1,8ML"
    )
    br_code = parse_medication(
        "(BR0270612) BENZILPENICILINA, USO: INJETÁVEL, "
        "DOSAGEM: 1.200.000UI, APRESENTACAO: BENZATINA, "
        "FRASCO-AMPOLA"
    )
    joined = parse_medication("Aciclovir50 mg/g")
    intravenous = parse_medication(
        "ALBUMINA HUMANA 200 G/L C/ 50 ML USO INTRAVENOSO"
    )
    typo = parse_medication("Ácidofólico 5 mg")

    assert brand_only.active_ingredient is None

    assert association.active_ingredient == "CEFTAZIDIMA + AVIBACTAM"
    assert association.strength == "2000 mg"

    assert adjunct.active_ingredient == "PRILOCAINA CLORIDRATO + FELIPRESSINA"
    assert adjunct.dosage_form == MedicationDosageForm.OTHER

    assert br_code.active_ingredient == "BENZILPENICILINA BENZATINA"
    assert br_code.strength == "1200000 ui"

    assert joined.active_ingredient == "ACICLOVIR"
    assert joined.strength == "50 mg/g"

    assert intravenous.strength == "200 g/l"
    assert intravenous.route == MedicationRoute.INJECTABLE

    assert typo.active_ingredient == "ACIDO FOLICO"


def test_medication_v1_tuning_keeps_numeric_denominator_context_bounded() -> None:
    unknown_form = parse_medication("DESLANOSIDEO 0,4MG/2ML")
    injectable = parse_medication(
        "ACIDO ASCORBICO (VITAMINA C) 500 MG/5ML INJETAVEL"
    )
    ophthalmic = parse_medication("CLORANFENICOL COLIRIO 32MG/8 ML")

    assert unknown_form.strength == "0.4 mg"
    assert injectable.strength == "500 mg/5 ml"
    assert ophthalmic.strength == "32 mg"
