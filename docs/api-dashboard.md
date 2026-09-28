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

- `GET /api/v1/products/discovery`
- `GET /api/v1/products/search?q=...`
- `GET /api/v1/products/{product_id}`
- `GET /api/v1/products/{product_id}/distribution`
- `GET /api/v1/products/{product_id}/history`
- `GET /api/v1/products/{product_id}/regions`
- `GET /api/v1/products/{product_id}/suppliers`
- `GET /api/v1/products/{product_id}/buyers`
- `GET /api/v1/products/{product_id}/signals`
- `GET /api/v1/products/{product_id}/records`
- `GET /api/v1/products/{product_id}/records.csv`

### Visões analíticas gerais

- `GET /api/v1/overview`
- `GET /api/v1/categories`
- `GET /api/v1/quality`
- `GET /api/v1/awards`
- `GET /api/v1/anomalies`
- `GET /api/v1/unrecognized`

## Descoberta guiada de produtos

`/api/v1/products/discovery` lista somente categorias presentes na base analítica publicada. Cada item informa o nome amigável, quantidade de identidades comparáveis, homologações e observações com preço defensável.

A interface usa essa resposta para mostrar atalhos clicáveis antes da pesquisa. Assim o usuário pode chegar a uma categoria sem conhecer a nomenclatura interna nem a forma exata usada no PNCP.

A busca também interpreta aliases comuns em português. Expressões como `adesivo odontológico`, `ionômero de vidro`, `resina flow`, `anestésico local` e `flúor` são resolvidas para a categoria correspondente antes de aplicar os demais termos da consulta.

Buscas genéricas continuam amplas. Por exemplo, `resina` não é forçada para uma única categoria.

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

A busca por produtos usa `limit` e `offset`, devolve o total de grupos compatíveis e permite navegação por páginas sem alterar a identidade do produto.

O parâmetro `sort` aceita:

- `coverage`: prioriza grupos com mais preços comparáveis;
- `procurements`: prioriza grupos com mais contratações;
- `latest`: prioriza grupos com observação mais recente;
- `name`: ordena pela identificação do produto.

As rotas de inteligência por produto aceitam os mesmos filtros opcionais:

- `state_code`: UF exata;
- `macroregion`: macrorregião;
- `supplier`: busca parcial por nome ou documento do fornecedor;
- `buyer`: busca parcial por órgão, CNPJ, unidade compradora ou código;
- `start_date`: data inicial inclusiva no formato `YYYY-MM-DD`;
- `end_date`: data final inclusiva no formato `YYYY-MM-DD`.

Os filtros são aplicados ao mesmo universo em resumo, distribuição, histórico, geografia, fornecedores, compradores, sinais e registros de evidência. Isso evita comparar números calculados sobre subconjuntos diferentes.

Todos os filtros são parametrizados e não interpolam entrada do usuário diretamente em SQL. A API rejeita intervalo em que `start_date` seja posterior a `end_date`.

## Exportação CSV

`/records.csv` usa o mesmo conjunto de filtros da análise e exporta todos os registros do recorte, percorrendo internamente as páginas necessárias.

O arquivo é entregue em UTF-8 com BOM e inclui identificadores da homologação, contratação, fornecedor, órgão comprador, localidade, valores, status da normalização, hashes de origem e link para o PNCP.

## URL compartilhável

A aplicação React serializa no endereço a pesquisa, filtros, ordenação, offset atual e `product_id` selecionado. Abrir essa URL reconstrói o mesmo recorte analítico e, quando houver produto selecionado, carrega diretamente a análise correspondente.

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
