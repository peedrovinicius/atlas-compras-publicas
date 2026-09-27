# Arquitetura multidomínio

## Objetivo

Separar o motor de identidade do domínio odontológico e permitir a entrada de novos domínios sem misturar regras, precedências ou benchmarks.

## Registro de domínios

O pacote agora possui um registro explícito em `identity/domains.py`.

Domínios atuais:

| Domínio | Status | Regras ativas |
| --- | --- | --- |
| Odontologia | active | sim |
| Medicamentos | benchmark_required | não |

## Regra de ativação

Um novo domínio só pode passar para `active` depois de:

1. definir sua taxonomia;
2. congelar dataset independente;
3. revisar rótulos;
4. medir uma baseline sem tuning;
5. criar regressões próprias;
6. documentar conflitos com outros domínios.

## Medicamentos

Medicamentos foi escolhido como o próximo domínio por ter forte presença em compras públicas e atributos próprios, como princípio ativo, concentração, forma farmacêutica e apresentação.

A v1.38 cria apenas o namespace e o registro do domínio.

Nenhum alias ou classificador de medicamentos foi ativado nesta release. Isso é intencional: o projeto não deve inferir uma taxonomia não validada apenas para aparentar cobertura multidomínio.

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

Criar uma taxonomia inicial e um benchmark independente antes de ativar qualquer classificação.
