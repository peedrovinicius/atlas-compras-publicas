import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";

import { downloadProductRecordsCsv, fetchProductAnalytics, fetchProductDiscovery, searchProducts, suggestProducts } from "./api";
import type {
  AnalyticsFilters,
  ProductAnalyticsBundle,
  ProductDiscoveryItem,
  ProductSearchFacets,
  ProductSearchItem,
  ProductSort,
} from "./types";

const DEFAULT_QUERY = "";
const PAGE_SIZE = 10;
const RECENT_SEARCHES_KEY = "atlas:recent-searches";
const RECENT_SEARCHES_LIMIT = 6;
type DetailView = "overview" | "market" | "evidence";

const DEFAULT_SORT: ProductSort = "relevance";
const SORT_OPTIONS: Array<{ value: ProductSort; label: string }> = [
  { value: "relevance", label: "Mais relevantes" },
  { value: "coverage", label: "Mais preços comparáveis" },
  { value: "procurements", label: "Mais compras" },
  { value: "latest", label: "Mais recentes" },
  { value: "name", label: "Nome" },
];
const EMPTY_FILTERS: AnalyticsFilters = {
  state_code: "",
  macroregion: "",
  supplier: "",
  buyer: "",
  start_date: "",
  end_date: "",
};
const FILTER_LABELS: Record<keyof AnalyticsFilters, string> = {
  state_code: "UF",
  macroregion: "Região",
  supplier: "Fornecedor",
  buyer: "Órgão",
  start_date: "Desde",
  end_date: "Até",
};
const FACET_LABELS: Record<string, string> = {
  shade: "Cor",
  presentation: "Apresentação",
  concentration_percent: "Concentração",
  resin_technology: "Tecnologia",
  curing_mode: "Cura",
  adhesive_strategy: "Estratégia adesiva",
  ionomer_use: "Uso",
  fluoride_formulation: "Formulação",
  anesthetic_active_ingredient: "Princípio ativo",
  anesthetic_vasoconstrictor: "Vasoconstrictor",
};

const FACET_VALUE_LABELS: Record<string, string> = {
  syringe: "Seringa",
  bottle: "Frasco",
  tube: "Tubo",
  jar: "Pote",
  cartridge: "Tubete",
  ampoule: "Ampola",
  kit: "Kit",
  package: "Pacote",
  bag: "Saco",
  light_cure: "Fotopolimerizável",
  dual_cure: "Cura dual",
  self_cure: "Autopolimerizável",
  self_etch: "Autocondicionante",
  etch_and_rinse: "Condicionamento total",
  universal: "Universal",
};

const REGION_OPTIONS = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"];
const UF_OPTIONS = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
  "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
  "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
];

function readRecentSearches(): string[] {
  try {
    const raw = window.localStorage.getItem(RECENT_SEARCHES_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((value): value is string => typeof value === "string")
      .map((value) => value.trim())
      .filter(Boolean)
      .slice(0, RECENT_SEARCHES_LIMIT);
  } catch {
    return [];
  }
}

function formatFacetValue(key: string, value: string): string {
  if (key === "shade") return `Cor ${value}`;
  if (key === "concentration_percent") return `Concentração ${value}%`;
  const friendly = FACET_VALUE_LABELS[value];
  if (friendly) return friendly;
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toLocaleUpperCase("pt-BR"));
}

function queryFacetValue(value: string): string {
  return value.replaceAll("_", " ");
}

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  return (
    target.tagName === "INPUT"
    || target.tagName === "TEXTAREA"
    || target.tagName === "SELECT"
    || target.isContentEditable
  );
}

function normalizeDiscoveryText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .trim();
}

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

function readInitialState() {
  const params = new URLSearchParams(window.location.search);
  const sortValue = params.get("sort");
  const sort: ProductSort = SORT_OPTIONS.some((option) => option.value === sortValue)
    ? (sortValue as ProductSort)
    : DEFAULT_SORT;
  const rawOffset = Number(params.get("offset") ?? "0");

  return {
    query: params.get("q")?.trim() || DEFAULT_QUERY,
    sort,
    offset: Number.isFinite(rawOffset) && rawOffset >= 0 ? rawOffset : 0,
    productId: params.get("product_id"),
    filters: {
      state_code: params.get("state_code") ?? "",
      macroregion: params.get("macroregion") ?? "",
      supplier: params.get("supplier") ?? "",
      buyer: params.get("buyer") ?? "",
      start_date: params.get("start_date") ?? "",
      end_date: params.get("end_date") ?? "",
    } satisfies AnalyticsFilters,
  };
}

function syncExplorerUrl(
  query: string,
  filters: AnalyticsFilters,
  sort: ProductSort,
  offset: number,
  productId: string | null = null,
) {
  const params = new URLSearchParams();
  params.set("q", query);
  if (sort !== DEFAULT_SORT) params.set("sort", sort);
  if (offset > 0) params.set("offset", String(offset));
  for (const [key, value] of Object.entries(filters)) {
    const cleaned = value.trim();
    if (cleaned) params.set(key, cleaned);
  }
  if (productId) params.set("product_id", productId);
  window.history.replaceState(null, "", `?${params.toString()}`);
}

