# Release candidata v1.75.0

## Identificação

- versão: `1.75.0`;
- branch de integração: `develop`;
- destino: `main`;
- Pull Request de produção: **a definir antes de aprovar o merge**;
- estado: **candidata, não publicada** (04/11/2026).

A release deve usar o commit efetivamente gerado pelo merge autorizado em `main`; não realizar deploy manual de commits intermediários.

## Escopo

A candidata reúne as melhorias acumuladas na `develop` desde a v1.74.0, especialmente identificação de proveniência PNCP/sintética/desconhecida (#77/#80), segurança de exportação CSV, evidências em relatório/PDF, testes de interface e contratos, auditoria de dependências e documentação do Render.

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
