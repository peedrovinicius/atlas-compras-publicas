## Resumo

Descreva o problema resolvido e a alteração realizada.

## Escopo

- [ ] captura PNCP
- [ ] normalização ou identidade
- [ ] benchmark
- [ ] analytics ou DuckDB
- [ ] API ou dashboard
- [ ] documentação
- [ ] testes ou CI

## Validação

Informe os comandos executados e o resultado relevante.

```bash
ruff check .
pytest -q
cd web && npm run build
```

Para PRs destinados à `main`:

- [ ] o trabalho foi consolidado e validado fora da `main`;
- [ ] o check `quality` está aprovado;
- [ ] a versão e a documentação de release estão sincronizadas quando aplicável;
- [ ] o impacto no deploy dos serviços canônicos foi verificado.

## Impacto metodológico

Explique se a mudança altera parser, taxonomia, benchmark, regra de comparação, preço normalizado ou critério de sinal. Se não houver impacto, registre isso explicitamente.

## Checklist

- [ ] a alteração está limitada ao escopo do PR;
- [ ] testes foram adicionados ou atualizados quando necessário;
- [ ] benchmarks congelados não foram reescritos;
- [ ] resultados pós-tuning continuam separados das baselines independentes;
- [ ] sinais estatísticos não são apresentados como prova de irregularidade;
- [ ] documentação foi atualizada quando o comportamento mudou.
