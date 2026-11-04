# Validação controlada de identidade do visitante no Render

> **Estado em 04/11/2026:** procedimento preparado para a issue #76 / PR #78. **Não executado na produção.** Nenhum passo deste documento autoriza deploy, mudança de variáveis ou tráfego de teste contra o serviço público.

## Hipótese documentada e limite da evidência

A [documentação de variáveis do Render](https://render.com/docs/environment-variables) indica `FORWARDED_ALLOW_IPS=*` em Python 3. Assim, o endereço ASGI pode ser afetado por cabeçalhos encaminhados: **não** usar `request.client.host` como prova de identidade autêntica no Render.

O [guia oficial de PocketBase no Render](https://render.com/articles/host-pocketbase-on-render) afirma que requisições a web services públicos passam pelo Cloudflare e que ele sobrescreve `CF-Connecting-IP` com o IP do visitante. Isso fundamenta a hipótese de segurança, mas não demonstra sozinho a topologia da instância específica, seus caminhos alternativos de ingresso ou configurações de runtime.

Nas mensagens de suporte consultadas até 04/11/2026, havia apenas respostas automáticas. Ainda falta confirmação técnica individual, ou validação operacional autorizada de staging.

## Escolha arquitetural que permanece pendente

O PR #78 suporta:

- **Modo não confiável:** `RENDER=true` e `ATLAS_TRUST_CF_CONNECTING_IP` ausente ou falso. Ignora os IPs de headers, porém **todos os usuários dividem 60 normalizações por 60 segundos por instância**. Seguro contra rotação simples de `X-Forwarded-For`, mas vulnerável à indisponibilidade de usuários legítimos por saturação da cota comum.
- **Modo com ingresso CF confiável:** `ATLAS_TRUST_CF_CONNECTING_IP=true` e `RENDER=true`. Usa um IP canônico por visitante; cabeçalho ausente, duplicado ou inválido gera HTTP 400; 60 normalizações/minuto por identidade, **por instância**. Exige contrato de ingresso confiável validado antes de habilitar.
- **Sem identidade de rede confiável:** usar controle gerenciado na borda ou autenticação/identidade comprovada. Não declarar o limitador como `por IP` se todos compartilham um único bucket.

## Experimento somente em ambiente de teste isolado

**Pré-condições:** obter autorização para criar/deployar uma instância separada da produção, sem dados privados; sem copiar segredos de produção; definir um teto de requisições; confirmar que não haverá auto-deploy para `main`. O ambiente precisa executar exatamente o commit aprovado do PR #78 e registrar apenas categorias/contagens, sem IPs brutos nem headers nos logs.

1. **Identidade constante, headers forjados:** de uma origem de teste A, executar chamadas de normalização em staging variando `X-Forwarded-For` e o valor fornecido pelo cliente em `CF-Connecting-IP`. Com o modo de confiança CF ativado e ingressando pelo hostname público do staging, espera-se 60 respostas permitidas na janela e HTTP 429 nas seguintes, independentemente dos valores forjados. Isso sugere que a borda substitui o header; não demonstra, sozinho, ausência de vias alternativas de acesso.
2. **Independência de visitantes:** antes do fim da janela de A, uma origem legítima de teste B, com IP público diferente e conexão separada, deve conseguir normalizar (HTTP 200), sem consumir a cota de A. Duas janelas/identidades devem continuar independentes.
3. **Cenários malformados:** executar testes unitários e HTTP locais já versionados para headers duplicados, lista de IPs, porta, escopo IPv6, header ausente e `X-Forwarded-For` falsificado. Em modo confiável, entradas CF inválidas precisam gerar HTTP 400 antes de consumir tokens. Não contar com a possibilidade de enviar headers falsos até a aplicação pela borda real, pois o Cloudflare pode sobrescrevê-los.
4. **Carga e memória:** confirmar que os buckets expiram, o limite de 4.096 identidades é respeitado e a resposta 429 inclui `Retry-After`. A capacidade do limitador por instância **não equivale** a limite distribuído para várias réplicas.
5. **Caminho de ingresso:** confirmar por documentação atualizada do provedor ou suporte técnico que todo tráfego público destinado ao serviço passa por um proxy que substitui `CF-Connecting-IP` e que não existe rota pública alternativa capaz de fazer a aplicação aceitar esse header fornecido pelo solicitante. Este requisito não é comprovado apenas pelo comportamento de 60 requisições.

A coleta deve registrar exclusivamente versão testada, horário UTC, flags relevantes, contagens 200/400/429, se houve separação A/B e conclusão do teste. Não guardar IPs pessoais, valores de headers, tokens ou payloads pessoais.

## Critérios de aceite do PR #78

- [ ] Confiança de ingresso e ausência de bypass confirmadas para a arquitetura efetiva do serviço;
- [ ] Testes locais e staging aprovados, incluindo duas origens independentes;
- [ ] Falhas 400/429, cota e expiração verificados sem vazamento de dados;
- [ ] Decisão explícita de operação quanto ao risco de indisponibilidade da cota compartilhada;
- [ ] Compatibilidade da configuração com o número de instâncias/workers confirmada;
- [ ] CI e CodeQL aprovados no último commit e revisão de segurança concluída;
- [ ] Plano de reversão aprovado antes de qualquer publicação.

**Não integrar automaticamente este PR nem habilitar `ATLAS_TRUST_CF_CONNECTING_IP` em produção com base apenas nos testes simulados.** A issue #76 permanece aberta até validação efetiva.
