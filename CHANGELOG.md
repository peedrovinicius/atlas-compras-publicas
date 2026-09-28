# Changelog

Este arquivo registra mudanças públicas relevantes do Atlas de Compras Públicas. Benchmarks e auditorias detalhadas permanecem documentados em `docs/`.

## 1.68.0

- busca de produtos passa a oferecer ordenação por relevância estruturada como padrão;
- categoria interpretada, cor e apresentação passam a contribuir para o score de relevância;
- autocomplete usa a mesma ordenação por relevância;
- aliases de apresentação em português passam a resolver valores estruturados como `syringe`, `bottle`, `cartridge` e `ampoule`;
- `tubete` e `carpule` passam a localizar apresentações normalizadas como `cartridge`;
- resultados expõem motivos de correspondência, como categoria, cor e apresentação;
- seleção direta do autocomplete limpa facets da busca anterior;
- regressões adicionadas para relevância, aliases e explicação dos matches;
- pacote, API, cliente PNCP e frontend sincronizados em 1.68.0.

## 1.67.0

- endpoint `/ready` valida a disponibilidade real do DuckDB e da tabela `silver_awards`;
- `/health` permanece como liveness simples da aplicação;
- configuração canônica de produção adicionada em `render.yaml`;
- Blueprint oficial define apenas frontend e API analítica;
- auto-deploy canônico passa a aguardar CI com `checksPass`;
- build da API pública usa amostra PNCP limitada e caminho explícito do DuckDB;
- frontend e documentação permanecem apontados para `atlas-compras-publicas-analytics`;
- pacote, API, cliente PNCP e frontend sincronizados em 1.67.0.

## 1.66.0

- Explorador de preços passa a exibir todas as categorias conhecidas que possuem observações de preço;
- cada categoria mostra quantidade de grupos comparáveis e observações de preço;
- categorias digitadas compatíveis continuam sendo priorizadas como sugestão;
- rótulo de exemplo rápido `Caso difícil` removido do Laboratório;
- pacote, API, cliente PNCP e frontend sincronizados em 1.66.0.

## 1.65.0

- skip link adicionado para acesso direto ao conteúdo principal;
- alternância Preços/Laboratório expõe estado ativo com `aria-pressed`;
- status da API passa a usar região de status acessível;
- resultados de busca anunciam quantidade encontrada sem poluir a interface;
- erros de busca passam a usar `role="alert"`;
- análise detalhada recebe foco após abertura de produto;
- resultados do Laboratório recebem foco após normalização concluída;
- seções principais expõem estado de carregamento com `aria-busy`;
- foco visível de inputs, selects e regiões interativas padronizado;
- preferência `prefers-reduced-motion` reduz animações e rolagem suave;
- pacote, API, cliente PNCP e frontend sincronizados em 1.65.0.

## 1.64.0

- ações secundárias da análise agrupadas em menu compacto;
- copiar link e exportar CSV deixam de competir visualmente com status e atualização;
- tabela mensal do histórico passa a ficar recolhida por padrão, mantendo o gráfico em destaque;
- tabela de sinais estatísticos passa a ser exibida sob demanda;
- quantidade de registros de evidência mostrada explicitamente no recorte;
- descrições das evidências limitadas na visão fechada e expandidas ao abrir;
- evidências passam para uma coluna em telas pequenas;
- hashes e metadados de evidência reorganizados para mobile;
- pacote, API, cliente PNCP e frontend sincronizados em 1.64.0.

## 1.63.0

- Laboratório deixa de carregar e analisar um exemplo automaticamente ao abrir o site;
- entrada do parser passa a iniciar vazia e focada na ação do usuário;
- seção de resultados só aparece após uma análise;
- aviso de cold start/plano gratuito removido da interface pública;
- botão de análise desabilitado quando não há entrada válida ou quando o limite de 20 descrições é excedido;
- hero, painéis, categorias e resultados do Laboratório alinhados ao sistema visual do Explorador;
- alturas fixas removidas dos painéis do Laboratório;
- categorias e resultados técnicos ficam mais compactos em desktop e mobile;
- pacote, API, cliente PNCP e frontend sincronizados em 1.63.0.

## 1.62.0

