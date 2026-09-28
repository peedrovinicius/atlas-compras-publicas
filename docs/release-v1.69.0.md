# Release v1.69.0

A v1.69.0 adiciona comparação direta entre produtos no Explorador de preços.

## Comparação lado a lado

Cada resultado passa a oferecer a ação `Comparar`.

É possível selecionar até 3 produtos e visualizar em uma única tabela:

- preço mediano normalizado;
- quantidade de preços comparáveis;
- número de compras;
- quantidade de UFs;
- apresentação;
- cor.

## Segurança metodológica

O Atlas só permite comparação quando os produtos selecionados pertencem à mesma categoria e usam a mesma unidade normalizada.

Essa restrição evita colocar lado a lado medianas calculadas sobre objetos ou unidades incompatíveis.

## Continuidade da busca

A seleção permanece ativa durante paginação da mesma consulta.

Quando a consulta, filtros ou ordenação mudam, a comparação é limpa para impedir mistura de contextos analíticos diferentes.

## Interface

Os cartões de resultado foram reorganizados para separar claramente:

- abertura da análise detalhada;
- inclusão ou remoção da comparação.

A tabela possui rolagem horizontal controlada em telas pequenas e mantém os valores principais legíveis no mobile.

## Validação

O gate funcional anterior à consolidação registrou:

- Ruff aprovado;
- 238 testes aprovados;
- build React/TypeScript aprovado;
- Vite concluído em 884 ms.
