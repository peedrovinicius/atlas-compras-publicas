# Procurement Intelligence BR

Plataforma auditável de inteligência de dados para compras públicas no Brasil.

O projeto constrói um motor reprodutível para coletar, normalizar, comparar e analisar compras públicas publicadas no Portal Nacional de Contratações Públicas (PNCP). A odontologia é o primeiro domínio implementado e funciona como uma vertical de alta complexidade para validar o núcleo genérico de ingestão, proveniência, identidade de produto, normalização de unidades, comparação de preços e detecção explicável de sinais atípicos.

## Status atual

**v1.4.0: negação, kits mistos e variantes lexicais**

O núcleo genérico já inclui:

- cliente tipado para a API pública do PNCP;
- captura auditável da contratação, itens e resultados;
- armazenamento bruto com SHA-256 e manifestos de proveniência;
- normalização textual, de massa e de volume;
- Product Identity Engine explicável;
- arquitetura preparada para múltiplos domínios;
- odontologia como primeiro domínio especializado;
- taxonomia odontológica determinística ampliada;
- extração de cor e concentração quando clinicamente relevantes;
- normalização de embalagem e quantidade física;
- Parquet + DuckDB;
- valores estimados e homologados;
- cálculo de economia;
- dimensões geográfica e temporal;
- grupos comparáveis hierárquicos;
- sinais robustos com MAD e IQR;
- score determinístico de qualidade da normalização;
- métricas de cobertura global e por categoria;
- fila auditável de itens ainda não reconhecidos;
- dataset público de avaliação manual versionado;
- métricas de acurácia, precisão, recall e F1 por categoria;
- avaliação separada de cor e concentração;
- relatório de erros de classificação rastreável à fonte;
- benchmark independente v2 congelado antes da avaliação;
- comparação explícita entre regressão interna e generalização;
- precedência semântica para distinguir produto comprado de termos citados no contexto;
- suporte a resina microhíbrida e anestésicos por princípio ativo;
- benchmark v2 pós-tuning preservado separadamente da baseline independente.

O GitHub Actions permanece desativado nesta fase para evitar consumo desnecessário de minutos de CI.

## Fonte dos dados

A fonte principal é a API pública do PNCP:

`https://pncp.gov.br/api/pncp`

O pipeline preserva como evidências independentes:

- metadados da contratação;
- itens;
- resultados de cada item.

Cada resposta capturada recebe SHA-256 e manifesto de coleta.

## Arquitetura

~~~mermaid
flowchart LR
    A[API PNCP] --> B[Evidência bruta SHA-256]
    B --> C[Validação estrutural]
    C --> D[Normalização por domínio]
    D --> E[Qualidade do normalizador]
    D --> F[Preço por unidade física]
    F --> G[Contexto geográfico e temporal]
    G --> H[Parquet + DuckDB]
    H --> I[Grupo comparável]
    I --> J[MAD / IQR]
    J --> K[Sinal explicável]
    E --> L[Fila de lacunas]
    K --> M[API]
    L --> M
    M --> N[Dashboard]
~~~

## Primeiro domínio: odontologia

A odontologia é a primeira vertical especializada do projeto. A taxonomia atual cobre categorias que aparecem de forma recorrente em compras odontológicas e serve como prova de que o motor genérico consegue incorporar regras de domínio explícitas e auditáveis.

Categorias atuais:

~~~text
composite_resin
flowable_resin
dental_adhesive
glass_ionomer
phosphoric_acid
alginate
fluoride_gel
prophylaxis_paste
calcium_hydroxide
zinc_oxide
eugenol
radiographic_fixer
radiographic_developer
local_anesthetic
unknown
~~~

A classificação é baseada em regras explícitas e vocabulário controlado. Não existe classificação probabilística oculta nesta etapa.

## Atributos críticos

Nem todas as categorias exigem os mesmos atributos.

Exemplos:

