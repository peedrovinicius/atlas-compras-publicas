import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dental_procurement_intelligence.identity import parse_product

TECHNICAL_ATTRIBUTE_FIELDS = (
    "resin_technology",
    "curing_mode",
    "adhesive_strategy",
    "ionomer_use",
    "fluoride_formulation",
    "anesthetic_active_ingredient",
    "anesthetic_vasoconstrictor",
)


@dataclass(frozen=True, slots=True)
class TechnicalAttributeExample:
    id: str
    description: str
    expected_category: str
    expected_attributes: dict[str, str | None]
    evaluated_attributes: tuple[str, ...]
    source_url: str
    source_item_number: int | None
    pncp_control_number: str | None
    label_status: str


@dataclass(frozen=True, slots=True)
class TechnicalAttributeFieldReport:
    evaluated_count: int
    correct_count: int
    accuracy: float | None
    positive_support: int
    positive_correct: int
    positive_accuracy: float | None
    false_positive_count: int
    false_negative_count: int
    mismatch_count: int


@dataclass(frozen=True, slots=True)
class TechnicalAttributeReport:
    dataset_path: str
    sample_count: int
    category_accuracy: float
    evaluated_attribute_count: int
    correct_attribute_count: int
    micro_accuracy: float
    per_attribute: dict[str, TechnicalAttributeFieldReport]


def load_technical_attribute_dataset(
    path: str | Path,
) -> list[TechnicalAttributeExample]:
    dataset_path = Path(path)
    examples: list[TechnicalAttributeExample] = []

    for line_number, line in enumerate(
        dataset_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        payload = json.loads(line)
        required = {
            "id",
            "description",
            "expected_category",
            "expected_attributes",
            "evaluated_attributes",
            "source_url",
        }
        missing = required.difference(payload)
        if missing:
            raise ValueError(
                f"Linha {line_number} sem campos obrigatórios: {sorted(missing)}"
            )

        expected = payload["expected_attributes"]
        evaluated = tuple(payload["evaluated_attributes"])
        if not isinstance(expected, dict):
            raise ValueError(
                f"Linha {line_number}: expected_attributes deve ser objeto"
            )
        if not evaluated:
            raise ValueError(
                f"Linha {line_number}: evaluated_attributes não pode ser vazio"
            )

        invalid_fields = sorted(
            set(expected).union(evaluated).difference(TECHNICAL_ATTRIBUTE_FIELDS)
        )
        if invalid_fields:
            raise ValueError(
                f"Linha {line_number} possui atributos inválidos: {invalid_fields}"
            )

        missing_labels = sorted(set(evaluated).difference(expected))
        if missing_labels:
            raise ValueError(
                f"Linha {line_number} sem rótulos para: {missing_labels}"
            )

        examples.append(
            TechnicalAttributeExample(
                id=str(payload["id"]),
                description=str(payload["description"]),
                expected_category=str(payload["expected_category"]),
                expected_attributes={
                    str(key): (
                        str(value) if value is not None else None
                    )
                    for key, value in expected.items()
                },
                evaluated_attributes=evaluated,
                source_url=str(payload["source_url"]),
                source_item_number=payload.get("source_item_number"),
                pncp_control_number=payload.get("pncp_control_number"),
                label_status=str(
                    payload.get("label_status", "manual_technical")
                ),
            )
        )

    if not examples:
        raise ValueError("O dataset de atributos técnicos está vazio")

    ids = [example.id for example in examples]
    if len(ids) != len(set(ids)):
        raise ValueError(
            "O dataset de atributos técnicos contém IDs duplicados"
        )

    return examples


def _field_report(
    expected: list[str | None],
    predicted: list[str | None],
) -> TechnicalAttributeFieldReport:
    evaluated_count = len(expected)
    if evaluated_count == 0:
        return TechnicalAttributeFieldReport(
            evaluated_count=0,
            correct_count=0,
            accuracy=None,
            positive_support=0,
            positive_correct=0,
            positive_accuracy=None,
            false_positive_count=0,
            false_negative_count=0,
            mismatch_count=0,
        )

    correct = sum(
        1
        for gold, guess in zip(expected, predicted, strict=True)
        if gold == guess
    )
    positives = [
        (gold, guess)
        for gold, guess in zip(expected, predicted, strict=True)
        if gold is not None
    ]
    positive_correct = sum(
        1 for gold, guess in positives if gold == guess
    )
    false_positive = sum(
        1
        for gold, guess in zip(expected, predicted, strict=True)
        if gold is None and guess is not None
    )
    false_negative = sum(
        1
        for gold, guess in zip(expected, predicted, strict=True)
        if gold is not None and guess is None
    )
    mismatch = sum(
        1
        for gold, guess in zip(expected, predicted, strict=True)
        if gold is not None and guess is not None and gold != guess
    )

    return TechnicalAttributeFieldReport(
        evaluated_count=evaluated_count,
        correct_count=correct,
        accuracy=round(correct / evaluated_count, 4),
        positive_support=len(positives),
        positive_correct=positive_correct,
        positive_accuracy=(
            round(positive_correct / len(positives), 4)
            if positives
            else None
        ),
        false_positive_count=false_positive,
        false_negative_count=false_negative,
        mismatch_count=mismatch,
    )


def evaluate_technical_attributes(
    path: str | Path,
) -> TechnicalAttributeReport:
    examples = load_technical_attribute_dataset(path)
    products = [parse_product(example.description) for example in examples]

    category_correct = sum(
        1
        for example, product in zip(examples, products, strict=True)
        if example.expected_category == product.category.value
    )

    per_attribute: dict[str, TechnicalAttributeFieldReport] = {}
    total_evaluated = 0
    total_correct = 0

    for field in TECHNICAL_ATTRIBUTE_FIELDS:
        expected: list[str | None] = []
        predicted: list[str | None] = []

        for example, product in zip(examples, products, strict=True):
            if field not in example.evaluated_attributes:
                continue
            expected.append(example.expected_attributes[field])
            predicted.append(getattr(product.technical_attributes, field))

        report = _field_report(expected, predicted)
        per_attribute[field] = report
        total_evaluated += report.evaluated_count
        total_correct += report.correct_count

    return TechnicalAttributeReport(
        dataset_path=Path(path).as_posix(),
        sample_count=len(examples),
        category_accuracy=round(category_correct / len(examples), 4),
        evaluated_attribute_count=total_evaluated,
        correct_attribute_count=total_correct,
        micro_accuracy=round(total_correct / total_evaluated, 4),
        per_attribute=per_attribute,
    )


def technical_attribute_errors(
    path: str | Path,
) -> list[dict[str, Any]]:
    examples = load_technical_attribute_dataset(path)
    errors: list[dict[str, Any]] = []

    for example in examples:
        product = parse_product(example.description)
        for field in example.evaluated_attributes:
            expected = example.expected_attributes[field]
            predicted = getattr(product.technical_attributes, field)
            if expected == predicted:
                continue

            errors.append(
                {
                    "id": example.id,
                    "description": example.description,
                    "attribute": field,
                    "expected": expected,
                    "predicted": predicted,
                    "expected_category": example.expected_category,
                    "predicted_category": product.category.value,
                    "source_item_number": example.source_item_number,
                    "pncp_control_number": example.pncp_control_number,
                    "source_url": example.source_url,
                }
            )

    return errors
