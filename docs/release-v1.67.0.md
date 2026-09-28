# Release v1.67.0

A v1.67.0 endurece o deploy público do Atlas depois da falha de banco analítico observada em produção.

## Readiness real

O endpoint `/health` continua indicando que o processo FastAPI está vivo.

O novo endpoint `/ready` verifica se:

- o arquivo DuckDB configurado existe;
- o arquivo pode ser aberto em modo somente leitura;
- a tabela analítica `silver_awards` está disponível.

Quando essas condições não são atendidas, `/ready` responde HTTP 503. Isso impede que uma instância sem banco analítico seja considerada pronta para receber tráfego.

## Blueprint canônico

O repositório passa a incluir `render.yaml` com apenas os dois componentes públicos oficiais:

1. `atlas-compras-publicas-analytics`;
2. `atlas-compras-publicas-web`.

A API usa `/ready` como health check de deploy.

O Blueprint também registra Python 3.12.11, `data/demo/atlas-demo.duckdb` como base publicada, amostragem limitada no PNCP e frontend apontado para a API analítica oficial.

## Separação entre liveness e readiness

`/health` diagnostica o processo HTTP.

`/ready` é o contrato de produção usado para decidir se o Explorador de preços pode receber tráfego.

## Render

A configuração canônica evita documentar ou recriar APIs paralelas. Serviços antigos já existentes no workspace não são removidos automaticamente pelo Blueprint e precisam ser desativados manualmente no Dashboard.

## Validação

A release adiciona testes para banco ausente e DuckDB válido com a tabela analítica exigida.
