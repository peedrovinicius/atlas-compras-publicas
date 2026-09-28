# Changelog

Este arquivo registra mudanças públicas relevantes do Atlas de Compras Públicas. Benchmarks e auditorias detalhadas permanecem documentados em `docs/`.

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
