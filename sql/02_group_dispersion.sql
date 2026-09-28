-- Dispersão dos preços dentro dos grupos comparáveis selecionados.

SELECT
    product_key,
    comparison_scope,
    COUNT(*) AS observations,
    MIN(awarded_price_per_base_unit) AS min_price,
    QUANTILE_CONT(awarded_price_per_base_unit, 0.25) AS q1_price,
    MEDIAN(awarded_price_per_base_unit) AS median_price,
    QUANTILE_CONT(awarded_price_per_base_unit, 0.75) AS q3_price,
    MAX(awarded_price_per_base_unit) AS max_price
FROM gold_price_signals
GROUP BY product_key, comparison_scope
HAVING COUNT(*) >= 5
ORDER BY observations DESC, product_key, comparison_scope;
