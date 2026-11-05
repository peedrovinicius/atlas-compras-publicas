# Release coordenado do limitador de IP no Render — PR #78

> **Estado: PLANEJAMENTO / NÃO AUTORIZADO PARA PUBLICAÇÃO.** Aplicável somente à API `atlas-compras-publicas-analytics` no Render **Free, uma instância, sem ingresso privado**, verificada em 04/11/2026. Este documento não altera a configuração do Render; não autoriza merge, deploy ou testes de carga na produção.

## Por que a ordem é crítica

A versão atualmente publicada (`main`, commit `37af797`) ainda utiliza `X-Forwarded-For` como chave de rate limit. O PR #78 corrige isso, mas no Render a nova implementação tem **dois modos distintos**:

| `ATLAS_TRUST_CF_CONNECTING_IP` | Efeito do PR #78 no Render |
| --- | --- |
| ausente / `false` | Todas as origens compartilham **60 normalizações a cada 60 s por instância**. Não publicar este modo como solução definitiva: pode bloquear usuários legítimos. |
| `true` | Usa um `CF-Connecting-IP` canônico para aplicar 60/60s **por visitante e por instância**, rejeitando header ausente, duplicado ou inválido com HTTP 400. Depende de ingresso público confiável. |

**Não usar `X-Forwarded-For` como identidade.** O Render declarou por e-mail que o Cloudflare rejeita requisições públicas nas quais o cliente envia `CF-Connecting-IP`; no plano Free o web service não recebe conexões privadas, mas essa garantia de isolamento precisa ser reavaliada antes de qualquer mudança de plano/topologia.

### Evidência obtida antes do release

