import json
from pathlib import Path

from dental_procurement_intelligence.evaluation import (
    evaluate_dataset,
    evaluation_errors,
)


def _write_dataset(path: Path) -> None:
    rows = [
        {
            "id": "1",
            "description": "RESINA COMPOSTA A2 SERINGA 4G",
            "expected_category": "composite_resin",
            "expected_shade": "A2",
            "expected_concentration_percent": None,
            "source_url": "https://example.test/1",
        },
        {
            "id": "2",
            "description": "BROCA DIAMANTADA 1014",
            "expected_category": "unknown",
            "expected_shade": None,
            "expected_concentration_percent": None,
            "source_url": "https://example.test/2",
        },
        {
            "id": "3",
            "description": "ACIDO FOSFORICO 37% SERINGA 2,5ML",
            "expected_category": "phosphoric_acid",
            "expected_shade": None,
            "expected_concentration_percent": 37,
            "source_url": "https://example.test/3",
        },
    ]
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_evaluation_report_calculates_category_and_attribute_metrics(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "evaluation.jsonl"
    _write_dataset(dataset)

    report = evaluate_dataset(dataset)

    assert report.sample_count == 3
    assert report.category_accuracy == 1.0
    assert report.macro_precision == 1.0
    assert report.macro_recall == 1.0
    assert report.macro_f1 == 1.0
    assert report.shade_support == 1
    assert report.shade_accuracy == 1.0
    assert report.concentration_support == 1
    assert report.concentration_accuracy == 1.0


def test_evaluation_includes_predicted_only_labels_in_macro_metrics(
    tmp_path: Path,
) -> None:
    dataset = tmp_path / "evaluation.jsonl"
    dataset.write_text(
        json.dumps(
            {
                "id": "x",
                "description": "EUGENOL",
                "expected_category": "unknown",
                "expected_shade": None,
                "expected_concentration_percent": None,
                "source_url": "https://example.test/x",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    report = evaluate_dataset(dataset)

    assert set(report.per_category) == {"eugenol", "unknown"}
    assert report.per_category["eugenol"]["support"] == 0
    assert report.per_category["eugenol"]["false_positive"] == 1
    assert report.macro_precision == 0.0
    assert report.macro_recall == 0.0
    assert report.macro_f1 == 0.0


def test_evaluation_errors_returns_only_category_mismatches(tmp_path: Path) -> None:
    dataset = tmp_path / "evaluation.jsonl"
    dataset.write_text(
        json.dumps(
            {
                "id": "x",
                "description": "RESINA COMPOSTA A2",
                "expected_category": "unknown",
                "expected_shade": None,
                "expected_concentration_percent": None,
                "source_url": "https://example.test/x",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    errors = evaluation_errors(dataset)

    assert len(errors) == 1
    assert errors[0]["expected_category"] == "unknown"
    assert errors[0]["predicted_category"] == "composite_resin"
