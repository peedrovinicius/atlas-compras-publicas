from decimal import Decimal

from dental_procurement_intelligence.identity import (
    IdentityDecision,
    ProductCategory,
    ProductIdentityEngine,
    parse_product,
)


def test_parser_structures_abbreviated_composite_resin() -> None:
    product = parse_product("RES FOTOP A2 C/2 SERINGAS 4G")

    assert product.category == ProductCategory.COMPOSITE_RESIN
    assert product.shade == "A2"
    assert product.presentation == "syringe"
    assert product.package_count == 2
    assert product.unit_quantity is not None
    assert product.unit_quantity.value == Decimal("4")
    assert product.unit_quantity.unit == "g"
    assert product.total_quantity is not None
    assert product.total_quantity.value == Decimal("8")


def test_engine_matches_equivalent_descriptions_with_explanation() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA FOTOPOLIMERIZAVEL COR A2 SERINGA 4 G",
        "RES FOTOP A2 SER 4G",
    )

    assert result.decision == IdentityDecision.MATCH
    assert result.score == Decimal("1.00")
    assert not result.conflicts
    assert "same shade: A2" in result.supporting_evidence


def test_engine_rejects_flowable_vs_composite_even_with_same_shade_and_mass() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA A2 SERINGA 2G",
        "RESINA FLOW A2 SERINGA 2G",
    )

    assert result.decision == IdentityDecision.INCOMPATIBLE
    assert any("category differs" in conflict for conflict in result.conflicts)


def test_engine_rejects_different_normalized_mass() -> None:
    result = ProductIdentityEngine().compare(
        "RESINA COMPOSTA A2 SERINGA 4G",
        "RESINA COMPOSTA A2 SERINGA 3.5G",
    )

    assert result.decision == IdentityDecision.INCOMPATIBLE
    assert any("unit quantity differs" in conflict for conflict in result.conflicts)
