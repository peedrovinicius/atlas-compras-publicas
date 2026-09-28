import { FormEvent, useEffect, useRef, useState } from "react";

import { fetchProductAnalytics, searchProducts } from "./api";
import type {
  AnalyticsFilters,
  ProductAnalyticsBundle,
  ProductSearchItem,
} from "./types";

const DEFAULT_QUERY = "resina";
const PAGE_SIZE = 10;
const EXAMPLES = ["resina", "ionômero", "anestésico", "flúor"];
const EMPTY_FILTERS: AnalyticsFilters = {
  state_code: "",
  macroregion: "",
  supplier: "",
  buyer: "",
  start_date: "",
  end_date: "",
};
const REGION_OPTIONS = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"];
const UF_OPTIONS = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
  "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
  "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
];

function money(value: number | null | undefined): string {
  if (value === null || value === undefined) return "Sem amostra";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(Number(value));
}

function number(value: number | null | undefined): string {
  return new Intl.NumberFormat("pt-BR").format(Number(value ?? 0));
}

function date(value: string | null | undefined): string {
  if (!value) return "Não informado";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

function shortHash(value: string | null | undefined): string {
  if (!value) return "hash não informado";
  return `${value.slice(0, 10)}…${value.slice(-8)}`;
}

function percent(value: number | null | undefined): string {
  if (value === null || value === undefined) return "Sem referência";
  const numeric = Number(value);
  return `${numeric > 0 ? "+" : ""}${numeric.toLocaleString("pt-BR", {
    maximumFractionDigits: 1,
  })}%`;
}

function Metric({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </div>
  );
}

export default function AnalyticsExplorer() {
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [filters, setFilters] = useState<AnalyticsFilters>({ ...EMPTY_FILTERS });
  const [appliedFilters, setAppliedFilters] = useState<AnalyticsFilters>({
    ...EMPTY_FILTERS,
  });
  const [appliedQuery, setAppliedQuery] = useState(DEFAULT_QUERY);
  const [results, setResults] = useState<ProductSearchItem[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [bundle, setBundle] = useState<ProductAnalyticsBundle | null>(null);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const detailRef = useRef<HTMLElement>(null);

  async function runSearch(
    nextQuery = query,
    nextFilters = filters,
    nextOffset = 0,
  ) {
    const cleaned = nextQuery.trim();
    if (cleaned.length < 2) {
      setError("Digite pelo menos 2 caracteres para pesquisar.");
      return;
    }

    setSearching(true);
    setError(null);
    setBundle(null);
    setSelectedId(null);

    try {
      const response = await searchProducts(
        cleaned,
        nextFilters,
        PAGE_SIZE,
        nextOffset,
      );
      setResults(response.items);
      setTotal(response.total);
      setOffset(response.offset);
      setAppliedQuery(cleaned);
      setAppliedFilters({ ...nextFilters });
    } catch (requestError) {
      setResults([]);
      setTotal(0);
      setOffset(0);
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Não foi possível pesquisar agora.",
      );
    } finally {
      setSearching(false);
    }
  }

  async function selectProduct(item: ProductSearchItem) {
    setSelectedId(item.product_id);
    setLoading(true);
    setError(null);

    try {
      const analytics = await fetchProductAnalytics(
        item.product_id,
        appliedFilters,
      );
      setBundle(analytics);
      window.requestAnimationFrame(() => {
        detailRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    } catch (requestError) {
      setBundle(null);
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Não foi possível carregar os detalhes.",
      );
    } finally {
      setLoading(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runSearch();
  }

  useEffect(() => {
    void runSearch(DEFAULT_QUERY, EMPTY_FILTERS, 0);
  }, []);

  const summary = bundle?.summary;
  const stats = summary?.price_stats;
  const maxDistributionCount = bundle?.distribution.bins.reduce(
    (maximum, bin) => Math.max(maximum, bin.count),
    0,
  ) ?? 0;
  const pageStart = total === 0 ? 0 : offset + 1;
  const pageEnd = Math.min(offset + results.length, total);
  const hasPreviousPage = offset > 0;
  const hasNextPage = offset + results.length < total;

  return (
    <>
      <section className="hero analytics-hero">
        <span className="eyebrow">Inteligência sobre compras públicas</span>
        <h1>Pesquise um produto e descubra quanto o governo está pagando por ele.</h1>
        <p>
          Compare preços homologados, evolução temporal, diferenças regionais,
          fornecedores, órgãos compradores e sinais estatísticos com rastreabilidade até o PNCP.
        </p>
      </section>

      <section className="panel analytics-search-panel">
        <form onSubmit={submit}>
          <label htmlFor="analytics-search">Produto ou característica</label>
          <div className="analytics-search-row">
            <input
              id="analytics-search"
              value={query}
              onChange={(event: { target: { value: string } }) => setQuery(event.target.value)}
              placeholder="Ex.: resina A2, ionômero, anestésico"
              autoComplete="off"
            />
            <button className="primary-button" type="submit" disabled={searching}>
              {searching ? "Pesquisando..." : "Pesquisar"}
            </button>
          </div>

          <div className="analytics-filter-heading">
            <span>Filtros opcionais</span>
            <button
              type="button"
              onClick={() => {
                const cleared = { ...EMPTY_FILTERS };
                setFilters(cleared);
                void runSearch(query, cleared, 0);
              }}
            >
              Limpar filtros
            </button>
          </div>

          <div className="analytics-filter-grid">
            <label>
              Região
              <select
                value={filters.macroregion}
                onChange={(event) =>
                  setFilters({ ...filters, macroregion: event.target.value })
                }
              >
                <option value="">Todas</option>
                {REGION_OPTIONS.map((region) => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
            </label>

            <label>
              UF
              <select
                value={filters.state_code}
                onChange={(event) =>
                  setFilters({ ...filters, state_code: event.target.value })
                }
              >
                <option value="">Todas</option>
                {UF_OPTIONS.map((uf) => (
                  <option key={uf} value={uf}>{uf}</option>
                ))}
              </select>
            </label>

            <label>
              Fornecedor
              <input
                value={filters.supplier}
                onChange={(event) =>
                  setFilters({ ...filters, supplier: event.target.value })
                }
                placeholder="Nome ou documento"
              />
            </label>

            <label>
              Órgão ou unidade
              <input
                value={filters.buyer}
                onChange={(event) =>
                  setFilters({ ...filters, buyer: event.target.value })
                }
                placeholder="Nome, CNPJ ou código"
              />
            </label>

            <label>
              Data inicial
              <input
                type="date"
                value={filters.start_date}
                onChange={(event) =>
                  setFilters({ ...filters, start_date: event.target.value })
                }
              />
            </label>

            <label>
              Data final
              <input
                type="date"
                value={filters.end_date}
                onChange={(event) =>
                  setFilters({ ...filters, end_date: event.target.value })
                }
              />
            </label>
          </div>
        </form>

        <div className="analytics-examples">
          <span>Exemplos</span>
          {EXAMPLES.map((example) => (
            <button
              type="button"
              key={example}
              onClick={() => {
                setQuery(example);
                void runSearch(example, filters, 0);
              }}
            >
              {example}
            </button>
          ))}
        </div>

        {error && <p className="analytics-error">{error}</p>}
      </section>

      <section className="analytics-results">
        <div className="results-header">
          <div>
            <span className="section-kicker">Resultados compatíveis</span>
            <h2>Produtos encontrados</h2>
          </div>
          {!searching && <span className="item-count">{number(total)} grupos</span>}
        </div>

        {searching ? (
          <div className="analytics-loading">Consultando a base analítica...</div>
        ) : results.length === 0 ? (
          <div className="empty-state">
            <strong>Nenhum produto encontrado.</strong>
            <span>Tente um termo mais amplo ou use um dos exemplos acima.</span>
          </div>
        ) : (
          <div className="analytics-result-list">
            {results.map((item) => (
              <button
                type="button"
                key={item.product_id}
                className={
                  selectedId === item.product_id
                    ? "analytics-result analytics-result-selected"
                    : "analytics-result"
                }
                onClick={() => void selectProduct(item)}
              >
                <span>
                  <strong>{item.display_name}</strong>
                  <small>{item.sample_description}</small>
                </span>
                <span className="analytics-result-meta">
                  {number(item.priced_observation_count)} preços · {number(item.procurement_count)} compras · {number(item.state_count)} UFs
                </span>
              </button>
            ))}
          </div>
        )}

        {!searching && total > 0 && (
          <div className="analytics-pagination">
            <button
              type="button"
              disabled={!hasPreviousPage}
              onClick={() =>
                void runSearch(
                  appliedQuery,
                  appliedFilters,
                  Math.max(0, offset - PAGE_SIZE),
                )
              }
            >
              Anterior
            </button>
            <span>{number(pageStart)}–{number(pageEnd)} de {number(total)}</span>
            <button
              type="button"
              disabled={!hasNextPage}
              onClick={() =>
                void runSearch(
                  appliedQuery,
                  appliedFilters,
                  offset + PAGE_SIZE,
                )
              }
            >
              Próxima
            </button>
          </div>
        )}
      </section>

      <section ref={detailRef} className="analytics-detail">
        {loading && <div className="analytics-loading">Carregando análise completa...</div>}

        {!loading && bundle && summary && stats && (
          <>
            <div className="analytics-title-row">
              <div>
                <span className="section-kicker">Análise consolidada</span>
                <h2>{summary.display_name}</h2>
                <p>{summary.sample_description}</p>
              </div>
              <span className={summary.sample_sufficient ? "sample-status" : "sample-status sample-status-warning"}>
                {summary.sample_sufficient
                  ? `${number(summary.price_sample_count)} preços comparáveis`
                  : `Amostra pequena: ${number(summary.price_sample_count)} preços`}
              </span>
            </div>

            {!summary.sample_sufficient && (
              <p className="sample-warning">
                A amostra está abaixo do mínimo metodológico de {number(summary.minimum_sample_size)} observações de preço. Interprete as estatísticas com cautela.
              </p>
            )}

            <div className="analytics-metrics">
              <Metric label="Mediana" value={money(stats.median_price)} note={summary.price_unit ?? "preço normalizado"} />
              <Metric label="Faixa central" value={`${money(stats.percentile_25)} a ${money(stats.percentile_75)}`} note="25º ao 75º percentil" />
              <Metric label="Compras" value={number(summary.procurement_count)} note="processos distintos" />
              <Metric label="Fornecedores" value={number(summary.supplier_count)} note="documentos distintos" />
              <Metric label="UFs" value={number(summary.state_count)} note="cobertura da amostra" />
              <Metric label="Período" value={`${date(summary.period_start)} a ${date(summary.period_end)}`} note="datas observadas" />
            </div>

            <div className="analytics-grid">
              <article className="analytics-card analytics-card-wide">
                <span className="section-kicker">Distribuição</span>
                <h3>Distribuição dos preços comparáveis</h3>
                {bundle.distribution.bins.length === 0 ? (
                  <p className="analytics-empty">Sem preços defensáveis suficientes para distribuir.</p>
                ) : (
                  <>
                    <p className="analytics-note">
                      {number(bundle.distribution.observations)} observações entre {money(bundle.distribution.min_price)} e {money(bundle.distribution.max_price)}.
                    </p>
                    <div className="distribution-chart" aria-label="Distribuição de preços por faixa">
                      {bundle.distribution.bins.map((bin) => {
                        const width = maxDistributionCount
                          ? Math.max(4, (bin.count / maxDistributionCount) * 100)
                          : 0;
                        return (
                          <div className="distribution-row" key={bin.index}>
                            <span>{money(bin.lower)} – {money(bin.upper)}</span>
                            <div className="distribution-track">
                              <div className="distribution-bar" style={{ width: `${width}%` }} />
                            </div>
                            <strong>{number(bin.count)}</strong>
                          </div>
                        );
                      })}
                    </div>
                  </>
                )}
              </article>

              <article className="analytics-card analytics-card-wide">
                <span className="section-kicker">Evolução</span>
                <h3>Histórico de preços</h3>
                {bundle.history.points.length === 0 ? (
                  <p className="analytics-empty">Sem série temporal defensável para este produto.</p>
                ) : (
                  <div className="analytics-table-wrap">
                    <table>
                      <thead><tr><th>Mês</th><th>Mediana</th><th>Faixa central</th><th>Observações</th></tr></thead>
                      <tbody>
                        {bundle.history.points.map((point) => (
                          <tr key={point.month}>
                            <td>{date(point.month)}</td>
                            <td>{money(point.median_price)}</td>
                            <td>{money(point.percentile_25)} a {money(point.percentile_75)}</td>
                            <td>{number(point.observations)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </article>

              <article className="analytics-card">
                <span className="section-kicker">Geografia</span>
                <h3>Comparação por UF</h3>
                <div className="analytics-rank-list">
                  {bundle.regions.states.slice(0, 8).map((state) => (
                    <div key={state.state_code}>
                      <span><strong>{state.state_code}</strong><small>{state.macroregion ?? "Região não informada"}</small></span>
                      <span><strong>{money(state.median_price)}</strong><small>{percent(state.difference_from_national_percent)}</small></span>
                    </div>
                  ))}
                </div>
              </article>

              <article className="analytics-card">
                <span className="section-kicker">Mercado</span>
                <h3>Fornecedores</h3>
                <div className="analytics-rank-list">
                  {bundle.suppliers.items.map((supplier) => (
                    <div key={supplier.supplier_document}>
                      <span><strong>{supplier.supplier_name ?? "Fornecedor sem nome"}</strong><small>{number(supplier.procurement_count)} compras</small></span>
                      <span><strong>{money(supplier.median_price)}</strong><small>{Number(supplier.sample_share_percent).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}% da amostra</small></span>
                    </div>
                  ))}
                </div>
              </article>

              <article className="analytics-card">
                <span className="section-kicker">Demanda pública</span>
                <h3>Órgãos compradores</h3>
                <div className="analytics-rank-list">
                  {bundle.buyers.items.map((buyer, index) => (
                    <div key={`${buyer.organization_cnpj ?? "org"}-${buyer.buyer_unit_code ?? index}`}>
                      <span><strong>{buyer.organization_name ?? buyer.buyer_unit_name ?? "Órgão sem nome"}</strong><small>{buyer.state_code ?? "UF não informada"} · {number(buyer.procurement_count)} compras</small></span>
                      <span><strong>{money(buyer.median_price)}</strong><small>{money(buyer.awarded_total_value)} homologados</small></span>
                    </div>
                  ))}
                </div>
              </article>

              <article className="analytics-card analytics-card-wide">
                <span className="section-kicker">Sinais estatísticos</span>
                <h3>Preços fora da distribuição observada</h3>
                <p className="analytics-note">{bundle.signals.disclaimer}</p>
                {bundle.signals.items.length === 0 ? (
                  <p className="analytics-empty">Nenhum sinal estatístico publicado para este produto.</p>
                ) : (
                  <div className="analytics-table-wrap">
                    <table>
                      <thead><tr><th>Data</th><th>Preço</th><th>Mediana</th><th>Método</th><th>UF</th><th>Fonte</th></tr></thead>
                      <tbody>
                        {bundle.signals.items.map((signal) => (
                          <tr key={signal.award_key}>
                            <td>{date(signal.analysis_date)}</td>
                            <td>{money(signal.awarded_price_per_base_unit)}</td>
                            <td>{money(signal.median_price)}</td>
                            <td>{signal.detection_method ?? "Não informado"}</td>
                            <td>{signal.state_code ?? "Não informada"}</td>
                            <td>{signal.pncp_url ? <a href={signal.pncp_url} target="_blank" rel="noreferrer">PNCP</a> : "Sem link"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </article>

              <article className="analytics-card analytics-card-wide">
                <span className="section-kicker">Rastreabilidade</span>
                <h3>Registros que sustentam a análise</h3>
                <div className="analytics-records">
                  {bundle.records.items.map((record) => (
                    <details className="evidence-card" key={record.award_key}>
                      <summary>
                        <span>
                          <strong>{money(record.awarded_price_per_base_unit)}</strong>
                          <small>{date(record.analysis_date)} · {record.state_code ?? "UF não informada"}</small>
                        </span>
                        <p>{record.original_description}</p>
                        <span>
                          <small>{record.supplier_name ?? "Fornecedor não informado"}</small>
                          <small>ver evidência</small>
                        </span>
                      </summary>
                      <div className="evidence-grid">
                        <div><span>Órgão</span><strong>{record.organization_name ?? "Não informado"}</strong></div>
                        <div><span>Unidade compradora</span><strong>{record.buyer_unit_name ?? "Não informada"}</strong></div>
                        <div><span>Local</span><strong>{[record.municipality_name, record.state_code].filter(Boolean).join(" / ") || "Não informado"}</strong></div>
                        <div><span>Modalidade</span><strong>{record.modality ?? "Não informada"}</strong></div>
                        <div><span>Quantidade homologada</span><strong>{record.awarded_quantity ?? "Não informada"}</strong></div>
                        <div><span>Valor total</span><strong>{money(record.awarded_total_value)}</strong></div>
                        <div><span>Status do preço</span><strong>{record.price_normalization_status ?? "Não informado"}</strong></div>
                        <div><span>Motivo</span><strong>{record.price_normalization_reason ?? "Não informado"}</strong></div>
                      </div>
                      <div className="evidence-hashes">
                        <small>contratação {shortHash(record.contract_source_sha256)}</small>
                        <small>item {shortHash(record.item_source_sha256)}</small>
                        <small>resultado {shortHash(record.result_source_sha256)}</small>
                        {record.pncp_url && <a href={record.pncp_url} target="_blank" rel="noreferrer">Abrir no PNCP</a>}
                      </div>
                    </details>
                  ))}
                </div>
              </article>
            </div>
          </>
        )}
      </section>
    </>
  );
}
