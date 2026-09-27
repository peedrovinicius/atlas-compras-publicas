from dental_procurement_intelligence.identity.models import ProductCategory
from dental_procurement_intelligence.identity.rules import (
    DENTAL_CATEGORY_SPECS,
    compile_category_rules,
)


def test_dental_rule_registry_has_unique_ids_and_priorities() -> None:
    rule_ids = [spec.rule_id for spec in DENTAL_CATEGORY_SPECS]
    priorities = [spec.priority for spec in DENTAL_CATEGORY_SPECS]

    assert len(rule_ids) == len(set(rule_ids))
    assert len(priorities) == len(set(priorities))
    assert priorities == sorted(priorities)


def test_dental_rule_registry_preserves_category_precedence() -> None:
    compiled = compile_category_rules(DENTAL_CATEGORY_SPECS)

    assert [category for category, _ in compiled] == [
        ProductCategory.FLOWABLE_RESIN,
        ProductCategory.COMPOSITE_RESIN,
        ProductCategory.ADHESIVE,
        ProductCategory.GLASS_IONOMER,
        ProductCategory.PHOSPHORIC_ACID,
        ProductCategory.ALGINATE,
        ProductCategory.FLUORIDE_GEL,
        ProductCategory.PROPHYLAXIS_PASTE,
        ProductCategory.CALCIUM_HYDROXIDE,
        ProductCategory.ZINC_OXIDE,
        ProductCategory.EUGENOL,
        ProductCategory.RADIOGRAPHIC_FIXER,
        ProductCategory.RADIOGRAPHIC_DEVELOPER,
        ProductCategory.LOCAL_ANESTHETIC,
    ]


def test_dental_rule_registry_contains_no_empty_term_sets() -> None:
    assert all(spec.terms for spec in DENTAL_CATEGORY_SPECS)
    assert all(all(term.strip() for term in spec.terms) for spec in DENTAL_CATEGORY_SPECS)
