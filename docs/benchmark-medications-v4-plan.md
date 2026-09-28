# Plano do holdout independente de medicamentos v4

## Objetivo

Construir o quarto holdout independente do domínio de medicamentos sem reutilizar processos, itens ou descrições dos benchmarks v1, v2 e v3.

O v4 mede a generalização do parser após a v1.48, antes de qualquer novo ajuste de regras. A baseline v4 só será válida porque o dataset foi congelado antes da primeira execução.

## Estado de partida

- Medicamentos v1: baseline independente preservada em 87,50%.
- Medicamentos v2: baseline independente preservada em 79,69%.
- Medicamentos v3: baseline independente preservada em 90,10%.
- Regressões pós-tuning v1, v2 e v3: 192/192 campos corretos em cada conjunto.
- Domínio: `benchmark_required`.

## Regra principal

Nenhuma correção do parser foi feita durante a construção do v4.

A ordem metodológica aplicada foi:

1. selecionar fontes públicas independentes;
2. checar colisão contra v1, v2 e v3;
3. montar o dataset v4;
4. congelar o arquivo `data/evaluation/medications-v4.jsonl`;
5. registrar o blob SHA e o commit de congelamento;
6. executar a primeira medição com o parser vigente sem alteração;
7. documentar a baseline independente;
8. só depois decidir se haverá tuning posterior.

Os itens 1 a 5 estão concluídos. Os itens 6 a 8 pertencem à próxima etapa.

## Inventário, colisão e congelamento

Documentos da trilha metodológica:

- [Pré-candidatos de fontes para medicamentos v4](medications-v4-candidate-sources.md)
- [Checagem de colisão do holdout de medicamentos v4](medications-v4-collision-check.md)
- [Triagem de itens para medicamentos v4](medications-v4-item-triage.md)
- [Congelamento do holdout de medicamentos v4](medications-v4-freeze.md)

## Critérios de independência

Um candidato ao v4 foi excluído quando:

- usava o mesmo número de controle PNCP de v1, v2 ou v3;
- reutilizava item já amostrado nos ciclos anteriores;
- repetia descrição idêntica ou praticamente idêntica a exemplo anterior;
- dependia de normalização manual feita em ciclo anterior;
- vinha de fonte sem descrição pública mínima para revisão.

## Composição final

O v4 foi congelado com:

- 48 exemplos;
- 8 fontes públicas;
- 192 campos avaliados;
- 4 campos por exemplo:
  - princípio ativo;
  - concentração;
  - forma farmacêutica;
  - via de administração.

## Decisão sobre distribuição

O desenho inicial previa 8 contratações com 6 itens por contratação. Durante a triagem, a distribuição foi ajustada para preservar somente descrições verificáveis nas fontes públicas abertas.

A composição final mantém 48 exemplos e 192 campos, mas com distribuição desigual entre fontes. Essa decisão foi registrada para evitar preenchimento artificial de exemplos e preservar a auditabilidade do holdout.

## Prioridades de amostragem preservadas

O v4 mantém pressão sobre os pontos que diferenciam baseline de regressão perfeita:

- associações de princípios ativos;
- sais e qualificadores após vírgula;
- composições descritas em campos semiestruturados;
- abreviações reais de forma farmacêutica;
- formas ambíguas entre oral, tópico, oftálmico e injetável;
- concentração sem unidade explícita;
- descrições curtas com pouca redundância;
- descrições longas com repetição do produto;
- medicamentos com apresentação explícita, mas sem via direta.

## Campos mínimos do JSONL

Cada linha do v4 mantém o contrato usado nos ciclos anteriores:

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

## Checklist antes do benchmark

- [x] Fontes públicas selecionadas.
- [x] Colisão por número de controle contra `medications-v1.jsonl` verificada.
- [x] Colisão por número de controle contra `medications-v2.jsonl` verificada.
- [x] Colisão por número de controle contra `medications-v3.jsonl` verificada.
- [x] Triagem item a item concluída.
- [x] `data/evaluation/medications-v4.jsonl` criado.
- [x] 48 exemplos revisados.
- [x] 192 campos esperados revisados.
- [x] Nenhum tuning aplicado antes da primeira medição.
- [x] Dataset congelado com commit e blob SHA.
- [ ] Baseline v4 registrada em JSON.
- [ ] Documento `docs/benchmark-medications-v4.md` criado após a medição.

## Critério de promoção do domínio

Mesmo que o v4 atinja resultado alto, o domínio só deve sair de `benchmark_required` se a nova baseline independente confirmar estabilidade em princípio ativo, não apenas em concentração, forma e via.

Como referência interna, o campo de princípio ativo permanece o principal gargalo consolidado dos ciclos v1–v3.
