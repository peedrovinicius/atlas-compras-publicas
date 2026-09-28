# Amostra analítica reproduzível

Os arquivos analíticos desta pasta são gerados localmente e não são versionados.

Fonte padrão da demonstração analítica:

- CNPJ: `15126437000305`
- ano: `2026`
- sequencial PNCP: `212`
- número de controle PNCP: `15126437000305-1-000212/2026`

Reconstrução completa:

```bash
atlas build-demo-data
```

O comando executa:

1. captura da contratação, itens e resultados no PNCP;
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

A captura consulta endpoints públicos do PNCP e só produz análises de preço quando existem resultados homologados disponíveis. A duração depende do tamanho da contratação e da disponibilidade do PNCP.

Os artefatos binários e a evidência bruta local são ignorados pelo Git. O repositório mantém apenas o código necessário para reconstruí-los.
