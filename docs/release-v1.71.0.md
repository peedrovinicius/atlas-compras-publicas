# Release v1.71.0

A v1.71.0 adiciona comparação direta entre uma proposta recebida e a distribuição histórica de preços do produto selecionado.

## Preço que recebi

Na visão geral da análise, o usuário pode informar um valor por unidade normalizada.

O Atlas então mostra:

- valor informado;
- diferença absoluta para a mediana;
- diferença percentual para a mediana;
- posição em relação a mínimo, P25, mediana, P75 e máximo;
- percentil aproximado estimado pela distribuição em faixas.

## Interpretação

O recurso é descritivo.

Ele não classifica uma proposta como preço justo, abusivo, correto ou incorreto. A finalidade é apenas mostrar onde o valor informado se posiciona em relação às observações públicas comparáveis.

## Metodologia

A comparação usa exatamente a mesma amostra da análise detalhada.

O percentil é apresentado como aproximado porque é estimado a partir dos bins da distribuição, e não da lista completa de observações individuais.

## Entrada

O campo aceita formato decimal brasileiro, como `18,90`.

Valores vazios, não numéricos ou não positivos não produzem comparação.

Ao selecionar outro produto, o valor informado anteriormente é limpo para evitar reaproveitamento acidental em outro contexto.
