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
