import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dental_procurement_intelligence.identity.medications import parse_medication


@dataclass(frozen=True, slots=True)
class MedicationFieldMetrics:
    evaluated_count: int
    correct_count: int
    accuracy: float
    false_positive_count: int
    false_negative_count: int
    mismatch_count: int


@dataclass(frozen=True, slots=True)
class MedicationEvaluationReport:
    sample_count: int
    evaluated_field_count: int
    correct_field_count: int
    micro_accuracy: float
    false_positive_count: int
    false_negative_count: int
    mismatch_count: int
    per_field: dict[str, MedicationFieldMetrics]


_FIELDS = (
    "active_ingredient",
    "strength",
    "dosage_form",
    "route",
)


def _value(result: Any, field: str) -> str | None:
    value = getattr(result, field)
    if hasattr(value, "value"):
        return value.value
    return value


def evaluate_medications(
    dataset_path: str | Path,
) -> MedicationEvaluationReport:
    rows = [
        json.loads(line)
        for line in Path(dataset_path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    counters = {
        field: {
            "evaluated": 0,
            "correct": 0,
            "false_positive": 0,
            "false_negative": 0,
            "mismatch": 0,
        }
        for field in _FIELDS
    }

    for row in rows:
        result = parse_medication(row["description"])
        for field in row["evaluated_fields"]:
            expected = row["expected"][field]
            predicted = _value(result, field)
            bucket = counters[field]
            bucket["evaluated"] += 1

            if expected == predicted:
                bucket["correct"] += 1
            elif expected is None and predicted is not None:
                bucket["false_positive"] += 1
            elif expected is not None and predicted is None:
                bucket["false_negative"] += 1
            else:
                bucket["mismatch"] += 1

    per_field: dict[str, MedicationFieldMetrics] = {}
    for field, bucket in counters.items():
        evaluated = bucket["evaluated"]
        if evaluated == 0:
            continue
        per_field[field] = MedicationFieldMetrics(
            evaluated_count=evaluated,
            correct_count=bucket["correct"],
            accuracy=round(bucket["correct"] / evaluated, 4),
            false_positive_count=bucket["false_positive"],
            false_negative_count=bucket["false_negative"],
            mismatch_count=bucket["mismatch"],
        )

    evaluated_total = sum(item.evaluated_count for item in per_field.values())
    correct_total = sum(item.correct_count for item in per_field.values())

    return MedicationEvaluationReport(
        sample_count=len(rows),
        evaluated_field_count=evaluated_total,
        correct_field_count=correct_total,
        micro_accuracy=round(correct_total / evaluated_total, 4)
        if evaluated_total
        else 0.0,
        false_positive_count=sum(
            item.false_positive_count for item in per_field.values()
        ),
        false_negative_count=sum(
            item.false_negative_count for item in per_field.values()
        ),
        mismatch_count=sum(
            item.mismatch_count for item in per_field.values()
        ),
        per_field=per_field,
    )


def medication_errors(dataset_path: str | Path) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    rows = [
        json.loads(line)
        for line in Path(dataset_path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    for row in rows:
        result = parse_medication(row["description"])
        for field in row["evaluated_fields"]:
            expected = row["expected"][field]
            predicted = _value(result, field)
            if expected != predicted:
                errors.append(
                    {
                        "id": row["id"],
                        "field": field,
                        "expected": expected,
                        "predicted": predicted,
                    }
                )
    return errors
