# Metodologia de sinais de preços atípicos

## Objetivo

A camada de anomalias prioriza registros para investigação analítica.

Ela não determina fraude, corrupção, superfaturamento jurídico ou irregularidade administrativa.

## Métrica analisada

A métrica é o preço homologado por unidade física normalizada, quando a descrição fornece informação suficiente para essa normalização.

Exemplos:

- R$/g;
- R$/mL.

Massa e volume não são convertidos entre si.

## Identidade do produto

Antes da análise estatística, o registro precisa ter:

- categoria conhecida;
- apresentação identificada;
- quantidade física identificada;
- unidade física identificada;
- preço homologado positivo.

A chave de produto baseline combina:

- categoria;
- apresentação;
- cor;
- unidade física;
- quantidade física.

## Referência temporal

A data do resultado homologado é preferida.

Quando ela não está disponível, utiliza-se a data de publicação da contratação.

Dessa data são derivados:

- ano;
- trimestre.

A ausência de uma referência temporal impede que o registro participe da análise v0.7.0.

## Referência geográfica

O PNCP fornece município, código IBGE e UF por meio da unidade administrativa da contratação.

A macrorregião é derivada da UF por tabela determinística.

## Hierarquia de comparação

Para cada registro, são construídos candidatos de grupo em cinco níveis:

1. UF + trimestre;
2. macrorregião + trimestre;
3. Brasil + trimestre;
4. macrorregião + ano;
5. Brasil + ano.

O algoritmo escolhe o primeiro nível da hierarquia que possui pelo menos a amostra mínima.

Se nenhum nível atingir o mínimo, o maior grupo disponível é preservado apenas para diagnóstico e recebe:

`detection_method = insufficient_sample`

Nenhum sinal é produzido.

## Tamanho mínimo

O padrão é exigir pelo menos cinco observações.

Esse limite é configurável, mas valores inferiores a três são rejeitados pelo código.

## Método MAD

Para o grupo escolhido:

`MAD = mediana(|xᵢ - mediana(x)|)`

Quando `MAD > 0`:

`modified z-score = 0,6744897501960817 × (x - mediana) / MAD`

O limiar padrão é:

`|modified z-score| >= 3,5`

## Fallback por IQR

Quando `MAD = 0` e existe dispersão:

`IQR = Q3 - Q1`

Limite inferior:

`Q1 - 1,5 × IQR`

Limite superior:

`Q3 + 1,5 × IQR`

## Variação insuficiente

Quando MAD e IQR são zero, o grupo não possui variação adequada para os critérios atuais.

O método registrado é:

`insufficient_variation`

Nenhum sinal é produzido.

## Campos de explicação

A tabela `gold_price_signals` preserva:

- chave do produto;
- chave do grupo;
- escopo geográfico-temporal;
- geografia utilizada;
- período utilizado;
- tamanho do grupo;
- mediana;
- Q1;
- Q3;
- IQR;
- MAD;
- modified z-score;
- método;
- indicador de sinal;
- contexto do item;
- referências de proveniência.

A visão `price_anomalies` contém apenas registros sinalizados.

A visão `anomaly_scope_summary` apresenta cobertura e sinais por escopo, geografia e período.

## Limitações

A versão atual ainda não controla diretamente:

- fabricante;
- linha comercial;
- composição detalhada;
- concentração;
- viscosidade;
- validade;
- frete;
- prazo de entrega;
- volume total contratado;
- diferenças de tributação;
- características específicas da modalidade.

Esses fatores podem explicar variações legítimas de preço.

Por isso, qualquer sinal é ponto de partida para revisão, e não conclusão.
