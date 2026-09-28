# Release v1.50.0

A v1.50.0 marca a passagem do Atlas de uma demonstração centrada no parser para uma aplicação pública de inteligência sobre compras públicas.

## Aplicação pública

A página inicial agora prioriza a pesquisa por produtos comparáveis. A interface consulta a mesma API e a mesma base DuckDB usadas pela camada analítica do projeto.

Para cada produto disponível, a aplicação pode apresentar:

- mediana, média, mínimo, máximo e percentis de preço;
- suficiência da amostra comparável;
- histórico mensal;
- comparação por macrorregião e UF;
- fornecedores presentes na amostra;
- órgãos e unidades compradoras;
- sinais estatísticos;
- registros de origem com hashes e link para o PNCP.

O parser interativo permanece disponível na área `Laboratório`.

## Segurança interpretativa

Sinais estatísticos continuam sendo tratados como indicadores analíticos, não como prova de fraude, sobrepreço ou irregularidade.

A aplicação também informa quando a amostra fica abaixo do mínimo metodológico.

## Rastreabilidade

A v1.50.0 expõe a cadeia de evidência até os registros que sustentam a análise.

~~~text
análise -> produto comparável -> homologação -> item -> contratação -> SHA-256 -> PNCP
~~~

## Exemplo público do parser

A issue #27 foi atendida com um exemplo proveniente do holdout congelado v5.

Descrição:

~~~text
PRIME ADESIVO FRASCO 4ML
~~~

O resultado documentado é protegido por `tests/test_documented_parser_example.py`, evitando que a documentação diverja silenciosamente do parser.

Detalhes: [exemplo real e reproduzível](exemplo-parser-real.md).

## Validação

A release mantém como gate:

~~~text
ruff check .
pytest -q
npm run build
~~~

A publicação deve ser considerada válida somente após a execução do workflow `CI` concluir com sucesso no commit final da release.
