# Arquitetura

## Objetivo

Produzir inteligência de preços sem perder a cadeia de evidências que conecta um resultado analítico ao registro original do PNCP.

## Fluxo principal

`API PNCP → raw → bronze → silver → gold → API analítica → dashboard`

Uma trilha paralela mede a qualidade da transformação:

`silver → métricas de cobertura → fila de lacunas → evolução da taxonomia`

## Raw

São armazenadas separadamente:

- resposta da contratação;
- resposta dos itens;
- resposta de resultados de cada item.

Cada objeto possui SHA-256 e manifesto de coleta.

A captura completa também mantém um manifesto estável por contratação em `data/raw/contracts`. Esse manifesto referencia os objetos imutáveis da captura e usa CNPJ, ano e sequencial do PNCP como identidade da contratação.

## Bronze

Modelos tipados representam:

- contratação;
- órgão;
- unidade administrativa;
- item;
- resultado homologado.

Nenhuma inferência semântica é misturada à validação estrutural.

## Silver

### silver_items

Contém:

- descrição original e normalizada;
- categoria;
- método de classificação;
- termos que deram suporte à classificação;
- apresentação;
- cor;
- concentração;
- quantidade por embalagem;
- medida física;
- preço normalizado;
- indicadores de cobertura;
- score e nível de qualidade;
- campos ausentes;
- SHA-256 da evidência.

### silver_awards

A reconstrução consolidada lê os manifestos de todas as contratações, seleciona uma captura por `procurement_key` e deduplica resultados por `award_key`. Reexecutar o mesmo conjunto de manifestos produz o mesmo conjunto lógico de linhas.

Contém:

- `procurement_key`;
- `award_key`;

- atributos canônicos do produto;
- cor e concentração;
- preços estimado e homologado;
- preço por unidade física;
- fornecedor e marca;
- resultado e situação;
- contexto temporal;
- contexto geográfico;
- hashes de proveniência.

## Qualidade

As visões atuais são:

- `normalization_quality_summary`;
- `normalization_quality_by_category`;
- `unrecognized_items`.

O score é determinístico e não probabilístico.

Itens com atributo crítico ausente não são considerados totalmente estruturados.


## Precisão monetária

Valores financeiros entram pelos modelos PNCP como `Decimal` e permanecem decimais nas camadas analíticas.

O schema Silver utiliza `DECIMAL(38,12)` para:

- valores unitários;
- valores totais;
- economia monetária;
- percentuais derivados persistidos;
- preços normalizados por unidade física.

A escala analítica é arredondada explicitamente com `ROUND_HALF_EVEN`. Nenhuma dessas colunas passa por `float` antes de Parquet ou DuckDB.

Ponto flutuante continua permitido para escores estatísticos derivados, como modified z-score, porque esses valores não representam dinheiro.

## Gold

A tabela `gold_price_signals` seleciona, para cada resultado elegível, o grupo geográfico-temporal mais específico com amostra suficiente.

A identidade técnica do grupo inclui:

- categoria;
- apresentação;
- cor;
- concentração;
- unidade física;
- quantidade física.

Hierarquia geográfico-temporal:

`UF/trimestre → região/trimestre → Brasil/trimestre → região/ano → Brasil/ano`

## Estatística

MAD com modified z-score é o método principal.

IQR é utilizado quando MAD é zero e existe dispersão.

Grupos com amostra insuficiente ou sem variação não geram sinal.

## Rastreabilidade

A cadeia é:

`sinal → grupo → homologação → item → contratação → evidências SHA-256 → PNCP`

A camada de qualidade adiciona:

`item → score → componentes do score → campos ausentes`

## Salvaguarda

Sinal estatístico não equivale a irregularidade.

Score de normalização não equivale a probabilidade de acerto.

O sistema deve apresentar explicitamente método, evidência, lacunas e limitações.
