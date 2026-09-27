# API e dashboard analítico

## Objetivo

Expor as camadas analíticas já existentes do Atlas sem duplicar regra de negócio.

A API e o dashboard usam a mesma camada de serviço sobre o DuckDB.

## Instalação da API

~~~bash
pip install -e ".[api]"
~~~

## Iniciar a API

~~~bash
dpi serve-api --database data/analytics.duckdb --host 127.0.0.1 --port 8000
~~~

Rotas v1:

- `GET /health`
- `GET /api/v1/domains`
- `GET /api/v1/overview`
- `GET /api/v1/categories`
- `GET /api/v1/quality`
- `GET /api/v1/awards`
- `GET /api/v1/anomalies`
- `GET /api/v1/unrecognized?limit=50`

A documentação OpenAPI é fornecida pelo FastAPI quando a API está em execução.

## Paginação e filtros

As coleções usam o envelope:

~~~json
{
  "items": [],
  "total": 0,
  "limit": 50,
  "offset": 0
}
~~~

Parâmetros comuns:

- `limit`: 1 a 500;
- `offset`: posição inicial, maior ou igual a zero.

Filtros disponíveis:

- `/api/v1/categories`: `category`;
- `/api/v1/awards`: `category`, `macroregion`, `year`;
- `/api/v1/anomalies`: `category`, `scope`;
- `/api/v1/unrecognized`: paginação por `limit` e `offset`.

Exemplo:

~~~text
/api/v1/awards?category=composite_resin&macroregion=Nordeste&year=2026&limit=25&offset=0
~~~

Os filtros são aplicados sem interpolação de entrada do usuário em SQL.

## Dashboard HTML

Gerar um snapshot:

~~~bash
dpi build-dashboard \
  --database data/analytics.duckdb \
  --output docs/dashboard.html
~~~

O arquivo gerado é autocontido e apresenta:

- total de itens;
- categorias identificadas;
- itens totalmente estruturados;
- qualidade média de normalização;
- preços normalizados por categoria;
- homologações e economia, quando disponíveis;
- sinais estatísticos, quando disponíveis;
- status dos domínios do motor de identidade.

## Fonte de verdade

O dashboard não possui números codificados no HTML.

Cada execução lê o DuckDB informado e gera o snapshot a partir das mesmas funções usadas pela API e pela CLI analítica.

## Segurança interpretativa

Os sinais estatísticos exibidos pelo dashboard são indicadores para priorização analítica.

Eles não constituem prova de fraude, sobrepreço, irregularidade ou responsabilidade de qualquer agente.

## Dependências

FastAPI e Uvicorn ficam no extra opcional `api`.

A geração estática do dashboard usa somente dependências já presentes no pacote base.

## Snapshot publicado

Enquanto ainda não existe um DuckDB consolidado versionado, o repositório publica
um snapshot metodológico real em:

- `docs/dashboard-quality-snapshot.html`;
- `docs/assets/dashboard-quality-snapshot.svg`;
- `docs/dashboard-quality-snapshot.json`.

Ele usa exclusivamente baselines congeladas do próprio projeto e não preenche
painéis de preços com dados fictícios.

## Próximas melhorias

- endpoint de contratação/item;
- gráficos interativos com dados reais;
- publicação automatizada do snapshot;
- autenticação quando houver implantação pública com operações não somente leitura.
