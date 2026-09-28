# Arquitetura multidomínio

## Objetivo

Separar o motor de identidade do domínio odontológico e permitir a entrada de novos domínios sem misturar regras, precedências ou benchmarks.

## Registro de domínios

O pacote agora possui um registro explícito em `identity/domains.py`.

Domínios atuais:

| Domínio | Status | Regras ativas |
| --- | --- | --- |
| Odontologia | active | sim |
| Medicamentos | experimental | não |

## Regra de ativação

Um novo domínio só pode passar para `active` depois de:

1. definir sua taxonomia;
2. congelar dataset independente;
3. revisar rótulos;
4. medir uma baseline sem tuning;
5. criar regressões próprias;
6. documentar conflitos com outros domínios.

## Medicamentos

O domínio farmacêutico possui parser próprio e quatro holdouts independentes congelados, v1-v4, com regressões preservadas.

Ele permanece como `experimental` porque ainda não participa do classificador principal de produtos do Atlas. O objetivo é validar generalização da arquitetura sem misturar regras odontológicas e farmacêuticas.

A auditoria da issue #30 confirmou que os 192 exemplos históricos pertencem ao escopo farmacêutico. Materiais, dispositivos e outros produtos de saúde deverão entrar em domínios próprios.

## Isolamento

As regras odontológicas continuam em `identity/rules/dental.py`.

O namespace de medicamentos está reservado em `identity/rules/medications.py`.

Esse isolamento permite que, futuramente, cada domínio tenha:

- regras próprias;
- atributos próprios;
- benchmarks próprios;
- versão de introdução;
- regressões independentes.

## Próximo passo do domínio de medicamentos

Manter o histórico v1-v4 preservado e só promover o domínio para `active` quando houver integração explícita com o motor multidomínio, regras de precedência e contrato público estável.

A fronteira completa está documentada em [Arquitetura de domínios de saúde](architecture-health-domains.md).
