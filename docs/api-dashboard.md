# API e aplicação analítica

## Objetivo

Expor a camada analítica do Atlas sem duplicar regra de negócio entre CLI, API e interface pública.

A API e o frontend consultam a mesma base DuckDB e usam as mesmas identidades de produto, critérios de normalização de preço e regras de rastreabilidade.

## Instalação da API

~~~bash
pip install -e ".[api]"
~~~

## Iniciar a API

~~~bash
atlas serve-api --database data/analytics.duckdb --host 127.0.0.1 --port 8000
~~~

A documentação OpenAPI é fornecida pelo FastAPI em `/docs`.

## Rotas principais

### Sistema e normalização

- `GET /health`
- `GET /api/v1/meta`
- `GET /api/v1/domains`
- `GET /api/v1/parser/categories`
- `GET /api/v1/normalize?description=...`
- `POST /api/v1/normalize/batch`

### Inteligência por produto

- `GET /api/v1/products/search?q=...`
- `GET /api/v1/products/{product_id}`
- `GET /api/v1/products/{product_id}/distribution`
- `GET /api/v1/products/{product_id}/history`
- `GET /api/v1/products/{product_id}/regions`
- `GET /api/v1/products/{product_id}/suppliers`
- `GET /api/v1/products/{product_id}/buyers`
- `GET /api/v1/products/{product_id}/signals`
- `GET /api/v1/products/{product_id}/records`

### Visões analíticas gerais

- `GET /api/v1/overview`
- `GET /api/v1/categories`
- `GET /api/v1/quality`
- `GET /api/v1/awards`
- `GET /api/v1/anomalies`
- `GET /api/v1/unrecognized`

## Pesquisa e identidade de produto

A busca pública opera sobre produtos já normalizados e exclui a categoria `unknown`.

Cada resultado recebe um `product_id` determinístico calculado a partir dos campos que definem a identidade comparável. A interface usa esse identificador para abrir as demais visões analíticas sem reconstruir regras no frontend.

A pesquisa retorna, entre outros campos:

- nome de exibição;
- descrição de exemplo;
- quantidade de homologações;
- quantidade de contratações;
- fornecedores distintos;
- UFs observadas;
- quantidade de observações com preço normalizado defensável.

## Resumo de preços

O endpoint de produto consolida estatísticas somente sobre observações cujo preço por unidade física foi considerado defensável.

A resposta inclui:

- mediana;
- média;
- mínimo e máximo;
- percentis 25 e 75;
- desvio padrão;
- quantidade física agregada;
- número de observações de preço;
- período coberto;
- indicador `sample_sufficient`.

A interface apresenta aviso quando a amostra fica abaixo do mínimo metodológico informado pela própria API.

## Distribuição de preços

`/distribution` considera somente observações com preço físico normalizado classificado como `defensible`. A rota divide a faixa entre mínimo e máximo em intervalos de largura uniforme e retorna a contagem por faixa.

O parâmetro `bins` aceita valores entre 5 e 40 e usa 10 por padrão. Quando todos os preços são iguais, a resposta retorna uma única faixa.

A visualização pública usa esses intervalos para mostrar a forma da distribuição sem recalcular preços no frontend.

## Histórico e geografia

`/history` agrupa por mês e expõe mediana, média, percentis, mínimo, máximo e volume de observações.

`/regions` fornece referência nacional, agregação por macrorregião e comparação por UF. A diferença percentual por estado é calculada em relação à mediana nacional do mesmo produto comparável.

## Fornecedores e órgãos compradores

`/suppliers` resume presença na amostra, contratações e mediana de preço por fornecedor.

`/buyers` resume órgãos e unidades compradoras, quantidade de contratações, valor homologado e mediana observada.

Essas visões são descritivas. Elas não atribuem qualidade, responsabilidade ou irregularidade a fornecedores ou órgãos públicos.

## Sinais estatísticos

`/signals` expõe registros marcados pela camada `gold_price_signals`, incluindo contexto de comparação, tamanho do grupo, quartis, MAD, z-score modificado quando disponível e método utilizado.

A resposta inclui obrigatoriamente o aviso interpretativo de que distância estatística não constitui prova de irregularidade.

## Rastreabilidade

`/records` retorna os registros que sustentam a análise do produto, incluindo:

- contratação e item;
- descrição original;
- fornecedor;
- órgão e unidade compradora;
- localidade e modalidade;
- valores homologados;
- status e motivo da normalização do preço;
- SHA-256 da contratação, item e resultado;
- link correspondente no PNCP quando reconstruível.

A cadeia de auditoria permanece:

~~~text
análise -> produto comparável -> homologação -> item -> contratação -> SHA-256 -> evidência original -> PNCP
~~~

## Aplicação React

A aplicação pública possui duas áreas.

### Explorar preços

É a experiência principal. Faz pesquisa por produto e apresenta resumo, distribuição de preços, histórico, geografia, fornecedores, órgãos compradores, sinais e cartões de evidência rastreáveis.

### Laboratório

Mantém o parser interativo. O usuário pode inserir até 20 descrições ou clicar nas categorias publicadas para executar um exemplo automaticamente e inspecionar a saída técnica.

O frontend não contém números analíticos codificados. Os resultados vêm da API.

## Paginação e filtros

Coleções paginadas usam `limit` e `offset`. Os limites máximos variam conforme a rota e são validados pela API.

Os filtros são parametrizados e não interpolam entrada do usuário diretamente em SQL.

## Dashboard HTML estático

O snapshot HTML continua disponível para inspeção metodológica e pode ser gerado com:

~~~bash
atlas build-dashboard \
  --database data/analytics.duckdb \
  --output docs/dashboard.html
~~~

A aplicação React não substitui esse artefato. O snapshot continua útil para reprodução local e documentação de qualidade.

## Segurança interpretativa

Os sinais estatísticos são instrumentos de priorização analítica.

Eles não constituem prova de fraude, sobrepreço, irregularidade ou responsabilidade de qualquer agente.

A cobertura da aplicação pública corresponde à base analítica publicada e não deve ser interpretada como cobertura integral do PNCP.
