import type {
  BatchResponse,
  NormalizationResult,
  ParserCategory,
  ProductAnalyticsBundle,
  ProductBuyers,
  ProductDistribution,
  ProductHistory,
  ProductRecords,
  ProductRegions,
  ProductSearchResponse,
  ProductSignals,
  ProductSummary,
  ProductSuppliers,
} from "./types";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ??
  "https://atlas-compras-publicas.onrender.com"
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

export async function searchProducts(
  query: string,
  limit = 12,
): Promise<ProductSearchResponse> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return get<ProductSearchResponse>(`/api/v1/products/search?${params.toString()}`);
}

export async function fetchProductAnalytics(
  productId: string,
): Promise<ProductAnalyticsBundle> {
  const encoded = encodeURIComponent(productId);
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
      get<ProductSummary>(`/api/v1/products/${encoded}`),
      get<ProductDistribution>(`/api/v1/products/${encoded}/distribution`),
      get<ProductHistory>(`/api/v1/products/${encoded}/history`),
      get<ProductRegions>(`/api/v1/products/${encoded}/regions`),
      get<ProductSuppliers>(`/api/v1/products/${encoded}/suppliers?limit=10`),
      get<ProductBuyers>(`/api/v1/products/${encoded}/buyers?limit=10`),
      get<ProductSignals>(`/api/v1/products/${encoded}/signals?limit=10`),
      get<ProductRecords>(`/api/v1/products/${encoded}/records?limit=12`),
    ]);

  return { summary, distribution, history, regions, suppliers, buyers, signals, records };
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