function HistoryChart({
  points,
}: {
  points: ProductAnalyticsBundle["history"]["points"];
}) {
  const visible = points.filter((point) => point.median_price !== null);
  if (visible.length === 0) return null;

  const values = visible.flatMap((point) => [
    Number(point.percentile_25 ?? point.median_price),
    Number(point.median_price),
    Number(point.percentile_75 ?? point.median_price),
  ]);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const range = Math.max(maxValue - minValue, 1);
  const width = 760;
  const height = 220;
  const padding = 24;
  const x = (index: number) =>
    visible.length === 1
      ? width / 2
      : padding + (index / (visible.length - 1)) * (width - padding * 2);
  const y = (value: number) =>
    height - padding - ((value - minValue) / range) * (height - padding * 2);

  const upper = visible.map((point, index) =>
    `${x(index)},${y(Number(point.percentile_75 ?? point.median_price))}`,
  );
  const lower = visible
    .map((point, index) =>
      `${x(index)},${y(Number(point.percentile_25 ?? point.median_price))}`,
    )
    .reverse();
  const median = visible
    .map((point, index) => `${x(index)},${y(Number(point.median_price))}`)
    .join(" ");

  return (
    <div className="history-chart">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Evolução da mediana e da faixa interquartil de preços"
      >
        <polygon className="history-band" points={[...upper, ...lower].join(" ")} />
        <polyline className="history-line" points={median} />
        {visible.map((point, index) => (
          <circle
            className="history-point"
            key={point.month}
            cx={x(index)}
            cy={y(Number(point.median_price))}
            r="4"
          >
            <title>{`${date(point.month)}: ${money(point.median_price)}`}</title>
          </circle>
        ))}
      </svg>
      <div className="history-chart-axis">
        <span>{date(visible[0].month)}</span>
        <span>{date(visible[visible.length - 1].month)}</span>
      </div>
    </div>
  );
}