- atalho `/` ou `Ctrl/Cmd+K` foca e seleciona o campo principal de busca;
- o atalho é ignorado quando o usuário já está digitando em input, textarea, select ou área editável;
- indicação visual discreta do atalho no campo de busca em desktop;
- descrições de resultados longas passam a ser limitadas a duas linhas;
- foco visível melhorado nos cartões de resultado;
- ação textual simplificada de `Abrir análise` para `Ver análise`;
- cards mobile mais compactos, com preço e ação na mesma linha;
- pacote, API, cliente PNCP e frontend sincronizados em 1.62.0.

## 1.61.0

- home do Explorador deixa de executar busca automática por `resina`;
- resultados só aparecem após pesquisa, categoria ou link compartilhado;
- primeira dobra fica focada em proposta de valor, busca e categorias;
- botões de pesquisa e aplicação de filtros só habilitam com termo válido;
- limpar filtros na home vazia não dispara erro de busca;
- URLs compartilhadas continuam restaurando pesquisa e produto normalmente;
- pacote, API, cliente PNCP e frontend sincronizados em 1.61.0.

## 1.60.0

- visão geral passa a abrir com resumo executivo em vez de seis cards equivalentes;
- mediana do preço normalizado ganha destaque principal;
- faixa central é apresentada como contexto direto da mediana;
- compras, fornecedores, UFs e período passam a ocupar uma camada secundária;
- data de atualização aparece no cabeçalho da análise;
- Mercado e Evidências ganham textos de contexto próprios;
- tabelas passam a ter cabeçalho fixo dentro da rolagem e realce de linha;
- listas de ranking e cartões de evidência ganham estados de hover mais claros;
- responsividade ajustada para o novo resumo executivo;
- pacote, API, cliente PNCP e frontend sincronizados em 1.60.0.

## 1.59.0

- análise de produto dividida em Visão geral, Mercado e Evidências;
- Visão geral concentra métricas, distribuição e histórico;
- Mercado concentra geografia, fornecedores e órgãos compradores;
- Evidências concentra sinais estatísticos e registros rastreáveis;
- navegação interna compacta e sticky em desktop;
- botão Voltar aos resultados reduz a rolagem manual após abrir um produto;
- seleção de novo produto retorna automaticamente para Visão geral;
- pacote, API, cliente PNCP e frontend sincronizados em 1.59.0.

## 1.58.0

- reforma visual ampla da interface pública;
- cabeçalho simplificado com navegação focada em Preços e Laboratório;
- hero mais compacto e orientado à proposta de valor;
- busca principal ampliada e visualmente priorizada;
- categorias convertidas em atalhos compactos;
- filtros avançados recolhidos por padrão;
- remoção de exemplos redundantes que competiam com autocomplete e categorias;
- cards de resultado com menos ruído visual e maior destaque para preço mediano;
- área analítica com sombras reduzidas, espaçamento mais consistente e melhor hierarquia;
- novos estados de carregamento em skeleton;
- título e metadados públicos atualizados;
- pacote, API, cliente PNCP e frontend sincronizados em 1.58.0.

## 1.57.0

- busca passa a devolver facetas de refinamento calculadas sobre todo o conjunto compatível;
- refinamentos clicáveis por cor, apresentação, concentração e atributos técnicos;
- contagens das facetas independem da página atual dos resultados;
- pesquisas recentes limitadas a seis consultas e mantidas apenas no `localStorage` do navegador;
- ação explícita para limpar o histórico local;
- refinamentos preservam filtros e ordenação atuais;
- teste de regressão protege as contagens das facetas mesmo com paginação;
- pacote, API, cliente PNCP e frontend sincronizados em 1.57.0.

## 1.56.0

- resultados de busca passam a expor mediana de preço normalizado antes da abertura da análise;
- cartões de resultado mostram compras, observações de preço, UFs e atualização mais recente;
- filtros ativos aparecem como chips removíveis acima dos resultados;
- busca vazia causada por filtros oferece ação para repetir sem o recorte;
- aliases seguros adicionados para termos usuais como `CIV`, `cimento de vidro`, `bonding` e `anestesia local`;
- teste de regressão garante a mediana nos resultados e os novos aliases;
- pacote, API, cliente PNCP e frontend sincronizados em 1.56.0.

## 1.55.0

