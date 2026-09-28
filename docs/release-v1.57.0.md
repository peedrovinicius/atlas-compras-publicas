# Release v1.57.0

A v1.57.0 deixa o Explorador de preços mais rápido para quem parte de uma busca ampla e quer chegar a um produto específico sem reescrever a consulta.

## Refinamentos clicáveis

A pesquisa passa a devolver facetas calculadas sobre todos os grupos compatíveis, antes da paginação.

Quando houver dados, o Explorador oferece refinamentos por:

- cor;
- apresentação;
- concentração;
- tecnologia;
- modo de cura;
- estratégia adesiva;
- uso;
- formulação;
- princípio ativo;
- vasoconstrictor.

Cada opção mostra a quantidade de grupos compatíveis.

Exemplo:

~~~text
resina
  Cor A2  14
  Cor A3  11
  Seringa 21
  Fotopolimerizável 18
~~~

Ao clicar em um refinamento, o atributo é acrescentado à consulta e a busca é refeita preservando os filtros e a ordenação atuais.

## Pesquisas recentes

O Explorador guarda até seis pesquisas recentes para reutilização rápida.

O histórico é armazenado somente em `localStorage` no navegador do usuário:

- não é enviado para a API;
- não é salvo no servidor;
- pode ser apagado pelo botão `Limpar`.

Pesquisas automáticas de inicialização e paginação não entram no histórico. Apenas ações de busca do usuário são registradas.

## Validação

A release inclui teste para confirmar que as facetas representam o conjunto completo da pesquisa mesmo quando a resposta atual está paginada.

O gate permanece:

~~~text
ruff check .
pytest -q
npm run build
~~~
