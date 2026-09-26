# Metodologia de sinais de preços atípicos

## Objetivo

O objetivo desta camada é priorizar registros para investigação analítica.

O sistema não tenta determinar fraude, corrupção, superfaturamento jurídico ou qualquer outra conclusão de natureza legal.

## Unidade analisada

A métrica utilizada é o preço homologado por unidade física normalizada, quando essa unidade pode ser extraída de forma defensável da descrição do item.

Exemplos:

- R$/g;
- R$/mL.

Massa e volume permanecem dimensões distintas.

## Formação dos grupos comparáveis

A implementação baseline utiliza a combinação de:

- categoria odontológica;
- apresentação;
- cor;
- unidade física normalizada;
- quantidade física normalizada.

Registros com categoria desconhecida, apresentação ausente, quantidade não identificada ou preço homologado não positivo não entram na análise de atipicidade.

A ausência de cor permanece explícita e não é misturada com uma cor conhecida.

## Tamanho mínimo

O padrão é exigir pelo menos 5 observações no grupo.

Grupos menores recebem o método:

`insufficient_sample`

e nunca geram sinal.

## Método MAD

A mediana é utilizada como medida central robusta.

O desvio absoluto mediano é definido como:

`MAD = mediana(|xᵢ - mediana(x)|)`

Quando `MAD > 0`, o sistema calcula:

`modified z-score = 0,6744897501960817 × (x - mediana) / MAD`

O limite padrão é:

`|modified z-score| >= 3,5`

O registro recebe:

`detection_method = modified_z_score`

## Fallback por IQR

Em conjuntos com muitos valores repetidos, o MAD pode ser zero.

Quando isso ocorre e `IQR > 0`, o sistema utiliza:

`IQR = Q3 - Q1`

Limite inferior:

`Q1 - 1,5 × IQR`

Limite superior:

`Q3 + 1,5 × IQR`

O registro recebe:

`detection_method = iqr_fallback`

## Variação insuficiente

Quando MAD e IQR são zero, não existe dispersão suficiente para aplicar os critérios atuais.

O método registrado é:

`insufficient_variation`

Nenhum sinal é produzido.

## Campos de explicação

Cada registro em `gold_price_signals` preserva:

- chave do grupo comparável;
- tamanho do grupo;
- mediana;
- primeiro quartil;
- terceiro quartil;
- IQR;
- MAD;
- modified z-score, quando aplicável;
- método utilizado;
- indicador booleano de sinal.

A visão `price_anomalies` contém somente os registros sinalizados.

## Limitações atuais

O grupo comparável ainda não captura todos os atributos técnicos possíveis de um produto odontológico.

Exemplos de fatores que podem alterar legitimamente o preço:

- fabricante;
- linha comercial;
- composição;
- geração tecnológica;
- viscosidade;
- concentração;
- acessórios incluídos;
- validade;
- região;
- frete;
- prazo de entrega;
- quantidade comprada;
- data da compra.

Por isso, qualquer sinal é um ponto de partida para análise, nunca uma conclusão.

## Próximas evoluções

A metodologia deverá ganhar:

1. dimensões geográficas;
2. janelas temporais;
3. atributos técnicos específicos por categoria;
4. grupos de comparação hierárquicos;
5. análise de sensibilidade;
6. métricas de qualidade e cobertura do normalizador;
7. avaliação manual de uma amostra de sinais.
