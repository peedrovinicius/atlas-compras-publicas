# Dental Procurement Intelligence

Plataforma auditável de inteligência de dados para compras públicas odontológicas no Brasil.

O projeto constrói um pipeline reprodutível para coletar, normalizar, comparar e analisar itens odontológicos publicados no Portal Nacional de Contratações Públicas (PNCP). O desafio principal não é apenas calcular preços, mas determinar quando descrições pouco padronizadas representam produtos realmente comparáveis e qual contexto temporal e geográfico é adequado para cada comparação.

## Status atual

**v0.7.0 — contexto geográfico e temporal**

O repositório já inclui:

- pacote Python tipado;
- cliente para a API pública do PNCP;
- captura dos metadados da contratação;
- captura de todos os itens e resultados de uma contratação;
- armazenamento bruto endereçado por conteúdo com SHA-256;
- manifesto de proveniência e verificação de integridade;
- Product Identity Engine com decisão explicável;
- normalização de embalagem e quantidade física;
- transformação analítica em Parquet;
- catálogo SQL local com DuckDB;
- integração entre itens e resultados homologados;
- cálculo de valor estimado equivalente, valor homologado e economia;
- preço homologado por unidade física;
- município, código IBGE, UF e macrorregião;
- data de análise, ano e trimestre;
- esfera administrativa e modalidade da contratação;
- grupos comparáveis hierárquicos por local e período;
- detecção robusta com MAD e IQR;
- rastreabilidade do sinal estatístico até as evidências brutas.

O GitHub Actions permanece desativado nesta fase para evitar consumo desnecessário de minutos de CI.

## Fonte dos dados

A fonte principal é a API pública do PNCP:

`https://pncp.gov.br/api/pncp`

A consulta de uma contratação fornece, entre outros campos, data de publicação, órgão, esfera, unidade administrativa, município, código IBGE e UF.

O pipeline preserva a resposta original da contratação, a resposta dos itens e cada resposta de resultados como evidências independentes.

## Arquitetura

~~~mermaid
flowchart LR
    A[API PNCP] --> B[Evidência bruta SHA-256]
    B --> C[Validação estrutural]
    C --> D[Normalização de produto]
    D --> E[Preço por unidade física]
    E --> F[Contexto geográfico]
    F --> G[Contexto temporal]
    G --> H[Parquet + DuckDB]
    H --> I[Grupo comparável hierárquico]
    I --> J[MAD / IQR]
    J --> K[Sinal explicável]
    K --> L[API]
    L --> M[Dashboard]
~~~

## Contexto oficial da contratação

A v0.7.0 incorpora o endpoint de detalhe da contratação.

São preservados na camada analítica:

~~~text
data de publicação
data do resultado
data usada na análise
ano
trimestre
município
código IBGE
UF
macrorregião
esfera administrativa
modalidade
SHA-256 da contratação
SHA-256 dos itens
SHA-256 dos resultados
~~~

A data do resultado homologado é utilizada como referência temporal quando disponível. Na ausência dela, utiliza-se a data de publicação da contratação.

A macrorregião é derivada deterministicamente da UF.

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

Diferenças relevantes de categoria, apresentação, cor ou quantidade podem impedir que dois registros sejam comparados.

## Preço normalizado

~~~text
Preço homologado: R$ 72,00
Embalagem: 2 seringas
Conteúdo por seringa: 4 g
Conteúdo total: 8 g

Preço homologado normalizado: R$ 9,00/g
~~~

Massa e volume permanecem dimensões distintas.

## Grupos comparáveis hierárquicos

A v0.7.0 deixa de utilizar um único recorte geográfico.

Para cada registro, o sistema tenta encontrar o grupo mais específico com pelo menos cinco observações:

~~~text
1. mesma UF + mesmo trimestre
2. mesma macrorregião + mesmo trimestre
3. Brasil + mesmo trimestre
4. mesma macrorregião + mesmo ano
5. Brasil + mesmo ano
~~~

Se nenhum nível atingir a amostra mínima, nenhum sinal é gerado.

A escolha do escopo fica registrada em:

- `comparison_scope`;
- `comparison_geography`;
- `comparison_period`;
- `group_size`.

Isso permite auditar exatamente contra qual população um preço foi comparado.

## Sinais robustos de preço

Quando o MAD é maior que zero:

`modified z-score = 0,67448975 × (preço - mediana) / MAD`

Limite padrão:

`|modified z-score| >= 3,5`

Quando o MAD é zero e existe dispersão interquartil, utiliza-se IQR como fallback.

Um sinal estatístico não constitui evidência de fraude, corrupção, superfaturamento jurídico ou irregularidade administrativa.

## Fluxo principal

~~~text
capture-contract
        ↓
contratação + itens + resultados brutos
        ↓
build-analytics
        ↓
build-awards --contract-raw ...
        ↓
detect-anomalies
        ↓
anomalies-summary
~~~

## Exemplos

Consultar metadados da contratação:

~~~bash
dpi contract --cnpj 10000000000003 --year 2021 --sequence 1
~~~

Capturar toda a contratação:

~~~bash
dpi capture-contract \
  --cnpj 10000000000003 \
  --year 2021 \
  --sequence 1
~~~

Construir homologações com contexto:

~~~bash
dpi build-awards \
  --contract-raw data/raw/objects/sha256/xx/contratacao.json \
  --items-raw data/raw/objects/sha256/yy/itens.json \
  --results-raw data/raw/objects/sha256/zz/resultado-1.json \
  --parquet data/silver/awards.parquet \
  --database data/analytics.duckdb
~~~

Detectar preços atípicos:

~~~bash
dpi detect-anomalies --database data/analytics.duckdb
~~~

## Estrutura do repositório

~~~text
src/dental_procurement_intelligence/
  pncp/             cliente PNCP e modelos tipados
  ingestion/        evidência bruta e captura completa
  identity/         identidade canônica e comparabilidade
  normalization/    texto, medidas e geografia
  analytics/        Parquet, DuckDB, homologações e sinais
  cli.py            interface de linha de comando

tests/              testes automatizados
docs/               arquitetura e metodologia
data/               contrato das camadas locais
~~~

## Rastreabilidade

A cadeia pretendida é:

`sinal → escopo comparável → homologação → item → contratação → SHA-256 → resposta original → PNCP`

## Roadmap

- [x] Estrutura inicial
- [x] Cliente PNCP
- [x] Normalização textual e de medidas
- [x] Ingestão bruta com SHA-256
- [x] Product Identity Engine — baseline
- [x] Parquet e DuckDB
- [x] Preço normalizado por unidade física
- [x] Resultados homologados
- [x] Estimado x homologado
- [x] Captura automática da contratação
- [x] Sinais robustos de preço — baseline
- [x] Dimensão geográfica
- [x] Dimensão temporal
- [x] Grupos comparáveis hierárquicos
- [ ] Expandir taxonomia odontológica
- [ ] Modelar atributos técnicos por categoria
- [ ] Adicionar recuperação semântica de candidatos
- [ ] Medir cobertura e qualidade do normalizador
- [ ] FastAPI de evidências
- [ ] Dashboard React com mapa e séries temporais
- [ ] Relatório público de qualidade dos dados

## Princípios

1. A evidência de origem é imutável.
2. Toda transformação deve ser reproduzível.
3. A equivalência de produtos deve ser explicável.
4. O grupo de comparação deve ser explícito.
5. Preços só podem ser comparados dentro de grupos defensáveis.
6. Ausência e incerteza permanecem explícitas.
7. Todo resultado analítico deve ser rastreável à fonte pública.
