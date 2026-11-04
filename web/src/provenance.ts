import type { DemoProvenance, ProvenanceSourceType } from "./types";

export const UNKNOWN_PROVENANCE: DemoProvenance = {
  source_type: "unknown",
  captured_at: null,
  procurement_keys: [],
  procurement_count: null,
  result_count: null,
  observation_count: null,
  notice: "Origem não verificada. Não interprete valores como preços reais.",
};

export function parseProvenance(input: unknown): DemoProvenance {
  if (!input || typeof input !== "object") return UNKNOWN_PROVENANCE;
  const data = input as Record<string, unknown>;
  if (
    data.source_type !== "offline_synthetic"
    && data.source_type !== "pncp_sample"
  ) return UNKNOWN_PROVENANCE;
  if (
    typeof data.captured_at !== "string"
    || !Array.isArray(data.procurement_keys)
    || !data.procurement_keys.every((key: unknown) => typeof key === "string")
    || typeof data.procurement_count !== "number"
    || typeof data.result_count !== "number"
    || typeof data.observation_count !== "number"
  ) return UNKNOWN_PROVENANCE;

  return {
    source_type: data.source_type,
    captured_at: data.captured_at,
    procurement_keys: data.procurement_keys,
    procurement_count: data.procurement_count,
    result_count: data.result_count,
    observation_count: data.observation_count,
    notice: typeof data.notice === "string" ? data.notice : "",
  };
}

export function provenanceDisplay(source: ProvenanceSourceType): {
  title: string;
  description: string;
  reportSource: string;
  filenameLabel: string;
} {
  if (source === "pncp_sample") {
    return {
      title: "Amostra obtida do PNCP",
      description: (
        "Registros capturados do PNCP para uma amostra de contratações. "
        + "Não representam todo o mercado nem garantem atualização em tempo real."
      ),
      reportSource: "Fonte: amostra de dados públicos capturada do PNCP.",
      filenameLabel: "pncp",
    };
  }
  if (source === "offline_synthetic") {
    return {
      title: "Dados demonstrativos — preços fictícios",
      description: (
        "Esta base foi gerada pelo fallback offline. Os preços, fornecedores "
        + "e resultados são totalmente sintéticos e NÃO são preços homologados."
      ),
      reportSource: (
        "ATENÇÃO: dados sintéticos de demonstração; "
        + "não constituem registros de compras públicas homologadas."
      ),
      filenameLabel: "sintetico",
    };
  }
  return {
    title: "Origem dos dados não verificada",
    description: (
      "Não foi possível comprovar a origem da base. "
      + "Não utilize estes valores como histórico real de preços públicos."
    ),
    reportSource: (
      "ATENÇÃO: proveniência não verificada. "
      + "Não apresentar como preços reais de compras públicas."
    ),
    filenameLabel: "origem-desconhecida",
  };
}
