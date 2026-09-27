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