export default function AnalyticsExplorer() {
  const initialState = useRef(readInitialState()).current;
  const [query, setQuery] = useState(initialState.query);
  const [filters, setFilters] = useState<AnalyticsFilters>({ ...initialState.filters });
  const [sort, setSort] = useState<ProductSort>(initialState.sort);
  const [appliedFilters, setAppliedFilters] = useState<AnalyticsFilters>({
    ...initialState.filters,
  });
  const [appliedQuery, setAppliedQuery] = useState(initialState.query);
  const [appliedSort, setAppliedSort] = useState<ProductSort>(initialState.sort);
  const [discovery, setDiscovery] = useState<ProductDiscoveryItem[]>([]);
  const [interpretedLabel, setInterpretedLabel] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<ProductSearchItem[]>([]);
  const [suggesting, setSuggesting] = useState(false);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);
  const [results, setResults] = useState<ProductSearchItem[]>([]);
  const [comparisonItems, setComparisonItems] = useState<ProductSearchItem[]>([]);
  const [facets, setFacets] = useState<ProductSearchFacets>({});
  const [hasSearched, setHasSearched] = useState(
    initialState.query.trim().length >= 2 || Boolean(initialState.productId),
  );
  const [recentSearches, setRecentSearches] = useState<string[]>(readRecentSearches);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(initialState.offset);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [bundle, setBundle] = useState<ProductAnalyticsBundle | null>(null);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shareFeedback, setShareFeedback] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [detailView, setDetailView] = useState<DetailView>("overview");
  const searchInputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLElement>(null);
  const detailRef = useRef<HTMLElement>(null);
  const suggestionRequestRef = useRef(0);

  async function runSearch(
    nextQuery = query,
    nextFilters = filters,
    nextOffset = 0,
    nextSort = sort,
    rememberSearch = false,
  ) {
    const cleaned = nextQuery.trim();
    if (cleaned.length < 2) {
      setError("Digite pelo menos 2 caracteres para pesquisar.");
      return;
    }

    const filtersChanged = Object.entries(nextFilters).some(
      ([key, value]) =>
        value !== appliedFilters[key as keyof AnalyticsFilters],
    );
    const searchContextChanged =
      cleaned !== appliedQuery
      || nextSort !== appliedSort
      || filtersChanged;

    if (nextOffset === 0 && searchContextChanged) {
      setComparisonItems([]);
    }

    setHasSearched(true);
    setSearching(true);
    setError(null);
    setBundle(null);
    setSelectedId(null);

    try {
      const response = await searchProducts(
        cleaned,
        nextFilters,
        nextSort,
        PAGE_SIZE,
        nextOffset,
      );
      setResults(response.items);
      setFacets(response.facets);
      setTotal(response.total);
      setInterpretedLabel(response.interpreted_label);
      setOffset(response.offset);
      setAppliedQuery(cleaned);
      setAppliedFilters({ ...nextFilters });
      setAppliedSort(nextSort);
      syncExplorerUrl(cleaned, nextFilters, nextSort, response.offset);
      if (rememberSearch && nextOffset === 0) {
        const nextRecent = [
          cleaned,
          ...recentSearches.filter(
            (item) =>
              normalizeDiscoveryText(item) !== normalizeDiscoveryText(cleaned),
          ),
        ].slice(0, RECENT_SEARCHES_LIMIT);
        setRecentSearches(nextRecent);
        try {
          window.localStorage.setItem(
            RECENT_SEARCHES_KEY,
            JSON.stringify(nextRecent),
          );
        } catch {
          // Histórico recente é apenas uma conveniência local.
        }
      }
    } catch (requestError) {
      setResults([]);
      setFacets({});
      setTotal(0);
      setInterpretedLabel(null);
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

  function clearRecentSearches() {
    setRecentSearches([]);
    try {
      window.localStorage.removeItem(RECENT_SEARCHES_KEY);
    } catch {
      // Sem efeito funcional se o armazenamento local estiver indisponível.
    }
  }

  function applyRefinement(value: string) {
    const refinement = queryFacetValue(value);
    const current = appliedQuery.trim();
    const normalizedCurrent = normalizeDiscoveryText(current.replaceAll("_", " "));
    const normalizedRefinement = normalizeDiscoveryText(refinement);
    if (normalizedCurrent.includes(normalizedRefinement)) return;

    const nextQuery = `${current} ${refinement}`.trim();
    setQuery(nextQuery);
    void runSearch(nextQuery, appliedFilters, 0, appliedSort, true);
  }

  function removeAppliedFilter(key: keyof AnalyticsFilters) {
    const nextFilters = { ...appliedFilters, [key]: "" };
    setFilters(nextFilters);
    void runSearch(appliedQuery, nextFilters, 0, appliedSort);
  }

  function clearAllAppliedFilters() {
    const nextFilters = { ...EMPTY_FILTERS };
    setFilters(nextFilters);
    void runSearch(appliedQuery, nextFilters, 0, appliedSort);
  }

  async function loadProduct(
    productId: string,
    nextFilters = appliedFilters,
    shouldScroll = true,
    nextQuery = appliedQuery,
    nextSort = appliedSort,
    nextOffset = offset,
  ) {
    setSelectedId(productId);
    setDetailView("overview");
    setLoading(true);
    setError(null);

    try {
      const analytics = await fetchProductAnalytics(
        productId,
        nextFilters,
      );
      setBundle(analytics);
      syncExplorerUrl(nextQuery, nextFilters, nextSort, nextOffset, productId);
      if (shouldScroll) {
        window.requestAnimationFrame(() => {
          detailRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
          detailRef.current?.focus({ preventScroll: true });
        });
      }
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

  async function selectProduct(item: ProductSearchItem) {
    await loadProduct(item.product_id);
  }

  function toggleComparison(item: ProductSearchItem) {
    const selected = comparisonItems.some(
      (candidate) => candidate.product_id === item.product_id,
    );
    if (selected) {
      setComparisonItems((current) =>
        current.filter((candidate) => candidate.product_id !== item.product_id),
      );
      return;
    }

    if (comparisonItems.length >= 3) {
      setError("Você pode comparar até 3 produtos por vez.");
      return;
    }

    const reference = comparisonItems[0];
    if (
      reference
      && (
        reference.product_category !== item.product_category
        || reference.normalized_quantity_unit !== item.normalized_quantity_unit
      )
    ) {
      setError(
        "Para comparar preços com segurança, selecione produtos da mesma categoria e unidade normalizada.",
      );
      return;
    }

    setError(null);
    setComparisonItems((current) => [...current, item]);
  }

  async function copyShareLink() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setShareFeedback("Link copiado");
    } catch {
      setShareFeedback("Copie a URL do navegador");
    }
  }

  async function exportCsv() {
    if (!selectedId) return;
    setExporting(true);
    setError(null);
    try {
      await downloadProductRecordsCsv(selectedId, appliedFilters);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Não foi possível exportar os registros.",
      );
    } finally {
      setExporting(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSuggestions([]);
    setActiveSuggestionIndex(-1);
    void runSearch(query, filters, 0, sort, true);
  }

  function handleSearchKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      setSuggestions([]);
      setActiveSuggestionIndex(-1);
      return;
    }

    if (suggestions.length === 0) return;

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveSuggestionIndex((current) =>
        current >= suggestions.length - 1 ? 0 : current + 1,
      );
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveSuggestionIndex((current) =>
        current <= 0 ? suggestions.length - 1 : current - 1,
      );
      return;
    }

    if (event.key === "Enter" && activeSuggestionIndex >= 0) {
      event.preventDefault();
      const item = suggestions[activeSuggestionIndex];
      if (item) void chooseSuggestion(item);
    }
  }

  async function chooseSuggestion(item: ProductSearchItem) {
    const currentQuery = query.trim() || item.sample_description;
    setSuggestions([]);
    setActiveSuggestionIndex(-1);
    setResults([item]);
    setFacets({});
    setTotal(1);
    setOffset(0);
    setAppliedQuery(currentQuery);
    setAppliedFilters({ ...filters });
    setAppliedSort("relevance");
    const nextRecent = [
      currentQuery,
      ...recentSearches.filter(
        (item) =>
          normalizeDiscoveryText(item) !== normalizeDiscoveryText(currentQuery),
      ),
    ].slice(0, RECENT_SEARCHES_LIMIT);
    setRecentSearches(nextRecent);
    try {
      window.localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(nextRecent));
    } catch {
      // Histórico recente é apenas uma conveniência local.
    }
    await loadProduct(
      item.product_id,
      filters,
      true,
      currentQuery,
      "relevance",
      0,
    );
  }

  useEffect(() => {
    function focusSearch(event: globalThis.KeyboardEvent) {
      if (isEditableTarget(event.target)) return;

      const shortcut =
        event.key === "/"
        || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k");

      if (!shortcut) return;

      event.preventDefault();
      searchInputRef.current?.focus();
      searchInputRef.current?.select();
    }

    window.addEventListener("keydown", focusSearch);
    return () => window.removeEventListener("keydown", focusSearch);
  }, []);

  useEffect(() => {
    const cleaned = query.trim();
    if (cleaned.length < 2 || cleaned === appliedQuery) {
      setSuggestions([]);
      setActiveSuggestionIndex(-1);
      setSuggesting(false);
      return;
    }

    const requestId = ++suggestionRequestRef.current;
    const timeout = window.setTimeout(() => {
      setSuggesting(true);
      void suggestProducts(cleaned, filters)
        .then((response) => {
          if (requestId !== suggestionRequestRef.current) return;
          setSuggestions(response.items);
          setActiveSuggestionIndex(-1);
        })
        .catch(() => {
          if (requestId !== suggestionRequestRef.current) return;
          setSuggestions([]);
          setActiveSuggestionIndex(-1);
        })
        .finally(() => {
          if (requestId === suggestionRequestRef.current) {
            setSuggesting(false);
          }
        });
    }, 250);

    return () => window.clearTimeout(timeout);
  }, [
    query,
    filters.state_code,
    filters.macroregion,
    filters.supplier,
    filters.buyer,
    filters.start_date,
    filters.end_date,
    appliedQuery,
  ]);

  useEffect(() => {
    void fetchProductDiscovery()
      .then((response) => setDiscovery(response.items))
      .catch(() => undefined);

    if (initialState.query.trim().length >= 2) {
      void (async () => {
        await runSearch(
          initialState.query,
          initialState.filters,
          initialState.offset,
          initialState.sort,
        );
        if (initialState.productId) {
          await loadProduct(
            initialState.productId,
            initialState.filters,
            false,
            initialState.query,
            initialState.sort,
            initialState.offset,
          );
        }
      })();
    }
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
  const normalizedQuery = normalizeDiscoveryText(query);
  const discoverySuggestions = discovery
    .filter((item) => {
      if (normalizedQuery.length < 2) return false;
      const label = normalizeDiscoveryText(item.label);
      return label.includes(normalizedQuery) || normalizedQuery.includes(label);
    })
    .slice(0, 4);
  const knownPriceCategories = discovery.filter(
    (item) => item.priced_observation_count > 0,
  );
  const discoveryHighlights = (
    discoverySuggestions.length > 0
      ? discoverySuggestions
      : knownPriceCategories
  );
  const activeFilterEntries = (
    Object.entries(appliedFilters) as Array<[keyof AnalyticsFilters, string]>
  ).filter(([, value]) => value.trim().length > 0);
  const hasAppliedFilters = activeFilterEntries.length > 0;
  const refinementGroups = Object.entries(facets)
    .map(([key, values]) => ({
      key,
      label: FACET_LABELS[key] ?? key,
      values: values.filter((item) => {
        const candidate = normalizeDiscoveryText(
          queryFacetValue(item.value),
        );
        const current = normalizeDiscoveryText(
          appliedQuery.replaceAll("_", " "),
        );
        return candidate.length > 0 && !current.includes(candidate);
      }),
    }))
    .filter((group) => group.values.length > 0)
    .slice(0, 4);

  return (
    <>
      <section className="hero analytics-hero analytics-hero-compact">
        <span className="eyebrow">Inteligência de preços públicos</span>
        <h1>Descubra quanto o governo paga pelo produto que você procura.</h1>
        <p>
          Pesquise do seu jeito. O Atlas organiza dados públicos do PNCP para comparar
          preços homologados, histórico e evidências em uma única análise.
        </p>
        <div className="analytics-trust-row" aria-label="Características do Atlas">
          <span>Dados públicos</span>
          <span>Preços homologados</span>
          <span>Fonte rastreável</span>
        </div>
      </section>

      <section className="panel analytics-search-panel">
        <form onSubmit={submit}>
          <div className="analytics-search-heading">
            <div>
              <span className="section-kicker">Explorador de preços</span>
              <label htmlFor="analytics-search">O que você quer pesquisar?</label>
            </div>
            <small>Digite um produto, cor, apresentação ou termo usado no dia a dia.</small>
          </div>
          <div className="analytics-search-row">
            <div className="analytics-search-input-wrap">
              <input
                ref={searchInputRef}
                id="analytics-search"
                value={query}
                onChange={(event: { target: { value: string } }) => setQuery(event.target.value)}
                placeholder="Ex.: resina A2, CIV, anestésico local"
                autoComplete="off"
                aria-autocomplete="list"
                aria-expanded={suggestions.length > 0}
                aria-controls="analytics-suggestions"
                aria-activedescendant={
                  activeSuggestionIndex >= 0
                    ? `analytics-suggestion-${suggestions[activeSuggestionIndex]?.product_id}`
                    : undefined
                }
                onKeyDown={handleSearchKeyDown}
              />
              <span className="analytics-search-shortcut" aria-hidden="true">
                /
              </span>
              {(suggesting || suggestions.length > 0) && (
                <div
                  id="analytics-suggestions"
                  className="analytics-suggestions"
                  role="listbox"
                >
                  {suggesting && suggestions.length === 0 ? (
                    <div className="analytics-suggestion-loading">
                      Procurando produtos...
                    </div>
                  ) : (
                    suggestions.map((item, index) => (
                      <button
                        type="button"
                        role="option"
                        id={`analytics-suggestion-${item.product_id}`}
                        aria-selected={activeSuggestionIndex === index}
                        className={
                          activeSuggestionIndex === index
                            ? "analytics-suggestion-active"
                            : undefined
                        }
                        key={item.product_id}
                        onMouseEnter={() => setActiveSuggestionIndex(index)}
                        onClick={() => void chooseSuggestion(item)}
                      >
                        <span>
                          <strong>{item.display_name}</strong>
                          <small className="analytics-result-description">{item.sample_description}</small>
                        </span>
                        <span>
                          {number(item.priced_observation_count)} preços
                        </span>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
            <button
              className="primary-button"
              type="submit"
              disabled={searching || query.trim().length < 2}
            >
              {searching ? "Pesquisando..." : "Pesquisar"}
            </button>
          </div>

          {discoveryHighlights.length > 0 && (
            <div className="analytics-known-categories">
              <div className="analytics-known-categories-heading">
                <div>
                  <span>
                    {discoverySuggestions.length > 0
                      ? "Talvez você esteja procurando"
                      : "Categorias conhecidas"}
                  </span>
                  <small>
                    {discoverySuggestions.length > 0
                      ? "Categorias compatíveis com o que você digitou"
                      : "Somente categorias com observações de preço na base"}
                  </small>
                </div>
                {discoverySuggestions.length === 0 && (
                  <strong>{number(knownPriceCategories.length)} categorias</strong>
                )}
              </div>
              <div className="analytics-known-category-grid">
                {discoveryHighlights.map((item) => (
                  <button
                    type="button"
                    key={item.product_category}
                    onClick={() => {
                      setQuery(item.label);
                      void runSearch(item.label, filters, 0, sort, true);
                    }}
                  >
                    <span>{item.label}</span>
                    <small>
                      {number(item.product_count)} grupos ·{" "}
                      {number(item.priced_observation_count)} preços
                    </small>
                  </button>
                ))}
              </div>
            </div>
          )}

          <details className="analytics-filter-drawer">
            <summary>
              <span>Filtros avançados</span>
              <small>
                {Object.values(filters).filter((value) => value.trim()).length > 0
                  ? `${Object.values(filters).filter((value) => value.trim()).length} ativos`
                  : "Região, fornecedor, órgão e período"}
              </small>
            </summary>
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

            <label>
              Ordenar resultados
              <select
                value={sort}
                onChange={(event) => setSort(event.target.value as ProductSort)}
              >
                {SORT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            </div>
            <div className="analytics-filter-actions">
              <button
                type="button"
                onClick={() => {
                  const cleared = { ...EMPTY_FILTERS };
                  setFilters(cleared);
                  if (hasSearched && query.trim().length >= 2) {
                    void runSearch(query, cleared, 0, sort);
                  }
                }}
              >
                Limpar
              </button>
              <button
                className="primary-button"
                type="submit"
                disabled={searching || query.trim().length < 2}
              >
                Aplicar filtros
              </button>
            </div>
          </details>
        </form>

        {recentSearches.length > 0 && (
          <div className="analytics-recent-searches">
            <div>
              <span>Pesquisas recentes</span>
              <button type="button" onClick={clearRecentSearches}>
                Limpar
              </button>
            </div>
            <div>
              {recentSearches.map((recent) => (
                <button
                  type="button"
                  key={recent}
                  onClick={() => {
                    setQuery(recent);
                    void runSearch(recent, filters, 0, sort, true);
                  }}
                >
                  {recent}
                </button>
              ))}
            </div>
          </div>
        )}

        {interpretedLabel && (
          <p className="analytics-interpreted">
            Busca reconhecida como <strong>{interpretedLabel}</strong>. Você pode continuar refinando por cor, apresentação ou filtros.
          </p>
        )}

        {error && (
          <p className="analytics-error" role="alert">
            {error}
          </p>
        )}
      </section>

      {hasSearched && (
      <section
        ref={resultsRef}
        className="analytics-results"
        tabIndex={-1}
        aria-busy={searching}
        aria-label="Resultados da pesquisa"
      >
        <div className="results-header">
          <div>
            <span className="section-kicker">Resultados compatíveis</span>
            <h2>
              {searching ? "Pesquisando..." : `Resultados para “${appliedQuery}”`}
            </h2>
          </div>
          {!searching && <span className="item-count">{number(total)} grupos</span>}
          <span className="sr-only" role="status" aria-live="polite">
            {!searching
              ? `${number(total)} grupos encontrados para ${appliedQuery}`
              : "Pesquisando produtos"}
          </span>
        </div>

        {hasAppliedFilters && (
          <div className="analytics-active-filters" aria-label="Filtros aplicados">
            <span>Filtrando por</span>
            {activeFilterEntries.map(([key, value]) => (
              <button
                type="button"
                key={key}
                title="Remover filtro"
                onClick={() => removeAppliedFilter(key)}
              >
                {FILTER_LABELS[key]}: {value}
                <b aria-hidden="true">×</b>
              </button>
            ))}
            <button
              type="button"
              className="analytics-clear-filter-chip"
              onClick={clearAllAppliedFilters}
            >
              Limpar todos
            </button>
          </div>
        )}

        {!searching && refinementGroups.length > 0 && results.length > 0 && (
          <div className="analytics-refinements">
            <span>Refinar resultados</span>
            {refinementGroups.map((group) => (
              <div key={group.key}>
                <small>{group.label}</small>
                <div>
                  {group.values.slice(0, 6).map((item) => (
                    <button
                      type="button"
                      key={`${group.key}-${item.value}`}
                      onClick={() => applyRefinement(item.value)}
                    >
                      {formatFacetValue(group.key, item.value)}
                      <b>{number(item.product_count)}</b>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {searching ? (
          <div className="analytics-loading-state" aria-live="polite">
            <span>Consultando a base analítica</span>
            <div />
            <div />
            <div />
          </div>
        ) : results.length === 0 ? (
          <div className="empty-state analytics-empty-recovery">
            <strong>Nenhum produto encontrado.</strong>
            <span>
              {hasAppliedFilters
                ? "O produto pode existir fora do recorte atual. Remova um filtro ou tente uma categoria abaixo."
                : "Tente um termo mais amplo ou escolha uma categoria disponível na base."}
            </span>
            {hasAppliedFilters && (
              <button
                type="button"
                className="analytics-empty-clear"
                onClick={clearAllAppliedFilters}
              >
                Tentar novamente sem filtros
              </button>
            )}
            {discovery.length > 0 && (
              <div className="analytics-empty-actions">
                {discovery.slice(0, 4).map((item) => (
                  <button
                    type="button"
                    key={item.product_category}
                    onClick={() => {
                      setQuery(item.label);
                      void runSearch(item.label, filters, 0, sort, true);
                    }}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <>
            <div className="analytics-result-list">
              {results.map((item) => {
                const compared = comparisonItems.some(
                  (candidate) => candidate.product_id === item.product_id,
                );

                return (
                  <article
                    key={item.product_id}
                    className={
                      selectedId === item.product_id
                        ? "analytics-result analytics-result-selected"
                        : "analytics-result"
                    }
                  >
                    <button
                      type="button"
                      className="analytics-result-main"
                      onClick={() => void selectProduct(item)}
                    >
                      <span>
                        <strong>{item.display_name}</strong>
                        <small>{item.sample_description}</small>
                        {item.match_reasons.length > 0 && (
                          <span className="analytics-match-reasons" aria-label="Por que combinou">
                            {item.match_reasons.map((reason) => (
                              <span key={reason}>{reason}</span>
                            ))}
                          </span>
                        )}
                        <span className="analytics-result-facts">
                          <span>{number(item.procurement_count)} compras</span>
                          <span>{number(item.priced_observation_count)} preços</span>
                          <span>{number(item.state_count)} UFs</span>
                          {item.latest_date && <span>até {date(item.latest_date)}</span>}
                        </span>
                      </span>
                      <span className="analytics-result-summary">
                        <strong>{money(item.median_price)}</strong>
                        <small>
                          {item.normalized_quantity_unit
                            ? `mediana por ${item.normalized_quantity_unit}`
                            : "mediana normalizada"}
                        </small>
                        {item.percentile_25 !== null && item.percentile_75 !== null && (
                          <span className="analytics-reference-range">
                            <span>Faixa central</span>
                            <b>{money(item.percentile_25)} – {money(item.percentile_75)}</b>
                          </span>
                        )}
                        <em>Ver análise</em>
                      </span>
                    </button>
                    <button
                      type="button"
                      className={
                        compared
                          ? "analytics-compare-toggle active"
                          : "analytics-compare-toggle"
                      }
                      aria-pressed={compared}
                      onClick={() => toggleComparison(item)}
                    >
                      {compared ? "Remover" : "Comparar"}
                    </button>
                  </article>
                );
              })}
            </div>

            {comparisonItems.length > 0 && (
              <section className="analytics-comparison" aria-label="Comparação de produtos">
                <div className="analytics-comparison-heading">
                  <div>
                    <span className="section-kicker">Comparação</span>
                    <h3>
                      {comparisonItems.length === 1
                        ? "Selecione mais um produto"
                        : `${comparisonItems.length} produtos lado a lado`}
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setComparisonItems([])}
                  >
                    Limpar
                  </button>
                </div>

                {comparisonItems.length >= 2 && (
                  <>
                    <p className="analytics-comparison-note">
                      Comparação restrita à mesma categoria e unidade normalizada.
                    </p>
                    <div className="analytics-comparison-table-wrap">
                      <table className="analytics-comparison-table">
                        <thead>
                          <tr>
                            <th>Métrica</th>
                            {comparisonItems.map((item) => (
                              <th key={item.product_id}>{item.display_name}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          <tr>
                            <th>Mediana</th>
                            {comparisonItems.map((item) => (
                              <td key={item.product_id}>
                                <strong>{money(item.median_price)}</strong>
                                <small>
                                  {item.normalized_quantity_unit
                                    ? ` por ${item.normalized_quantity_unit}`
                                    : ""}
                                </small>
                              </td>
                            ))}
                          </tr>
                          <tr>
                            <th>Faixa central (P25–P75)</th>
                            {comparisonItems.map((item) => (
                              <td key={item.product_id}>
                                {item.percentile_25 !== null && item.percentile_75 !== null
                                  ? `${money(item.percentile_25)} – ${money(item.percentile_75)}`
                                  : "Sem amostra"}
                              </td>
                            ))}
                          </tr>
                          <tr>
                            <th>Faixa observada</th>
                            {comparisonItems.map((item) => (
                              <td key={item.product_id}>
                                {item.min_price !== null && item.max_price !== null
                                  ? `${money(item.min_price)} – ${money(item.max_price)}`
                                  : "Sem amostra"}
                              </td>
                            ))}
                          </tr>
                          <tr>
                            <th>Preços comparáveis</th>
                            {comparisonItems.map((item) => (
                              <td key={item.product_id}>
                                {number(item.priced_observation_count)}
                              </td>
                            ))}
                          </tr>
                          <tr>
                            <th>Compras</th>
                            {comparisonItems.map((item) => (
                              <td key={item.product_id}>
                                {number(item.procurement_count)}
                              </td>
                            ))}
                          </tr>
                          <tr>
                            <th>UFs</th>
                            {comparisonItems.map((item) => (
                              <td key={item.product_id}>
                                {number(item.state_count)}
                              </td>
                            ))}
                          </tr>
                          <tr>
                            <th>Apresentação</th>
                            {comparisonItems.map((item) => (
                              <td key={item.product_id}>
                                {item.presentation
                                  ? formatFacetValue("presentation", item.presentation)
                                  : "Não informada"}
                              </td>
                            ))}
                          </tr>
                          <tr>
                            <th>Cor</th>
                            {comparisonItems.map((item) => (
                              <td key={item.product_id}>
                                {item.shade ?? "Não informada"}
                              </td>
                            ))}
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </>
                )}
              </section>
            )}
          </>
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
                  appliedSort,
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
                  appliedSort,
                )
              }
            >
              Próxima
            </button>
          </div>
        )}
      </section>
      )}

      <section
        ref={detailRef}
        className="analytics-detail"
        tabIndex={-1}
        aria-busy={loading}
        aria-label="Análise detalhada do produto"
      >
        {loading && (
          <div className="analytics-loading-state analytics-loading-detail" aria-live="polite">
            <span>Preparando a análise completa</span>
            <div />
            <div />
            <div />
          </div>
        )}

        {!loading && bundle && summary && stats && (
          <>
            <div className="analytics-title-row">
              <div>
                <span className="section-kicker">Análise consolidada</span>
                <h2 id="analytics-detail-title">{summary.display_name}</h2>
                <p>{summary.sample_description}</p>
              </div>
              <div className="analytics-title-actions">
                <span className={summary.sample_sufficient ? "sample-status" : "sample-status sample-status-warning"}>
                  {summary.sample_sufficient
                    ? `${number(summary.price_sample_count)} preços comparáveis`
                    : `Amostra pequena: ${number(summary.price_sample_count)} preços`}
                </span>
                {summary.latest_update && (
                  <span className="analytics-updated">
                    Atualizado {date(summary.latest_update)}
                  </span>
                )}
                <details className="analytics-actions-menu">
                  <summary>Ações</summary>
                  <div>
                    <button type="button" onClick={() => void copyShareLink()}>
                      {shareFeedback ?? "Copiar link"}
                    </button>
                    <button
                      type="button"
                      disabled={exporting}
                      onClick={() => void exportCsv()}
                    >
                      {exporting ? "Exportando..." : "Exportar CSV"}
                    </button>
                  </div>
                </details>
              </div>
            </div>

            <div className="analytics-detail-toolbar">
              <button
                type="button"
                className="analytics-back-results"
                onClick={() =>
                  resultsRef.current?.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                  })
                }
              >
                Voltar aos resultados
              </button>
              <div className="analytics-detail-tabs" role="tablist" aria-label="Seções da análise">
                <button
                  type="button"
                  role="tab"
                  aria-selected={detailView === "overview"}
                  className={detailView === "overview" ? "active" : ""}
                  onClick={() => setDetailView("overview")}
                >
                  Visão geral
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={detailView === "market"}
                  className={detailView === "market" ? "active" : ""}
                  onClick={() => setDetailView("market")}
                >
                  Mercado
                </button>
                <button
                  type="button"
                  role="tab"
                  aria-selected={detailView === "evidence"}
                  className={detailView === "evidence" ? "active" : ""}
                  onClick={() => setDetailView("evidence")}
                >
                  Evidências
                </button>
              </div>
            </div>

            {!summary.sample_sufficient && (
              <p className="sample-warning">
                A amostra está abaixo do mínimo metodológico de {number(summary.minimum_sample_size)} observações de preço. Interprete as estatísticas com cautela.
              </p>
            )}

            <section className="analytics-executive-summary" hidden={detailView !== "overview"}>
              <div className="analytics-price-hero">
                <span>Preço de referência</span>
                <strong>{money(stats.median_price)}</strong>
                <small>{summary.price_unit ?? "preço normalizado"}</small>
                <p>
                  Metade das observações comparáveis está entre{" "}
                  <b>{money(stats.percentile_25)}</b> e{" "}
                  <b>{money(stats.percentile_75)}</b>.
                </p>
              </div>
              <div className="analytics-summary-stats">
                <div><span>Compras</span><strong>{number(summary.procurement_count)}</strong><small>processos distintos</small></div>
                <div><span>Fornecedores</span><strong>{number(summary.supplier_count)}</strong><small>documentos distintos</small></div>
                <div><span>UFs</span><strong>{number(summary.state_count)}</strong><small>cobertura observada</small></div>
                <div><span>Período</span><strong>{date(summary.period_start)}</strong><small>até {date(summary.period_end)}</small></div>
              </div>
            </section>

            {detailView === "market" && (
              <div className="analytics-view-intro">
                <div>
                  <span className="section-kicker">Leitura de mercado</span>
                  <h3>Onde se compra, quem fornece e quem demanda.</h3>
                </div>
                <p>
                  Compare diferenças regionais e concentração entre fornecedores e órgãos compradores.
                </p>
              </div>
            )}

            {detailView === "evidence" && (
              <div className="analytics-view-intro">
                <div>
                  <span className="section-kicker">Base auditável</span>
                  <h3>Do indicador de preço até o registro de origem.</h3>
                </div>
                <p>
                  {number(bundle.signals.items.length)} sinais estatísticos e{" "}
                  {number(bundle.records.total)} registros disponíveis neste recorte.
                </p>
              </div>
            )}

            <div className="analytics-grid">
              <article className="analytics-card analytics-card-wide" hidden={detailView !== "overview"}>
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

              <article className="analytics-card analytics-card-wide" hidden={detailView !== "overview"}>
                <span className="section-kicker">Evolução</span>
                <h3>Histórico de preços</h3>
                {bundle.history.points.length === 0 ? (
                  <p className="analytics-empty">Sem série temporal defensável para este produto.</p>
                ) : (
                  <>
                    <HistoryChart points={bundle.history.points} />
                    <details className="analytics-data-disclosure">
                      <summary>
                        <span>Ver tabela detalhada</span>
                        <small>{number(bundle.history.points.length)} períodos</small>
                      </summary>
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
                    </details>
                  </>
                )}
              </article>

              <article className="analytics-card" hidden={detailView !== "market"}>
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

              <article className="analytics-card" hidden={detailView !== "market"}>
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

              <article className="analytics-card" hidden={detailView !== "market"}>
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

              <article className="analytics-card analytics-card-wide" hidden={detailView !== "evidence"}>
                <span className="section-kicker">Sinais estatísticos</span>
                <h3>Preços fora da distribuição observada</h3>
                <p className="analytics-note">{bundle.signals.disclaimer}</p>
                {bundle.signals.items.length === 0 ? (
                  <p className="analytics-empty">Nenhum sinal estatístico publicado para este produto.</p>
                ) : (
                  <details className="analytics-data-disclosure">
                    <summary>
                      <span>Ver sinais detectados</span>
                      <small>{number(bundle.signals.items.length)} registros</small>
                    </summary>
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
                  </details>
                )}
              </article>

              <article className="analytics-card analytics-card-wide" hidden={detailView !== "evidence"}>
                <span className="section-kicker">Rastreabilidade</span>
                <h3>Registros que sustentam a análise</h3>
                <p className="analytics-note">
                  Mostrando {number(bundle.records.items.length)} de {number(bundle.records.total)} registros neste recorte.
                </p>
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
