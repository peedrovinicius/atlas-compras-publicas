from dental_procurement_intelligence.api.catalog import (
    resolve_product_search_query,
)


def test_search_aliases_ignore_accents_and_case() -> None:
    category, residual, label = resolve_product_search_query(
        "ADESIVO ODONTOLÓGICO"
    )

    assert category == "dental_adhesive"
    assert residual == []
    assert label == "Adesivo odontológico"


def test_search_aliases_tolerate_small_typo() -> None:
    category, residual, label = resolve_product_search_query(
        "ionomero de vidor A2"
    )

    assert category == "glass_ionomer"
    assert residual == ["a2"]
    assert label == "Ionômero de vidro"


def test_generic_resin_query_remains_broad() -> None:
    category, residual, label = resolve_product_search_query("resina")

    assert category is None
    assert residual == ["resina"]
    assert label is None


def test_unrelated_term_is_not_guessed() -> None:
    category, residual, label = resolve_product_search_query("escova dental")

    assert category is None
    assert residual == ["escova", "dental"]
    assert label is None
