from decimal import Decimal, ROUND_HALF_EVEN, localcontext

import polars as pl


ANALYTIC_DECIMAL_PRECISION = 38
ANALYTIC_DECIMAL_SCALE = 12
ANALYTIC_DECIMAL_QUANTUM = Decimal("1").scaleb(-ANALYTIC_DECIMAL_SCALE)
ANALYTIC_DECIMAL_DTYPE = pl.Decimal(
    precision=ANALYTIC_DECIMAL_PRECISION,
    scale=ANALYTIC_DECIMAL_SCALE,
)


def analytic_decimal(value: Decimal | None) -> Decimal | None:
    """Normaliza valores decimais para a escala analítica sem usar float."""

    if value is None:
        return None

    with localcontext() as context:
        context.prec = ANALYTIC_DECIMAL_PRECISION + ANALYTIC_DECIMAL_SCALE
        return value.quantize(
            ANALYTIC_DECIMAL_QUANTUM,
            rounding=ROUND_HALF_EVEN,
        )
