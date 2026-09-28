import json
from pathlib import Path


def test_quality_snapshot_includes_medications_v1_to_v4_rollup() -> None:
    snapshot = json.loads(
        Path("docs/dashboard-quality-snapshot.json").read_text(encoding="utf-8")
    )

    medications = snapshot["medications"]

    assert medications["sample_count"] == 192
    assert medications["evaluated_field_count"] == 768
    assert medications["correct_field_count"] == 683
    assert medications["weighted_micro_accuracy"] == 0.8893

    assert set(medications["holdouts"]) == {"v1", "v2", "v3", "v4"}
    assert medications["holdouts"]["v1"]["micro_accuracy"] == 0.875
    assert medications["holdouts"]["v2"]["micro_accuracy"] == 0.7969
    assert medications["holdouts"]["v3"]["micro_accuracy"] == 0.901
    assert medications["holdouts"]["v4"]["micro_accuracy"] == 0.9844
    assert medications["holdouts"]["v4"]["micro_accuracy"] == 0.9844

    assert medications["per_field"]["active_ingredient"] == 0.7344
    assert medications["per_field"]["strength"] == 0.9635
    assert medications["per_field"]["dosage_form"] == 0.9323
    assert medications["per_field"]["route"] == 0.9271
