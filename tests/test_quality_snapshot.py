import json
from pathlib import Path


def test_quality_snapshot_includes_medications_v1_to_v3_rollup() -> None:
    snapshot = json.loads(
        Path("docs/dashboard-quality-snapshot.json").read_text(encoding="utf-8")
    )

    medications = snapshot["medications"]

    assert medications["sample_count"] == 144
    assert medications["evaluated_field_count"] == 576
    assert medications["correct_field_count"] == 494
    assert medications["weighted_micro_accuracy"] == 0.8576

    assert set(medications["holdouts"]) == {"v1", "v2", "v3"}
    assert medications["holdouts"]["v1"]["micro_accuracy"] == 0.875
    assert medications["holdouts"]["v2"]["micro_accuracy"] == 0.7969
    assert medications["holdouts"]["v3"]["micro_accuracy"] == 0.901

    assert medications["per_field"]["active_ingredient"] == 0.6528
    assert medications["per_field"]["strength"] == 0.9514
    assert medications["per_field"]["dosage_form"] == 0.9167
    assert medications["per_field"]["route"] == 0.9097
