import json
from pathlib import Path

from dental_procurement_intelligence.evaluation import evaluate_medications


def test_frozen_medications_v1_is_perfect_after_tuning() -> None:
    report = evaluate_medications(
        Path("data/evaluation/medications-v1.jsonl")
    )

    assert report.sample_count == 48
    assert report.evaluated_field_count == 192
    assert report.correct_field_count == 192
    assert report.micro_accuracy == 1.0
    assert report.false_positive_count == 0
    assert report.false_negative_count == 0
    assert report.mismatch_count == 0


def test_frozen_medications_v2_preserves_independent_baseline() -> None:
    baseline = json.loads(
        Path("data/evaluation/medications-v2-baseline.json").read_text(
            encoding="utf-8"
        )
    )

    assert baseline["sample_count"] == 48
    assert baseline["evaluated_field_count"] == 192
    assert baseline["correct_field_count"] == 153
    assert baseline["micro_accuracy"] == 0.7969
    assert baseline["false_positive_count"] == 0
    assert baseline["false_negative_count"] == 0
    assert baseline["mismatch_count"] == 39


def test_frozen_medications_v2_is_perfect_after_tuning() -> None:
    report = evaluate_medications(
        Path("data/evaluation/medications-v2.jsonl")
    )

    assert report.sample_count == 48
    assert report.evaluated_field_count == 192
    assert report.correct_field_count == 192
    assert report.micro_accuracy == 1.0
    assert report.false_positive_count == 0
    assert report.false_negative_count == 0
    assert report.mismatch_count == 0


def test_frozen_medications_v3_preserves_independent_baseline() -> None:
    baseline = json.loads(
        Path("data/evaluation/medications-v3-baseline.json").read_text(
            encoding="utf-8"
        )
    )

    assert baseline["sample_count"] == 48
    assert baseline["evaluated_field_count"] == 192
    assert baseline["correct_field_count"] == 173
    assert baseline["micro_accuracy"] == 0.901
    assert baseline["false_positive_count"] == 0
    assert baseline["false_negative_count"] == 5
    assert baseline["mismatch_count"] == 14


def test_frozen_medications_v3_is_perfect_after_tuning() -> None:
    report = evaluate_medications(
        Path("data/evaluation/medications-v3.jsonl")
    )

    assert report.sample_count == 48
    assert report.evaluated_field_count == 192
    assert report.correct_field_count == 192
    assert report.micro_accuracy == 1.0
    assert report.false_positive_count == 0
    assert report.false_negative_count == 0
    assert report.mismatch_count == 0
