from decimal import Decimal

from dental_procurement_intelligence.identity import parse_product
from dental_procurement_intelligence.identity.models import ProductCategory


def test_documented_parser_example_matches_current_parser() -> None:
    product = parse_product("PRIME ADESIVO FRASCO 4ML")

    assert product.original_description == "PRIME ADESIVO FRASCO 4ML"
    assert product.normalized_description == "PRIME ADESIVO FRASCO 4ML"
    assert product.category == ProductCategory.ADHESIVE
    assert product.presentation == "bottle"
    assert product.shade is None
    assert product.concentration_percent is None
    assert product.package_count is None
    assert product.measurement_resolution == "single"
    assert product.unit_quantity is not None
    assert product.unit_quantity.value == Decimal("4")
    assert product.unit_quantity.unit == "ml"
    assert product.total_quantity is None
    assert product.matched_terms == ("ADESIVO",)
    assert product.technical_attributes.identified_count() == 0
