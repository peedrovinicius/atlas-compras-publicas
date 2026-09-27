# Atributos técnicos v12 após tuning da v1.37

## Baseline independente preservada

- categorias: 35/48, 72,92%;
- atributos: 67/77, 87,01%;
- falsos positivos: 0;
- falsos negativos: 10;
- mismatches: 0.

## Correções aplicadas

A v1.37 adiciona apenas variantes observadas no v12:

- `MEPIVACANA`;
- `SV` como ausência de vasoconstritor;
- `IONOMERO VIDRO`, `IONOMERO RESTAURADOR` e `MAXXION-R`;
- `AUTO-CONDICIONANTE`;
- `FENILEFINA`;
- `RESINA DENTAL`, `MICRO HIBRIDA`, `RESINA Z 100`;
- formas `REVELADOR/FIXADOR ... RX`;
- formas `REVELADOR/FIXADOR DE FILME RADIOGRAFICO`;
- `FOTO IONOFAST`;
- epinefrina sem separação antes da concentração;
- exclusão contextual para pasta de moldagem com óxido de zinco/eugenol.

## Resultado pós-tuning

| Métrica | Resultado |
| --- | ---: |
| Categorias | 48/48 |
| Atributos | 77/77 |
| Micro accuracy | 100,00% |
| Falsos positivos | 0 |
| Falsos negativos | 0 |
| Mismatches | 0 |

O v11 também permaneceu em 48/48 categorias e 80/80 atributos no espelho determinístico atualizado.
