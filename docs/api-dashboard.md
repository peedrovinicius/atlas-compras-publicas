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

## Próximas melhorias

- paginação e filtros da API;
- endpoint de contratação/item;
- gráficos interativos com dados reais;
- publicação automatizada do snapshot;
- autenticação quando houver implantação pública com operações não somente leitura.
