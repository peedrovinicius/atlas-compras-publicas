import test from "node:test";
import assert from "node:assert/strict";

import { analyticsFilterParams, decodeApiResponse } from "../src/api-utils.ts";

const blankFilters = {
  state_code: "",
  macroregion: "",
  supplier: "",
  buyer: "",
  start_date: "",
  end_date: "",
};

test("preserves API error messages for users", async () => {
  const response = new Response(JSON.stringify({ detail: "Produto não encontrado" }), {
    status: 404,
    headers: { "Content-Type": "application/json" },
  });
  await assert.rejects(decodeApiResponse(response), /Produto não encontrado/);
});

test("uses a safe fallback for malformed API errors", async () => {
  const response = new Response("temporary upstream failure", { status: 502 });
  await assert.rejects(
    decodeApiResponse(response),
    /Não foi possível concluir a solicitação/,
  );
});

test("returns a successful API JSON payload", async () => {
  const payload = { items: [{ id: "dental_adhesive" }] };
  const response = new Response(JSON.stringify(payload), { status: 200 });
  assert.deepEqual(await decodeApiResponse(response), payload);
});

test("trims filters and omits blanks to avoid accidental broad filters", () => {
  const query = analyticsFilterParams({
    ...blankFilters,
    state_code: " CE ",
    supplier: "  Saúde & Cia  ",
    buyer: "   ",
    start_date: "2026-01-01",
  });
  assert.equal(query.get("state_code"), "CE");
  assert.equal(query.get("supplier"), "Saúde & Cia");
  assert.equal(query.get("start_date"), "2026-01-01");
  assert.equal(query.has("buyer"), false);
  assert.equal(query.has("macroregion"), false);
  assert.equal(query.size, 3);
});

test("does not mutate filters supplied by the calling screen", () => {
  const filters = { ...blankFilters, state_code: " CE " };
  analyticsFilterParams(filters);
  assert.equal(filters.state_code, " CE ");
});
