# Dental Procurement Intelligence

Plataforma auditável de inteligência de dados para compras públicas odontológicas no Brasil.

O projeto constrói um pipeline reprodutível para coletar, normalizar, comparar e analisar itens odontológicos publicados no Portal Nacional de Contratações Públicas (PNCP). O desafio principal não é apenas calcular preços, mas determinar quando descrições pouco padronizadas representam produtos realmente comparáveis.

## Status atual

**v0.4.0 — camada analítica com Parquet e DuckDB**

O repositório já inclui:

- pacote Python tipado;
- cliente para a API pública do PNCP;
- modelos estruturados para itens e resultados homologados;
- normalização determinística de textos e medidas;
- armazenamento bruto endereçado por conteúdo com SHA-256;
- manifesto de proveniência e verificação de integridade;
- Product Identity Engine com decisão explicável;
- normalização de embalagem e quantidade física;
- transformação analítica em Parquet;
- catálogo SQL local com DuckDB;
- cálculo de preço normalizado por unidade física;
- testes automatizados para as principais regras.

O GitHub Actions continua desativado nesta fase. As validações foram desenhadas para execução local, evitando consumo desnecessário de minutos de CI.

## Problema

Descrições de compras públicas frequentemente apresentam abreviações, erros, variações de embalagem e unidades incompatíveis.

Exemplos:

`RES FOTOP A2 C/2 SER 4G`

`RESINA COMPOSTA FOTOPOLIMERIZAVEL COR A2 SERINGA 4 G`

Uma comparação direta pelo texto ou pelo preço unitário informado pode ser enganosa.

A pergunta central do projeto é:

> Estes registros representam produtos comparáveis o suficiente para uma análise de preço, e conseguimos explicar essa decisão?

## Fonte dos dados

A fonte principal é a API pública de produção do PNCP:

`https://pncp.gov.br/api/pncp`

O pipeline preserva o conteúdo bruto recebido da fonte antes de qualquer transformação.

## Arquitetura

~~~mermaid
flowchart LR
    A[API PNCP] --> B[Evidência bruta]
    B --> C[Validação estrutural]
    C --> D[Normalização textual]
    D --> E[Product Identity Engine]
    E --> F[Normalização de unidades]
    F --> G[Parquet]
    G --> H[DuckDB]
    H --> I[Grupos comparáveis]
    I --> J[Análise robusta de preços]
    J --> K[API de evidências]
    K --> L[Dashboard]
~~~

### Camadas de dados

- **raw** — resposta original e imutável da fonte;
- **bronze** — registros tipados e estruturalmente validados;
- **silver** — atributos de produto, unidades e medidas normalizadas;
- **gold** — grupos comparáveis, estatísticas e alertas explicáveis.

## Product Identity Engine

Uma descrição como:

`RES FOTOP A2 C/2 SERINGAS 4G`

já pode ser transformada em uma representação estruturada:

~~~text
categoria: composite_resin
cor: A2
apresentacao: syringe
quantidade_embalagem: 2
quantidade_unitaria: 4 g
quantidade_total: 8 g
~~~

O motor não usa apenas similaridade textual. Diferenças relevantes de categoria, apresentação, cor ou quantidade podem tornar dois itens incompatíveis mesmo quando os textos parecem semelhantes.

## Preço normalizado

Além do preço unitário informado pelo PNCP, a camada analítica calcula preço por unidade física quando a descrição oferece informação suficiente.

Exemplo:

~~~text
Preço do item: R$ 80,00
Embalagem: 2 seringas
Conteúdo por seringa: 4 g
Conteúdo total: 8 g

Preço normalizado: R$ 10,00/g
~~~

Esse valor permite comparações mais defensáveis entre embalagens diferentes.

## Início rápido

Recomendado: Python 3.12 ou superior.

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
~~~

No Windows PowerShell:

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
~~~

Consultar itens de uma contratação conhecida:

~~~bash
dpi items --cnpj 10000000000003 --year 2021 --sequence 1
~~~

Capturar a resposta bruta com manifesto SHA-256:

~~~bash
dpi capture-items --cnpj 10000000000003 --year 2021 --sequence 1
~~~

Construir a camada analítica a partir de um arquivo bruto capturado:

~~~bash
dpi build-analytics \
  --raw data/raw/objects/sha256/xx/arquivo.json \
  --parquet data/silver/items.parquet \
  --database data/analytics.duckdb
~~~

Consultar o resumo analítico:

~~~bash
dpi analytics-summary --database data/analytics.duckdb
~~~

## Estrutura do repositório

~~~text
src/dental_procurement_intelligence/
  pncp/             cliente PNCP e modelos tipados
  ingestion/        evidência bruta e proveniência
  identity/         identidade canônica e comparabilidade
  normalization/    normalização textual e de medidas
  analytics/        Parquet, DuckDB e métricas analíticas
  cli.py            interface de linha de comando

tests/              testes automatizados
docs/               arquitetura e decisões técnicas
data/               contrato das camadas locais
~~~

## Princípio de auditabilidade

Cada linha da camada analítica mantém o SHA-256 do arquivo bruto que a originou.

Isso permite rastrear:

`indicador → registro analítico → registro normalizado → evidência bruta → PNCP`

## Salvaguarda metodológica

Um preço estatisticamente atípico não constitui evidência de fraude, corrupção ou ilegalidade.

Os futuros mecanismos de detecção de anomalias servirão para priorizar registros que merecem revisão. Cada sinal deverá apresentar população de comparação, método utilizado, tamanho da amostra e evidências de origem.

## Roadmap

- [x] Estrutura inicial do projeto
- [x] Cliente de itens e resultados do PNCP
- [x] Normalização textual
- [x] Extração de medidas
- [x] Ingestão bruta com hash de conteúdo
- [x] Vocabulário odontológico canônico — baseline
- [x] Normalização de embalagem e unidade — baseline
- [x] Product Identity Engine explicável — baseline
- [x] Camada analítica Parquet
- [x] Catálogo e consultas locais com DuckDB
- [x] Preço normalizado por unidade física
- [ ] Expandir taxonomia odontológica validada
- [ ] Adicionar recuperação semântica de candidatos
- [ ] Incorporar resultados homologados à camada analítica
- [ ] Detecção robusta de preços atípicos
- [ ] API FastAPI de evidências
- [ ] Interface analítica em React
- [ ] Relatório público de metodologia e qualidade dos dados

## Princípios

1. A evidência de origem é imutável.
2. Toda transformação deve ser reproduzível.
3. A equivalência de produtos deve ser explicável.
4. Preços só podem ser comparados dentro de grupos defensáveis.
5. Ausência e incerteza devem permanecer explícitas.
6. Todo resultado analítico deve ser rastreável à fonte pública.
