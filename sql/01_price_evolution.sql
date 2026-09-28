-- Evolução mensal do preço homologado normalizado.
-- Considera apenas observações cuja normalização física foi considerada defensável.

WITH monthly AS (
    SELECT
        product_category,
        macroregion,
        DATE_TRUNC('month', analysis_date) AS month,
        COUNT(*) AS observations,
        MEDIAN(awarded_price_per_base_unit) AS median_price
    FROM silver_awards
    WHERE price_normalization_status = 'defensible'
      AND awarded_price_per_base_unit IS NOT NULL
      AND analysis_date IS NOT NULL
    GROUP BY 1, 2, 3
)
SELECT
    product_category,
    macroregion,
    month,
    observations,
    median_price,
    LAG(median_price) OVER (
        PARTITION BY product_category, macroregion
        ORDER BY month
    ) AS previous_median,
    ROUND(
        100 * (
            CAST(median_price AS DOUBLE)
            / NULLIF(
                CAST(
                    LAG(median_price) OVER (
                        PARTITION BY product_category, macroregion
                        ORDER BY month
                    ) AS DOUBLE
                ),
                0
            )
            - 1
        ),
        2
    ) AS change_percent
FROM monthly
ORDER BY product_category, macroregion, month;
