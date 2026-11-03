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

## Identidade do cliente e limite de normalização (PR #78)

A API aplica um limite de 60 normalizações por 60 segundos, mantendo contadores **em memória por
instância**. O código usa `request.client.host` do escopo ASGI e não interpreta diretamente
`X-Forwarded-For`. Isso evita confiar em cabeçalhos do usuário *dentro da aplicação*, mas
**não basta para garantir uma identidade segura em produção**: o Uvicorn pode alterar o
endereço do escopo ASGI quando recebe cabeçalhos de um proxy configurado como confiável.

Antes de integrar ou publicar uma alteração no limitador:

1. Conferir o comando efetivo de inicialização do serviço `atlas-compras-publicas-analytics`
   no painel do Render, além da definição versionada em `render.yaml`.
2. Conferir o valor efetivo de `FORWARDED_ALLOW_IPS` e as opções
   `--proxy-headers` / `--forwarded-allow-ips` do Uvicorn. A confiança irrestrita
   (`*`) **não é segura por padrão**; só pode ser adotada se toda conexão vier de
   um proxy confiável que remova ou sobrescreva valores potencialmente falsificados.
3. Verificar, em ambiente controlado e sem registrar endereços IP brutos em logs públicos,
   se requisições da mesma origem com `X-Forwarded-For` falsificado compartilham
   o limite e se duas origens legítimas não dividem indevidamente o mesmo contador.
4. Se o servidor enxergar somente o IP do balanceador, corrigir a resolução do cliente
   pela camada de proxy confiável **antes** de chamar o rate limiting de "por usuário".
   Não tentar resolver isso lendo o primeiro IP de `X-Forwarded-For` na rota.
5. Se o serviço ganhar múltiplas instâncias ou workers, substituir os contadores locais
   por armazenamento distribuído com expiração e limites definidos. Mesmo com um só
   processo, a cardinalidade de clientes em memória exige monitoramento.

Referências operacionais:
[Uvicorn — proxies confiáveis](https://uvicorn.dev/deployment/),
[Uvicorn — parâmetros](https://uvicorn.dev/settings/) e
[Render — tráfego e rate limiting](https://render.com/articles/how-render-handles-ddos-attacks/).

Os testes de `tests/test_api_app.py` cobrem falsificação de cabeçalho no TestClient
e isolamento de dois endereços ASGI sintéticos. **Esses testes não inspecionam a
configuração do proxy real do Render.**

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
