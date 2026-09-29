# Checklist de release

Use este checklist antes de qualquer merge de `develop` para `main`.

## 1. Código

- [ ] alteração concluída na `develop`;
- [ ] nenhuma mudança incremental pendente;
- [ ] Ruff aprovado;
- [ ] testes aprovados;
- [ ] build React/TypeScript aprovado;
- [ ] novos comportamentos cobertos por regressão quando aplicável.

## 2. Contratos

- [ ] versão em `pyproject.toml` atualizada;
- [ ] `__version__` sincronizado;
- [ ] versão de `web/package.json` sincronizada;
- [ ] User-Agent do cliente PNCP sincronizado com major/minor;
- [ ] `docs/release-vX.Y.Z.md` existe;
- [ ] `CHANGELOG.md` atualizado;
- [ ] README e índice de documentação atualizados quando aplicável.

A suíte `tests/test_release_integrity.py` verifica automaticamente os principais contratos acima.

## 3. Render

Antes do merge, confirme que a arquitetura de produção continua composta somente por:

- `atlas-compras-publicas-web`;
- `atlas-compras-publicas-analytics`.

Também confirme:

- [ ] `render.yaml` contém apenas esses dois serviços;
- [ ] ambos usam `autoDeployTrigger: checksPass`;
- [ ] frontend aponta para `atlas-compras-publicas-analytics.onrender.com`;
- [ ] não há dependência de serviço duplicado;
- [ ] workspace possui capacidade de build disponível.

Não faça merge em `main` enquanto o Render estiver bloqueado por falta de minutos.

## 4. Pull Request

- [ ] PR aponta de `develop` para `main`;
- [ ] check `quality` aprovado;
- [ ] PR contém resumo técnico e impacto metodológico;
- [ ] documentação de release está incluída;
- [ ] não existem mudanças fora do escopo;
- [ ] PR deixou de ser draft somente quando estiver pronto para produção.

## 5. Merge

O merge na `main` deve representar uma unidade pronta para produção.

- [ ] fazer apenas um merge consolidado;
- [ ] evitar commits corretivos imediatamente após o merge;
- [ ] aguardar os serviços canônicos iniciarem o deploy;
- [ ] não disparar redeploy manual enquanto um deploy automático válido estiver em andamento.

## 6. Validação em produção

Depois que os dois serviços canônicos terminarem o deploy, execute manualmente o workflow `Production smoke test` no GitHub Actions.

Ele verifica automaticamente:

- frontend público;
- versão publicada do bundle comparada com `web/package.json`;
- `/health`;
- `/ready`;
- discovery de produtos;
- uma busca real na API.

Depois complete a validação funcional abaixo.

Frontend:

- [ ] página inicial abre;
- [ ] Explorar preços funciona;
- [ ] busca retorna resultados;
- [ ] P25, mediana e P75 aparecem;
- [ ] comparador aceita somente produtos compatíveis;
- [ ] `Preço que recebi` funciona;
- [ ] percentil aproximado aparece quando houver distribuição;
- [ ] `Gerar relatório / PDF` funciona;
- [ ] exportação CSV funciona;
- [ ] links para evidências do PNCP continuam válidos.

API:

- [ ] `/health` responde;
- [ ] `/ready` confirma disponibilidade da base;
- [ ] busca de produtos responde;
- [ ] análise detalhada responde;
- [ ] endpoints de distribuição, histórico, regiões, fornecedores, compradores, sinais e registros respondem.

## 7. Pós-release

- [ ] confirmar que o smoke test validou a mesma versão declarada em `web/package.json`;
- [ ] confirmar versão publicada;
- [ ] registrar qualquer incidente;
- [ ] fechar issues concluídas;
- [ ] manter `develop` como próxima área de trabalho;
- [ ] não usar `main` para desenvolvimento incremental.
