import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from dental_procurement_intelligence.identity import parse_product


@dataclass(frozen=True, slots=True)
class EvaluationExample:
    id: str
    description: str
    expected_category: str
    expected_shade: str | None
    expected_concentration_percent: Decimal | None
    source_url: str
    source_item_number: int | None
    pncp_control_number: str | None
    label_status: str


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    dataset_path: str
    sample_count: int
    category_accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    category_error_count: int
    shade_support: int
    shade_accuracy: float | None
    concentration_support: int
    concentration_accuracy: float | None
    per_category: dict[str, dict[str, float | int]]


def load_evaluation_dataset(path: str | Path) -> list[EvaluationExample]:
    dataset_path = Path(path)
    examples: list[EvaluationExample] = []

    for line_number, line in enumerate(
        dataset_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        payload = json.loads(line)
        required = {"id", "description", "expected_category", "source_url"}
        missing = required.difference(payload)
        if missing:
            raise ValueError(
                f"Linha {line_number} sem campos obrigatórios: {sorted(missing)}"
            )

        concentration = payload.get("expected_concentration_percent")
        examples.append(
            EvaluationExample(
                id=str(payload["id"]),
                description=str(payload["description"]),
                expected_category=str(payload["expected_category"]),
                expected_shade=payload.get("expected_shade"),
                expected_concentration_percent=(
                    Decimal(str(concentration))
                    if concentration is not None
                    else None
                ),
                source_url=str(payload["source_url"]),
                source_item_number=payload.get("source_item_number"),
                pncp_control_number=payload.get("pncp_control_number"),
                label_status=str(payload.get("label_status", "manual")),
            )
        )

    if not examples:
        raise ValueError("O dataset de avaliação está vazio")

    ids = [example.id for example in examples]
    if len(ids) != len(set(ids)):
        raise ValueError("O dataset de avaliação contém IDs duplicados")

    return examples


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _category_metrics(
    expected: list[str],
    predicted: list[str],
) -> dict[str, dict[str, float | int]]:
    labels = sorted(set(expected))
    metrics: dict[str, dict[str, float | int]] = {}

    for label in labels:
        tp = sum(
            1
            for gold, guess in zip(expected, predicted, strict=True)
            if gold == label and guess == label
        )
        fp = sum(
            1
            for gold, guess in zip(expected, predicted, strict=True)
            if gold != label and guess == label
        )
        fn = sum(
            1
            for gold, guess in zip(expected, predicted, strict=True)
            if gold == label and guess != label
        )
        support = sum(1 for gold in expected if gold == label)
        precision = _safe_divide(tp, tp + fp)
        recall = _safe_divide(tp, tp + fn)
        f1 = _safe_divide(2 * precision * recall, precision + recall)

        metrics[label] = {
            "support": support,
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }

    return metrics


def _attribute_accuracy(
    expected: list[Any | None],
    predicted: list[Any | None],
) -> tuple[int, float | None]:
    pairs = [
        (gold, guess)
        for gold, guess in zip(expected, predicted, strict=True)
        if gold is not None
    ]
    if not pairs:
        return 0, None
    correct = sum(1 for gold, guess in pairs if gold == guess)
    return len(pairs), round(correct / len(pairs), 4)


def evaluate_dataset(path: str | Path) -> EvaluationReport:
    examples = load_evaluation_dataset(path)
    products = [parse_product(example.description) for example in examples]

    expected_categories = [example.expected_category for example in examples]
    predicted_categories = [product.category.value for product in products]
    per_category = _category_metrics(expected_categories, predicted_categories)

    correct = sum(
        1
        for expected, predicted in zip(
            expected_categories,
            predicted_categories,
            strict=True,
        )
        if expected == predicted
    )

    macro_precision = sum(
        float(metric["precision"]) for metric in per_category.values()
    ) / len(per_category)
    macro_recall = sum(
        float(metric["recall"]) for metric in per_category.values()
    ) / len(per_category)
    macro_f1 = sum(
        float(metric["f1"]) for metric in per_category.values()
    ) / len(per_category)

    expected_shades = [example.expected_shade for example in examples]
    predicted_shades = [product.shade for product in products]
    shade_support, shade_accuracy = _attribute_accuracy(
        expected_shades,
        predicted_shades,
    )

    expected_concentrations = [
        example.expected_concentration_percent for example in examples
    ]
    predicted_concentrations = [
        product.concentration_percent for product in products
    ]
    concentration_support, concentration_accuracy = _attribute_accuracy(
        expected_concentrations,
        predicted_concentrations,
    )

    return EvaluationReport(
        dataset_path=Path(path).as_posix(),
        sample_count=len(examples),
        category_accuracy=round(correct / len(examples), 4),
        macro_precision=round(macro_precision, 4),
        macro_recall=round(macro_recall, 4),
        macro_f1=round(macro_f1, 4),
        category_error_count=len(examples) - correct,
        shade_support=shade_support,
        shade_accuracy=shade_accuracy,
        concentration_support=concentration_support,
        concentration_accuracy=concentration_accuracy,
        per_category=per_category,
    )


def evaluation_errors(path: str | Path) -> list[dict[str, Any]]:
    examples = load_evaluation_dataset(path)
    errors: list[dict[str, Any]] = []

    for example in examples:
        product = parse_product(example.description)
        if product.category.value == example.expected_category:
            continue

        errors.append(
            {
                "id": example.id,
                "description": example.description,
                "expected_category": example.expected_category,
                "predicted_category": product.category.value,
                "source_item_number": example.source_item_number,
                "pncp_control_number": example.pncp_control_number,
                "source_url": example.source_url,
            }
        )

    return errors
