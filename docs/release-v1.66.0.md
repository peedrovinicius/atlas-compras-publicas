# Release v1.66.0

A v1.66.0 facilita a descoberta de produtos no Explorador de preços.

## Categorias conhecidas

O Explorador passa a mostrar diretamente todas as categorias reconhecidas que possuem observações de preço na base analítica.

Cada botão informa:

- nome da categoria;
- quantidade de grupos de produto;
- quantidade de observações de preço.

Ao clicar, a categoria é pesquisada imediatamente.

Quando o usuário digita um termo que se aproxima de uma categoria conhecida, a interface continua priorizando as categorias compatíveis.

## Laboratório

O exemplo rápido com o rótulo `Caso difícil` foi removido.

O parser continua tratando descrições não reconhecidas normalmente, mas sem apresentar esse rótulo na interface pública.

## Validação

O gate funcional registrou:

- Ruff aprovado;
- 226 testes aprovados;
- build React/TypeScript aprovado;
- Vite concluído em 593 ms;
- GitHub Actions concluído com sucesso.
