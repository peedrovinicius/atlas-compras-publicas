-- Cobertura dos principais campos estruturados por categoria do parser.

SELECT
    product_category,
    COUNT(*) AS items,
    ROUND(100 * AVG(CAST(category_identified AS INTEGER)), 2) AS category_pct,
    ROUND(
        100 * AVG(CAST(presentation_identified AS INTEGER)),
        2
    ) AS presentation_pct,
    ROUND(
        100 * AVG(CAST(measurement_identified AS INTEGER)),
        2
    ) AS measurement_pct,
    ROUND(100 * AVG(CAST(fully_structured AS INTEGER)), 2) AS fully_structured_pct,
    ROUND(AVG(normalization_quality_score), 4) AS average_quality_score
FROM silver_items
GROUP BY product_category
ORDER BY items DESC, product_category;
