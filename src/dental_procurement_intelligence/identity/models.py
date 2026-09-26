from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class ProductCategory(StrEnum):
    COMPOSITE_RESIN = "composite_resin"
    FLOWABLE_RESIN = "flowable_resin"
    ADHESIVE = "dental_adhesive"
    GLASS_IONOMER = "glass_ionomer"
    UNKNOWN = "unknown"


class QuantityDimension(StrEnum):
    MASS = "mass"
    VOLUME = "volume"


@dataclass(frozen=True, slots=True)
class Quantity:
    value: Decimal
    unit: str
    dimension: QuantityDimension


@dataclass(frozen=True, slots=True)
class CanonicalProduct:
    original_description: str
    normalized_description: str
    category: ProductCategory
    presentation: str | None
    shade: str | None
    package_count: int | None
    unit_quantity: Quantity | None
    total_quantity: Quantity | None
    matched_terms: tuple[str, ...]
