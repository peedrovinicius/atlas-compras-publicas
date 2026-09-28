# Amostra analítica reproduzível

Os arquivos analíticos desta pasta são gerados localmente e não são versionados.

Fontes padrão da demonstração analítica:

- `15126437000305-1-000212/2026` - CHC/UFPR, Curitiba/PR;
- `18277947000100-1-000259/2026` - Município de Guarda-Mor/MG;
- `39485412000102-1-000004/2026` - Município de Queimados/RJ.

Todas são contratações públicas odontológicas. A inclusão no conjunto publicado depende de captura válida e resultados homologados disponíveis no PNCP.

Reconstrução completa:

```bash
atlas build-demo-data
```

O comando executa:

1. captura de cada contratação, seus itens e resultados no PNCP;
2. persistência das respostas brutas com SHA-256 e manifestos;
3. construção de `silver_items`;
4. construção de `silver_awards`;
5. geração de `gold_price_signals`;
6. criação das visões de qualidade.

Artefatos gerados:

```text
data/demo/
  raw/
  silver/items.parquet
  silver/awards.parquet
  atlas-demo.duckdb
```

A captura consulta endpoints públicos do PNCP e consolida as contratações em uma única base. `silver_items` usa a chave composta `(procurement_key, item_number)`, evitando colisões entre compras. Análises de preço só são produzidas quando existem resultados homologados e normalização de preço defensável.

Os artefatos binários e a evidência bruta local são ignorados pelo Git. O repositório mantém apenas o código necessário para reconstruí-los.
