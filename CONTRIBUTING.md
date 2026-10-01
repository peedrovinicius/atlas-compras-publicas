# Contribuindo

Contribuições são bem-vindas quando ajudam a melhorar a qualidade, a rastreabilidade ou a cobertura analítica do projeto.

## Antes de começar

1. Verifique se já existe uma issue sobre o tema.
2. Para mudanças maiores, descreva primeiro o problema e o escopo em uma issue.
3. Evite misturar correções de parser, mudanças metodológicas e refatorações no mesmo Pull Request.

## Boas primeiras contribuições

Mudanças pequenas e verificáveis são úteis quando preservam as baselines e a rastreabilidade. Bons pontos de entrada incluem:

- documentação e exemplos de uso;
- testes para regras já existentes;
- mensagens de erro e validações de entrada;
- casos de benchmark novos, desde que independentes dos conjuntos usados no tuning;
- melhorias de legibilidade sem alterar a metodologia.

Mudanças em parser, taxonomia ou critérios de sinal devem ser discutidas em uma issue antes da implementação.

## Ambiente local

Instale o projeto em modo de desenvolvimento:

```bash
pip install -e ".[dev]"
```

Execute as verificações principais:

```bash
ruff check .
pytest -q
```

## Regras de qualidade

- preserve a rastreabilidade entre dado derivado e fonte pública;
- não altere benchmarks congelados para melhorar métricas retroativamente;
- mantenha resultados pós-tuning separados das baselines independentes;
- use dados públicos ou fixtures pequenas e fictícias em testes;
- não apresente sinal estatístico como prova de irregularidade;
- atualize a documentação quando uma mudança afetar contratos, taxonomias ou metodologia.

## Fluxo de branches

O desenvolvimento normal acontece fora da `main`.

Fluxo recomendado:

1. use `develop` como integração das mudanças em andamento;
2. execute a CI completa em `develop`;
3. abra Pull Request de `develop` para `main`;
4. só faça merge quando o check `quality` estiver aprovado;
5. trate o merge na `main` como uma release/deploy, não como área de trabalho.

Evite commits incrementais diretamente na `main`. Isso mantém o histórico de release limpo e evita disparar builds de produção para mudanças ainda não consolidadas.

## Deploy

A configuração canônica do Render está em `render.yaml` e possui somente dois serviços:

- `atlas-compras-publicas-web`;
- `atlas-compras-publicas-analytics`.

Serviços Render criados manualmente fora desse Blueprint não fazem parte da arquitetura canônica.

O deploy de produção deve ocorrer somente após CI aprovada e merge na `main`. Alterações em `develop` não devem ser usadas como origem de produção.

## Pull Requests

Inclua:

- o problema resolvido;
- o escopo da alteração;
- os testes executados;
- impacto em benchmarks, quando houver;
- impacto metodológico, quando houver;
- confirmação de que a CI passou antes do merge.

Mudanças pequenas e verificáveis são mais fáceis de revisar.
