# Holdout independente v5

## Objetivo

O v5 encerra o ciclo sequencial de benchmarks usados para orientar diretamente novas regras.

A amostra foi congelada antes da medição e permanece sem tuning na v1.7.0.

## Fontes

1. Lago dos Rodrigues/MA, PNCP `01612541000133-1-000047/2026`;
2. Rolim de Moura/RO, PNCP `04394805000118-1-000083/2026`;
3. Jacareí/SP, PNCP `46694139000183-1-000863/2026`;
4. Niterói/RJ, PNCP `34906284000100-1-000015/2026`;
5. Pinhais/PR, PNCP `76416932000181-1-000363/2026`.

## Resultado

| Métrica | Resultado |
| --- | ---: |
| Amostras | 48 |
| Categorias corretas | 38 |
| Erros | 10 |
| Acurácia | 79,17% |
| Macro precision | 0,7179 |
| Macro recall | 0,6250 |
| Macro F1 | 0,6483 |
| Cor | 3/7 |
| Concentração | 1/1 |

## Erros observados

### Ionômero

`IONOMERO RESTAURADOR AUTOPOLIMERIZAVEL` não é reconhecido porque a taxonomia atual exige formas mais específicas.

### Pasta profilática

`PASTA PROFIATICA` expõe sensibilidade a erro ortográfico.

### Resina curta e comercial

Sete resinas não são reconhecidas quando a descrição omite “composta” ou utiliza nome comercial.

Além da categoria, o padrão `A 2` com espaço também reduz a acurácia de extração de cor.

### Fluoreto de sódio em gel

`FLUORETO DE SODIO 2% GEL NEUTRO` não coincide com os padrões atuais de `fluoride_gel`.

## Decisão metodológica

Esses 10 erros não serão usados imediatamente para ajustar a taxonomia.

A intenção é manter o v5 como holdout independente enquanto a próxima etapa fortalece a camada multi-contratação.

Isso evita que cada benchmark novo seja transformado automaticamente em conjunto de treinamento.

## Próxima etapa

A prioridade seguinte é construir ingestão analítica de múltiplas contratações com:

- chave estável de contratação;
- chave estável de resultado;
- deduplicação;
- reconstrução idempotente;
- dataset consolidado para análises geográficas e temporais reais.