- resinas e ionômeros: cor pode ser crítica para comparação;
- ácido fosfórico, flúor em gel e anestésicos: concentração pode ser crítica;
- todas as categorias: apresentação e medida física aumentam a capacidade de comparação.

Exemplo:

~~~text
ACIDO FOSFORICO 37% GEL SERINGA 2,5ML
~~~

pode produzir:

~~~text
categoria: phosphoric_acid
concentracao: 37%
apresentacao: syringe
quantidade: 2.5 ml
~~~

Dois ácidos com concentrações diferentes são incompatíveis para o Product Identity Engine.

Se um atributo crítico estiver ausente, o motor retorna `review` em vez de `match`.

## Qualidade do normalizador

O projeto não trata o score como probabilidade de acerto de uma IA.

O score é determinístico e explicável.

Ele considera:

- categoria identificada;
- apresentação identificada;
- medida física identificada;
- atributo crítico da categoria, quando aplicável.

Cada item recebe:

~~~text
normalization_quality_score
normalization_quality_level
fully_structured
category_identified
presentation_identified
measurement_identified
critical_attribute_name
critical_attribute_identified
missing_fields
classification_method
~~~

Níveis:

- `high` : score alto e estrutura mínima completa;
- `medium` : informação útil, mas existe alguma lacuna relevante;
- `low` : estrutura insuficiente para confiar na normalização.

Um score alto, por si só, não transforma um item incompleto em `high`: se faltar atributo crítico, o nível máximo é `medium`.

## Métricas de cobertura

Depois de executar `build-analytics`, o sistema pode gerar um resumo de qualidade:

~~~bash
dpi normalization-quality --database data/analytics.duckdb
~~~

O resultado inclui:

~~~text
total_items
category_identified_items
category_coverage_percent
presentation_identified_items
presentation_coverage_percent
measurement_identified_items
measurement_coverage_percent
fully_structured_items
fully_structured_percent
price_normalizable_items
price_normalizable_percent
average_quality_score
~~~

Para detalhar por categoria:

~~~bash
dpi normalization-quality \
  --database data/analytics.duckdb \
  --by-category
~~~

## Fila de itens não reconhecidos

Itens classificados como `unknown` não são escondidos.

Eles ficam disponíveis para revisão:

~~~bash
dpi unrecognized-items \
  --database data/analytics.duckdb \
  --limit 50
~~~

Essa fila permite expandir a taxonomia com base em lacunas observadas nos dados reais, em vez de adicionar regras arbitrárias.

## Benchmark v1

A v0.9.0 introduz um benchmark de regressão versionado em `data/evaluation/v1.jsonl`.

A primeira amostra contém **37 descrições públicas rotuladas manualmente**, distribuídas entre 14 rótulos, incluindo `unknown`. Ela contém casos positivos e negativos e preserva URL de origem, número do item e número de controle PNCP quando disponível.

Resultado da baseline executada sobre o código do commit `6800b8a`:

~~~text
amostras:                  37
acurácia de categoria:     100,00%
macro precision:           1,0000
macro recall:              1,0000
macro F1:                  1,0000
erros de categoria:        0

cor:
  suporte:                  8
  acurácia:                 100,00%

concentração:
  suporte:                  5
  acurácia:                 100,00%
~~~

Esses números **não representam acurácia estimada em produção**. A amostra v1 é pequena e participou da evolução das regras, portanto funciona como benchmark de regressão: uma mudança futura não deve quebrar comportamentos já revisados sem justificativa explícita.

A próxima etapa de validação deverá usar uma amostra maior e separada, congelada antes do desenvolvimento das novas regras.

Executar:

~~~bash
dpi evaluate-taxonomy --dataset data/evaluation/v1.jsonl
~~~

Listar divergências:

~~~bash
dpi evaluation-errors --dataset data/evaluation/v1.jsonl
~~~

O snapshot completo está em `data/evaluation/v1-baseline.json` e a metodologia em `docs/benchmark-v1.md`.

## Benchmark independente v2

