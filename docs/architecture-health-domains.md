# Arquitetura de domínios de saúde

## Decisão

O namespace histórico `medications` permanece restrito a medicamentos.

Ele não será renomeado para `health_products` e não será usado como guarda-chuva para materiais, dispositivos ou outros insumos de saúde.

Novos tipos de produto de saúde deverão entrar em domínios próprios, com taxonomia, regras e benchmarks independentes.

## Evidência da auditoria

Foram revisados os quatro holdouts congelados:

| Dataset | Exemplos | Campos avaliados |
| --- | ---: | ---: |
| medications-v1 | 48 | 192 |
| medications-v2 | 48 | 192 |
| medications-v3 | 48 | 192 |
| medications-v4 | 48 | 192 |
| **Total** | **192** | **768** |

Dos 192 exemplos:

- 191 possuem princípio ativo esperado explicitamente;
- 1 exemplo, `BENESTARE 625 MG CPR`, não possui princípio ativo rotulado, mas é apresentado como comprimido oral;
- os casos de fronteira identificados continuam farmacológicos: formulações tópicas, oftálmicas, injetáveis, anestésicos em tubete e medicamentos acompanhados de diluente;
- não foram identificados dispositivos médicos, materiais clínicos ou insumos não farmacológicos nos holdouts v1-v4.

Conclusão: o problema arquitetural não está nos datasets congelados. Ele está no risco de usar o nome `medications` como domínio amplo para qualquer produto de saúde futuro.

## Fronteiras propostas

### dental

Produtos odontológicos estruturados pela taxonomia atual do Atlas.

Exemplos:

- resinas;
- adesivos;
- ionômeros;
- alginatos;
- materiais radiográficos;
- materiais preventivos e restauradores.

### medications

Medicamentos e formulações farmacêuticas.

Atributos próprios:

- princípio ativo;
- concentração ou dosagem;
- forma farmacêutica;
- via de administração.

O parser e os benchmarks v1-v4 permanecem aqui.

### medical_devices

Reservado para dispositivos médicos.

Não deve reutilizar regras farmacêuticas apenas porque o item pertence ao setor de saúde.

Status inicial: não implementado.

### health_materials

Reservado para materiais e consumíveis clínicos de saúde que não sejam medicamentos nem dispositivos.

Status inicial: não implementado.

### health_other

Categoria de triagem para futuros itens de saúde cuja fronteira ainda não tenha taxonomia validada.

Não deve ser ativada como classificador automático sem benchmark próprio.

## Regras de arquitetura

1. Um domínio não é definido pelo órgão comprador, mas pelo tipo de produto.
2. Estar em uma licitação de saúde não transforma o item em medicamento.
3. Cada domínio possui regras, atributos e benchmark independentes.
4. Nenhum domínio novo entra em `active` sem dataset congelado e baseline independente.
5. Artefatos históricos não são renomeados retroativamente.
6. Compatibilidade é preferível a rename destrutivo.
7. A API deve distinguir domínio suportado de domínio planejado.

## Preservação histórica

Os seguintes artefatos permanecem com o nome `medications`:

- `data/evaluation/medications-v1.jsonl` a `medications-v4.jsonl`;
- respectivas baselines e pós-tuning;
- documentos de benchmark já publicados;
- `parse_medication`;
- testes históricos que validam os resultados publicados.

Isso preserva hashes, referências em documentação e reprodutibilidade.

## Migração do código atual

### Agora

- manter `IdentityDomain.MEDICATIONS`;
- manter `parse_medication`;
- corrigir documentação que descreve medicamentos como "próximo domínio" ou como namespace vazio;
- marcar medicamentos como domínio experimental validado por benchmark, sem misturá-lo ao parser odontológico principal;
- impedir documentação futura de usar `medications` como sinônimo de produtos de saúde.

### Depois

Quando houver dataset real de outro tipo de produto:

1. criar novo domínio explícito;
2. congelar holdout;
3. medir baseline antes de tuning;
4. criar regras próprias;
5. adicionar descriptor ao registro;
6. só então expor o domínio como suportado pela API.

## O que não será feito

- renomear v1-v4;
- mover medicamentos para um domínio genérico `health_products`;
- classificar materiais ou dispositivos com `parse_medication`;
- criar `medications-v5` antes de uma necessidade real de benchmark farmacêutico;
- inferir taxonomias de materiais e dispositivos sem dados independentes.

## Resultado da issue #30

A auditoria conclui que a série v1-v4 é coerente com o domínio farmacêutico.

A reorganização necessária é de fronteiras e documentação, não de reclassificação retroativa dos 192 exemplos.
