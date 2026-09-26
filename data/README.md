# Camadas locais de dados

Os datasets gerados pelo pipeline não são versionados diretamente no Git.

O projeto utiliza as seguintes pastas locais:

- `raw/` — respostas imutáveis do PNCP e manifestos de proveniência;
- `bronze/` — registros de origem tipados;
- `silver/` — atributos, unidades, preços e produtos normalizados;
- `gold/` — tabelas analíticas e futuros sinais explicáveis de anomalia.

Arquivos Parquet e bancos DuckDB são gerados localmente e permanecem ignorados pelo Git.

O repositório deve conter apenas documentação, schemas e fixtures pequenas de teste. Bases reais em grande volume devem ser reproduzíveis a partir das fontes públicas, e não armazenadas como artefatos opacos.