A v1.0.0 adiciona uma amostra **separada das fontes usadas no v1** e congelada antes da primeira medição.

Fontes do v2:

- Itanhaém/SP : PNCP `46578498000175-1-000289/2026`;
- Araioses/MA : PNCP `06450191000170-1-000068/2026`.

A amostra contém **48 itens** e foi commitada antes de qualquer ajuste de regra motivado por seus resultados.

Baseline do código congelado no commit `78780c9`:

~~~text
amostras:                  48
categorias corretas:       35
erros de categoria:        13
acurácia de categoria:     72,92%
macro precision:           0,6240
macro recall:              0,5366
macro F1:                  0,5404

cor:
  suporte:                  7
  acurácia:                 100,00%

concentração:
  suporte:                  5
  acurácia:                 100,00%
~~~

Os principais erros observados, **sem ajuste posterior nesta versão**, foram:

- resina microhíbrida não reconhecida como `composite_resin`;
- adesivo com redações novas não reconhecido;
- um adesivo contendo a expressão “resina composta” classificado falsamente como resina;
- lidocaína, articaína e mepivacaína descritas pelo princípio ativo não reconhecidas como `local_anesthetic`;
- um kit de acabamento contendo “resina composta” classificado falsamente como produto restaurador.

Esse resultado é deliberadamente publicado porque mede melhor a capacidade de generalização do estado atual do sistema do que o benchmark v1.

O v1 continua útil como teste de regressão. O v2 passa a ser a referência independente inicial.

Executar:

~~~bash
dpi evaluate-taxonomy --dataset data/evaluation/v2.jsonl
~~~

Listar erros:

~~~bash
dpi evaluation-errors --dataset data/evaluation/v2.jsonl
~~~

O snapshot está em `data/evaluation/v2-baseline.json` e a análise detalhada em `docs/benchmark-v2.md`.

## Resultado pós-tuning da v1.1.0

A v1.1.0 usa os 13 erros observados no benchmark v2 para melhorar a taxonomia, **sem alterar nenhum rótulo do dataset congelado**.

Mudanças principais:

- resina microhíbrida passa a ser reconhecida como `composite_resin`;
- descrições iniciadas por `ADESIVO` ganham precedência sobre menções contextuais a “resina composta”;
- kits de acabamento e polimento deixam de ser confundidos com a própria resina;
- lidocaína, articaína e mepivacaína passam a identificar `local_anesthetic`;
- apresentação `ampola` passa a ser reconhecida como cartucho/recipiente clínico equivalente na camada de apresentação.

Revalidação determinística:

~~~text
benchmark v1
  amostras:               37
  categorias corretas:    37
  erros:                   0
  acurácia:                100,00%

benchmark v2 pós-tuning
  amostras:               48
  categorias corretas:    48
  erros:                   0
  acurácia:                100,00%
  macro precision:         1,0000
  macro recall:            1,0000
  macro F1:                1,0000
  cor:                     7/7
  concentração:            5/5
~~~

O resultado pós-tuning **não substitui** a baseline independente original de 72,92%. Os dois snapshots permanecem no repositório:

- `data/evaluation/v2-baseline.json` : medição independente antes de qualquer ajuste;
- `data/evaluation/v2-post-v1.1.json` : desempenho depois das correções guiadas pelos erros do v2.

O próximo teste relevante precisa ser um **v3 com fontes novas**, congelado antes de qualquer ajuste, para verificar se a melhora generaliza.

## Benchmark independente v3

O v3 foi congelado no commit `aec504c` antes de qualquer alteração na taxonomia motivada por seus resultados.

A amostra contém **42 itens de cinco fontes novas**:

- Crisólita/MG, PNCP `01614283000124-1-000014/2026`;
- Serra/ES, PNCP `27174093000127-1-000260/2026`;
- São Luís/MA, Pregão Eletrônico `90057/2026`;
- Itaipulândia/PR, PNCP `95725057000164-1-000297/2026`;
- Pojuca/BA, PNCP `13806237000106-1-000153/2026`.

