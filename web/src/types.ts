export type Quantity = {
  value: string;
  unit: string;
  dimension: string;
};

export type TechnicalAttributes = {
  resin_technology: string | null;
  curing_mode: string | null;
  adhesive_strategy: string | null;
  ionomer_use: string | null;
  fluoride_formulation: string | null;
  anesthetic_active_ingredient: string | null;
  anesthetic_vasoconstrictor: string | null;
};

export type NormalizationResult = {
  atlas_version: string;
  classification_method: string;
  original_description: string;
  normalized_description: string;
  category: string;
  presentation: string | null;
  shade: string | null;
  concentration_percent: string | null;
  package_count: number | null;
  measurement_resolution: string;
  unit_quantity: Quantity | null;
  total_quantity: Quantity | null;
  technical_attributes: TechnicalAttributes;
  matched_terms: string[];
};

export type ParserCategory = {
  id: string;
  label: string;
  fallback: boolean;
};

export type BatchResponse = {
  count: number;
  items: NormalizationResult[];
};
