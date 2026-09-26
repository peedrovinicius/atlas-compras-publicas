from dataclasses import dataclass
from enum import StrEnum

from dental_procurement_intelligence.identity.models import CanonicalProduct, Quantity
from dental_procurement_intelligence.normalization import normalize_description


class PriceNormalizationStatus(StrEnum):
    DEFENSIBLE = "defensible"
    REVIEW = "review"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class PriceNormalizationAssessment:
    status: PriceNormalizationStatus
    reason: str
    basis: Quantity | None


_PACKAGE_PROCUREMENT_UNITS = {
    "CAIXA",
    "CX",
    "PACOTE",
    "PCT",
    "KIT",
    "CONJUNTO",
    "ESTOJO",
    "EMBALAGEM",
    "CARTELA",
    "BLISTER",
    "FARDO",
}

_SINGLE_ITEM_PROCUREMENT_UNITS = {
    "UN",
    "UND",
    "UNID",
    "UNIDADE",
    "SERINGA",
    "FRASCO",
    "CAPSULA",
    "TUBO",
    "BISNAGA",
    "POTE",
    "SACHE",
    "ENVELOPE",
    "TUBETE",
    "CARPULE",
    "AMPOLA",
}


def _canonical_procurement_unit(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    return normalize_description(value)


def assess_price_normalization(
    product: CanonicalProduct,
    procurement_unit: str | None,
) -> PriceNormalizationAssessment:
    """Define se o preço pode ser dividido por uma quantidade física defensável."""

    if product.unit_quantity is None:
        return PriceNormalizationAssessment(
            status=PriceNormalizationStatus.UNAVAILABLE,
            reason="physical_measurement_missing",
            basis=None,
        )

    if product.package_count is not None:
        if product.total_quantity is None or product.package_count < 1:
            return PriceNormalizationAssessment(
                status=PriceNormalizationStatus.REVIEW,
                reason="invalid_explicit_package",
                basis=None,
            )
        return PriceNormalizationAssessment(
            status=PriceNormalizationStatus.DEFENSIBLE,
            reason="explicit_package_count",
            basis=product.total_quantity,
        )

    canonical_unit = _canonical_procurement_unit(procurement_unit)

    if canonical_unit is None:
        return PriceNormalizationAssessment(
            status=PriceNormalizationStatus.REVIEW,
            reason="procurement_unit_missing",
            basis=None,
        )

    if canonical_unit in _PACKAGE_PROCUREMENT_UNITS:
        return PriceNormalizationAssessment(
            status=PriceNormalizationStatus.REVIEW,
            reason="package_count_missing_for_procurement_package",
            basis=None,
        )

    if canonical_unit in _SINGLE_ITEM_PROCUREMENT_UNITS:
        return PriceNormalizationAssessment(
            status=PriceNormalizationStatus.DEFENSIBLE,
            reason="single_item_procurement_unit",
            basis=product.unit_quantity,
        )

    return PriceNormalizationAssessment(
        status=PriceNormalizationStatus.REVIEW,
        reason="procurement_unit_not_mapped",
        basis=None,
    )