Baseline independente da taxonomia atual:

~~~text
amostras:                  42
categorias corretas:       38
erros de categoria:        4
acurácia de categoria:     90,48%
macro precision:           0,6598
macro recall:              0,6931
macro F1:                  0,6731

cor:
  suporte:                  1
  acurácia:                 100,00%

concentração:
  suporte:                  6
  acurácia:                 100,00%
~~~

Os quatro erros ficaram concentrados em casos semanticamente úteis:

- `OXIDO ZINCO` não reconhecido por ausência da preposição “de”;
- `FIXADOR RADIOLOGICO` não reconhecido pela variante lexical;
- `SEM EUGENOL` classificado incorretamente como `eugenol`;
- kit misto de resinas e adesivo classificado como `dental_adhesive`.

Durante esta etapa também foi corrigido o avaliador: categorias presentes somente nas previsões agora entram nas métricas macro. Isso impede que um falso positivo em uma classe ausente dos rótulos da amostra seja ignorado.

A baseline original permanece preservada em `data/evaluation/v3-baseline.json`.

O próximo passo é corrigir os quatro erros **sem alterar o v3** e depois criar um v4 com fontes ainda não vistas.

## Resultado pós-tuning da v1.4.0

A v1.4.0 corrige os quatro erros revelados pelo benchmark v3 sem alterar nenhum rótulo congelado.

Mudanças aplicadas:

- `OXIDO ZINCO` passa a ser reconhecido como `zinc_oxide`;
- `FIXADOR RADIOLOGICO` passa a ser reconhecido como `radiographic_fixer`;
- termos explicitamente negados, como `SEM EUGENOL`, deixam de ativar a categoria;
- kits que combinam famílias diferentes, como resinas e adesivo, passam a ser tratados como `unknown` em vez de serem reduzidos a uma categoria única.

A regra de negação cobre atualmente padrões como:

~~~text
SEM <termo>
ISENTO DE <termo>
LIVRE DE <termo>
NAO CONTEM <termo>
~~~

Revalidação após as correções:

~~~text
benchmark v1
  amostras:               37
  corretas:               37
  erros:                   0
  acurácia:                100,00%

benchmark v2
  amostras:               48
  corretas:               48
  erros:                   0
  acurácia:                100,00%

benchmark v3 pós-tuning
  amostras:               42
  corretas:               42
  erros:                   0
  acurácia:                100,00%
  macro precision:         1,0000
  macro recall:            1,0000
  macro F1:                1,0000
~~~

O resultado pós-tuning do v3 não substitui sua baseline independente original de 90,48%. Os dois snapshots permanecem separados:

- `data/evaluation/v3-baseline.json`: medição independente anterior às correções;
- `data/evaluation/v3-post-v1.4.json`: desempenho depois das correções guiadas pelos quatro erros.

A próxima validação relevante deve usar um v4 composto por fontes ainda não vistas.

## Product Identity Engine

Uma descrição como:

`RES FOTOP A2 C/2 SERINGAS 4G`

pode ser transformada em:

~~~text
categoria: composite_resin
cor: A2
apresentacao: syringe
quantidade_embalagem: 2
quantidade_unitaria: 4 g
quantidade_total: 8 g
~~~

O motor considera conflitos de categoria, apresentação, quantidade e atributos críticos.

Decisões possíveis:

~~~text
match
review
incompatible
~~~

## Preço normalizado

Quando há informação suficiente, o pipeline calcula preço por unidade física.

~~~text
Preço homologado: R$ 72,00
Embalagem: 2 seringas
Conteúdo por seringa: 4 g
Conteúdo total: 8 g

Preço homologado normalizado: R$ 9,00/g
~~~

Massa e volume permanecem dimensões distintas.

## Contexto geográfico e temporal

A camada de homologações preserva:

- data de publicação;
- data do resultado;
- ano;
- trimestre;
- município;
- código IBGE;
- UF;
- macrorregião;
- esfera administrativa;
- modalidade.

