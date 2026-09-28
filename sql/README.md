# SQL do Atlas

Consultas analíticas versionadas para demonstrar o uso direto do warehouse DuckDB.

| Arquivo | Tabela principal | Pergunta |
| --- | --- | --- |
| `01_price_evolution.sql` | `silver_awards` | Como o preço mediano evolui por categoria e região? |
| `02_group_dispersion.sql` | `gold_price_signals` | Qual a dispersão dos grupos comparáveis? |
| `03_regional_gap.sql` | `silver_awards` | Quais regiões mais diferem da mediana nacional? |
| `04_normalization_coverage.sql` | `silver_items` | Qual a cobertura da estruturação por categoria? |
| `05_signal_trace.sql` | `gold_price_signals` | Como rastrear um sinal até a evidência de origem? |

Exemplo com DuckDB CLI:

```bash
duckdb data/analytics.duckdb < sql/01_price_evolution.sql
```

A consulta `05_signal_trace.sql` usa um parâmetro posicional `?` para `award_key` e é destinada a execução parametrizada pela aplicação ou por cliente DuckDB.
