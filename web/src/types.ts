export type ProductSort = "coverage" | "procurements" | "latest" | "name";

export type AnalyticsFilters = {
  state_code: string;
  macroregion: string;
  supplier: string;
  buyer: string;
  start_date: string;
  end_date: string;
};

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

export type ProductSearchItem = {
  product_id: string;
  product_category: string;
  presentation: string | null;
  shade: string | null;
  normalized_quantity_unit: string | null;
  award_count: number;
  procurement_count: number;
  supplier_count: number;
  state_count: number;
  priced_observation_count: number;
  latest_date: string | null;
  sample_description: string;
  display_name: string;
};

export type ProductSearchResponse = {
  query: string;
  sort: ProductSort;
  filters: {
    state_code: string | null;
    macroregion: string | null;
    supplier: string | null;
    buyer: string | null;
    start_date: string | null;
    end_date: string | null;
  };
  items: ProductSearchItem[];
  total: number;
  limit: number;
  offset: number;
};

export type PriceStats = {
  median_price: number | null;
  average_price: number | null;
  min_price: number | null;
  max_price: number | null;
  percentile_25: number | null;
  percentile_75: number | null;
  standard_deviation: number | null;
  total_physical_quantity: number | null;
};

export type ProductSummary = {
  product_id: string;
  product_category: string;
  presentation: string | null;
  shade: string | null;
  normalized_quantity_unit: string | null;
  award_count: number;
  procurement_count: number;
  item_count: number;
  supplier_count: number;
  state_count: number;
  period_start: string | null;
  period_end: string | null;
  latest_update: string | null;
  sample_description: string;
  price_sample_count: number;
  display_name: string;
  minimum_sample_size: number;
  sample_sufficient: boolean;
  price_unit: string | null;
  price_stats: PriceStats;
};

export type DistributionBin = {
  index: number;
  lower: number;
  upper: number;
  count: number;
};

export type ProductDistribution = {
  product_id: string;
  observations: number;
  bin_count: number;
  min_price: number | null;
  max_price: number | null;
  bins: DistributionBin[];
};

export type HistoryPoint = {
  month: string;
  observations: number;
  procurement_count: number;
  state_count: number;
  median_price: number | null;
  average_price: number | null;
  percentile_25: number | null;
  percentile_75: number | null;
  min_price: number | null;
  max_price: number | null;
};

export type ProductHistory = {
  product_id: string;
  points: HistoryPoint[];
  total_observations: number;
};

export type RegionSummary = {
  observations: number;
  procurement_count: number;
  state_count?: number;
  median_price: number | null;
};

export type StateRegionSummary = RegionSummary & {
  state_code: string;
  macroregion: string | null;
  difference_from_national_percent: number | null;
};

export type MacroregionSummary = RegionSummary & {
  macroregion: string;
};

export type ProductRegions = {
  product_id: string;
  national: RegionSummary;
  regions: MacroregionSummary[];
  states: StateRegionSummary[];
};

export type SupplierItem = {
  supplier_document: string;
  supplier_name: string | null;
  award_count: number;
  procurement_count: number;
  median_price: number | null;
  priced_observation_count: number;
  sample_share_percent: number;
};

export type ProductSuppliers = {
  product_id: string;
  items: SupplierItem[];
  total: number;
  limit: number;
  offset: number;
};

export type BuyerItem = {
  organization_cnpj: string | null;
  organization_name: string | null;
  buyer_unit_code: string | null;
  buyer_unit_name: string | null;
  state_code: string | null;
  macroregion: string | null;
  award_count: number;
  procurement_count: number;
  awarded_total_value: number | null;
  median_price: number | null;
  priced_observation_count: number;
};

export type ProductBuyers = {
  product_id: string;
  items: BuyerItem[];
  total: number;
  limit: number;
  offset: number;
};

export type SignalItem = {
  award_key: string;
  procurement_key: string;
  item_number: number | null;
  original_description: string;
  supplier_name: string | null;
  supplier_document: string | null;
  organization_name: string | null;
  state_code: string | null;
  analysis_date: string | null;
  awarded_price_per_base_unit: number | null;
  comparison_scope: string | null;
  comparison_geography: string | null;
  comparison_period: string | null;
  scope_group_key: string | null;
  group_size: number | null;
  median_price: number | null;
  q1_price: number | null;
  q3_price: number | null;
  mad_price: number | null;
  modified_z_score: number | null;
  detection_method: string | null;
  is_price_signal: boolean;
  contract_source_sha256: string | null;
  item_source_sha256: string | null;
  result_source_sha256: string | null;
  pncp_url: string | null;
};

export type ProductSignals = {
  product_id: string;
  items: SignalItem[];
  total: number;
  limit: number;
  offset: number;
  disclaimer: string;
};

export type TraceableRecord = {
  award_key: string;
  procurement_key: string;
  item_number: number | null;
  result_sequence: number | null;
  original_description: string;
  supplier_name: string | null;
  supplier_document: string | null;
  organization_name: string | null;
  buyer_unit_name: string | null;
  municipality_name: string | null;
  state_code: string | null;
  macroregion: string | null;
  modality: string | null;
  analysis_date: string | null;
  awarded_unit_value: number | null;
  awarded_quantity: number | null;
  awarded_total_value: number | null;
  awarded_price_per_base_unit: number | null;
  price_normalization_status: string | null;
  price_normalization_reason: string | null;
  contract_source_sha256: string | null;
  item_source_sha256: string | null;
  result_source_sha256: string | null;
  pncp_url: string | null;
};

export type ProductRecords = {
  product_id: string;
  items: TraceableRecord[];
  total: number;
  limit: number;
  offset: number;
};

export type ProductAnalyticsBundle = {
  summary: ProductSummary;
  distribution: ProductDistribution;
  history: ProductHistory;
  regions: ProductRegions;
  suppliers: ProductSuppliers;
  buyers: ProductBuyers;
  signals: ProductSignals;
  records: ProductRecords;
};
