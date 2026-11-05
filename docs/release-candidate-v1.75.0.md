# Release candidata v1.75.0

## Identificação

- versão: `1.75.0`;
- branch de integração: `develop`;
- destino: `main`;
- Pull Request de produção: [#83](https://github.com/peedrovinicius/atlas-compras-publicas/pull/83) (**draft, não autorizado**);
- estado: **candidata, não publicada** (04/11/2026).

A release deve usar o commit efetivamente gerado pelo merge autorizado em `main`; não realizar deploy manual de commits intermediários.

## Escopo

A candidata reúne as melhorias acumuladas na `develop` desde a v1.74.0, especialmente identificação de proveniência PNCP/sintética/desconhecida (#77/#80), segurança de exportação CSV, evidências em relatório/PDF, testes de interface e contratos, auditoria de dependências e documentação do Render.

## Dependência de segurança — issue #76

O release depende da correção de identidade de IP do [PR #78](https://github.com/peedrovinicius/atlas-compras-publicas/pull/78), ainda em rascunho e não integrada à `develop`. O ensaio no [staging Render Free #41941772404](https://github.com/peedrovinicius/atlas-compras-publicas/actions/runs/41941772404) aprovou a separação das cotas entre dois endereços públicos, a rejeição de `X-Forwarded-For` falsificado como identidade e o uso de `offline_synthetic` na versão combinada.

**Bloqueio obrigatório:** antes de publicar o código do PR #78 em produção, preparar `ATLAS_TRUST_CF_CONNECTING_IP=true` com **Save only** no painel do serviço canônico (sem iniciar deploy) e verificar que o plano continua Free, com somente uma instância e sem ingresso privado. Sem a flag, a nova implementação compartilharia uma cota global de **60 normalizações/minuto por instância**. A conexão Render disponível em ChatGPT **não expõe a modalidade Save only**, portanto nenhuma atualização automática de ambiente deve substituir esse passo.

A configuração ativa do serviço possui `healthCheckPath` vazio; o Blueprint indica `/ready`. Reconciliar essa divergência e registrar o plano de rollback antes da aprovação final. A documentação detalhada ficará no [runbook do PR #78](https://github.com/peedrovinicius/atlas-compras-publicas/blob/fix/normalization-rate-limit-client-identity-20261103/docs/runbook-release-proxy-render.md), após sua integração autorizada.

## Gates antes de qualquer merge

- [ ] CI e CodeQL aprovados no **head final** do PR de release;
- [ ] contrato de versão Python, frontend, relatório e User-Agent PNCP consistente com v1.75.0;
- [ ] revisão do diff completo contra `main`, inclusive alterações de segurança pendentes em PRs separados;
- [ ] confirmar capacidade de build na conta Render;
- [ ] reconciliar a configuração ativa do Render com `render.yaml` (comando do frontend, fallback, health check), **sem alteração automática**;
- [ ] autorização expressa de merge em `main` (pode disparar auto-deploy).

## Validação obrigatória após publicação autorizada

- [ ] registrar SHA e estado dos deploys de API e frontend;
- [ ] comparar `/health`, `/ready` e `/api/v1/meta`: mesma origem, data UTC, chaves e contagens;
- [ ] confirmar `pncp_sample` ou `offline_synthetic` (nunca inferir dados reais de `unknown`);
- [ ] validar banner visível, CSV, relatório impresso/PDF e links de evidência quando PNCP;
- [ ] executar workflow manual `Production smoke test` e registrar o resultado;
- [ ] concluir a issue #77 somente após validar a versão publicada.

**Não fazer merge nem deploy com este documento como única evidência de aprovação.**
