# Release v1.56.0

A v1.56.0 reduz o número de cliques necessários para decidir qual resultado abrir no Explorador de preços.

## Resultados mais informativos

Cada grupo encontrado passa a mostrar imediatamente:

- mediana do preço normalizado defensável;
- número de compras;
- número de observações de preço;
- quantidade de UFs;
- atualização mais recente;
- descrição pública de exemplo.

A análise detalhada continua sendo a fonte completa para percentis, distribuição, fornecedores, órgãos compradores, sinais e evidências.

## Filtros visíveis

Depois de pesquisar, os filtros aplicados aparecem como chips acima dos resultados.

Cada chip pode ser removido individualmente. Também existe uma ação para limpar todos os filtros sem perder o termo pesquisado.

Quando um recorte retorna zero produtos, o Explorador oferece `Tentar novamente sem filtros` antes dos atalhos por categoria.

## Vocabulário cotidiano

Foram adicionados aliases conservadores para termos comuns na odontologia:

~~~text
CIV -> Ionômero de vidro
cimento de vidro -> Ionômero de vidro
bonding -> Adesivo odontológico
anestesia local -> Anestésico local
~~~

Os aliases continuam limitados a categorias conhecidas para evitar inferências livres sobre produtos.

## Validação

A busca continua coberta por testes automatizados. A v1.56.0 adiciona proteção explícita para a mediana retornada na lista de resultados e para os novos termos de pesquisa.

O gate permanece:

~~~text
ruff check .
pytest -q
npm run build
~~~
