# Metodologia de sinais de preços atípicos

## Objetivo

A camada de anomalias prioriza registros para investigação analítica.

Ela não determina fraude, corrupção, superfaturamento jurídico ou irregularidade administrativa.

## Métrica analisada

A métrica é o preço homologado por unidade física normalizada, somente quando descrição, embalagem e unidade de compra sustentam uma base física defensável.

Exemplos:

- R$/g;
- R$/mL.

Massa e volume não são convertidos entre si.

## Identidade técnica do produto

Antes da análise estatística, o registro precisa ter:

- categoria conhecida;
- apresentação identificada;
- quantidade física identificada;
- unidade física identificada;
- `price_normalization_status = defensible`;
- preço homologado positivo;
- referência temporal.

Os demais estados são:

- `review`: existe medida física, mas a base do preço é ambígua;
- `unavailable`: não existe medida física suficiente para normalizar o preço.

A chave técnica do produto combina:

- categoria;
- apresentação;
- cor;
- concentração;
- quantidade por embalagem quando explícita;
- quantidade unitária;
- unidade da quantidade unitária;
- quantidade física total usada como base do preço;
- unidade física.

Isso impede, por exemplo, que `1 seringa de 4 g` e `2 seringas de 4 g` sejam tratados como a mesma configuração comercial.

A ausência de atributo técnico permanece explícita.

## Referência temporal

A data do resultado homologado é preferida.

Quando ela não está disponível, utiliza-se a data de publicação da contratação.

Dessa data são derivados ano e trimestre.

## Referência geográfica

O PNCP fornece município, código IBGE e UF pela unidade administrativa da contratação.

A macrorregião é derivada deterministicamente da UF.

## Hierarquia de comparação

Para cada registro, são construídos candidatos em cinco níveis:

1. UF + trimestre;
2. macrorregião + trimestre;
3. Brasil + trimestre;
4. macrorregião + ano;
5. Brasil + ano.

O algoritmo escolhe o primeiro nível com pelo menos a amostra mínima.

Se nenhum nível atingir o mínimo, o maior grupo disponível é preservado para diagnóstico e recebe:

`detection_method = insufficient_sample`

Nenhum sinal é produzido.

## Tamanho mínimo

O padrão é cinco observações.

Valores inferiores a três são rejeitados pelo código.

## Método MAD

`MAD = mediana(|xᵢ - mediana(x)|)`

Quando `MAD > 0`:

`modified z-score = 0,6744897501960817 × (x - mediana) / MAD`

Limiar padrão:

`|modified z-score| >= 3,5`

## Fallback por IQR

Quando `MAD = 0` e existe dispersão:

`IQR = Q3 - Q1`

Limite inferior:

`Q1 - 1,5 × IQR`

Limite superior:

`Q3 + 1,5 × IQR`

## Variação insuficiente

Quando MAD e IQR são zero:

`detection_method = insufficient_variation`

Nenhum sinal é produzido.

## Campos de explicação

A tabela `gold_price_signals` preserva:

- chave do produto;
- chave do grupo;
- escopo;
- geografia;
- período;
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
- proveniência.

## Limitações

A versão atual ainda não controla diretamente todos os atributos comerciais e clínicos possíveis, como:

- fabricante;
- linha comercial;
- composição detalhada;
- viscosidade;
- validade;
- frete;
- prazo de entrega;
- tributação;
- características específicas da modalidade.

Esses fatores podem explicar variações legítimas de preço.

Qualquer sinal é ponto de partida para revisão, não conclusão.
