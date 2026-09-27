# Revisão da arquitetura de regras e contextos

## Objetivo

Avaliar se o motor de identidade técnica ainda deve crescer dentro de um único parser baseado em listas de termos, exceções e precedência implícita.

## Estado atual

O núcleo de identidade está concentrado em:

- `identity/parser.py`;
- `identity/models.py`;
- `identity/engine.py`;
- `identity/physical.py`.

A avaliação técnica está separada em `evaluation/technical.py` e `evaluation/runner.py`.

O parser atual combina no mesmo módulo:

- normalização semântica posterior à normalização textual;
- aliases de categoria;
- regras de atributos;
- exclusões contextuais;
- precedência entre famílias;
- tratamento de negação;
- regras de ambiguidade;
- exceções introduzidas por holdouts específicos.

Essa abordagem foi adequada para construir e validar rapidamente a taxonomia inicial, mas a sequência v1–v11 mostra que o custo de adicionar novas regras está aumentando.

## Riscos identificados

### Precedência implícita

A ordem em `_classify_category` funciona como parte da regra de negócio.

Uma nova condição adicionada antes de outra pode mudar resultados sem que isso fique evidente na declaração da regra.

### Alias e contexto misturados

Uma lista de aliases responde “que forma lexical identifica a categoria”.

Uma exclusão responde “em que contexto essa forma não representa a categoria”.

Hoje ambas coexistem no mesmo fluxo e dependem de condicionais específicos.

### Crescimento de exceções locais

Casos como:

- marca de referência;
- composição subordinada;
- cimento com óxido de zinco;
- selante citando resina;
- alternativas explícitas;
- conflito entre vasoconstritores;

são semanticamente diferentes, mas terminam tratados como condicionais vizinhas.

### Risco de overfitting lexical

Cada holdout pode sugerir um novo alias muito específico.

Sem uma camada de abstração, o parser pode atingir regressão perfeita nos conjuntos conhecidos sem melhorar proporcionalmente a generalização.

### Dificuldade para expansão multidomínio

Odontologia já exige um conjunto substancial de regras próprias.

Adicionar medicamentos, equipamentos, alimentos, materiais de construção ou outros domínios no mesmo `parser.py` criaria acoplamento e precedências difíceis de auditar.

## Decisão arquitetural

**Não continuar expandindo indefinidamente o parser monolítico.**

O motor baseado em regras continua apropriado para o estágio atual porque oferece:

- explicabilidade;
- rastreabilidade;
- baixo custo operacional;
- testes determinísticos;
- facilidade de auditoria.

A mudança recomendada não é substituir regras por ML neste momento. É tornar o motor de regras **declarativo, modular e auditável**.

## Arquitetura-alvo

### 1. Normalização lexical

Responsável somente por forma textual:

- acentos;
- espaços;
- separadores;
- hífens;
- pontuação interna;
- abreviações controladas;
- erros ortográficos aprovados.

Essa camada não decide categoria.

### 2. Registro declarativo de regras

Criar uma estrutura como `RuleSpec` contendo, no mínimo:

- `rule_id`;
- domínio;
- categoria alvo;
- evidências positivas;
- evidências negativas;
- prioridade explícita;
- tipo de contexto;
- versão de introdução;
- benchmark que motivou a regra.

As regras deixam de depender apenas da posição física no arquivo.

### 3. Detectores de contexto

Separar funções reutilizáveis para:

- produto principal versus composição;
- marca de referência;
- material acessório;
- negação;
- alternativa explícita;
- conflito entre valores;
- kit misto;
- aplicação ou indicação que apenas cita outro material.

### 4. Geração de candidatos

Em vez de retornar a primeira categoria encontrada, o parser deve produzir candidatos com evidências.

Exemplo conceitual:

`Candidate(category, rule_id, evidence, priority, exclusions)`

### 5. Resolução

Uma etapa posterior resolve os candidatos com regras explícitas de:

- prioridade;
- exclusão;
- ambiguidade;
- conflito.

Quando a evidência não for suficiente, o resultado deve permanecer `unknown` em vez de escolher uma categoria por ordem incidental.

### 6. Extração de atributos

Atributos continuam condicionados à categoria resolvida.

Funções de ambiguidade devem ser compartilhadas para evitar padrões diferentes entre:

- tecnologia de resina;
- vasoconstritor;
- formulação de flúor;
- modo de cura;
- estratégia adesiva.

### 7. Domínios isolados

A estrutura deve permitir algo como:

`identity/rules/dental/`

e, futuramente:

`identity/rules/<novo_dominio>/`

O núcleo compartilhado resolve candidatos e contexto sem conhecer detalhes de cada setor.

## Plano de refatoração

### Fase A: refatoração sem mudança de comportamento

Prioridade imediata.

- extrair constantes e aliases de `parser.py`;
- criar registro de regras;
- manter exatamente os mesmos resultados atuais;
- executar regressão sobre datasets congelados;
- não adicionar novos aliases durante essa fase.

### Fase B: normalização lexical controlada

- centralizar pontuação e separadores;
- representar abreviações/typos aprovados em tabela própria;
- remover aliases duplicados que diferem apenas pela forma normalizável.

### Fase C: candidatos e resolução

- substituir first-match implícito por evidência + prioridade;
- centralizar exclusões contextuais;
- tornar ambiguidade um estado explícito.

### Fase D: arquitetura multidomínio

- mover odontologia para um pacote de regras do domínio;
- definir interface comum para novos domínios;
- impedir que regra de um domínio afete outro.

## Guardrails obrigatórios

Antes e depois de cada fase:

- datasets congelados não podem ser alterados;
- baselines históricas não podem ser regravadas;
- SHAs de artefatos históricos devem permanecer estáveis;
- regressões pós-tuning protegidas devem ser executadas;
- qualquer mudança de saída precisa ter justificativa e benchmark independente.

## Relação com o v12

O v12 já foi congelado e medido contra o parser v1.34.

A recomendação é realizar **a Fase A de forma comportamentalmente neutra antes do tuning do v12**.

Isso cria uma base modular para corrigir as lacunas do v12 sem continuar aumentando o parser monolítico.

Se a Fase A mudar qualquer saída dos holdouts protegidos, ela não é uma refatoração neutra e deve ser corrigida antes de prosseguir.

## O que não fazer agora

- não introduzir modelo de linguagem na classificação principal;
- não treinar ML nos próprios holdouts congelados;
- não substituir `unknown` por adivinhação probabilística;
- não misturar regras de novos domínios dentro das tabelas odontológicas;
- não transformar o benchmark em teste que obrigue os erros históricos a permanecerem no parser atual.

## Próxima decisão técnica

O próximo incremento estrutural recomendado é:

**refatorar o motor de regras sem mudança de comportamento, validar regressões, e somente depois executar o tuning do v12.**