## Grupos comparáveis

A análise de preços procura o grupo mais específico com amostra suficiente:

~~~text
1. mesma UF + mesmo trimestre
2. mesma macrorregião + mesmo trimestre
3. Brasil + mesmo trimestre
4. mesma macrorregião + mesmo ano
5. Brasil + mesmo ano
~~~

A chave técnica do produto também considera:

- categoria;
- apresentação;
- cor;
- concentração;
- unidade física;
- quantidade física.

## Sinais robustos de preço

Método principal:

`modified z-score = 0,67448975 × (preço - mediana) / MAD`

Limite padrão:

`|modified z-score| >= 3,5`

Quando MAD é zero e existe dispersão, utiliza-se IQR como fallback.

Um sinal estatístico não constitui evidência de fraude, corrupção, superfaturamento jurídico ou irregularidade administrativa.

## Fluxo principal

~~~text
capture-contract
        ↓
evidências raw
        ↓
build-analytics
        ├── normalization-quality
        └── unrecognized-items
        ↓
build-awards
        ↓
detect-anomalies
        ↓
anomalies-summary
~~~

## Estrutura

~~~text
src/dental_procurement_intelligence/  # namespace interno preservado por compatibilidade
  pncp/             cliente e modelos do PNCP
  ingestion/        evidência e captura
  identity/         taxonomia, identidade e qualidade
  evaluation/       benchmark e métricas de avaliação
  normalization/    texto, medidas e geografia
  analytics/        lakehouse, homologações, qualidade e sinais
  cli.py            interface de linha de comando

tests/
docs/
data/
~~~

## Rastreabilidade

A cadeia pretendida é:

`sinal → grupo comparável → homologação → item → contratação → SHA-256 → resposta original → PNCP`

A qualidade da normalização também permanece auditável por item.

## Roadmap

- [x] Estrutura inicial
- [x] Cliente PNCP
- [x] Evidência imutável com SHA-256
- [x] Product Identity Engine
- [x] Parquet e DuckDB
- [x] Preço normalizado
- [x] Resultados homologados
- [x] Dimensões geográfica e temporal
- [x] Sinais robustos de preço
- [x] Taxonomia odontológica ampliada
- [x] Concentração como atributo técnico crítico
- [x] Score determinístico de qualidade
- [x] Métricas de cobertura
- [x] Fila de itens não reconhecidos
- [x] Dataset de avaliação manual versionado
- [x] Benchmark de regressão com métricas por categoria
- [x] Criar amostra de validação independente e congelada
- [x] Executar baseline independente v2
- [x] Melhorar regras usando os erros do v2 sem alterar seus rótulos
- [x] Revalidar v1 sem regressão
- [x] Registrar desempenho pós-tuning do v2
- [x] Criar benchmark v3 com novas fontes ainda não vistas
- [x] Corrigir cálculo macro para classes previstas sem suporte
- [x] Corrigir os quatro erros do v3 sem alterar seus rótulos
- [x] Revalidar v1, v2 e v3 sem regressão
- [x] Registrar desempenho pós-tuning do v3
- [ ] Criar benchmark v4 com fontes ainda não vistas
- [ ] Extrair contrato formal de plugins de domínio
- [ ] Adicionar segunda vertical além de odontologia
- [ ] Modelar atributos técnicos específicos por categoria
- [ ] Adicionar recuperação semântica de candidatos
- [ ] FastAPI de evidências
- [ ] Dashboard React com mapa, séries e qualidade
- [ ] Relatório público de qualidade dos dados

## Princípios

1. A evidência de origem é imutável.
2. Toda transformação é reproduzível.
3. Regras de classificação são explícitas.
4. Ausência de informação não é tratada como confirmação.
5. A equivalência de produtos deve ser explicável.
6. O grupo de comparação deve ser explícito.
7. Qualidade e cobertura devem ser mensuradas.
8. Todo resultado analítico deve ser rastreável à fonte pública.
