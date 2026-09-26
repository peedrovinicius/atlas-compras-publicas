# Ajustes pós-v2 — v1.1.0

## Contexto

O benchmark v2 congelado mediu 72,92% de acurácia de categoria antes de qualquer ajuste.

Os 13 erros revelaram três classes de problema:

1. vocabulário incompleto;
2. precedência semântica inadequada;
3. falsos positivos causados por termos de contexto.

## Alterações

### Resina microhíbrida

Foram adicionadas variantes explícitas:

- `RESINA MICROHIBRIDA`;
- `RESINA MICRO-HIBRIDA`;
- `RESINA NANOHIBRIDA`;
- `RESINA NANO-HIBRIDA`.

### Adesivo

Se a descrição contém o núcleo `ADESIVO`, essa evidência passa a ter precedência sobre menções posteriores a “resina composta”.

Isso corrige casos como:

`ADESIVO PARA RESTAURACOES DE RESINA COMPOSTA PRIMER E BOND UNIVERSAL`

### Contexto de uso

Descrições de kit/pontas para acabamento ou polimento de resina são explicitamente excluídas da classificação como `composite_resin`.

A presença da expressão “resina composta” deixa de ser suficiente quando o produto comprado é claramente um acessório de acabamento.

### Anestésicos

Foram adicionados princípios ativos como evidência explícita de `local_anesthetic`:

- lidocaína;
- articaína;
- mepivacaína.

## Resultado

### v1

Permaneceu em 37/37 categorias corretas.

### v2 pós-tuning

Passou de:

`35/48 = 72,92%`

para:

`48/48 = 100,00%`

com macro F1 1,0000.

## Limitação metodológica

O desempenho pós-tuning do v2 não deve ser chamado de validação independente.

Os erros do v2 foram usados para orientar as mudanças da v1.1.0.

Por isso, a baseline original continua preservada e o próximo teste de generalização deverá usar um v3 criado a partir de fontes novas e congelado antes de qualquer alteração de regra.
