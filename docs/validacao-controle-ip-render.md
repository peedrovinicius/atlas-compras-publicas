# Validação controlada de identidade do visitante no Render

> **Estado em 04/11/2026:** procedimento preparado para a issue #76 / PR #78. **Não executado na produção.** Nenhum passo deste documento autoriza deploy, mudança de variáveis ou tráfego de teste contra o serviço público.

## Hipótese documentada e limite da evidência

A [documentação de variáveis do Render](https://render.com/docs/environment-variables) indica `FORWARDED_ALLOW_IPS=*` em Python 3. Assim, o endereço ASGI pode ser afetado por cabeçalhos encaminhados: **não** usar `request.client.host` como prova de identidade autêntica no Render.

O [guia oficial de PocketBase no Render](https://render.com/articles/host-pocketbase-on-render) afirma que requisições a web services públicos passam pelo Cloudflare e que ele sobrescreve `CF-Connecting-IP` com o IP do visitante. Isso fundamenta a hipótese de segurança, mas não demonstra sozinho a topologia da instância específica, seus caminhos alternativos de ingresso ou configurações de runtime.

Em 04/11/2026 às 15:10:53 UTC, uma resposta de suporte do Render informou por e-mail que o tráfego público passa pelo Cloudflare e pelos balanceadores do Render; que requisições públicas com `CF-Connecting-IP` fornecido pelo cliente são rejeitadas pelo Cloudflare; e que não se deve usar `X-Forwarded-For`. Confirmou também que requisições pela rede privada do mesmo workspace/região **não passam pelo Cloudflare** e podem carregar `CF-Connecting-IP` definido pelo serviço chamador. O suporte declarou que **não há mecanismo fornecido para distinguir na aplicação requisições internas de externas**. A resposta confirma a política declarada para o caminho público, mas **não autoriza confiar indistintamente em `CF-Connecting-IP` em todos os caminhos de ingresso**. A mensagem não identifica explicitamente seu autor como engenheiro humano. O suporte não informou o valor efetivo de `FORWARDED_ALLOW_IPS` nesta instância. A validação operacional de staging permanece pendente.

## Situação atual da instância Free (confirmada em 04/11/2026)

A leitura do serviço `atlas-compras-publicas-analytics` no Render indica **plano Free, uma instância, região Virginia, deploy em `main`**. A [documentação atual de serviços gratuitos](https://render.com/docs/free) e a [matriz de rede privada](https://render.com/articles/how-render-handles-private-networking) estabelecem que web services gratuitos **não recebem requisições pela rede privada**, embora possam iniciar conexões privadas para outros serviços.

Assim, a exceção de `CF-Connecting-IP` definido por serviços internos **não se aplica ao ingresso da API no plano Free atual**; o tráfego público segue a garantia comunicada pelo suporte de que valores fornecidos pelo solicitante são rejeitados pelo Cloudflare. Isso **não autoriza ativar a flag sem staging**, nem comprova endereços e regras internas de uma possível infraestrutura diferente. Se o serviço for migrado para um plano que aceite tráfego privado, **desabilitar `ATLAS_TRUST_CF_CONNECTING_IP` e reavaliar o limite de confiança antes da migração**; o flag isolado não distingue tráfego público de privado.

## Escolha arquitetural que permanece pendente

O PR #78 suporta:

- **Modo não confiável:** `RENDER=true` e `ATLAS_TRUST_CF_CONNECTING_IP` ausente ou falso. Ignora os IPs de headers, porém **todos os usuários dividem 60 normalizações por 60 segundos por instância**. Seguro contra rotação simples de `X-Forwarded-For`, mas vulnerável à indisponibilidade de usuários legítimos por saturação da cota comum.
- **Modo com ingresso CF confiável:** `ATLAS_TRUST_CF_CONNECTING_IP=true` e `RENDER=true`. Usa um IP canônico por visitante; cabeçalho ausente, duplicado ou inválido gera HTTP 400; 60 normalizações/minuto por identidade, **por instância**. **No Free atual, o ingresso privado é proibido pelo Render; isso precisa ser confirmado novamente no gate de release.** Não habilitar se o serviço passar a aceitar tráfego privado capaz de definir esse header, pois o código não distingue ingressos internos e públicos.
- **Sem identidade de rede confiável:** usar controle gerenciado na borda ou autenticação/identidade comprovada. Não declarar o limitador como `por IP` se todos compartilham um único bucket.

## Experimento somente em ambiente de teste isolado

**Pré-condições:** obter autorização para criar/deployar uma instância separada da produção, sem dados privados; sem copiar segredos de produção; definir um teto de requisições; confirmar que não haverá auto-deploy para `main`. O ambiente precisa executar exatamente o commit aprovado do PR #78 e registrar apenas categorias/contagens, sem IPs brutos nem headers nos logs.

1. **Identidade constante, `X-Forwarded-For` forjado:** de uma origem de teste A, executar chamadas de normalização em staging variando **apenas** `X-Forwarded-For`, sem enviar manualmente `CF-Connecting-IP`. Com o modo de confiança CF ativado e ingressando pelo hostname público do staging, espera-se uma cota de 60 respostas permitidas por minuto e HTTP 429 depois do limite, independentemente de `X-Forwarded-For`.
2. **`CF-Connecting-IP` fornecido pelo cliente:** em uma série **separada, limitada e autorizada**, enviar esse header manualmente e verificar a rejeição **na borda Cloudflare** descrita no e-mail do Render. Não presumir HTTP 200, nem contabilizar essas requisições no teste da cota por visitante; distinguir erro da borda de resposta da aplicação.
3. **Independência de visitantes:** antes do fim da janela de A, uma origem legítima de teste B, com IP público diferente e conexão separada, deve conseguir normalizar (HTTP 200), sem consumir a cota de A. Duas janelas/identidades devem continuar independentes.
4. **Cenários malformados:** executar testes unitários e HTTP locais já versionados para headers duplicados, lista de IPs, porta, escopo IPv6, header ausente e `X-Forwarded-For` falsificado. Em modo confiável, entradas CF inválidas precisam gerar HTTP 400 antes de consumir tokens. Não contar com a possibilidade de enviar headers falsos até a aplicação pela borda real, pois o Cloudflare pode sobrescrevê-los.
5. **Carga e memória:** confirmar que os buckets expiram, o limite de 4.096 identidades é respeitado e a resposta 429 inclui `Retry-After`. A capacidade do limitador por instância **não equivale** a limite distribuído para várias réplicas.
6. **Caminho de ingresso:** confirmar por documentação atualizada do provedor ou suporte técnico que todo tráfego público destinado ao serviço passa por um proxy que substitui `CF-Connecting-IP` e que não existe rota pública alternativa capaz de fazer a aplicação aceitar esse header fornecido pelo solicitante. Este requisito não é comprovado apenas pelo comportamento de 60 requisições.

A coleta deve registrar exclusivamente versão testada, horário UTC, flags relevantes, contagens 200/400/429, se houve separação A/B e conclusão do teste. Não guardar IPs pessoais, valores de headers, tokens ou payloads pessoais.

## Critérios de aceite do PR #78

- [ ] Plano Free, limitação de recebimento de tráfego privado e integridade do ingresso público confirmados novamente para o serviço no gate de release;
- [ ] Testes locais e staging aprovados, incluindo duas origens independentes;
- [ ] Falhas 400/429, cota e expiração verificados sem vazamento de dados;
- [ ] Decisão explícita de operação quanto ao risco de indisponibilidade da cota compartilhada;
- [ ] Compatibilidade da configuração com o número de instâncias/workers confirmada;
- [ ] CI e CodeQL aprovados no último commit e revisão de segurança concluída;
- [ ] Plano de reversão aprovado antes de qualquer publicação.

**Não integrar automaticamente este PR nem habilitar `ATLAS_TRUST_CF_CONNECTING_IP` em produção com base apenas nos testes simulados.** A issue #76 permanece aberta até validação efetiva.
