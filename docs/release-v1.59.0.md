# Release v1.59.0

A v1.59.0 conclui a segunda etapa da reforma de interface do Atlas.

## Problema resolvido

Depois de abrir um produto, a análise completa ainda exigia uma rolagem longa para atravessar gráficos, mercado, sinais e evidências.

A release separa esse conteúdo em três visões focadas, sem remover nenhum dado.

## Visão geral

Reúne:

- mediana e faixa central;
- compras, fornecedores, UFs e período;
- distribuição dos preços comparáveis;
- histórico mensal.

## Mercado

Reúne:

- comparação por UF;
- fornecedores;
- órgãos compradores.

## Evidências

Reúne:

- sinais estatísticos;
- registros que sustentam a análise;
- hashes de origem;
- links para o PNCP.

## Navegação

A análise ganhou uma barra compacta de navegação interna.

Em desktop ela permanece disponível durante a leitura. Em telas pequenas, volta ao fluxo normal para não consumir espaço fixo.

Também foi incluída a ação `Voltar aos resultados`.

Ao abrir outro produto, a análise retorna automaticamente para `Visão geral`.

## Metodologia

A mudança é exclusivamente de experiência de uso.

Nenhuma regra de cálculo, normalização, comparação ou sinal estatístico foi alterada.

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
- build web aprovado.
