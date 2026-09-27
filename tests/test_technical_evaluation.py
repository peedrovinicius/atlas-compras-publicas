import json
from pathlib import Path

from dental_procurement_intelligence.evaluation import (
    evaluate_technical_attributes,
    technical_attribute_errors,
)


def _write_dataset(path: Path) -> None:
    rows = [
        {
            "id": "ta-1",
            "description": (
                "RESINA COMPOSTA NANOHIBRIDA A2 "
                "FOTOPOLIMERIZAVEL SERINGA 4G"
            ),
            "expected_category": "composite_resin",
            "expected_attributes": {
                "resin_technology": "nanohybrid",
                "curing_mode": "light_cure",
            },
            "evaluated_attributes": [
                "resin_technology",
                "curing_mode",
            ],
            "source_url": "https://example.test/1",
        },
        {
            "id": "ta-2",
            "description": "FLUOR EM GEL FRASCO 200ML",
            "expected_category": "fluoride_gel",
            "expected_attributes": {
                "fluoride_formulation": None,
            },
            "evaluated_attributes": [
                "fluoride_formulation",
            ],
            "source_url": "https://example.test/2",
        },
        {
            "id": "ta-3",
            "description": "LIDOCAINA 2% COM EPINEFRINA TUBETE 1.8ML",
            "expected_category": "local_anesthetic",
            "expected_attributes": {
                "anesthetic_active_ingredient": "lidocaine",
                "anesthetic_vasoconstrictor": "epinephrine",
            },
            "evaluated_attributes": [
                "anesthetic_active_ingredient",
                "anesthetic_vasoconstrictor",
            ],
            "source_url": "https://example.test/3",
        },
    ]
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_technical_attribute_report_counts_reviewed_fields(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "technical.jsonl"
    _write_dataset(dataset)

    report = evaluate_technical_attributes(dataset)

    assert report.sample_count == 3
    assert report.category_accuracy == 1.0
    assert report.evaluated_attribute_count == 5
    assert report.correct_attribute_count == 5
    assert report.micro_accuracy == 1.0

    resin = report.per_attribute["resin_technology"]
    assert resin.evaluated_count == 1
    assert resin.positive_support == 1
    assert resin.positive_accuracy == 1.0

    fluoride = report.per_attribute["fluoride_formulation"]
    assert fluoride.evaluated_count == 1
    assert fluoride.positive_support == 0
    assert fluoride.false_positive_count == 0


def test_technical_attribute_report_distinguishes_error_types(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "technical.jsonl"
    rows = [
        {
            "id": "fp",
            "description": "FLUOR EM GEL NEUTRO FRASCO 200ML",
            "expected_category": "fluoride_gel",
            "expected_attributes": {
                "fluoride_formulation": None,
            },
            "evaluated_attributes": ["fluoride_formulation"],
            "source_url": "https://example.test/fp",
        },
        {
            "id": "fn",
            "description": "ADESIVO DENTAL FRASCO 5ML",
            "expected_category": "dental_adhesive",
            "expected_attributes": {
                "adhesive_strategy": "universal",
            },
            "evaluated_attributes": ["adhesive_strategy"],
            "source_url": "https://example.test/fn",
        },
        {
            "id": "mismatch",
            "description": "RESINA COMPOSTA NANOHIBRIDA A2 SERINGA 4G",
            "expected_category": "composite_resin",
            "expected_attributes": {
                "resin_technology": "microhybrid",
            },
            "evaluated_attributes": ["resin_technology"],
            "source_url": "https://example.test/mismatch",
        },
    ]
    dataset.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )

    report = evaluate_technical_attributes(dataset)

    assert report.micro_accuracy == 0.0
    assert (
        report.per_attribute["fluoride_formulation"].false_positive_count
        == 1
    )
    assert (
        report.per_attribute["adhesive_strategy"].false_negative_count
        == 1
    )
    assert report.per_attribute["resin_technology"].mismatch_count == 1

    errors = technical_attribute_errors(dataset)
    assert len(errors) == 3
    assert {error["id"] for error in errors} == {"fp", "fn", "mismatch"}


def test_technical_attribute_dataset_requires_explicit_review_fields(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "technical.jsonl"
    dataset.write_text(
        json.dumps(
            {
                "id": "x",
                "description": "RESINA COMPOSTA A2",
                "expected_category": "composite_resin",
                "expected_attributes": {},
                "evaluated_attributes": ["resin_technology"],
                "source_url": "https://example.test/x",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    try:
        evaluate_technical_attributes(dataset)
    except ValueError as error:
        message = str(error)
    else:
        raise AssertionError("Rótulo técnico ausente deveria falhar")

    assert "resin_technology" in message


def test_frozen_technical_v6_is_perfect_after_tuning() -> None:
    dataset = Path("data/evaluation/technical-attributes-v6.jsonl")

    report = evaluate_technical_attributes(dataset)

    assert report.sample_count == 48
    assert report.category_accuracy == 1.0
    assert report.evaluated_attribute_count == 90
    assert report.correct_attribute_count == 90
    assert report.micro_accuracy == 1.0
    assert sum(
        item.false_positive_count for item in report.per_attribute.values()
    ) == 0
    assert sum(
        item.false_negative_count for item in report.per_attribute.values()
    ) == 0
    assert sum(
        item.mismatch_count for item in report.per_attribute.values()
    ) == 0


def test_frozen_technical_v7_preserves_independent_baseline() -> None:
    baseline_path = Path(
        "data/evaluation/technical-attributes-v7-baseline.json"
    )
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    assert baseline["sample_count"] == 48
    assert baseline["category_accuracy"] == 0.8958
    assert baseline["evaluated_attribute_count"] == 83
    assert baseline["correct_attribute_count"] == 76
    assert baseline["micro_accuracy"] == 0.9157
    assert baseline["false_positive_count"] == 1
    assert baseline["false_negative_count"] == 6
    assert baseline["mismatch_count"] == 0


def test_frozen_technical_v7_is_perfect_after_tuning() -> None:
    dataset = Path("data/evaluation/technical-attributes-v7.jsonl")

    report = evaluate_technical_attributes(dataset)

    assert report.sample_count == 48
    assert report.category_accuracy == 1.0
    assert report.evaluated_attribute_count == 83
    assert report.correct_attribute_count == 83
    assert report.micro_accuracy == 1.0
    assert sum(
        item.false_positive_count for item in report.per_attribute.values()
    ) == 0
    assert sum(
        item.false_negative_count for item in report.per_attribute.values()
    ) == 0
    assert sum(
        item.mismatch_count for item in report.per_attribute.values()
    ) == 0


def test_frozen_technical_v8_preserves_independent_baseline() -> None:
    baseline_path = Path(
        "data/evaluation/technical-attributes-v8-baseline.json"
    )
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    assert baseline["sample_count"] == 48
    assert baseline["category_correct"] == 43
    assert baseline["category_accuracy"] == 0.8958
    assert baseline["evaluated_attribute_count"] == 83
    assert baseline["correct_attribute_count"] == 75
    assert baseline["micro_accuracy"] == 0.9036
    assert baseline["false_positive_count"] == 5
    assert baseline["false_negative_count"] == 3
    assert baseline["mismatch_count"] == 0


def test_frozen_technical_v8_is_perfect_after_tuning() -> None:
    dataset = Path("data/evaluation/technical-attributes-v8.jsonl")

    report = evaluate_technical_attributes(dataset)

    assert report.sample_count == 48
    assert report.category_accuracy == 1.0
    assert report.evaluated_attribute_count == 83
    assert report.correct_attribute_count == 83
    assert report.micro_accuracy == 1.0
    assert sum(
        item.false_positive_count for item in report.per_attribute.values()
    ) == 0
    assert sum(
        item.false_negative_count for item in report.per_attribute.values()
    ) == 0
    assert sum(
        item.mismatch_count for item in report.per_attribute.values()
    ) == 0
