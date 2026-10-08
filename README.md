<div align="center">

# Atlas e Preços

**Dados públicos do PNCP transformados em análises de preços rastreáveis.**

[![CI](https://github.com/peedrovinicius/atlas-compras-publicas/actions/workflows/ci.yml/badge.svg)](https://github.com/peedrovinicius/atlas-compras-publicas/actions/workflows/ci.yml)

[Explorar aplicação](https://atlas-compras-publicas-web.onrender.com/) · [API / OpenAPI](https://atlas-compras-publicas-analytics.onrender.com/docs) · [Documentação técnica](docs/README.md) · [CHANGELOG](CHANGELOG.md)

</div>

## Por que existe

Descrições de compras públicas usam nomes, medidas e embalagens heterogêneos. Comparar preços sem normalizar os itens pode misturar produtos incompatíveis. O Atlas captura informações do PNCP, estrutura os itens e preserva a evidência de origem antes de construir grupos de comparação e estatísticas.

## Funcionalidades em destaque

- Captura de contratações, itens e resultados do PNCP com rastreabilidade por SHA-256.
- Normalização de categorias, apresentações, medidas e atributos odontológicos.
- Grupos comparáveis com regras conservadoras para preço por unidade física.
- Consulta de mediana, distribuição, evolução temporal e diferenças por UF.
- Investigação de fornecedores, órgãos compradores e registros de origem.
- Sinais estatísticos explicáveis por MAD/IQR, **sem presumir irregularidade**.
- Exportação de registros filtrados em CSV e compartilhamento de análises.
- Laboratório interativo para testar descrições reais no normalizador.

**[Abrir a demonstração](https://atlas-compras-publicas-web.onrender.com/)** — o tempo de inicialização depende das condições de hospedagem. Consulte [a documentação da interface e dos endpoints](docs/api-dashboard.md). Uma captura verificada da aplicação ainda será incluída aqui.

## Exemplo rastreável de normalização

**Entrada:** `PRIME ADESIVO FRASCO 4ML` (holdout `data/evaluation/v5.jsonl`, item `lr-350`).

**Saída documentada:** adesivo odontológico · frasco · 4 ml por unidade · medida não ambígua.

[Ver item, origem, limitações e teste de reprodução](docs/exemplo-parser-real.md). Este exemplo demonstra **normalização**, não uma comparação de preço homologado.

## Qualidade: resultados e limites

| Avaliação | Amostra | Resultado |
| --- | ---: | ---: |
| Holdout odontológico v5 — categorias | 48 itens | **38/48 = 79,17%**; IC Wilson 95% ≈ **65,7%–88,3%** |
| Histórico de campos técnicos, ciclos v1–v12 | 984 campos em 548 exemplos | 899/984 = **91,36%** |

O holdout v5 preserva uma avaliação de categorias com amostra limitada. Já os **91,36%** são um **resumo histórico de ciclos com versões e dificuldades diferentes**, não a estimativa de generalização de um único parser em produção. O intervalo de Wilson acima considera os 48 itens como observações independentes; a representatividade das fontes continua sendo uma limitação. Não misture acurácia de categoria e acurácia de campos técnicos.

[Holdout v5](docs/benchmark-v5.md) · [Ciclos técnicos v1–v12](docs/benchmark-technical-consolidated-v1-v12.md) · [Metodologia de qualidade](docs/qualidade-normalizador.md)

## Como executar

Requer Python 3.12+.

```bash
git clone https://github.com/peedrovinicius/atlas-compras-publicas.git
cd atlas-compras-publicas
python -m pip install -e ".[dev]"
atlas evaluate-taxonomy --dataset data/evaluation/v5.jsonl
```

O comando acima usa um dataset versionado e não precisa consultar a API do PNCP. Para construir a demo analítica: `atlas build-demo-data`. Essa rotina tenta consultar o PNCP e pode recorrer a um fallback determinístico; **dados de fallback não devem ser apresentados como preços reais**. [Leia as condições e a origem da amostra](data/demo/README.md).

## Dados e metodologia

Fluxo: **PNCP → evidência original → normalização → Parquet/DuckDB → grupos comparáveis → análise e sinais**.

A cobertura publicada **não corresponde ao universo completo do PNCP**. Contagens verificadas de contratações, itens, homologações, UFs e período precisam ser extraídas da mesma versão do banco analítico; não são inventadas no README. A interpretação de preços depende da unidade, da identidade comparável e da suficiência amostral.

[Arquitetura](docs/architecture.md) · [Modelo do warehouse](docs/warehouse-v1.md) · [Metodologia MAD/IQR](docs/metodologia-anomalias.md) · [Consultas SQL](sql/05_signal_trace.sql)

## Desenvolvimento

Backend em Python (Polars, Pydantic, DuckDB e FastAPI) e frontend React/TypeScript. O CI executa Ruff, pytest e build TypeScript/Vite. **O build não equivale a testes automatizados de interface**; essa cobertura ainda precisa ser implementada e validada.

O nome público da aplicação é **Atlas e Preços**; o repositório técnico mantém o identificador `atlas-compras-publicas`. O pacote Python interno `dental_procurement_intelligence` e o alias legado `dpi` permanecem por compatibilidade até uma migração testada.

**English:** Atlas de Compras Públicas is an auditable public-procurement analytics project focused on product normalization, comparable prices, and traceable evidence from Brazil's PNCP. Statistical outlier signals do not imply wrongdoing.

[Documentação](docs/README.md) · [Segurança](SECURITY.md) · [Contribuição](CONTRIBUTING.md) · [Licença MIT](LICENSE) · [Arquivo técnico do README anterior](docs/README-legacy-detailed.md)
