import test from "node:test";
import assert from "node:assert/strict";

import {
  UNKNOWN_PROVENANCE,
  parseProvenance,
  provenanceDisplay,
} from "../src/provenance.ts";

const real = {
  source_type: "pncp_sample",
  captured_at: "2026-11-03T23:00:00+00:00",
  procurement_keys: ["pncp:15126437000305:2026:212"],
  procurement_count: 1,
  result_count: 3,
  observation_count: 3,
  notice: "Amostra capturada do PNCP.",
};

test("identifies an explicitly tagged PNCP sample, never the entire market", () => {
  const parsed = parseProvenance(real);
  assert.equal(parsed.source_type, "pncp_sample");
  assert.match(provenanceDisplay(parsed.source_type).description, /amostra/i);
});

test("synthetic labels warn that prices and suppliers are fictional", () => {
  const parsed = parseProvenance({ ...real, source_type: "offline_synthetic" });
  assert.equal(parsed.source_type, "offline_synthetic");
  const message = provenanceDisplay(parsed.source_type);
  assert.match(message.title, /fictícios/i);
  assert.match(message.reportSource, /sintéticos/i);
  assert.equal(message.filenameLabel, "sintetico");
});

test("missing and obsolete API metadata never claim PNCP origin", () => {
  for (const input of [null, {}, { provenance: real }, { ...real, source_type: "invalid" }]) {
    assert.deepEqual(parseProvenance(input), UNKNOWN_PROVENANCE);
    assert.match(provenanceDisplay("unknown").reportSource, /não verificada/i);
  }
});

test("rejects incomplete PNCP metadata rather than inferring real records", () => {
  assert.equal(
    parseProvenance({ ...real, procurement_count: undefined }).source_type,
    "unknown",
  );
  assert.equal(
    parseProvenance({ ...real, procurement_keys: "bad" }).source_type,
    "unknown",
  );
});
