# 0671 — Skill Refinement Loop — Plan

## Architecture Overview

```
┌─ EXISTING (keeps working) ──────────────────────────────┐
│  /sw:done → sw:code-reviewer → simplify → sw:grill      │
│                → sw:judge-llm → PM validation           │
│                                                          │
│  sw:reflect stop-hook → learnings → CLAUDE.md           │
│  sw:skill-gen ← reads skill-signals.json (creation)     │
│  rubric.md (per-increment quality contract)             │
└──────────────────────────────────────────────────────────┘
                    │
                    │  add feedback edge ↓
                    ▼
┌─ NEW (this increment) ──────────────────────────────────┐
│                                                          │
│  Gate failure in judge-llm / rubric / code-review        │
│            │                                             │
│            │  (if finding traces to skill instructions)  │
│            ▼                                             │
│  skill-signals.json (schemaVersion: 2)                   │
│            │                                             │
│            │  { type: "refinement", source, targetSkill, │
│            │    severity, incrementId, evidence }        │
│            ▼                                             │
│  sw:skill-refine <skill>                                 │
│     ├─ aggregate signals (last N increments)             │
│     ├─ read current SKILL.md                             │
│     ├─ Haiku → propose diff + rationale                  │
│     ├─ interactive approve/reject/edit                   │
│     └─ on approve → write + git commit + ledger entry    │
│                                                          │
│  sw:reflect stop-hook nudge                              │
│     └─ one-line prompt at /sw:done close                 │
│                                                          │
│  sw:reflect --status (dashboard)                         │
│     └─ show skills needing refinement                    │
└──────────────────────────────────────────────────────────┘
```

## Components & File Ownership

### Package: specweave (repositories/anton-abyzov/specweave)

| Component | Path | Action |
|-----------|------|--------|
| Signal schema | `src/types/skill-signals.ts` | extend with refinement type |
| Signal store | `src/core/skill-signals/writer.ts` | add `appendRefinement()` |
| Signal store | `src/core/skill-signals/reader.ts` | add `listForSkill()`, `migrateV1toV2()` |
| Judge-llm emitter | `plugins/specweave/skills/judge-llm/` + `src/skills/judge-llm.ts` | emit signal on skill-attributable rejection |
| Rubric emitter | `src/core/rubric/evaluator.ts` | emit signal on criterion failure + skill attribution |
| Code-reviewer emitter | `plugins/specweave/skills/code-reviewer/` | emit signal on critical finding attributed to skill |
| New skill | `plugins/specweave/skills/skill-refine/SKILL.md` | new skill definition |
| Skill-refine CLI | `src/skills/skill-refine.ts` | implementation |
| Reflect nudge | `lib/hooks/reflection-stop.ts` | add nudge logic |
| Reflect status | `plugins/specweave/skills/reflect/` + `src/skills/reflect-status.ts` | add dashboard section |
| Refinement ledger | `.specweave/state/skill-refinements.json` (runtime-created) | append-only |
| ADRs | `.specweave/docs/internal/architecture/adr/0671-*` | 4 new ADRs |

### Package: vskill (repositories/anton-abyzov/vskill)

| Component | Path | Action |
|-----------|------|--------|
| No changes this increment | — | — |

### Package: vskill-platform (repositories/anton-abyzov/vskill-platform)

| Component | Path | Action |
|-----------|------|--------|
| No changes this increment | — | explicitly deferred to Phase 3 |

## ADRs (codify the red lines)

### ADR-0671-01 — No runtime self-mutation of active skills
**Decision:** During an active `/sw:do` or `/sw:done` session, no SpecWeave process writes to any `SKILL.md` file. Refinements are explicit user actions gated by approval.
**Consequence:** Deterministic replay is preserved; grill/judge-llm evaluate a stable skill surface.
**Alternative rejected:** Hermes-style in-flight mutation — violates reproducibility guarantees that enterprise users (SOC2/GxP) depend on.

### ADR-0671-02 — Registry version immutability
**Decision:** A skill published to verified-skill.com at version X is bit-identical forever. Refinements produce a NEW version requiring a NEW review.
**Consequence:** Supply-chain integrity is preserved; installed skills match reviewed skills.
**Alternative rejected:** Post-review mutation on the registry — would break the "verified" brand promise.

