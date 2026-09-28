# Release v1.51.0

A v1.51.0 torna a exploração de preços realmente navegável por recortes analíticos, sem criar divergência entre a busca e os detalhes do produto.

## Filtros compartilhados

A busca e todas as visões de um produto aceitam os mesmos filtros opcionais:

- período inicial e final;
- macrorregião;
- UF;
- fornecedor por nome ou documento;
- órgão ou unidade compradora por nome, CNPJ ou código.

O mesmo conjunto é reaplicado a resumo, distribuição, histórico, geografia, fornecedores, órgãos compradores, sinais estatísticos e registros de evidência.

Essa decisão evita que a interface mostre, por exemplo, uma lista filtrada para Ceará e depois calcule a mediana usando registros nacionais.

## Paginação

A pesquisa pública usa `limit` e `offset` e retorna o total de identidades compatíveis.

O frontend usa páginas de 10 grupos e fornece navegação Anterior/Próxima, mostrando o intervalo atual e o total de resultados.

## Interface

A área Explorar preços ganhou controles para:

- região;
- UF;
- fornecedor;
- órgão ou unidade;
- data inicial;
- data final;
- limpeza rápida dos filtros.

Os controles permanecem opcionais. Sem filtros, a experiência continua consultando toda a base analítica publicada.

## Segurança e consistência

Os filtros continuam parametrizados no DuckDB. Entrada do usuário não é interpolada diretamente em SQL.

Intervalos com data inicial posterior à data final são rejeitados.

## Validação

A implementação foi protegida por testes que verificam:

- filtragem combinada;
- paginação com total preservado;
- resumo filtrado;
- registros filtrados;
- distribuição calculada apenas sobre o subconjunto selecionado.

O gate de release permanece:

~~~text
ruff check .
pytest -q
npm run build
~~~
