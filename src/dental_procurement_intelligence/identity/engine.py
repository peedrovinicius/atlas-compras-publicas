from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any

from dental_procurement_intelligence.identity.models import CanonicalProduct, ProductCategory
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

    def compare(self, left_description: str, right_description: str) -> IdentityResult:
        left = parse_product(left_description)
        right = parse_product(right_description)
        support: list[str] = []
        conflicts: list[str] = []
        missing: list[str] = []
        score = Decimal("0")
        critical_missing = False

        same_known_category = False
        if ProductCategory.UNKNOWN in (left.category, right.category):
            missing.append("category could not be identified for at least one item")
        elif left.category != right.category:
            conflicts.append(f"category differs: {left.category} vs {right.category}")
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

        score += self._compare_optional(
            "presentation",
            left.presentation,
            right.presentation,
            Decimal("0.15"),
            support,
            conflicts,
            missing,
        )

        if left.unit_quantity is None or right.unit_quantity is None:
            missing.append("unit quantity missing for at least one item")
        elif left.unit_quantity.dimension != right.unit_quantity.dimension:
            conflicts.append(
                "quantity dimension differs: "
                f"{left.unit_quantity.dimension} vs {right.unit_quantity.dimension}"
            )
        elif left.unit_quantity.value == right.unit_quantity.value:
            support.append(
                "same normalized unit quantity: "
                f"{left.unit_quantity.value} {left.unit_quantity.unit}"
            )
            score += Decimal("0.25")
        else:
            conflicts.append(
                "normalized unit quantity differs: "
                f"{left.unit_quantity.value} {left.unit_quantity.unit} vs "
                f"{right.unit_quantity.value} {right.unit_quantity.unit}"
            )

        if conflicts:
            decision = IdentityDecision.INCOMPATIBLE
        elif critical_missing:
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
