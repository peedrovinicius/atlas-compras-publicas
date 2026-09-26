# Dental Procurement Intelligence

Plataforma auditável de inteligência de dados para compras públicas odontológicas no Brasil.

O projeto constrói um pipeline reprodutível para coletar, normalizar, comparar e analisar itens odontológicos publicados no Portal Nacional de Contratações Públicas (PNCP). O desafio principal não é apenas calcular preços, mas determinar quando descrições pouco padronizadas representam produtos realmente comparáveis, medir a qualidade dessa normalização e deixar explícito quando o sistema ainda não possui evidência suficiente.

## Status atual

**v0.8.0 — taxonomia ampliada e qualidade do normalizador**

O repositório já inclui:

- cliente tipado para a API pública do PNCP;
- captura auditável da contratação, itens e resultados;
- armazenamento bruto com SHA-256 e manifestos de proveniência;
- normalização textual, de massa e de volume;
- Product Identity Engine explicável;
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
- fila auditável de itens ainda não reconhecidos.

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
    C --> D[Normalização odontológica]
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

## Taxonomia odontológica

A v0.8.0 expande a classificação determinística para categorias que aparecem de forma recorrente em compras odontológicas.

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

- `high` — score alto e estrutura mínima completa;
- `medium` — informação útil, mas existe alguma lacuna relevante;
- `low` — estrutura insuficiente para confiar na normalização.

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
src/dental_procurement_intelligence/
  pncp/             cliente e modelos do PNCP
  ingestion/        evidência e captura
  identity/         taxonomia, identidade e qualidade
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
- [ ] Validar taxonomia contra uma amostra real maior
- [ ] Modelar atributos técnicos específicos por categoria
- [ ] Adicionar recuperação semântica de candidatos
- [ ] Criar dataset de avaliação manual versionado
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
