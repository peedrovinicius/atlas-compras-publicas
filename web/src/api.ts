import type {
  AnalyticsFilters,
  BatchResponse,
  NormalizationResult,
  ParserCategory,
  ProductAnalyticsBundle,
  ProductBuyers,
  ProductDistribution,
  ProductDiscoveryResponse,
  ProductHistory,
  ProductRecords,
  ProductRegions,
  ProductSearchResponse,
  ProductSignals,
  ProductSort,
  ProductSummary,
  ProductSuppliers,
} from "./types";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ??
  "https://atlas-compras-publicas-analytics.onrender.com"
).replace(/\/$/, "");

async function decode<T>(response: Response): Promise<T> {
  let body: unknown;

  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    const detail =
      body &&
      typeof body === "object" &&
      "detail" in body &&
      typeof body.detail === "string"
        ? body.detail
        : "Não foi possível concluir a solicitação.";
    throw new Error(detail);
  }

  return body as T;
}

function analyticsFilterParams(filters: AnalyticsFilters): URLSearchParams {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    const cleaned = value.trim();
    if (cleaned) params.set(key, cleaned);
  }
  return params;
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  return decode<T>(response);
}

export async function fetchCategories(): Promise<ParserCategory[]> {
  return get<ParserCategory[]>("/api/v1/parser/categories");
}

export async function normalizeDescriptions(
  descriptions: string[],
): Promise<NormalizationResult[]> {
  if (descriptions.length === 1) {
    const query = new URLSearchParams({ description: descriptions[0] });
    return [await get<NormalizationResult>(`/api/v1/normalize?${query.toString()}`)];
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/normalize/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(descriptions),
  });
  const body = await decode<BatchResponse>(response);
  return body.items;
}

export async function fetchProductDiscovery(): Promise<ProductDiscoveryResponse> {
  return get<ProductDiscoveryResponse>("/api/v1/products/discovery");
}

export async function suggestProducts(
  query: string,
  filters: AnalyticsFilters,
): Promise<ProductSearchResponse> {
  return searchProducts(query, filters, "relevance", 6, 0);
}

export async function searchProducts(
  query: string,
  filters: AnalyticsFilters,
  sort: ProductSort,
  limit = 10,
  offset = 0,
): Promise<ProductSearchResponse> {
  const params = analyticsFilterParams(filters);
  params.set("q", query);
  params.set("sort", sort);
  params.set("limit", String(limit));
  params.set("offset", String(offset));
  return get<ProductSearchResponse>(`/api/v1/products/search?${params.toString()}`);
}

export async function fetchProductAnalytics(
  productId: string,
  filters: AnalyticsFilters,
): Promise<ProductAnalyticsBundle> {
  const encoded = encodeURIComponent(productId);
  const filterQuery = analyticsFilterParams(filters);
  const withFilters = (path: string, extra?: Record<string, string>) => {
    const params = new URLSearchParams(filterQuery);
    for (const [key, value] of Object.entries(extra ?? {})) {
      params.set(key, value);
    }
    const query = params.toString();
    return query ? `${path}?${query}` : path;
  };
  const [
    summary,
    distribution,
    history,
    regions,
    suppliers,
    buyers,
    signals,
    records,
  ] = await Promise.all([
      get<ProductSummary>(withFilters(`/api/v1/products/${encoded}`)),
      get<ProductDistribution>(
        withFilters(`/api/v1/products/${encoded}/distribution`),
      ),
      get<ProductHistory>(withFilters(`/api/v1/products/${encoded}/history`)),
      get<ProductRegions>(withFilters(`/api/v1/products/${encoded}/regions`)),
      get<ProductSuppliers>(
        withFilters(`/api/v1/products/${encoded}/suppliers`, { limit: "10" }),
      ),
      get<ProductBuyers>(
        withFilters(`/api/v1/products/${encoded}/buyers`, { limit: "10" }),
      ),
      get<ProductSignals>(
        withFilters(`/api/v1/products/${encoded}/signals`, { limit: "10" }),
      ),
      get<ProductRecords>(
        withFilters(`/api/v1/products/${encoded}/records`, { limit: "12" }),
      ),
    ]);

  return { summary, distribution, history, regions, suppliers, buyers, signals, records };
}

export async function downloadProductRecordsCsv(
  productId: string,
  filters: AnalyticsFilters,
): Promise<void> {
  const encoded = encodeURIComponent(productId);
  const params = analyticsFilterParams(filters);
  const query = params.toString();
  const path = `/api/v1/products/${encoded}/records.csv${query ? `?${query}` : ""}`;
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    await decode<never>(response);
  }

  const blob = await response.blob();
  const href = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = href;
  anchor.download = `atlas-${productId.slice(0, 8)}-registros.csv`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(href);
}

export async function checkHealth(): Promise<{
  ok: boolean;
  version: string | null;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      return { ok: false, version: null };
    }
    const body = (await response.json()) as { version?: string };
    return { ok: true, version: body.version ?? null };
  } catch {
    return { ok: false, version: null };
  }
}

export { API_BASE_URL };
