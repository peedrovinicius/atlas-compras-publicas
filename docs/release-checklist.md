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


### Conferência de divergência entre Blueprint e serviço ativo (03/11/2026)

A configuração **consultada no Render** para o serviço `atlas-compras-publicas-analytics`
(`main`, auto-deploy após checks) usa atualmente:

```bash
pip install -e ".[api]" && atlas build-demo-data --output-root data/demo
```

O `render.yaml` versionado acrescenta `--offline-fallback`. Esta diferença
**não impede** o fallback para a amostra padrão: `build_demo_data()` chama o
fallback quando a captura padrão falha ou não produz resultados, mesmo com
`allow_offline_seed=False`. A flag é necessária apenas para permitir fallback
em uma contratação fornecida explicitamente (`--cnpj/--year/--sequence`).

O Blueprint também declara `healthCheckPath: /ready`, enquanto o serviço
ativo consultado não apresenta health check configurado. Assim, o Blueprint
**não deve ser presumido como a configuração efetivamente aplicada**.

- [ ] antes da próxima publicação autorizada, conferir no painel do Render
      build command, health check, branch, gatilho automático e variáveis
      relevantes contra `render.yaml`;
- [ ] manter o fallback padrão e a identificação `offline_synthetic` testados;
- [ ] após deploy autorizado, registrar o commit dos dois serviços e conferir
      `/health`, `/ready`, `/api/v1/meta`, CSV e aviso visual;
- [ ] não alterar a configuração do Render durante esta conferência.

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
- canonical, Open Graph, JSON-LD e manifesto;
- `robots.txt`, `sitemap.xml` e `.well-known/security.txt`;
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
- [ ] links para evidências do PNCP continuam válidos;
- [ ] `robots.txt`, `sitemap.xml`, manifesto e `security.txt` respondem publicamente;
- [ ] canonical e metadados sociais apontam para a URL oficial.

API:

- [ ] `/health` responde;
- [ ] `/ready` confirma disponibilidade da base;
- [ ] busca de produtos responde;
- [ ] análise detalhada responde;
- [ ] endpoints de distribuição, histórico, regiões, fornecedores, compradores, sinais e registros respondem.

## 7. Proveniência da amostra

- [ ] inspecionar `/api/v1/meta` e `/ready` no serviço publicado;
- [ ] a origem deve ser `pncp_sample` ou `offline_synthetic`;
- [ ] se `unknown`, não declarar nem publicar valores como preços reais;
- [ ] conferir data UTC, chaves de contratações e contagens de observações;
- [ ] comparar a origem da API com o aviso visual no frontend;
- [ ] se a origem for `offline_synthetic`, confirmar o aviso explícito de
      valores fictícios, inclusive no relatório/PDF e exportação CSV;
- [ ] conferir no CSV a coluna `data_source_type` e o nome do arquivo;
- [ ] registrar a proveniência efetivamente publicada no release.

O smoke de produção deve **falhar fechado** se a proveniência estiver ausente,
inválida ou declarada como `unknown`. Um ambiente offline sintético pode ser
aceito como demonstração, mas não como histórico de compras públicas reais.

## 8. Pós-release

- [ ] confirmar que o smoke test validou a mesma versão declarada em `web/package.json`;
- [ ] confirmar versão publicada;
- [ ] registrar qualquer incidente;
- [ ] fechar issues concluídas;
- [ ] manter `develop` como próxima área de trabalho;
- [ ] não usar `main` para desenvolvimento incremental.
