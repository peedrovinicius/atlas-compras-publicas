# Plano do holdout independente de medicamentos v4

## Objetivo

Construir o quarto holdout independente do domínio de medicamentos sem reutilizar processos, itens ou descrições dos benchmarks v1, v2 e v3.

O v4 deve medir a generalização do parser após a v1.48, antes de qualquer novo ajuste de regras. A baseline v4 só será válida se o dataset for congelado antes da primeira execução.

## Estado de partida

- Medicamentos v1: baseline independente preservada em 87,50%.
- Medicamentos v2: baseline independente preservada em 79,69%.
- Medicamentos v3: baseline independente preservada em 90,10%.
- Regressões pós-tuning v1, v2 e v3: 192/192 campos corretos em cada conjunto.
- Domínio: `benchmark_required`.

## Regra principal

Nenhuma correção do parser pode ser feita durante a construção do v4.

A ordem metodológica é obrigatória:

1. selecionar fontes públicas independentes;
2. checar colisão contra v1, v2 e v3;
3. montar o dataset v4;
4. congelar o arquivo `data/evaluation/medications-v4.jsonl`;
5. registrar o blob SHA e o commit de congelamento;
6. executar a primeira medição com o parser vigente sem alteração;
7. documentar a baseline independente;
8. só depois decidir se haverá tuning posterior.

## Critérios de independência

Um candidato ao v4 deve ser excluído se:

- usar o mesmo número de controle PNCP de v1, v2 ou v3;
- reutilizar item já amostrado nos ciclos anteriores;
- repetir descrição idêntica ou praticamente idêntica a exemplo anterior;
- depender de normalização manual feita em ciclo anterior;
- vier de fonte secundária sem rastreabilidade mínima até a contratação pública.

## Tamanho planejado

O v4 deve manter o padrão dos ciclos anteriores:

- 48 exemplos;
- 8 contratações inéditas;
- 6 itens por contratação;
- 192 campos avaliados;
- 4 campos por exemplo:
  - princípio ativo;
  - concentração;
  - forma farmacêutica;
  - via de administração.

## Prioridades de amostragem

O v4 deve aumentar a pressão nos pontos que ainda diferenciam baseline de regressão perfeita:

- associações com três ou mais princípios ativos;
- sais e qualificadores após vírgula;
- composições descritas em campos semiestruturados;
- abreviações reais de forma farmacêutica;
- formas ambíguas entre oral, tópico, oftálmico e injetável;
- concentração sem unidade explícita;
- erros reais de grafia;
- descrições curtas com pouca redundância;
- descrições longas com repetição do produto;
- medicamentos com apresentação explícita, mas sem via direta.

## Campos mínimos do JSONL

Cada linha do v4 deve manter o contrato usado nos ciclos anteriores:

```json
{
  "id": "med4-...",
  "description": "...",
  "expected": {
    "active_ingredient": "...",
    "strength": "...",
    "dosage_form": "...",
    "route": "..."
  },
  "evaluated_fields": [
    "active_ingredient",
    "strength",
    "dosage_form",
    "route"
  ],
  "source_url": "...",
  "source_item_number": 1,
  "pncp_control_number": "...",
  "label_status": "frozen_medications_v4",
  "source_description_mode": "source_faithful_excerpt"
}
```

## Checklist antes do congelamento

- [ ] 8 contratações inéditas selecionadas.
- [ ] Colisão contra `medications-v1.jsonl` verificada.
- [ ] Colisão contra `medications-v2.jsonl` verificada.
- [ ] Colisão contra `medications-v3.jsonl` verificada.
- [ ] 48 exemplos revisados.
- [ ] 192 campos esperados revisados.
- [ ] Nenhum tuning aplicado antes da primeira medição.
- [ ] Dataset congelado com commit e blob SHA.
- [ ] Baseline v4 registrada em JSON.
- [ ] Documento `docs/benchmark-medications-v4.md` criado após a medição.

## Critério de promoção do domínio

Mesmo que o v4 atinja resultado alto, o domínio só deve sair de `benchmark_required` se a nova baseline independente confirmar estabilidade em princípio ativo, não apenas em concentração, forma e via.

Como referência interna, o campo de princípio ativo permanece o principal gargalo consolidado dos ciclos v1–v3.
