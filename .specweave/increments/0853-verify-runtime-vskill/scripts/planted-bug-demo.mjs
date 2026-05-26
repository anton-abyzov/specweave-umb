#!/usr/bin/env node
// Anthropic phase-3-verify "planted-bug" demo (video ~26:00).
//
// "If you were to run the unit tests in this case, then you would actually
//  pass the tests — we've deliberately put the verification in wrong just to
//  demonstrate that the test matrix itself will actually pass." (Ara, Anthropic)
//
// We do the same here for both U-INSTALL units. Two scenarios:
//   1. AC-US4-01 — inject a wrong invariant on an existing fixture → must FAIL
//   2. AC-US4-02 — inject an act() that throws → must verdict=BLOCKED

import { runFixture } from "./runner.mjs";

// Construct a synthetic unit independently — does NOT touch the real registry.
const plantedBugUnit = {
  id: "DEMO-PLANTED-BUG",
  command: "synthetic — does not run a real command",
  surfaceSchema: {
    safeParse: (s) => ({ success: true, data: s }),
  },
  invariants: [
    {
      id: "two-plus-two-is-five",
      description: "DELIBERATELY WRONG: claims 2+2=5",
      predicate: (s) => s.two_plus_two === 5,
    },
  ],
  fixtures: [
    {
      id: "lie-fixture",
      description: "happy-looking fixture with a planted lie",
      probe: true,
      act: async () => ({ two_plus_two: 4 }), // truth — invariant is wrong
    },
  ],
};

const blockedUnit = {
  id: "DEMO-BLOCKED",
  command: "synthetic — act() throws",
  surfaceSchema: { safeParse: (s) => ({ success: true, data: s }) },
  invariants: [{ id: "noop", description: "noop", predicate: () => true }],
  fixtures: [
    {
      id: "throwing-act",
      description: "act() throws — should produce BLOCKED, not FAIL",
      probe: true,
      act: async () => {
        throw new Error("simulated unreachable backend");
      },
    },
  ],
};

const r1 = await runFixture(plantedBugUnit, plantedBugUnit.fixtures[0]);
const r2 = await runFixture(blockedUnit, blockedUnit.fixtures[0]);

console.log("Planted-bug demo — proves the runner catches lies and distinguishes BLOCKED");
console.log("=".repeat(72));
console.log("Scenario 1: invariant says 2+2=5 (lie), act returns 4 (truth)");
console.log("   verdict:", r1.verdict, "  expected: FAIL");
console.log("   failing check:", r1.checks.find((c) => c.status === "fail")?.id);
console.log("");
console.log("Scenario 2: act() throws synthetic error");
console.log("   verdict:", r2.verdict, "  expected: BLOCKED");
console.log("   blockedReason head:", r2.blockedReason?.split("\n")[0]);
console.log("");

const ok = r1.verdict === "FAIL" && r2.verdict === "BLOCKED";
console.log(ok ? "✅ DEMO PASSED — runner caught both" : "❌ DEMO FAILED");
process.exit(ok ? 0 : 1);