- busca textual genérica passa a ignorar diferenças de acentuação;
- autocomplete navegável por teclado com setas, Enter e Escape;
- estado ativo das sugestões exposto com atributos ARIA;
- seleção por teclado abre diretamente a análise do produto;
- estado sem resultados oferece atalhos para categorias realmente disponíveis na base;
- teste de regressão para pesquisa sem acento em descrição pública acentuada;
- pacote, API, cliente PNCP e frontend sincronizados em 1.55.0.

## 1.54.0

- autocomplete com até seis produtos reais enquanto o usuário digita;
- sugestões iniciadas a partir de dois caracteres, com debounce de 250 ms;
- sugestões respeitam os filtros ativos do Explorador;
- seleção de sugestão abre diretamente a análise sem etapa intermediária;
- tolerância conservadora a pequenos erros de digitação nos aliases de categorias;
- preferência por expressões específicas quando uma forma curta e uma forma aproximada competem;
- proteção contra classificação de termos não relacionados;
- novos testes dedicados ao resolvedor de aliases;
- pacote, API, cliente PNCP e frontend sincronizados em 1.54.0.

## 1.53.0

- descoberta guiada no Explorador de preços com categorias disponíveis na base;
- atalhos de categoria exibem quantidade de grupos comparáveis e observações de preço;
- aliases em português permitem buscar por nomes humanos sem conhecer a taxonomia interna;
- interpretação específica para resina composta, resina flow, adesivo, ionômero, ácido fosfórico, flúor, anestésico e demais categorias odontológicas atuais;
- buscas amplas como `resina` continuam retornando múltiplos tipos em vez de serem forçadas para uma única categoria;
- interface informa quando a consulta foi reconhecida como uma categoria;
- novos testes de regressão para aliases e descoberta de categorias;
- pacote, API, cliente PNCP e frontend sincronizados em 1.53.0.

## 1.52.0

- ordenação pública por cobertura de preços, quantidade de compras, atualização mais recente ou nome;
- exportação CSV de todos os registros do recorte filtrado, com UTF-8 BOM e metadados de origem;
- estado da exploração serializado na URL para compartilhar pesquisa, filtros, ordenação, página e produto selecionado;
- ação de copiar link da análise diretamente na interface;
- histórico visual nativo com mediana e faixa interquartil, sem dependência adicional de gráficos;
- testes de regressão para ordenação, paginação interna da exportação e resposta CSV;
- pacote, API, cliente PNCP e frontend sincronizados em 1.52.0.

## 1.51.0

- filtros compartilhados por período, macrorregião, UF, fornecedor e órgão/unidade compradora;
- filtros aplicados de forma consistente a resumo, distribuição, histórico, geografia, fornecedores, compradores, sinais e evidências;
- pesquisa de produtos com paginação real por `limit` e `offset`, preservando o total de grupos compatíveis;
- interface pública com controles para aplicar e limpar filtros;
- navegação Anterior/Próxima na lista de produtos;
- testes de regressão para filtros, paginação e consistência das estatísticas filtradas;
- pacote, API, cliente PNCP e frontend sincronizados em 1.51.0.

## 1.50.0

- aplicação pública reorganizada com `Explorar preços` como experiência principal e `Laboratório` para o parser;
- busca por produtos comparáveis, resumo estatístico e distribuição de preços homologados;
- histórico mensal e comparação geográfica por região e UF;
- visões públicas de fornecedores e órgãos compradores;
- sinais estatísticos com aviso interpretativo e cartões de evidência rastreáveis até o PNCP;
- exemplo público do parser documentado a partir do holdout v5 e protegido por teste automatizado;
- documentação da API e README atualizados para refletir a camada analítica publicada;
- versão do pacote, API e cliente PNCP sincronizada em 1.50.0.

## 1.49.0

- congelamento do holdout independente de medicamentos v4 com 48 exemplos e 192 campos;
- baseline independente v4 preservada em 189/192 campos corretos, equivalente a 98,44% de micro accuracy;
- regressão pós-tuning v1.49 registrada separadamente em 192/192 campos corretos;
- snapshot de qualidade consolidado para medicamentos v1-v4;
- consolidação técnica atualizada para v1-v12, com 548 exemplos e 984 campos;
- integridade dos holdouts de medicamentos v1-v4 protegida por hashes;
- documentação pública, templates de colaboração e governança do repositório ampliados.

Detalhes: [release v1.49.0](docs/release-v1.49.0.md) e [auditoria v1.49.0](docs/audit-v1.49.0.md).
