from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any

from dental_procurement_intelligence.identity.models import (
    CanonicalProduct,
    ProductCategory,
)
from dental_procurement_intelligence.identity.parser import parse_product


_SHADE_CRITICAL = {
    ProductCategory.COMPOSITE_RESIN,
    ProductCategory.FLOWABLE_RESIN,
    ProductCategory.GLASS_IONOMER,
}

_CONCENTRATION_CRITICAL = {
    ProductCategory.PHOSPHORIC_ACID,
    ProductCategory.FLUORIDE_GEL,
    ProductCategory.LOCAL_ANESTHETIC,
}

_TECHNICAL_ATTRIBUTE_RULES: dict[
    ProductCategory,
    tuple[tuple[str, str, bool], ...],
] = {
    ProductCategory.COMPOSITE_RESIN: (
        ("resin_technology", "resin technology", False),
        ("curing_mode", "curing mode", False),
    ),
    ProductCategory.FLOWABLE_RESIN: (
        ("resin_technology", "resin technology", False),
        ("curing_mode", "curing mode", False),
    ),
    ProductCategory.ADHESIVE: (
        ("adhesive_strategy", "adhesive strategy", False),
        ("curing_mode", "curing mode", False),
    ),
    ProductCategory.GLASS_IONOMER: (
        ("ionomer_use", "ionomer use", False),
        ("curing_mode", "curing mode", False),
    ),
    ProductCategory.FLUORIDE_GEL: (
        ("fluoride_formulation", "fluoride formulation", False),
    ),
    ProductCategory.LOCAL_ANESTHETIC: (
        (
            "anesthetic_active_ingredient",
            "anesthetic active ingredient",
            True,
        ),
        (
            "anesthetic_vasoconstrictor",
            "anesthetic vasoconstrictor",
            False,
        ),
    ),
}


class IdentityDecision(StrEnum):
    MATCH = "match"
    REVIEW = "review"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True, slots=True)
class IdentityResult:
    decision: IdentityDecision
    score: Decimal
    left: CanonicalProduct
    right: CanonicalProduct
    supporting_evidence: tuple[str, ...]
    conflicts: tuple[str, ...]
    missing_evidence: tuple[str, ...]