- Staging isolado `srv-dbls24l9el5s73ek6rk0`, com `ATLAS_TRUST_CF_CONNECTING_IP=true`, `autoDeployTrigger=off` e banco somente sintético.
- [Smoke com árvore combinada `a0005ad9`](https://github.com/peedrovinicius/atlas-compras-publicas/actions/runs/41941772404): `offline_synthetic` (1 compra, 12 resultados, 12 observações); origem A **60 HTTP 200 + 1 HTTP 429** variando XFF; origem B com IP público distinto **HTTP 200** em 11,9 s; header CF fornecido manualmente **HTTP 403**.
- O 403 é compatível com rejeição na borda, mas o status isolado não identifica conclusivamente qual componente gerou a resposta.
- CI e CodeQL do head `8fed213b` aprovados. Revalidar qualquer novo head antes de decidir pela publicação.
- Serviço canônico ligado à `main`, `autoDeployTrigger=checksPass`, plano Free e uma instância.
- **Divergência de health check:** `render.yaml` declara `healthCheckPath: /ready`, mas o serviço ativo tem caminho vazio (verificação TCP padrão). Não presumir aplicação automática do Blueprint ao serviço ativo.

## Etapa A — Preparar sem publicar

- [ ] Confirmar novamente no Render: nome e ID `srv-dat74p17lnhs73bu6u7g`, plano **Free**, região Virginia, somente uma instância, ausência de tráfego privado de ingresso, branch `main` e trigger de deploy `checksPass`.
- [ ] Confirmar ausência de deploy concorrente, disponibilidade de minutos/build e janela controlada; **congelar outros merges na `main`** até o release.
- [ ] Revisar/autorizar separadamente os PRs #78 (segurança) e #82 (versionamento v1.75.0) e integrá-los na `develop` somente após aprovação expressa.
- [ ] Abrir/revisar PR final `develop` → `main`, manter **draft** até CI, CodeQL, revisão dos 13 arquivos de segurança, release notes e contrato de versão estarem aprovados.
- [ ] Conferir no Dashboard do Render o comando de build real e `/ready`; **não alterar o health check sem verificar os efeitos operacionais**. Preferir caminho HTTP `/ready` antes da publicação, pois TCP não comprova o estado do banco analítico.
- [ ] Registrar o **último deploy estável da API e do frontend** e a versão de origem; confirmar plano de rollback e acesso ao Dashboard.

## Etapa B — Armar a configuração sem disparar deploy

**Exige autorização explícita de alteração de configuração de produção.** O conector disponível do Render não expõe a escolha `Save only`; **não usar** a ação de atualização de env vars para esta etapa, pois não há garantia de que ela evitará um deploy.

No Dashboard Render:

1. Abrir o serviço canônico [atlas-compras-publicas-analytics](https://dashboard.render.com/web/srv-dat74p17lnhs73bu6u7g), **não o staging**.
2. Abrir **Environment → Add Environment Variable**.
3. Definir **somente** `ATLAS_TRUST_CF_CONNECTING_IP=true`. Preservar todas as variáveis preexistentes.
4. Selecionar no menu **Save only**, **não** `Save and deploy` nem `Save, rebuild, and deploy`.
5. Verificar visualmente a variável salva, o tipo de operação e que **nenhum novo deploy** foi iniciado. Registrar a confirmação na checklist do release.

O Render confirma que *Save only* armazena o valor para o **próximo deploy**, sem aplicar ao processo em execução: https://render.com/docs/configure-environment-variables

**Cuidado:** se ocorrer qualquer deploy enquanto a configuração está armada, o valor salvo será aplicado naquele deploy, mesmo que não seja o release planejado. Não considerar a etapa B uma autorização para publicar. O código atualmente em `main` não lê a flag; contudo, sua versão antiga continua com o problema de `X-Forwarded-For` até que seja corrigida por um release autorizado.

## Etapa C — Merge/publicação, somente mediante aprovação

- [ ] Confirmar por segunda vez o estado `Save only`, o serviço correto, o plano Free, `main`, o número do PR final e o commit aprovado.
- [ ] Confirmar que a configuração ativa do Render tem um caminho de readiness apropriado (`/ready`) ou registrar o bloqueio e resolvê-lo antes de continuar.
- [ ] Confirmar CI e CodeQL **no commit final** do PR de release; nenhuma revisão pendente nem mudança nova.
- [ ] Obter **autorização expressa** de merge em `main` e do deploy que esse merge disparará nos serviços canônicos.
- [ ] Executar **um único merge** do release; não disparar deploy manual concorrente. O Render usa `checksPass` e poderá iniciar automaticamente API e frontend.
- [ ] Esperar ambos os serviços ficarem `live`, verificar SHAs e versão publicada e inspecionar erros de inicialização sem armazenar IPs reais em logs públicos.

## Etapa D — Smoke de produção de baixo impacto

- [ ] `/health`, `/ready` e `/api/v1/meta` com status esperado e versionamento coerente; `provenance.source_type` deve ser `pncp_sample` ou `offline_synthetic`, **nunca** tratar `unknown` como real.
- [ ] Conferir no frontend o aviso de proveniência, CSV com `data_source_type`, PDF/relatório e links de evidência.
- [ ] Uma normalização comum de teste deve devolver HTTP 200. **Não executar o ensaio de 61 chamadas nem provocar 429 deliberadamente na produção**; esse cenário foi validado no staging.
- [ ] Inspecionar métricas/logs agregados de 400/429 e disponibilidade, sem divulgar IPs ou cabeçalhos de visitantes.
- [ ] Rodar o workflow manual `Production smoke test` e vincular suas evidências ao PR/issue.

## Etapa E — Reversão se algo falhar

- Se ocorrer erro crítico ou bloquear usuários legítimos, **interromper novos merges** e usar o [Dashboard → API → Deploys → Rollback](https://render.com/docs/rollbacks) para recuperar um deploy anterior conhecido como estável. O rollback pelo Dashboard desativa o auto-deploy; confirmar isso antes de retomar a publicação.
- O rollback **não restaura automaticamente todas as variáveis atuais**. Conferir a configuração, inclusive `ATLAS_TRUST_CF_CONNECTING_IP`, antes de qualquer deploy seguinte.
- Voltar ao commit anterior **reintroduz temporariamente** o risco do rate limiter baseado em `X-Forwarded-For`. Registrar o incidente e corrigir antes de novo release.
- Em eventual upgrade para plano que receba tráfego privado, **não manter confiança indistinta em `CF-Connecting-IP`**; desabilitar a flag ou autenticar/distinguir o ingresso antes da mudança de topologia.

## Bloqueios ainda abertos

- [ ] Preparação coordenada `Save only` ainda **não executada** em produção.
- [ ] Health check HTTP `/ready` ainda **não configurado** no serviço canônico observado.
- [ ] PRs #78 e #82 ainda não integrados na `develop`.
- [ ] PR final para `main`, revisão global, CI/CodeQL e autorização de publicação pendentes.
- [ ] Smoke de produção pendente (não substituir por evidência de staging).

**Regra:** nenhum merge ou deploy de produção se algum bloqueio relevante permanecer sem decisão explicitamente aprovada.
