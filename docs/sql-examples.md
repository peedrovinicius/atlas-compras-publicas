# Exemplos de SQL no DuckDB

O Atlas usa DuckDB como camada analítica local. As consultas abaixo usam tabelas e views criadas pelo próprio pipeline e servem para inspecionar estrutura, qualidade, homologações e sinais sem substituir a metodologia documentada.

## Resumo por categoria

A view `category_price_summary` é criada a partir de `silver_items`.

```sql
SELECT
    product_category,
    item_count,
    priced_item_count,
    median_normalized_price,
    min_normalized_price,
    max_normalized_price
FROM category_price_summary
ORDER BY item_count DESC, product_category;
```

## Cobertura da normalização

```sql
SELECT
    product_category,
    COUNT(*) AS item_count,
    SUM(CASE WHEN fully_structured THEN 1 ELSE 0 END) AS fully_structured_count,
    ROUND(AVG(normalization_quality_score), 3) AS average_quality_score
FROM silver_items
GROUP BY product_category
ORDER BY item_count DESC, product_category;
```

## Itens que exigem revisão

```sql
SELECT
    item_number,
    original_description,
    product_category,
    presentation,
    measurement_resolution,
    price_normalization_reason,
    missing_fields
FROM silver_items
WHERE price_normalization_status <> 'defensible'
   OR fully_structured = FALSE
ORDER BY product_category, item_number;
```

## Homologações por região e ano

A view `award_savings_summary` é criada a partir de `silver_awards`.

```sql
SELECT
    product_category,
    macroregion,
    analysis_year,
    result_count,
    procurement_count,
    estimated_total_equivalent,
    awarded_total_value,
    economy_total,
    economy_percent
FROM award_savings_summary
ORDER BY analysis_year DESC, product_category, macroregion;
```

## Sinais estatísticos por escopo

A view `anomaly_scope_summary` resume a camada `gold_price_signals`.

```sql
SELECT
    comparison_scope,
    comparison_geography,
    comparison_period,
    analyzed_rows,
    signal_count,
    median_group_size
FROM anomaly_scope_summary
ORDER BY comparison_period DESC, comparison_scope;
```

## Sinais com maior desvio

```sql
SELECT
    product_category,
    original_description,
    comparison_scope,
    comparison_geography,
    comparison_period,
    awarded_price_per_base_unit,
    median_price,
    modified_z_score,
    detection_method
FROM price_anomalies
ORDER BY ABS(COALESCE(modified_z_score, 0)) DESC;
```

## Observação metodológica

Essas consultas expõem a camada SQL existente no projeto. Elas não significam que painéis públicos de preços ou sinais já estejam publicados. O Atlas mantém a distinção entre implementação analítica, base local consolidada e resultados públicos revisados.

Sinal estatístico também não é tratado como prova de irregularidade. Consulte [metodologia de sinais](metodologia-anomalias.md) para os critérios de elegibilidade, agrupamento e interpretação.
