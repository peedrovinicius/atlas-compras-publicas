from decimal import ROUND_HALF_EVEN, Decimal, localcontext

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
    if not value.is_finite():
        raise ValueError("Valor decimal analítico deve ser finito")

    with localcontext() as context:
        context.prec = ANALYTIC_DECIMAL_PRECISION + ANALYTIC_DECIMAL_SCALE
        quantized = value.quantize(
            ANALYTIC_DECIMAL_QUANTUM,
            rounding=ROUND_HALF_EVEN,
        )

    integer_digits = 1 if quantized == 0 else max(quantized.adjusted() + 1, 1)
    max_integer_digits = ANALYTIC_DECIMAL_PRECISION - ANALYTIC_DECIMAL_SCALE
    if integer_digits > max_integer_digits:
        raise ValueError(
            "Valor decimal excede a precisão analítica configurada"
        )
    return quantized
