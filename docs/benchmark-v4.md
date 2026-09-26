# Benchmark independente v4

## Objetivo

O v4 mede a generalização da taxonomia depois das correções orientadas pelo v3.

O dataset foi congelado antes da avaliação e não foi alterado para favorecer o resultado.

## Fontes

A amostra usa quatro fontes novas de 2026:

1. Patos do Piauí/PI, PNCP `41522285000108-1-000032/2026`;
2. Ambulatório Naval da Penha/RJ, PNCP `00394502000144-1-006510/2026`;
3. São Paulo/SP, PNCP `13864377000130-1-001041/2026`;
4. Inhuma/PI, PNCP `06553739000107-1-000028/2026`.

## Resultado

| Métrica | Resultado |
| --- | ---: |
| Amostras | 48 |
| Categorias corretas | 41 |
| Erros | 7 |
| Acurácia | 85,42% |
| Macro precision | 0,6672 |
| Macro recall | 0,6178 |
| Macro F1 | 0,6187 |
| Concentração | 3/3 |

## Sete erros encontrados

### Pluralização

Três classes falharam por variações simples de número:

- `RESINAS FLUIDAS`;
- `ADESIVOS`;
- `IONOMEROS DE VIDRO`.

Isso mostra que a taxonomia ainda depende demais de sequências literais singulares.

### Anestésico genérico

`CAIXAS DE ANESTESICO SS.WHITI100` ficou como `unknown`.

A taxonomia reconhece princípios ativos e formas específicas, mas ainda não usa o contexto odontológico para validar o termo genérico.

### Flúor em gel

`FLUOR ACIDO GEL` ficou como `unknown`.

A ordem das palavras não coincide com os padrões atuais.

### Bulk fill fluida

Uma resina `bulk fill` descrita explicitamente como fluida foi classificada como `composite_resin`.

A regra atual encontra `RESINA COMPOSTA` antes de interpretar a informação de viscosidade distante no texto.

### Alginato como componente

Um isolante odontológico cuja composição contém alginato de sódio foi classificado como `alginate`.

Esse erro reforça a necessidade de distinguir a identidade do produto dos componentes presentes na formulação.

## Interpretação

O v4 não invalida as melhorias anteriores. Ele apresenta novas formas linguísticas e novas relações de contexto que ainda não haviam sido testadas.

A baseline de 85,42% deve permanecer preservada mesmo depois das futuras correções.

## Próximo passo

A próxima versão poderá corrigir esses sete erros sem alterar o v4.

Depois disso, o teste de generalização deve continuar em um v5 com fontes novas.
