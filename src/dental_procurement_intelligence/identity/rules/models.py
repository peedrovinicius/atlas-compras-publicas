from dataclasses import dataclass

from dental_procurement_intelligence.identity.models import ProductCategory


@dataclass(frozen=True, slots=True)
class CategoryRuleSpec:
    rule_id: str
    category: ProductCategory
    terms: tuple[str, ...]
    priority: int
    introduced_by: str


def compile_category_rules(
    specs: tuple[CategoryRuleSpec, ...],
) -> tuple[tuple[ProductCategory, tuple[str, ...]], ...]:
    ordered = sorted(specs, key=lambda spec: spec.priority)
    return tuple((spec.category, spec.terms) for spec in ordered)
