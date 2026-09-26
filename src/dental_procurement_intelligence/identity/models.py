from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class ProductCategory(StrEnum):
    COMPOSITE_RESIN = "composite_resin"
    FLOWABLE_RESIN = "flowable_resin"
    ADHESIVE = "dental_adhesive"
    GLASS_IONOMER = "glass_ionomer"
    PHOSPHORIC_ACID = "phosphoric_acid"
    ALGINATE = "alginate"
    FLUORIDE_GEL = "fluoride_gel"
    PROPHYLAXIS_PASTE = "prophylaxis_paste"
    CALCIUM_HYDROXIDE = "calcium_hydroxide"
    ZINC_OXIDE = "zinc_oxide"
    EUGENOL = "eugenol"
    RADIOGRAPHIC_FIXER = "radiographic_fixer"
    RADIOGRAPHIC_DEVELOPER = "radiographic_developer"
    LOCAL_ANESTHETIC = "local_anesthetic"
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
    concentration_percent: Decimal | None
    package_count: int | None
    measurement_candidates: tuple[Quantity, ...]
    measurement_resolution: str
    unit_quantity: Quantity | None
    total_quantity: Quantity | None
    matched_terms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NormalizationQuality:
    score: Decimal
    level: str
    fully_structured: bool
    category_identified: bool
    presentation_identified: bool
    measurement_identified: bool
    critical_attribute_name: str | None
    critical_attribute_identified: bool | None
    missing_fields: tuple[str, ...]
