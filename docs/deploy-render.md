# Deploy no Render

Este documento descreve a configuração canônica de produção do Atlas de Compras Públicas.

## Arquitetura canônica

A produção usa somente dois serviços definidos em `render.yaml`:

1. `atlas-compras-publicas-web`
   - tipo: Static Site
   - origem: branch `main`
   - build: `cd web && npm ci --no-audit --no-fund && npm run build`
   - publish path: `web/dist`

2. `atlas-compras-publicas-analytics`
   - tipo: Web Service
   - runtime: Python
   - origem: branch `main`
   - build: `pip install -e ".[api]" && atlas build-demo-data --output-root data/demo --offline-fallback`
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

## Proveniência dos dados publicados

A geração da base analítica no Blueprint utiliza `--offline-fallback`. Se a coleta de
contratações e resultados do PNCP falhar ou for insuficiente, o gerador poderá usar
a amostra **inteiramente sintética** de `analytics/demo_data.py` para manter a demo
disponível. Esse comportamento **não prova que o deploy publicado contenha preços
homologados reais**.

Antes de afirmar que um resultado apresentado no site veio do PNCP:

1. inspecionar o resultado e os manifestos da captura no build da versão publicada;
2. verificar se as chaves de contratos e os hashes representam a amostra PNCP esperada;
3. identificar uso de `offline-seed` ou de `Fornecedor demonstrativo`, que caracteriza
   dados fictícios;
4. registrar a origem e a data de reconstrução no relatório de release;
5. não apresentar dados sintéticos como preços reais de compras homologadas.

A aplicação ainda precisa de um indicador automatizado e visível de proveniência
na API e no frontend, registrado na issue
[#77](https://github.com/peedrovinicius/atlas-compras-publicas/issues/77).
Até a implementação, a inspeção manual é uma etapa obrigatória da publicação.

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
   processo, monitorar o limite de 4.096 clientes ativos por janela, a limpeza de
   entradas expiradas e possíveis respostas 429 quando a capacidade é atingida.
   Essa proteção limita memória, mas não impede esgotamento deliberado de cotas
   por requisições de origens variadas.

Referências operacionais:
[Uvicorn — proxies confiáveis](https://uvicorn.dev/deployment/),
[Uvicorn — parâmetros](https://uvicorn.dev/settings/) e
[Render — tráfego e rate limiting](https://render.com/articles/how-render-handles-ddos-attacks/).

Os testes de `tests/test_api_app.py` cobrem falsificação de cabeçalho no TestClient
e isolamento de dois endereços ASGI sintéticos. **Esses testes não inspecionam a
configuração do proxy real do Render.**

### Verificação do Render em 03/11/2026

No workspace `My Workspace`, o serviço canônico `atlas-compras-publicas-analytics`
estava ligado à `main` com **uma instância**, `autoDeployTrigger: checksPass`,
e o comando `uvicorn ... --factory --host 0.0.0.0 --port $PORT`.
Na tela de Environment fornecida pelo proprietário, **não aparecia**
`FORWARDED_ALLOW_IPS` entre as variáveis personalizadas. Entretanto,
[a documentação oficial do Render](https://render.com/docs/environment-variables)
registra o valor padrão `FORWARDED_ALLOW_IPS=*` no runtime Python 3.
Portanto, a tela não prova que Uvicorn use somente `127.0.0.1` e `::1`.
A configuração efetiva precisa ser confirmada no processo.
O Render informa que o tráfego público chega via Cloudflare e balanceadores;
portanto **a identidade real do visitante não foi demonstrada em produção**:
a origem do socket vista pelo Uvicorn e a integridade da cadeia `X-Forwarded-For`
ainda precisam ser verificadas em um ambiente controlado.

Os dois novos testes reproduzem casos com `ProxyHeadersMiddleware` real
do Uvicorn: cadeia sintética com dois proxies permitidos, prefixo falsificado,
identidades distintas e rejeição de cabeçalhos vindos de peer não autorizado.
Esses testes asseguram o contrato do middleware nessa topologia sintética,
**não** certificam quais IPs ou cabeçalhos o Render utiliza.

O Render documenta `FORWARDED_ALLOW_IPS=*` como padrão do runtime Python.
Não presumir que a variável esteja ausente no processo só porque não aparece
na tela de configuração. Antes do merge e do deploy, confirmar o comportamento
da cadeia de proxies e dos cabeçalhos encaminhados, definir uma política
compatível de confiança e testar a separação das cotas entre visitantes,
sem expor IPs reais em logs públicos. Se a plataforma não permitir essa
garantia, registrar a limitação e escolher um limitador por identidade autenticada
ou uma solução de borda gerenciada, em vez de confiar em cabeçalhos arbitrários.

### Experimento HTTP local com Uvicorn real

A suíte `tests/test_proxy_http_transport.py` abre um socket **somente em
`127.0.0.1`**, inicia o próprio Uvicorn em uma thread temporária, executa
requisições HTTP usando `httpx` e encerra o servidor ao final.
Os testes verificam três cenários reproduzíveis:

- **Peer não confiável:** variar o cabeçalho forjado não evita o HTTP 429;
- **Dois proxies explicitamente confiáveis:** prefixos falsos são ignorados,
  uma origem atinge HTTP 429 e outra origem preserva sua cota;
- **Contraprova com `*`:** o Uvicorn aceita como cliente o primeiro endereço
  falsificável da cadeia, demonstrando por que não adotar confiança irrestrita.

Não são feitas requisições ao Render. Nenhum IP real de usuário é coletado.
Mesmo com esses testes aprovados, **a identidade dos visitantes no Render
continua não comprovada** até verificar os peers reais e a integridade da
cadeia de encaminhamento no ambiente de hospedagem.

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
- proveniência da base publicada confirmada (PNCP versus fallback sintético);
- links de evidência para o PNCP continuam acessíveis.

## Regra operacional

Um merge na `main` deve representar uma mudança pronta para produção.

A `main` não deve ser usada como branch de trabalho.
