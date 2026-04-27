---
increment: 0785-vskill-platform-docs-pass
title: "Tasks"
created: 2026-04-27
---

# Tasks: vskill-platform docs pass

## Stage 1 — Readability tokens (agent: `readability-css`)

### T-001: Add tier-scoped text tokens to globals.css
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-05 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given the light theme is active
- When `.tier-card[data-tier="certified"] .tier-card-desc` is rendered
- Then `getComputedStyle().color` resolves to a value with ≥4.5:1 contrast against `#FEF9C3`

Add to `:root` light block in `src/app/globals.css`:
- `--tier-certified-text: #5C3A00`
- `--tier-certified-rank: #6B4400`
- `--tier-verified-text: #2D2D5F`

Add dark-theme variants in `[data-theme="dark"]` (alias to `--text-strong` if visual review accepts).

### T-002: Apply tokens in `.tier-card` and `.tier-pill` selectors
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Notes**: `.tier-pill[data-tier="certified"]` already uses `--tier-certified` (#A16207) on `--tier-certified-bg` (#FEF9C3) ≈ 4.7:1 — passes AA. Pill renders only a single label (no body text), so no override needed. Verified tier card desc gets new `--tier-verified-text` for parity even though current `--text-muted` on `#EEF2FF` likely passes AA already.
**Test Plan (Given/When/Then)**:
- Given the light theme
- When the user navigates to `/trust` or `/docs/getting-started`
- Then the gold "Certified" card body text and "HIGHEST" label are clearly readable (visual + contrast inspection)

In `globals.css`:
- `.tier-card[data-tier="certified"] .tier-card-desc { color: var(--tier-certified-text); }`
- `.tier-card[data-tier="certified"] .tier-card-rank { color: var(--tier-certified-rank); }`
- Mirror for `.tier-card[data-tier="verified"] .tier-card-desc` using `--tier-verified-text`
- Same for `.tier-pill[data-tier="certified"]` content

### T-003: Verify TierBadge.tsx and SearchPalette.tsx inherit new tokens
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed
**Notes**: Both files render compact tier badges/pills using `var(--tier-{certified,verified}-bg)` + `var(--tier-{certified,verified})` for the *label color only* (not body text). Neither file uses `.tier-card`, `.tier-card-desc`, or `.tier-card-rank`. No shadowing of new tokens. Inline color override at `getting-started/page.tsx:259` is on `.tier-card-name` (the brand-colored tier name like "CERTIFIED" — saturated `--tier-certified` #A16207 on #FEF9C3 ≈ 4.7:1, passes AA). Out of scope for this stage; flagged for `vocab-and-counts` agent only if it changes the markup.
**Test Plan (Given/When/Then)**:
- Given a CERTIFIED skill card in the marketplace or search palette
- When rendered in light theme
- Then body text contrast ratio is ≥4.5:1

Read `TierBadge.tsx` and `SearchPalette.tsx`; remove any inline `style={{ color }}` overrides that would shadow the new tokens. If absent, no edits needed — just confirm.

## Stage 2 — Counts wiring (agent: `counts-content`)

### T-004: Refresh `generated-counts.ts` via prebuild
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Notes**: Re-ran `npm run prebuild`. Generator script's strict `^\s*id:\s*"` regex confirms vskill ships **52** scan patterns today (my earlier loose grep over-counted by 1). COUNTS file is in sync with source-of-truth.
**Test Plan**:
- Given the umbrella repo with sibling `vskill/` source
- When `npm run prebuild` runs in `vskill-platform/`
- Then `src/lib/generated-counts.ts` shows `scanPatterns: 52` (verified by generator)

### T-005: Wire COUNTS into `src/app/layout.tsx` meta
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-04 | **Status**: [x] completed
**Test Plan**: Read literal `52`/`53` substring against `description` meta after change → not found.
**Notes**: layout.tsx was already wired in a prior pass. Verified `description`, `openGraph.description`, and `twitter.description` all interpolate `${COUNTS.scanPatterns}` and `${COUNTS.agentPlatforms}`. No edits needed.

### T-006: Wire COUNTS into all `/docs/*` pages
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Notes (counts-content slice)**: Wired `${COUNTS.scanPatterns}`, `${COUNTS.skills}`, `${COUNTS.plugins}`, `${COUNTS.agentPlatforms}` into docs/page.tsx (DocCard descriptions + Quick Verify caption), getting-started/page.tsx (metadata, hero prose, scan-step, ASCII pipeline, agents section heading, skills-vs-plugins detail, learn-more callout, next-steps NavLinks), submitting/page.tsx (added import; verification step + timeline row), plugins/page.tsx (added import; metadata, hero badge, what-are-plugins detail, install pipeline prose, catalog intro), security-guidelines/layout.tsx (added import; metadata + openGraph). FAQ page was the faq-vocab agent's slice.
**Test Plan**:
- Given a built site (`npm run build`)
- When `grep -E '\b(52|53|14|8)\s+(static|patterns|platforms|plugins|skills|agents)\b' .next/server/app/**/*.html` runs
- Then result is empty

Files: `src/app/docs/page.tsx`, `src/app/docs/faq/page.tsx`, `src/app/docs/getting-started/page.tsx`, `src/app/docs/submitting/page.tsx`, `src/app/docs/plugins/page.tsx`, `src/app/docs/security-guidelines/layout.tsx`.

For each: add `import { COUNTS } from "@/lib/generated-counts";` and replace literals with `${COUNTS.X}` interpolations. Preserve markdown emphasis around dynamic value.

### T-007: Verify "9 threat categories" against vskill source
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**Test Plan**: Count distinct `category` values in `vskill/src/scanner/patterns.ts` matches the rendered claim.
**Notes**: COUNTS (auto-generated from `scripts/sync-agents-json.cjs`) does not yet expose `threatCategories`. Adding a generator field is out-of-scope for this docs-pass increment. Left the "9 threat categories" literal in place and added a `TODO(0785): expose threatCategories in COUNTS` comment in `security-guidelines/layout.tsx` so the next prebuild rev can promote it. Single source of truth for now: hand-maintained alongside `vskill/src/scanner/patterns.ts`.

## Stage 3 — Time-bound copy (agent: `time-copy-refresh`)

### T-008: Past-tense rewrite of insights page launch teaser
**User Story**: US-003 | **AC**: AC-US3-01 | **Status**: [x] completed
**Test Plan (visual)**: `/insights/claude-code` rendered — no future-tense reference to April or May 2026.
**Notes**: Rewrote the BUDDY card line at `src/app/insights/claude-code/page.tsx:392` from "Teaser window: April 1-7 2026. Full launch gated for May 2026." to "The April 2026 teaser window has come and gone; the source-coded May 2026 launch flag has not flipped publicly as of this writing." Preserves marketing intent (still tells readers what the source said about timing) without making future-tense claims now in the past. Historical leak-date references (lines 309/313/375) preserved verbatim.

`src/app/insights/claude-code/page.tsx:392` — rewrite the launch-window block in past tense, OR remove the teaser if past-tense reads awkwardly. Preserve the historical leak-date reference (line 309/313/375).

### T-009: Soften FAQ report-triage SLA
**User Story**: US-003 | **AC**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: `/docs/faq` rendered — "24 hours" not present; replacement reads honestly.

`src/app/docs/faq/page.tsx:102` — replace "Reports are reviewed within 24 hours." with "We triage reports within a few business days. Critical or active-exploitation reports are escalated immediately."

## Stage 4 — Tier vocabulary (agent: `counts-content` continues)

### T-010: Update TierBadge.tsx semantic labels
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**: Render each TierBadge variant — labels are "Scanned" / "Verified" / "Certified" (or "Tainted" verdict). Existing snapshot tests still pass after re-recording.
**Notes**: `TIER_LABELS` map updated: VERIFIED→"Scanned", CERTIFIED→"Verified", TAINTED/BLOCKED/REJECTED unchanged. Updated comment block to reference 0785/US-004 rationale. Existing test file `src/app/components/__tests__/TierBadge.test.tsx` (4 expectations on the old strings) WILL FAIL — flagged below for team-lead.

**Test breakage to coordinate** (do NOT auto-edit per agent constraints):
- `src/app/components/__tests__/TierBadge.test.tsx` lines 21-22, 25-26, 35-37, 40-42 still assert old strings ("Trusted Publisher", "Security-Scanned"). Tests must be updated to "Verified" / "Scanned" once labels finalize.
- `src/app/skills/[owner]/[repo]/[skill]/versions/VersionCard.tsx:22` and `versions/[version]/page.tsx:36` use the literal string "Trusted Publisher" — but as a `VENDOR_AUTO` *certMethod* label (different domain — describes WHO certified, not the public tier ladder). NOT touched. The matching test `versions/__tests__/VersionCard.test.tsx:34-36` still passes unchanged.

### T-011: Update TrustBadge.tsx tooltip / aria-labels
**User Story**: US-004 | **AC**: AC-US4-04 | **Status**: [x] completed
**Test Plan**: T0–T4 SVG badges — tooltip text uses ladder labels. Screen-reader reads "Certified" not "T4".
**Notes**: T1 label "UNSCANNED" → "LOW TRUST", T2 label "BASIC" → "SCANNED" to match the public ladder. T0/T3/T4 already aligned (BLOCKED/VERIFIED/CERTIFIED). Added `aria-label={\`${tier}: ${config.label}\`}` and matching `title` attribute to BOTH render branches (ladder pill + plain pill). Screen readers now announce "T4: CERTIFIED" instead of "T4". The TX prefix and `data-trust-tier` attribute remain in the DOM for test stability and API parity per task spec.

### T-012: FAQ entry explaining T0–T4 vs ladder
**User Story**: US-004 | **AC**: AC-US4-03 | **Status**: [x] completed
**Test Plan**: `/docs/faq` rendered — new Q&A explains the relationship.

Add to `src/app/docs/faq/page.tsx`:
> **Q: What's the difference between Scanned/Verified/Certified and the T0–T4 numbers I see in the API?**
> A: Scanned/Verified/Certified is our public 3-tier ladder. T0–T4 is the internal trust-score enum used by the database, scoring math, and API. T4 corresponds to Certified, T3 to Verified, T2 to Scanned, T1 to a low-trust state, and T0 to blocked. Most users only need to know the public ladder.

### T-013: Spot-check ladder copy on /trust and /docs/getting-started
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: Manual: `/trust` and `/docs/getting-started` use canonical "Scanned/Verified/Certified" labels — no rogue "Trusted Publisher" or "Security-Scanned" copy.
**Notes**: `/trust` (`src/app/trust/page.tsx:223-246` `TrustTierLadder`) already canonical: "Scanned"/"Verified"/"Certified" with matching ranks (Baseline/Recommended/Highest). `/docs/getting-started` `TIER_LADDER` (lines 103-128) already canonical. Repo-wide grep for "Trusted Publisher"/"Security-Scanned" returns hits only in (a) TierBadge tests (flagged in T-010), (b) VersionCard / version-detail page where "Trusted Publisher" is a `VENDOR_AUTO` certMethod label — different domain, intentionally preserved. No copy edits needed in either page.

## Stage 5 — Verification (main agent)

### T-014: Visual + contrast verification with preview tools
**User Story**: US-001, US-002, US-003, US-004 | **Status**: [x] completed
**Notes**: Visual verification done — gold "Certified" card body text now ~10:1 contrast (was ~3.5:1, failed WCAG AA). Light + dark theme screenshots clean.
**Test Plan**:
- `preview_start` against `npm run dev` of vskill-platform
- `preview_inspect` reads computed color of `.tier-card[data-tier="certified"] .tier-card-desc` — confirms ≥4.5:1
- `preview_screenshot` of `/trust` and `/docs/getting-started` in light + dark theme — visually clean

### T-015: typecheck + build + grep gate
**User Story**: US-002 | **AC**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Notes**: All numeric copy in app pages now sourced from `COUNTS.*` (auto-generated by `npm run prebuild`). 3 hand-typed literals remain as documented TODO follow-ups (`9 threat categories` x3, `14 DCI patterns` in FAQ, frontmatter description in security-guidelines/page.mdx).
**Test Plan**:
- `npm run typecheck` exits 0
- `npm run build` exits 0
- `grep -E '\b(52|53|14|8)\s+(static|patterns|platforms|plugins|skills|agents)\b' .next/server/app/**/*.html` returns 0 lines

### T-016: Closure pipeline via /sw:done
**Status**: [x] completed
Runs code-reviewer → simplify → grill → judge-llm → PM 3-gate via `/sw:done 0785`.
