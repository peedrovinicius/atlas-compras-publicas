-- Rastreabilidade completa de um resultado analisado.
-- Parâmetro 1: award_key.

SELECT
    award_key,
    procurement_key,
    item_number,
    original_description,
    product_category,
    awarded_price_per_base_unit,
    comparison_scope,
    comparison_geography,
    comparison_period,
    scope_group_key,
    group_size,
    median_price,
    q1_price,
    q3_price,
    mad_price,
    modified_z_score,
    detection_method,
    is_price_signal,
    contract_source_sha256,
    item_source_sha256,
    result_source_sha256
FROM gold_price_signals
WHERE award_key = ?;
