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

## Pull Requests

Inclua:

- o problema resolvido;
- o escopo da alteração;
- os testes executados;
- impacto em benchmarks, quando houver;
- impacto metodológico, quando houver.

Mudanças pequenas e verificáveis são mais fáceis de revisar.