### ADR-0671-03 — No "self-improving" marketing language
**Decision:** Documentation and marketing for specweave and vskill may not use the phrase "self-improving skills" or equivalent until (a) reproducibility guarantees are formally documented and (b) an audit-log format ships.
**Consequence:** Truthfulness in messaging; avoids support burden from enterprise users demanding an audit trail we don't have.
**Alternative rejected:** Adopt Hermes' marketing copy verbatim — creates a credibility liability.

### ADR-0671-04 — No Goodhart loop on gate signals
**Decision:** A refinement signal emitted by gate G (judge-llm / rubric / code-review) may not be used as the validation target for a refinement applied to the skill that produced the signal within the same session. The signal matures across sessions.
**Consequence:** Prevents the skill from being "refined to pass the gate that caught it", which would collapse the gate into a rubber stamp.
**Alternative rejected:** Same-session closed loop — Goodhart's law would degrade gate quality over time.

## Data Schemas

### skill-signals.json (v2)

```jsonc
{
  "schemaVersion": 2,
  "signals": [
    // Existing v1 generation signal (unchanged)
    {
      "id": "sig_01HX...",
      "type": "generation",
      "source": "sw:reflect",
      "pattern": "repeated migration pre-flight",
      "confidence": 0.8,
      "incrementIds": ["0650", "0652", "0658"],
      "detectedAt": "2026-04-15T..."
    },
    // NEW v2 refinement signal
    {
      "id": "sig_01HY...",
      "type": "refinement",
      "source": "judge-llm" | "rubric" | "code-reviewer",
      "targetSkill": "sw:architect",
      "severity": "low" | "medium" | "high",
      "incrementId": "0671",
      "evidence": "judge-llm-report.json#findings[3] cites skill ACtivity 'always-use-microservices' as inappropriate for CRUD scope",
      "detectedAt": "2026-04-20T...",
      "consumedBy": null  // nulled until a refinement uses this signal
    }
  ]
}
```

### skill-refinements.json (new, append-only ledger)

```jsonc
{
  "refinements": [
    {
      "id": "ref_01HZ...",
      "targetSkill": "sw:architect",
      "author": "anton.abyzov@gmail.com",
      "signalIds": ["sig_01HY...", "sig_01HX..."],
      "diffSha": "abc123...",  // git commit SHA
      "rationale": "Relax microservices default for CRUD scope (3 signals across 0650-0670)",
      "appliedAt": "2026-04-22T..."
    }
  ]
}
```

## Skill Attribution Heuristics (how gates identify which skill is at fault)

Gates don't always know which skill caused a failure. Heuristics, in priority order:

1. **Direct trace:** if the failing step's originating tool call was made from within a skill's Task() prompt, attribute to that skill.
2. **Slash-command trace:** if the increment was initiated with `/sw:<skill>`, attribute to that skill on gate failure.
3. **Evidence pattern match:** if the failure evidence text contains a phrase from a skill's SKILL.md (exact-match, 6+ words), attribute to that skill.
4. **Fallback:** emit NO signal (better than wrong signal). Prefer precision over recall.

## Rollout

- **MVP (this increment, 3-4 days):** Phase 1 full scope above.
- **Phase 2 (separate increment, post-0670):** Hermes skill content port via `vskill skill import`.
- **Phase 3 (deferred, new increment when demand justifies):** Registry-side leaderboard + opt-in telemetry + audit-log format. Not tracked on current roadmap.

## Dependencies

- **Hard:** `0670-skill-builder-universal` must ship Phase 1 of its generator extraction first so `sw:skill-refine` can reuse the diff/write primitives cleanly. Phase 1 of 0670 is already active; this increment is sequenced after it.
- **Soft:** `0663-rubric-quality-contracts` (already shipped 2026-04-12) is leveraged for the rubric signal source.
- **None:** this increment does NOT require vskill-platform changes.

## Non-goals (restated from spec, reinforced here)

- No runtime self-mutation.
- No auto-merge.
- No opt-in telemetry (local-only).
- No registry-side changes.
- No cross-user aggregation of signals.
