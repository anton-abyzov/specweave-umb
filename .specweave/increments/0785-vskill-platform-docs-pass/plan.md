---
increment: 0785-vskill-platform-docs-pass
title: "Architecture & implementation plan"
created: 2026-04-27
---

# Plan: vskill-platform docs pass

## Architecture decisions

### AD-001: Tier-scoped CSS tokens, not global token override
The `--text-muted` token is used site-wide in dozens of contexts. Overriding it globally to satisfy gold-bg contrast would cascade into other surfaces. Instead, introduce **tier-scoped tokens** — `--tier-certified-text`, `--tier-certified-rank`, `--tier-verified-text` — applied only inside `.tier-card[data-tier="..."]` and `.tier-pill[data-tier="..."]` selectors.

**Trade-off**: One more token per tier. Gain: zero blast radius, easy future palette tweaks, parallel structure between tiers makes intent obvious.

### AD-002: Keep `generated-counts.ts` generator; force build-time refresh
The auto-generator already exists (`scripts/sync-agents-json.cjs`, runs on `prebuild`). Don't replace it — just stop bypassing it. Replace literal counts in copy with `${COUNTS.X}` interpolations. The `prebuild` hook ensures a fresh build always has fresh counts.

**Trade-off**: Couples copy to a build-time hook. Gain: single source of truth, drift-resistant. Risk: if `prebuild` is skipped (uncommon), counts stale by one cycle — accepted.

### AD-003: No doc-framework migration
User asked "maybe migrate to something better." The current Next.js `app/docs/*` setup ships full React control, theme integration, and shared component library — moving to Docusaurus/Mintlify would lose that and require rewriting 11 pages of marketing copy. Improve in place; reconsider migration when docs surface > 30 pages.

### AD-004: Single public ladder vocabulary
Three vocabularies coexist today (T0–T4 enum, "Scanned/Verified/Certified" ladder, "Security-Scanned/Trusted Publisher/Tainted" semantics). Pick the **already-dominant ladder** ("Scanned/Verified/Certified") for all user-facing surfaces. Keep T0–T4 enum internal (DB, scoring math, FAQ deep dive). Rename TierBadge labels to match ladder.

**Trade-off**: Small TS interface churn in `TierBadge.tsx` consumers. Gain: one mental model for users.

## Component map

### Stage 1 — Readability tokens
| File | Change |
|------|--------|
| `src/app/globals.css:9-117` | Add 3 light-theme tier-scoped text tokens |
| `src/app/globals.css:119-216` | Add dark-theme variants (or alias to existing `--text-strong`) |
| `src/app/globals.css:802-932` | Apply tokens in `.tier-card[data-tier]` + `.tier-pill[data-tier]` selectors |
| `src/app/components/TierBadge.tsx` | Verify CERTIFIED variant inherits tokens (no inline color overrides) |
| `src/app/components/SearchPalette.tsx` | Verify gold tier indicator inherits tokens |

### Stage 2 — Counts wiring
| File | Literal → COUNTS |
|------|------------------|
| `src/app/layout.tsx` | "52 security patterns, 53 agent platforms" → `${COUNTS.scanPatterns}` / `${COUNTS.agentPlatforms}` |
| `src/app/docs/page.tsx` | "3-tier" stays (semantic), "14 expert skills" → `${COUNTS.skills}` |
| `src/app/docs/faq/page.tsx` | "53 platforms", "52 static patterns", "14 DCI patterns" → COUNTS |
| `src/app/docs/getting-started/page.tsx` | "Works With 53 Agents" title + ladder copy |
| `src/app/docs/submitting/page.tsx` | "52 patterns", timeline table |
| `src/app/docs/plugins/page.tsx` | "8 domain plugins / 14 expert skills" |
| `src/app/docs/security-guidelines/layout.tsx` | "9 threat categories" — verify against vskill source |

### Stage 3 — Time-bound copy
| File | Change |
|------|--------|
| `src/app/insights/claude-code/page.tsx:392` | Past-tense rewrite of April/May 2026 launch teaser |
| `src/app/docs/faq/page.tsx:102` | "24 hours" → realistic triage cadence |

### Stage 4 — Tier vocabulary
| File | Change |
|------|--------|
| `src/app/components/TierBadge.tsx` | Semantic labels match public ladder |
| `src/app/components/TrustBadge.tsx` | Tooltip / aria-label uses ladder labels |
| `src/app/docs/faq/page.tsx` | New Q: "T0–T4 vs Scanned/Verified/Certified — what's the difference?" |
| `src/app/trust/page.tsx`, `src/app/docs/getting-started/page.tsx` | Spot-check ladder copy uses canonical labels |

## Execution: parallel sub-agents

Three implementation agents work disjoint file sets:

| Agent | Scope |
|-------|-------|
| `readability-css` | Stage 1: globals.css tokens + verify 4 consumers |
| `counts-content` | Stages 2 & 4: counts wiring (7 files) + tier vocab (4 files) |
| `time-copy-refresh` | Stage 3: insights page + FAQ SLA |

Disjoint files → no merge conflicts. Main agent runs Stage 5 (verification with preview_*) after all three complete.

## Verification

1. `cd repositories/anton-abyzov/vskill-platform && npm run prebuild` → `generated-counts.ts` shows `scanPatterns: 52` (matches the strict-regex count in vskill source)
2. `npm run dev`; `preview_start`; visit `/trust`, `/docs/getting-started` light + dark; `preview_screenshot` + `preview_inspect` for contrast
3. `npm run typecheck`
4. `npm run build`; grep built HTML for orphan literal counts
5. Manual smoke of 7 doc pages
6. `/sw:done 0785` runs full closure pipeline (code-reviewer → simplify → grill → judge-llm → PM 3-gate)
