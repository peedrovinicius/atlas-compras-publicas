import type {
  BatchResponse,
  NormalizationResult,
  ParserCategory,
} from "./types";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ??
  "https://atlas-compras-publicas.onrender.com"
).replace(/\/$/, "");

async function decode<T>(response: Response): Promise<T> {
  const body = await response.json();

  if (!response.ok) {
    const detail =
      typeof body?.detail === "string"
        ? body.detail
        : "Não foi possível concluir a solicitação.";
    throw new Error(detail);
  }

  return body as T;
}

export async function fetchCategories(): Promise<ParserCategory[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/parser/categories`);
  return decode<ParserCategory[]>(response);
}

export async function normalizeDescriptions(
  descriptions: string[],
): Promise<NormalizationResult[]> {
  if (descriptions.length === 1) {
    const query = new URLSearchParams({ description: descriptions[0] });
    const response = await fetch(
      `${API_BASE_URL}/api/v1/normalize?${query.toString()}`,
    );
    return [await decode<NormalizationResult>(response)];
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/normalize/batch`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(descriptions),
  });
  const body = await decode<BatchResponse>(response);
  return body.items;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export { API_BASE_URL };
