from decimal import Decimal

import pytest

from dental_procurement_intelligence.analytics.numeric import analytic_decimal


def test_analytic_decimal_rounds_half_even_at_twelve_places() -> None:
    assert analytic_decimal(Decimal("1.0000000000005")) == Decimal(
        "1.000000000000"
    )
    assert analytic_decimal(Decimal("1.0000000000015")) == Decimal(
        "1.000000000002"
    )


def test_analytic_decimal_rejects_non_finite_values() -> None:
    with pytest.raises(ValueError, match="finito"):
        analytic_decimal(Decimal("NaN"))


def test_analytic_decimal_rejects_integer_overflow() -> None:
    with pytest.raises(ValueError, match="precisão"):
        analytic_decimal(Decimal("1E+26"))
