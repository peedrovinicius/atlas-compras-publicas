-- Diferença entre a mediana regional e a mediana nacional por categoria.

WITH regional AS (
    SELECT
        product_category,
        macroregion,
        MEDIAN(awarded_price_per_base_unit) AS regional_median,
        COUNT(*) AS regional_observations
    FROM silver_awards
    WHERE price_normalization_status = 'defensible'
      AND awarded_price_per_base_unit IS NOT NULL
      AND macroregion IS NOT NULL
    GROUP BY 1, 2
),
national AS (
    SELECT
        product_category,
        MEDIAN(awarded_price_per_base_unit) AS national_median,
        COUNT(*) AS national_observations
    FROM silver_awards
    WHERE price_normalization_status = 'defensible'
      AND awarded_price_per_base_unit IS NOT NULL
    GROUP BY 1
)
SELECT
    regional.product_category,
    regional.macroregion,
    regional.regional_observations,
    national.national_observations,
    regional.regional_median,
    national.national_median,
    ROUND(
        100 * (
            CAST(regional.regional_median AS DOUBLE)
            / NULLIF(CAST(national.national_median AS DOUBLE), 0)
            - 1
        ),
        2
    ) AS delta_percent
FROM regional
JOIN national USING (product_category)
ORDER BY ABS(delta_percent) DESC, product_category, macroregion;