class ProductIdentityEngine:
    """Baseline determinístico e explicável para comparabilidade de itens."""

    def compare(
        self,
        left_description: str,
        right_description: str,
    ) -> IdentityResult:
        left = parse_product(left_description)
        right = parse_product(right_description)
        support: list[str] = []
        conflicts: list[str] = []
        missing: list[str] = []
        score = Decimal("0")
        critical_missing = False

        same_known_category = False
        if ProductCategory.UNKNOWN in (left.category, right.category):
            missing.append(
                "category could not be identified for at least one item"
            )
        elif left.category != right.category:
            conflicts.append(
                f"category differs: {left.category} vs {right.category}"
            )
        else:
            same_known_category = True
            support.append(f"same category: {left.category}")
            score += Decimal("0.45")

        if same_known_category and left.category in _SHADE_CRITICAL:
            critical_missing = left.shade is None or right.shade is None
            score += self._compare_optional(
                "shade",
                left.shade,
                right.shade,
                Decimal("0.15"),
                support,
                conflicts,
                missing,
            )
        elif same_known_category and left.category in _CONCENTRATION_CRITICAL:
            critical_missing = (
                left.concentration_percent is None
                or right.concentration_percent is None
            )
            score += self._compare_optional(
                "concentration_percent",
                left.concentration_percent,
                right.concentration_percent,
                Decimal("0.15"),
                support,
                conflicts,
                missing,
            )

        technical_missing = False
        if same_known_category:
            technical_missing = self._compare_technical_attributes(
                left,
                right,
                support,
                conflicts,
                missing,
            )

        score += self._compare_optional(
            "presentation",
            left.presentation,
            right.presentation,
            Decimal("0.15"),
            support,
            conflicts,
            missing,
        )

        physical_score, packaging_missing = self._compare_physical_configuration(
            left,
            right,
            support,
            conflicts,
            missing,
        )
        score += physical_score

        if conflicts:
            decision = IdentityDecision.INCOMPATIBLE
        elif critical_missing or technical_missing or packaging_missing:
            decision = IdentityDecision.REVIEW
        elif score >= Decimal("0.75"):
            decision = IdentityDecision.MATCH
        else:
            decision = IdentityDecision.REVIEW

        return IdentityResult(
            decision=decision,
            score=score,
            left=left,
            right=right,
            supporting_evidence=tuple(support),
            conflicts=tuple(conflicts),
            missing_evidence=tuple(missing),
        )

    @staticmethod
    def _compare_technical_attributes(
        left: CanonicalProduct,
        right: CanonicalProduct,
        support: list[str],
        conflicts: list[str],
        missing: list[str],
    ) -> bool:
        rules = _TECHNICAL_ATTRIBUTE_RULES.get(left.category, ())
        has_missing = False

        for field_name, label, required in rules:
            left_value = getattr(left.technical_attributes, field_name)
            right_value = getattr(right.technical_attributes, field_name)

            if left_value is None and right_value is None:
                if required:
                    missing.append(f"{label} missing for both items")
                    has_missing = True
                continue

            if left_value is None or right_value is None:
                missing.append(f"{label} missing for one item")
                has_missing = True
                continue

            if left_value != right_value:
                conflicts.append(
                    f"{label} differs: {left_value} vs {right_value}"
                )
                continue

            support.append(f"same {label}: {left_value}")

        return has_missing

    @staticmethod
    def _compare_physical_configuration(
        left: CanonicalProduct,
        right: CanonicalProduct,
        support: list[str],
        conflicts: list[str],
        missing: list[str],
    ) -> tuple[Decimal, bool]:
        if left.unit_quantity is None or right.unit_quantity is None:
            missing.append("unit quantity missing for at least one item")
            return Decimal("0"), False

        if left.unit_quantity.dimension != right.unit_quantity.dimension:
            conflicts.append(
                "quantity dimension differs: "
                f"{left.unit_quantity.dimension} vs "
                f"{right.unit_quantity.dimension}"
            )
            return Decimal("0"), False

        if left.package_count is None and right.package_count is None:
            if left.unit_quantity.value != right.unit_quantity.value:
                conflicts.append(
                    "normalized unit quantity differs: "
                    f"{left.unit_quantity.value} {left.unit_quantity.unit} vs "
                    f"{right.unit_quantity.value} {right.unit_quantity.unit}"
                )
                return Decimal("0"), False

            support.append(
                "same normalized unit quantity: "
                f"{left.unit_quantity.value} {left.unit_quantity.unit}"
            )
            return Decimal("0.25"), False

        if (left.package_count is None) != (right.package_count is None):
            missing.append("package count missing for one item")
            return Decimal("0"), True

        if left.package_count != right.package_count:
            conflicts.append(
                f"package count differs: "
                f"{left.package_count} vs {right.package_count}"
            )
            return Decimal("0"), False

        if left.unit_quantity.value != right.unit_quantity.value:
            conflicts.append(
                "normalized unit quantity differs: "
                f"{left.unit_quantity.value} {left.unit_quantity.unit} vs "
                f"{right.unit_quantity.value} {right.unit_quantity.unit}"
            )
            return Decimal("0"), False

        if left.total_quantity is None or right.total_quantity is None:
            missing.append(
                "total package quantity missing for at least one item"
            )
            return Decimal("0"), True

        if left.total_quantity.dimension != right.total_quantity.dimension:
            conflicts.append(
                "total quantity dimension differs: "
                f"{left.total_quantity.dimension} vs "
                f"{right.total_quantity.dimension}"
            )
            return Decimal("0"), False

        if left.total_quantity.value != right.total_quantity.value:
            conflicts.append(
                "total package quantity differs: "
                f"{left.total_quantity.value} {left.total_quantity.unit} vs "
                f"{right.total_quantity.value} {right.total_quantity.unit}"
            )
            return Decimal("0"), False

        support.append(f"same package count: {left.package_count}")
        support.append(
            "same total package quantity: "
            f"{left.total_quantity.value} {left.total_quantity.unit}"
        )
        return Decimal("0.25"), False

    @staticmethod
    def _compare_optional(
        label: str,
        left: Any | None,
        right: Any | None,
        weight: Decimal,
        support: list[str],
        conflicts: list[str],
        missing: list[str],
    ) -> Decimal:
        if left is None or right is None:
            missing.append(f"{label} missing for at least one item")
            return Decimal("0")
        if left != right:
            conflicts.append(f"{label} differs: {left} vs {right}")
            return Decimal("0")
        support.append(f"same {label}: {left}")
        return weight
