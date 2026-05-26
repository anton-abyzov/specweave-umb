// Build-gate test — Anthropic phase-3-verify rule:
//   "every VerifiableUnit MUST have at least one probe fixture; otherwise the
//    suite is only a happy-path replay and the framework can't catch lies."
// We also enforce ≥1 declared invariant per unit (warn → soft pass for MVP).

import { test } from "node:test";
import assert from "node:assert/strict";

import { listUnits } from "./registry.mjs";
// Imports register the units.
import "./units/install.verify.mjs";
import "./units/skill-new.verify.mjs";
import "./units/remove.verify.mjs";
import "./units/list.verify.mjs";
import "./units/info.verify.mjs";
import "./units/outdated.verify.mjs";
import "./units/audit.verify.mjs";
import "./units/pin.verify.mjs";
import "./units/init.verify.mjs";
import "./units/lockfile-cycle.verify.mjs";
import "./units/studio-api.verify.mjs";

test("AC-US2-01: every unit has at least one probe fixture", () => {
  for (const u of listUnits()) {
    const probes = u.fixtures.filter((f) => f.probe === true);
    assert.ok(
      probes.length >= 1,
      `Unit "${u.id}" has no probe fixtures — only the happy path is covered. Add at least one fixture with probe: true.`,
    );
  }
});

test("AC-US2-02: every unit declares at least one invariant", () => {
  for (const u of listUnits()) {
    assert.ok(
      u.invariants.length >= 1,
      `Unit "${u.id}" declares zero invariants — surface would be unverified beyond schema.`,
    );
  }
});

test("manifest is non-empty (sanity)", () => {
  const units = listUnits();
  assert.ok(units.length >= 10, `expected ≥10 registered units after expansion, got ${units.length}`);
});
