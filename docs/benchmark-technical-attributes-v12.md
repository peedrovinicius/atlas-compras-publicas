# Benchmark independente de atributos técnicos v12

## Resultado independente

| Métrica | Resultado |
| --- | ---: |
| Exemplos | 48 |
| Categorias corretas | 35/48 |
| Acurácia de categoria | 72,92% |
| Campos técnicos avaliados | 77 |
| Campos técnicos corretos | 67 |
| Micro accuracy | 87,01% |
| Falsos positivos | 0 |
| Falsos negativos | 10 |
| Mismatches | 0 |

## Principais lacunas

- `MEPIVACANA` não é interpretada como mepivacaína;
- `SV` não é interpretado como sem vasoconstritor;
- `IONOMERO VIDRO` e `KIT - IONOMERO RESTAURADOR` não entram na identidade atual;
- `AUTO-CONDICIONANTE` não casa com as variantes existentes;
- `FENILEFINA` não é reconhecida como fenilefrina;
- `RESINA DENTAL MICRO HIBRIDA, FOTO` não casa com identidade/atributos atuais;
- abreviações `REVELADOR RX`, `FIXADOR RX` e formas equivalentes ficam fora;
- `RESINA Z100` não é reconhecida;
- pasta de moldagem com óxido de zinco e eugenol é promovida indevidamente para `zinc_oxide`;
- `FOTO IONOFAST` não produz modo de cura.

## Decisão metodológica

Nenhuma dessas lacunas será corrigida na v1.35.

A baseline independente permanece:

- 72,92% de acurácia de categoria;
- 87,01% de micro accuracy técnica.
