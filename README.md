# Atlas de Compras Públicas

**Inteligência de dados auditável para compras públicas no Brasil.**

O Atlas transforma dados públicos do Portal Nacional de Contratações Públicas (PNCP) em informação comparável, rastreável e explicável. O projeto combina engenharia de dados, normalização de produtos, análise de preços e validação quantitativa para apoiar a exploração de compras públicas em diferentes regiões e períodos.

A odontologia é a primeira vertical implementada e funciona como um domínio de alta complexidade para validar o núcleo analítico.

## O que o projeto entrega

| Camada | Capacidade |
| --- | --- |
| Coleta | Captura de contratações, itens e resultados diretamente do PNCP |
| Rastreabilidade | Evidências imutáveis com SHA-256 e manifestos de proveniência |
| Consolidação | Múltiplas contratações com chaves estáveis, deduplicação e reconstrução idempotente |
| Normalização | Padronização de descrições, apresentações, medidas e atributos técnicos |
| Identidade | Product Identity Engine com regras explícitas e decisões auditáveis |
| Análise | Comparação de preços com contexto geográfico e temporal |
| Qualidade | Score determinístico, métricas de cobertura e fila de itens não reconhecidos |
| Sinais | Detecção estatística com MAD e IQR, sem tratar sinal como prova de irregularidade |

## Arquitetura

~~~mermaid
flowchart LR
    A[API PNCP] --> B[Evidência bruta]
    B --> C[Validação]
    C --> D[Normalização]
    D --> E[Qualidade]
    D --> F[Preço normalizado]
    F --> G[Contexto geográfico e temporal]
    G --> H[Parquet + DuckDB]
    H --> I[Grupos comparáveis]
    I --> J[MAD / IQR]
    J --> K[Sinais explicáveis]
~~~

A cadeia de rastreabilidade segue o princípio:

`sinal → grupo comparável → homologação → item → contratação → SHA-256 → resposta original → PNCP`

## Stack

- Python 3.12+
- Polars
- DuckDB
- Pydantic
- httpx
- pytest
- Ruff
- Parquet

## Validação

A taxonomia é avaliada com datasets manuais versionados e fontes públicas separadas entre ciclos de desenvolvimento.

| Benchmark | Amostras | Acurácia independente |
| --- | ---: | ---: |
| v2 | 48 | 72,92% |
| v3 | 42 | 90,48% |
| v4 | 48 | 85,42% |
| v5 holdout | 48 | 79,17% |

O **v5 permanece como holdout não ajustado**, preservando uma referência independente antes de novas alterações na taxonomia. Resultados pós-tuning dos ciclos anteriores são mantidos separadamente e não substituem suas baselines originais.

Documentação completa:

- [Benchmark v1](docs/benchmark-v1.md)
- [Benchmark v2](docs/benchmark-v2.md)
- [Benchmark v3](docs/benchmark-v3.md)
- [Benchmark v4](docs/benchmark-v4.md)
- [Benchmark v5](docs/benchmark-v5.md)

## Exemplo de normalização

Entrada:

~~~text
RES FOTOP A2 C/2 SERINGAS 4G
~~~

Saída estruturada:

~~~text
categoria: composite_resin
cor: A2
apresentacao: syringe
quantidade_embalagem: 2
quantidade_unitaria: 4 g
quantidade_total: 8 g
~~~

Quando a descrição permite, o pipeline também normaliza o preço pela quantidade física, mantendo massa e volume como dimensões distintas.

## Uso rápido

Instalação em modo de desenvolvimento:

~~~bash
pip install -e ".[dev]"
~~~

Capturar uma contratação:

~~~bash
dpi capture-contract \
  --cnpj <CNPJ> \
  --year <ANO> \
  --sequence <SEQUENCIAL>
~~~

Construir a camada analítica:

~~~bash
dpi build-analytics \
  --raw <ARQUIVO_DE_ITENS> \
  --database data/analytics.duckdb
~~~

Consolidar todas as contratações capturadas:

~~~bash
dpi build-award-dataset \
  --bundles-root data/raw/contracts \
  --database data/analytics.duckdb
~~~

Gerar sinais estatísticos:

~~~bash
dpi detect-anomalies --database data/analytics.duckdb
~~~

## Estrutura

~~~text
src/dental_procurement_intelligence/
  pncp/             cliente e modelos do PNCP
  ingestion/        captura e evidências
  identity/         taxonomia e identidade de produto
  evaluation/       benchmarks e métricas
  normalization/    texto, medidas e geografia
  analytics/        lakehouse, homologações e sinais
  cli.py            interface de linha de comando

data/
docs/
tests/
~~~

O namespace Python histórico é mantido por compatibilidade interna. O produto público é **Atlas de Compras Públicas**.

## Documentação técnica

- [Arquitetura](docs/architecture.md)
- [Dataset multi-contratação](docs/multi-contratacao.md)
- [Metodologia de sinais de preço](docs/metodologia-anomalias.md)
- [Qualidade do normalizador](docs/qualidade-normalizador.md)
- [Benchmarks e validação](docs/benchmark-v5.md)

## Próximos passos

- reforçar comparabilidade de embalagem e quantidade física
- qualificar a confiança da normalização de preço por unidade física
- expandir a arquitetura para novos domínios
- disponibilizar API e dashboard analítico

## Fonte dos dados

Os dados são obtidos da API pública do **Portal Nacional de Contratações Públicas (PNCP)**.

O projeto preserva a evidência de origem e separa dados brutos, transformações analíticas e resultados derivados para permitir auditoria e reprodução.
