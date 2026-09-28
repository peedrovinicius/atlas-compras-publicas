# Release v1.60.0

A v1.60.0 conclui a terceira etapa da reforma visual do Atlas, agora concentrada na leitura da análise de um produto.

## Resumo executivo

A Visão geral deixou de abrir com seis cartões equivalentes.

O primeiro bloco agora destaca a pergunta principal da análise:

**qual é o preço de referência observado?**

A mediana recebe maior peso visual e a faixa entre os percentis 25 e 75 aparece logo abaixo como contexto.

Compras, fornecedores, UFs e período continuam visíveis, mas em uma camada secundária.

## Atualização da análise

Quando disponível, a data de atualização do produto aparece junto às ações de compartilhamento e exportação.

## Mercado

A aba Mercado ganhou uma introdução curta que explica o objetivo da leitura:

- diferenças geográficas;
- fornecedores;
- órgãos compradores.

## Evidências

A aba Evidências informa imediatamente quantos sinais estatísticos e quantos registros sustentam o recorte atual.

## Tabelas e listas

Foram aplicados ajustes de leitura:

- números tabulares;
- cabeçalhos fixos dentro de tabelas roláveis;
- realce de linha ao passar o cursor;
- estados de hover em rankings e cartões de evidência.

## Responsividade

O resumo executivo vira uma única coluna em telas menores. Os indicadores secundários continuam em grade compacta no mobile.

## Metodologia

Nenhuma regra de preço, agrupamento, normalização, comparação, sinal estatístico ou rastreabilidade foi alterada.

## Validação

Gate executado antes da consolidação:

~~~text
ruff check .
pytest -q
npm run build
~~~

Resultado:

- 226 testes aprovados;
- Ruff aprovado;
- build Vite aprovado em 836 ms.
