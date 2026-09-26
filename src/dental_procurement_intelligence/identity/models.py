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
class TechnicalAttributes:
    resin_technology: str | None = None
    curing_mode: str | None = None
    adhesive_strategy: str | None = None
    ionomer_use: str | None = None
    fluoride_formulation: str | None = None
    anesthetic_active_ingredient: str | None = None
    anesthetic_vasoconstrictor: str | None = None

    def identified_count(self) -> int:
        return sum(
            value is not None
            for value in (
                self.resin_technology,
                self.curing_mode,
                self.adhesive_strategy,
                self.ionomer_use,
                self.fluoride_formulation,
                self.anesthetic_active_ingredient,
                self.anesthetic_vasoconstrictor,
            )
        )


@dataclass(frozen=True, slots=True)
class CanonicalProduct:
    original_description: str
    normalized_description: str
    category: ProductCategory
    presentation: str | None
    shade: str | None
    concentration_percent: Decimal | None
    technical_attributes: TechnicalAttributes
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
