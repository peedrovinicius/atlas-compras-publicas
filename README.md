<div align="center">

# Atlas de Compras Públicas

Dados do PNCP transformados em pipeline auditável para normalização de itens, comparação de preços e detecção explicável de sinais.

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-analytics-FFF000?logo=duckdb&logoColor=000)

[Snapshot de qualidade](docs/dashboard-quality-snapshot.html) · [Documentação](docs/README.md) · [Changelog](CHANGELOG.md) · [Arquitetura](docs/architecture.md) · [Issues](https://github.com/peedrovinicius/atlas-compras-publicas/issues) · [Como contribuir](CONTRIBUTING.md)

</div>

## Visão geral

O Atlas transforma dados públicos do Portal Nacional de Contratações Públicas em conjuntos comparáveis, rastreáveis e auditáveis. A cadeia cobre captura, preservação da evidência original, normalização de produtos, consolidação analítica e detecção estatística de sinais.

<table>
<tr>
<td align="center"><strong>548</strong><br/><sub>exemplos técnicos</sub></td>
<td align="center"><strong>984</strong><br/><sub>campos técnicos avaliados</sub></td>
<td align="center"><strong>91,36%</strong><br/><sub>micro accuracy técnica ponderada</sub></td>
<td align="center"><strong>192</strong><br/><sub>exemplos de medicamentos</sub></td>
</tr>
</table>

<p align="center">
  <img src="docs/assets/dashboard-quality-snapshot.svg" alt="Snapshot real de qualidade do Atlas de Compras Públicas" width="100%" />
</p>

<sub>Snapshot gerado de baselines congeladas e versionadas. Resultados pós-tuning são documentados separadamente e não substituem as medições independentes.</sub>

A odontologia é a primeira vertical em produção. Medicamentos permanecem em validação independente porque a evolução do domínio separa baseline congelada, pós-tuning e promoção metodológica.

## O que o projeto entrega

| Camada | Capacidade |
| --- | --- |
| Coleta | Captura de contratações, itens e resultados diretamente do PNCP |
| Rastreabilidade | Evidências com SHA-256 e manifestos de proveniência |
| Consolidação | Múltiplas contratações com chaves estáveis e reconstrução idempotente |
| Normalização | Padronização de descrições, apresentações, medidas e atributos técnicos |
| Identidade | Product Identity Engine com atributos específicos por categoria |
| Preço físico | Conversão defensável por unidade física quando a descrição permite |
| Análise | Comparação de preços com contexto geográfico e temporal |
| Qualidade | Benchmarks congelados, regressões pós-tuning e snapshot auditável |
| Sinais | MAD e IQR como sinais estatísticos, sem tratar sinal como prova |

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

`sinal -> grupo comparável -> homologação -> item -> contratação -> SHA-256 -> resposta original -> PNCP`

## Stack

- Python 3.12+
- Polars
- DuckDB
- Pydantic
- httpx
- pytest
- Ruff
- Parquet

## Validação principal

A taxonomia odontológica possui ciclos independentes de benchmark. O v5 permanece como holdout não ajustado e preserva uma referência independente antes de novas alterações.

| Benchmark | Amostras | Acurácia independente |
| --- | ---: | ---: |
| v2 | 48 | 72,92% |
| v3 | 42 | 90,48% |
| v4 | 48 | 85,42% |
| v5 holdout | 48 | 79,17% |

## Atributos técnicos

A extração de atributos técnicos possui 12 ciclos independentes. O snapshot consolidado atual resume:

| Grupo | Exemplos | Campos | Campos corretos | Micro accuracy ponderada |
| --- | ---: | ---: | ---: | ---: |
| Atributos técnicos v1-v12 | 548 | 984 | 899 | 91,36% |

Documentos principais:

- [Benchmark técnico v12](docs/benchmark-technical-attributes-v12.md)
- [Regressão técnica v12 pós-tuning v1.37](docs/benchmark-technical-attributes-v12-post-tuning.md)
- [Consolidação técnica v1-v12](docs/benchmark-technical-consolidated-v1-v12.md)
- [Revisão da arquitetura de regras e contextos](docs/architecture-rules-review.md)

## Medicamentos

Medicamentos é um domínio separado da produção. As baselines independentes são preservadas e os resultados pós-tuning ficam em documentos próprios.

| Holdout | Parser medido | Exemplos | Campos | Corretos | Micro accuracy |
| --- | --- | ---: | ---: | ---: | ---: |
| medicamentos v1 | v1.40.0 | 48 | 192 | 168 | 87,50% |
| medicamentos v2 | v1.44.0 | 48 | 192 | 153 | 79,69% |
| medicamentos v3 | v1.46.0 | 48 | 192 | 173 | 90,10% |
| medicamentos v4 | pós-v1.48 vigente | 48 | 192 | 189 | 98,44% |
| **Total ponderado** |  | **192** | **768** | **683** | **88,93%** |

Pós-tuning v1.49.0:

| Conjunto | Resultado | Observação |
| --- | ---: | --- |
| medicamentos v4 pós-v1.49 | 192/192 | Regressão separada, sem substituir a baseline independente |

O domínio permanece em `benchmark_required`. A baseline independente continua sendo o critério metodológico principal, e o pós-tuning serve apenas para validar correções pontuais.

Comandos:

~~~bash
dpi evaluate-medications --dataset data/evaluation/medications-v4.jsonl
dpi medication-errors --dataset data/evaluation/medications-v4.jsonl
~~~

Documentos principais:

- [Benchmark independente de medicamentos v1](docs/benchmark-medications-v1.md)
- [Medicamentos v1 pós-tuning v1.44](docs/benchmark-medications-v1-post-tuning.md)
- [Benchmark independente de medicamentos v2](docs/benchmark-medications-v2.md)
- [Medicamentos v2 pós-tuning v1.46](docs/benchmark-medications-v2-post-tuning.md)
- [Benchmark independente de medicamentos v3](docs/benchmark-medications-v3.md)
- [Medicamentos v3 pós-tuning v1.48](docs/benchmark-medications-v3-post-tuning.md)
- [Benchmark independente de medicamentos v4](docs/benchmark-medications-v4.md)
- [Medicamentos v4 pós-tuning v1.49](docs/benchmark-medications-v4-post-tuning.md)
- [Congelamento do holdout de medicamentos v4](docs/medications-v4-freeze.md)
- [Consolidação de medicamentos v1-v4](docs/benchmark-medications-consolidated-v1-v4.md)

## Evidências de qualidade

O snapshot publicado é gerado exclusivamente das baselines congeladas do projeto: 548 exemplos técnicos, 984 campos técnicos, 192 exemplos de medicamentos e 768 campos de medicamentos.

- [Abrir snapshot HTML](docs/dashboard-quality-snapshot.html)
- [Dados auditáveis do snapshot](docs/dashboard-quality-snapshot.json)
- [Consolidação técnica v1-v12](docs/benchmark-technical-consolidated-v1-v12.md)
- [Consolidação de medicamentos v1-v4](docs/benchmark-medications-consolidated-v1-v4.md)

O snapshot não simula preços, homologações ou sinais. Esses painéis só serão publicados quando existir uma base DuckDB analítica consolidada.

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

## API e dashboard

~~~bash
pip install -e ".[api]"
dpi serve-api --database data/analytics.duckdb
dpi build-dashboard --database data/analytics.duckdb --output docs/dashboard.html
~~~

- [Documentação da API e dashboard](docs/api-dashboard.md)

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
- [Arquitetura multidomínio](docs/multidomain-architecture.md)
- [API e dashboard analítico](docs/api-dashboard.md)
- [Dataset multi-contratação](docs/multi-contratacao.md)
- [Metodologia de sinais de preço](docs/metodologia-anomalias.md)
- [Precisão monetária](docs/precisao-monetaria.md)
- [Qualidade do normalizador](docs/qualidade-normalizador.md)
- [Release v1.49.0](docs/release-v1.49.0.md)
- [Auditoria v1.49.0](docs/audit-v1.49.0.md)

## Fonte dos dados

Os dados são obtidos da API pública do Portal Nacional de Contratações Públicas. O projeto preserva dados brutos, transformações e resultados derivados para permitir auditoria e reprodução.

## Contribuindo

Contribuições externas são bem-vindas quando preservam rastreabilidade, baselines independentes e metodologia documentada. Consulte [CONTRIBUTING.md](CONTRIBUTING.md) antes de abrir um Pull Request.

Governança do repositório: [Segurança](SECURITY.md) · [Suporte](SUPPORT.md) · [Código de Conduta](CODE_OF_CONDUCT.md)
