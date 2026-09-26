# Dataset independente de atributos técnicos v1

O arquivo `technical-attributes-v1.jsonl` foi congelado antes da medição da baseline.

## Objetivo

Medir a extração de atributos técnicos separadamente da taxonomia principal.

Cada linha define explicitamente quais campos foram revisados por meio de `evaluated_attributes`. Um valor `null` em `expected_attributes` significa que o campo foi revisado e não está explicitamente informado na descrição.

## Fontes

A amostra usa oito contratações públicas que não participaram dos benchmarks v1 a v5:

- Ministério Público do Estado do Pará, PNCP `05054960000158-1-000037/2026`;
- Fundo Municipal de Saúde de Petrolina de Goiás/GO, PNCP `10839115000128-1-000138/2026`;
- Município de Morretes/PR, PNCP `76022490000199-1-000045/2026`;
- Fundo Municipal de Saúde de Aparecida de Goiânia/GO, PNCP `11809185000104-1-000021/2026`;
- Universidade de São Paulo, Ribeirão Preto/SP, PNCP `63025530000104-1-002467/2026`;
- Município de Quarto Centenário/PR, PNCP `01619104000141-1-000122/2026`;
- Município de Pinhal Grande/RS, PNCP `94444346000122-1-000159/2026`;
- Estado da Bahia, Polícia Militar, PNCP `13937032000160-1-002282/2026`.

## Composição

- 33 exemplos;
- descrições públicas;
- rótulos manuais baseados somente no conteúdo explícito das descrições;
- campos positivos e negativos;
- URLs e números de controle preservados;
- nenhuma alteração das regras de atributos entre o congelamento e a primeira medição.

## Campos avaliados

- `resin_technology`;
- `curing_mode`;
- `adhesive_strategy`;
- `ionomer_use`;
- `fluoride_formulation`;
- `anesthetic_active_ingredient`;
- `anesthetic_vasoconstrictor`.

## Regra metodológica

A baseline inicial deve ser preservada integralmente.

Erros observados só podem orientar mudanças depois que o resultado independente for registrado. O holdout v5 da taxonomia permanece separado e não é reutilizado aqui.
