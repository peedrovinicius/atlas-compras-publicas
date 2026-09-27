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
| Identidade | Product Identity Engine com atributos técnicos específicos por categoria |
| Preço físico | Base defensável e valores financeiros preservados em decimal |
| Análise | Comparação de preços com contexto geográfico e temporal |
| Qualidade | Score determinístico, cobertura semântica e cobertura de atributos técnicos |
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

A extração de atributos técnicos possui benchmark independente próprio:

| Benchmark técnico | Exemplos | Campos revisados | Micro accuracy |
| --- | ---: | ---: | ---: |
| atributos técnicos v1 | 33 | 61 | 85,25% |
| atributos técnicos v2 | 41 | 77 | 93,51% |
| atributos técnicos v3 | 45 | 86 | 94,19% |
| atributos técnicos v4 | 45 | 87 | 88,51% |
| atributos técnicos v5 | 48 | 92 | 86,96% |

O v1 atingiu 100% na regressão pós-tuning v1.14. A baseline independente original permanece 85,25%.

O v2 usa oito contratações inéditas. Após o tuning da v1.16, o mesmo conjunto atingiu 100%, mas a baseline independente permanece 93,51%.

O v3 usa mais oito contratações inéditas. Após o tuning da v1.18, o mesmo conjunto atingiu 100% nos atributos e 45/45 categorias, mas as baselines independentes permanecem 94,19% e 93,33%.

O v4 adiciona contexto negativo, abreviações comerciais e grafias não padronizadas. A baseline independente ficou em 88,51%, com 42/45 categorias corretas e um falso positivo contextual. Após o tuning da v1.20, o mesmo conjunto atingiu 100% nos atributos e 45/45 categorias, sem substituir a baseline independente.

O v5 amplia os negativos contextuais e alternativas explícitas. A baseline independente ficou em 86,96%, com 39/48 categorias corretas, 2 falsos positivos técnicos e 10 falsos negativos.

Documentação completa:

- [Benchmark v1](docs/benchmark-v1.md)
- [Benchmark v2](docs/benchmark-v2.md)
- [Benchmark v3](docs/benchmark-v3.md)
- [Benchmark v4](docs/benchmark-v4.md)
- [Benchmark v5](docs/benchmark-v5.md)
- [Benchmark de atributos técnicos v1](docs/benchmark-technical-attributes-v1.md)
- [Regressão técnica pós-tuning v1.14](docs/benchmark-technical-attributes-v1-post-tuning.md)
- [Benchmark de atributos técnicos v2](docs/benchmark-technical-attributes-v2.md)
- [Regressão técnica v2 pós-tuning v1.16](docs/benchmark-technical-attributes-v2-post-tuning.md)
- [Benchmark de atributos técnicos v3](docs/benchmark-technical-attributes-v3.md)
- [Regressão técnica v3 pós-tuning v1.18](docs/benchmark-technical-attributes-v3-post-tuning.md)
- [Benchmark de atributos técnicos v4](docs/benchmark-technical-attributes-v4.md)
- [Regressão técnica v4 pós-tuning v1.20](docs/benchmark-technical-attributes-v4-post-tuning.md)
- [Benchmark de atributos técnicos v5](docs/benchmark-technical-attributes-v5.md)

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

Quando descrição, embalagem e medidas sustentam a conversão, o pipeline normaliza o preço pela quantidade física. Múltiplas medidas incompatíveis e kits heterogêneos ficam em `review` e não entram nos sinais estatísticos.

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
- [Precisão monetária](docs/precisao-monetaria.md)
- [Atributos técnicos](docs/atributos-tecnicos.md)
- [Qualidade do normalizador](docs/qualidade-normalizador.md)
- [Benchmarks e validação](docs/benchmark-v5.md)

## Próximos passos

- corrigir relações contextuais do benchmark técnico v5 sem alterar a baseline
- criar validação independente após o próximo ciclo de contexto
- expandir a arquitetura para novos domínios
- disponibilizar API e dashboard analítico

## Fonte dos dados

Os dados são obtidos da API pública do **Portal Nacional de Contratações Públicas (PNCP)**.

O projeto preserva a evidência de origem e separa dados brutos, transformações analíticas e resultados derivados para permitir auditoria e reprodução.
