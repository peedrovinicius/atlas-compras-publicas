# Release v1.55.0

A v1.55.0 continua reduzindo o esforço para encontrar um produto no Explorador de preços.

## Busca sem depender de acentos

Consultas textuais genéricas agora são normalizadas antes da comparação com o conteúdo analítico.

Exemplo:

~~~text
protetica
~~~

pode localizar uma descrição que contenha:

~~~text
PROTÉTICA
~~~

A normalização serve apenas para pesquisa. O texto público original e a identidade comparável permanecem intactos.

## Autocomplete pelo teclado

A lista de sugestões ganhou navegação completa por teclado:

- seta para baixo seleciona a próxima sugestão;
- seta para cima seleciona a anterior;
- Enter abre a sugestão ativa;
- Escape fecha a lista.

A sugestão ativa também é refletida com `aria-selected` e `aria-activedescendant`.

## Recuperação sem resultado

Uma pesquisa vazia deixou de ser um beco sem saída.

Quando nenhum produto é encontrado, o Explorador apresenta atalhos para categorias existentes na base publicada. O usuário pode clicar em uma delas e continuar imediatamente.

## Validação

A release inclui teste de regressão que confirma uma busca sem acento contra uma descrição acentuada no DuckDB.

O gate permanece:

~~~text
ruff check .
pytest -q
npm run build
~~~
