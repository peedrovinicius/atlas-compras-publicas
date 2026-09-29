# Deploy no Render

Este documento descreve a configuração canônica de produção do Atlas de Compras Públicas.

## Arquitetura canônica

A produção usa somente dois serviços definidos em `render.yaml`:

1. `atlas-compras-publicas-web`
   - tipo: Static Site
   - origem: branch `main`
   - build: `cd web && npm install --no-audit --no-fund && npm run build`
   - publish path: `web/dist`

2. `atlas-compras-publicas-analytics`
   - tipo: Web Service
   - runtime: Python
   - origem: branch `main`
   - build: `pip install -e ".[api]" && atlas build-demo-data --output-root data/demo`
   - start: `uvicorn "dental_procurement_intelligence.api.app:create_app" --factory --host 0.0.0.0 --port $PORT`
   - readiness: `/ready`

Serviços criados manualmente fora desse Blueprint não fazem parte da arquitetura oficial.

## Fluxo de release

O desenvolvimento não deve ocorrer diretamente na `main`.

Fluxo:

1. implementar na branch `develop`;
2. aguardar a CI completa;
3. abrir ou atualizar Pull Request para `main`;
4. confirmar o check `quality`;
5. consolidar versão, changelog e release notes;
6. fazer um único merge para `main`;
7. aguardar o deploy dos dois serviços canônicos;
8. validar produção.

Esse fluxo evita que cada commit incremental consuma um build de produção.

## Auto deploy

A configuração declarada no repositório usa:

```yaml
autoDeployTrigger: checksPass
```

O objetivo é que o Render só publique depois dos checks associados à mudança terem sido aprovados.

Se o painel do Render mostrar auto deploy por `commit`, a configuração do serviço está divergente do Blueprint e deve ser corrigida no painel antes da próxima release.

## Serviços duplicados

Se existirem serviços adicionais ligados ao mesmo repositório, confirme se são usados antes de removê-los.

Na auditoria de 29/09/2026 foram identificados como duplicados:

- `atlas-compras-publicas-api`;
- `atlas-compras-publicas`.

Os serviços canônicos permanecem:

- `atlas-compras-publicas-web`;
- `atlas-compras-publicas-analytics`.

## Limite de build

Quando o Render registrar:

`Build canceled: your workspace has run out of build pipeline minutes for the current billing period.`

não se trata de falha do código.

Nesse estado:

- não repetir deploys;
- não enviar commits incrementais para `main`;
- continuar o trabalho em `develop`;
- usar GitHub Actions como validação;
- restaurar a capacidade de build do workspace antes da próxima publicação.

## Validação pós-deploy

Depois de cada release, verificar:

- frontend público carrega sem erro;
- busca do Explorador responde;
- detalhes de produto carregam;
- P25, mediana e P75 aparecem corretamente;
- comparação lado a lado funciona apenas para grupos compatíveis;
- `Preço que recebi` calcula a posição sem produzir conclusão normativa;
- relatório imprimível/PDF abre corretamente;
- `/health` responde;
- `/ready` confirma disponibilidade do DuckDB;
- links de evidência para o PNCP continuam acessíveis.

## Regra operacional

Um merge na `main` deve representar uma mudança pronta para produção.

A `main` não deve ser usada como branch de trabalho.
