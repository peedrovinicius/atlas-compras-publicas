# Release v1.58.0

A v1.58.0 é uma reforma visual da experiência pública do Atlas.

## Objetivo

A interface havia acumulado recursos úteis, mas muitos controles competiam pela atenção logo na entrada. Esta release reorganiza a experiência em uma sequência mais clara:

1. entender o que o Atlas faz;
2. pesquisar um produto;
3. refinar se necessário;
4. comparar resultados;
5. abrir a análise completa.

## Cabeçalho

O cabeçalho foi simplificado.

A navegação principal agora destaca apenas:

- Preços;
- Laboratório;
- status resumido da API;
- acesso ao código.

O Swagger saiu da navegação principal e permanece acessível pelo rodapé.

## Busca

O campo principal ganhou mais destaque e altura.

As categorias deixaram de aparecer como blocos grandes e passaram a funcionar como atalhos compactos.

Os exemplos redundantes foram removidos porque autocomplete, categorias e pesquisas recentes já cobrem essa função.

## Filtros

Região, UF, fornecedor, órgão, período e ordenação continuam disponíveis, mas agora ficam recolhidos em `Filtros avançados`.

Isso reduz o ruído para quem quer apenas pesquisar um produto, sem remover profundidade para quem precisa de recortes específicos.

## Resultados

Os cartões ficaram mais leves visualmente e mantêm em destaque:

- nome comparável;
- descrição pública de exemplo;
- mediana do preço;
- compras;
- observações de preço;
- UFs;
- atualização.

## Análise

A área detalhada ganhou:

- menos sombras;
- cartões mais compactos;
- melhor espaçamento;
- hierarquia tipográfica mais consistente;
- carregamento em skeleton.

## Mobile

A busca passa para uma coluna, categorias ganham rolagem horizontal, filtros avançados ocupam uma única coluna e os resultados preservam leitura confortável em telas pequenas.

## Validação

O redesenho não altera metodologia, API analítica ou regras de cálculo.

Gate executado:

~~~text
ruff check .
pytest -q
npm run build
~~~

Resultado antes da consolidação da release:

- 226 testes aprovados;
- Ruff aprovado;
- build Vite aprovado.
