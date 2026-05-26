// Runner — single execution path. Three audiences (CLI / vitest / agent) all call into here.
// Mirrors src/verify/core/runner.ts in cwc-workshops/phase-3-verify.
import { mkdtempSync, mkdirSync, writeFileSync, renameSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { runSchema } from "./verifiers/schema.mjs";
import { runInvariants } from "./verifiers/invariants.mjs";
import { listUnits, buildManifest } from "./registry.mjs";

/**
 * @param {import("./verify-types.mjs").VerifiableUnit} unit
 * @param {import("./verify-types.mjs").Fixture} fixture
 * @returns {Promise<import("./verify-types.mjs").FixtureResult>}
 */
export async function runFixture(unit, fixture) {
  const start = Date.now();
  const workdir = mkdtempSync(join(tmpdir(), `verify-${unit.id}-${fixture.id}-`));
  /** @type {import("./verify-types.mjs").FixtureCtx} */
  const ctx = { workdir, env: {} };

  let surface;
  try {
    surface = await fixture.act(ctx);
  } catch (err) {
    // Anthropic distinction: act-time exception = BLOCKED (we couldn't observe), not FAIL.
    return {
      unitId: unit.id,
      fixtureId: fixture.id,
      probe: !!fixture.probe,
      verdict: "BLOCKED",
      checks: [],
      durationMs: Date.now() - start,
      blockedReason: err instanceof Error ? `${err.message}\n${err.stack}` : String(err),
    };
  }

  const schemaChecks = runSchema(unit.surfaceSchema, surface);
  const invChecks = await runInvariants(unit.invariants, surface);
  const checks = [...schemaChecks, ...invChecks];

  // Verdict: any fail → FAIL. Else PASS. (warn does not downgrade.)
  const verdict = checks.some((c) => c.status === "fail") ? "FAIL" : "PASS";

  return {
    unitId: unit.id,
    fixtureId: fixture.id,
    probe: !!fixture.probe,
    verdict,
    checks,
    surface,
    durationMs: Date.now() - start,
  };
}

/** @param {import("./verify-types.mjs").VerifiableUnit} unit */
export async function runUnit(unit) {
  /** @type {import("./verify-types.mjs").FixtureResult[]} */
  const fixtures = [];
  for (const f of unit.fixtures) {
    fixtures.push(await runFixture(unit, f));
  }
  const verdict = fixtures.some((f) => f.verdict === "FAIL")
    ? "FAIL"
    : fixtures.some((f) => f.verdict === "BLOCKED")
      ? "BLOCKED"
      : "PASS";
  return { unitId: unit.id, command: unit.command, verdict, fixtures };
}

/** @returns {Promise<import("./verify-types.mjs").RunAllResult>} */
export async function runAll() {
  /** @type {import("./verify-types.mjs").UnitResult[]} */
  const units = [];
  for (const u of listUnits()) {
    units.push(await runUnit(u));
  }
  const verdict = units.some((u) => u.verdict === "FAIL")
    ? "FAIL"
    : units.some((u) => u.verdict === "BLOCKED")
      ? "BLOCKED"
      : "PASS";
  return {
    version: "1.0",
    runAt: new Date().toISOString(),
    verdict,
    units,
  };
}

/** Atomic write — tmp + rename. AC-US3-02. */
export function writeJsonAtomic(path, obj) {
  mkdirSync(join(path, ".."), { recursive: true });
  const tmp = `${path}.tmp.${process.pid}.${Date.now()}`;
  writeFileSync(tmp, JSON.stringify(obj, null, 2), { mode: 0o644 });
  renameSync(tmp, path);
}

/** Cleanup tmp workdir explicitly (caller's choice). */
export function cleanupWorkdir(dir) {
  try {
    rmSync(dir, { recursive: true, force: true });
  } catch {
    /* best effort */
  }
}

export { buildManifest };
