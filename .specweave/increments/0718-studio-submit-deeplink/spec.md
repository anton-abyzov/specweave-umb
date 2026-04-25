---
increment: 0718-studio-submit-deeplink
title: Local Studio Submit-your-skill deep-link to verified-skill.com
type: feature
priority: P2
status: completed
created: 2026-04-25T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
parallel: true
siblings:
  - 0716-studio-search-api-and-telemetry
  - 0717-studio-find-ui
brainstorm: .specweave/docs/brainstorms/2026-04-24-local-studio-discovery-submission.md
---

# Feature: Local Studio "Submit your skill" deep-link to verified-skill.com

## Overview

The smallest of the three sibling increments. Local Studio gains a "Submit your skill" CTA in two places: above the [/studio/find](../0717-studio-find-ui/) result grid (component owned by 0717, behavior bound here) and in the Studio main nav. Click opens `https://verified-skill.com/submit?repoUrl=<encoded>` in a new tab — no in-Studio OAuth, no in-Studio submission form, no token storage.

The deep-link URL prefills `?repoUrl=` from the active Studio workspace's git remote when available. Resolution happens server-side via `git config --get remote.origin.url` (the browser never reads the filesystem). Fire-and-forget telemetry POST to sibling [0716](../0716-studio-search-api-and-telemetry/)'s `submit-click` endpoint records the click for conversion analysis.

**Hard requirement (user-confirmed)**: NO authorization in Local Studio. Adding OAuth to Studio is a 1-week careful build with real attack surface for zero feature gain — `verified-skill.com` already has the GitHub OAuth flow.

## Out of scope

- In-Studio submission form / wizard.
- In-Studio OAuth or token storage.
- Cross-host repo support — only `https://github.com/<owner>/<repo>` URLs prefill. GitLab / self-hosted produce `repoUrl: null` (user can paste manually on the website).
- Auto-detecting repos outside the active Studio workspace.
- Submission status polling — that's a future increment if users ask.

## User Stories

### US-001: Submit CTA in Studio nav and above /studio/find (P2)
**Project**: vskill-platform

**As a** Studio user with a skill to share
**I want** a clear "Submit your skill" call-to-action visible from anywhere in Studio
**So that** I can publish without first finding the website manually.

**Acceptance Criteria**:
- [x] **AC-US1-01**: A "Submit your skill" button is visible in the Studio main nav across every Studio page (rendered in `StudioLayout` or equivalent).
- [x] **AC-US1-02**: A persistent CTA also renders above the result grid on `/studio/find` — implemented by binding 0717's `SubmitDeepLink` stub component (FR-002 of 0717).
- [x] **AC-US1-03**: Both CTAs use the same underlying click handler (single source of truth — DRY) and the same `useSubmitDeepLink` hook.
- [x] **AC-US1-04**: Button label is "Submit your skill" with an upload icon (icon `aria-hidden`); ARIA label includes "opens new tab".
- [x] **AC-US1-05**: Clicking opens `https://verified-skill.com/submit?repoUrl=<encoded>` in a new browser tab via `window.open(url, '_blank', 'noopener,noreferrer')`. The host is hard-coded — never derived from input.
- [x] **AC-US1-06**: A one-line confirmation toast "Opening verified-skill.com..." appears on click and auto-dismisses after 2s.

---

### US-002: Workspace repoUrl resolver (P2)
**Project**: vskill-platform

**As a** Studio user clicking Submit
**I want** the deep-link to prefill my repository URL
**So that** I don't have to copy-paste it on the website.

**Acceptance Criteria**:
- [x] **AC-US2-01**: New endpoint `GET /api/v1/studio/workspace-info` returns `{ repoUrl: string | null }`. The browser never reads the filesystem.
- [x] **AC-US2-02**: Server-side runs `git config --get remote.origin.url` via `child_process.execFile` (argv form, explicit `cwd`, no shell). The Studio workspace root MUST be a real directory before shelling out — verified by `fs.access`.
- [x] **AC-US2-03**: Result cached per-process via a `Map` for the Studio session lifetime — cold path one execFile (~50ms), warm path O(1).
- [x] **AC-US2-04**: Normalization — SSH remote (`git@github.com:owner/repo.git`) is converted to `https://github.com/owner/repo`; trailing `.git` is stripped.
- [x] **AC-US2-05**: Only `github.com` hosts pass through. GitLab, Bitbucket, self-hosted, or unparseable URLs → `repoUrl: null`. The user can paste manually on the website.
- [x] **AC-US2-06**: Click handler awaits workspace-info with a **200ms timeout**. If exceeded, opens the deep-link without `?repoUrl=` rather than blocking — Studio must always feel responsive on click.
- [x] **AC-US2-07**: Composed URL uses `URL` + `searchParams.set` (not string concatenation) — prevents query injection. `URL` constructor validates the result.
- [x] **AC-US2-08**: Pop-up-blocker fallback — if `window.open` returns `null`, show a toast with a clickable anchor `<a href={url} target="_blank" rel="noopener noreferrer">Click here to open verified-skill.com/submit</a>`.

---

### US-003: Click telemetry to submit-click endpoint (P2)
**Project**: vskill-platform

**As a** product owner
**I want** to log Submit-CTA clicks with the search query context
**So that** we can measure the discover→submit conversion rate.

**Acceptance Criteria**:
- [x] **AC-US3-01**: Click fires a `POST` to `/api/v1/studio/telemetry/submit-click` (owned by sibling 0716) with payload `{ repoUrl?: string, q?: string, ts: number }`. `q` is read from the current URL params if user is on `/studio/find?q=…`; otherwise omitted.
- [x] **AC-US3-02**: Telemetry is fire-and-forget — `window.open` is NOT blocked on the telemetry response.
- [x] **AC-US3-03**: Multiple rapid clicks are debounced at 500ms — telemetry fires at most twice in a 500ms window.
- [x] **AC-US3-04**: Telemetry endpoint failure (404, 5xx, network) is swallowed silently — UX continues without warning. Verified by a test that mocks the telemetry endpoint as failing.
- [x] **AC-US3-05**: During parallel build (before 0716 deploys), MSW handler returns 204 so the click flow is testable end-to-end without 0716.

## Functional Requirements

### FR-001: Single source of truth — `useSubmitDeepLink` hook
Both CTAs share one hook at `src/app/studio/hooks/useSubmitDeepLink.ts` that orchestrates: workspace-info fetch (200ms timeout) → URL composition → telemetry POST → `window.open`. No duplicated logic between nav button and find-page banner.

### FR-002: Last-submission tooltip (cosmetic) — read-side DEFERRED
**Implemented (write side):** After every click attempt (including popup-blocked), the hook writes `localStorage.setItem('studio.lastSubmitOpenedAt', <ISO>)`. Failure to write is swallowed. Tested.

**Deferred (read side / tooltip rendering):** The "Last opened <relative time> ago" tooltip on subsequent hovers is intentionally NOT implemented in this increment. Spec labels FR-002 as "cosmetic"; the persisted timestamp is the load-bearing contract for any future reader (e.g., a follow-up Studio onboarding nudge). Rendering the relative-time tooltip is tracked as follow-up — does not block 0718 closure.

### FR-003: Bind 0717's SubmitDeepLink stub
The find-page consumer (`FindClient.tsx`) renders 0718's `<SubmitFindBanner />`, which binds `useSubmitDeepLink`. Both Studio CTAs (nav + find page) share that single hook — DRY satisfied. The 0717 stub `src/app/studio/find/components/SubmitDeepLink.tsx` remains as a 0717-owned fallback presentation surface for future callers but is not on the find page's hot path.

## Performance budgets

| Path | Budget |
|---|---|
| Click → window.open (cold workspace-info) | <250ms perceived |
| Click → window.open (warm workspace-info) | <50ms perceived |
| workspace-info timeout cap | 200ms (after which we proceed without `?repoUrl=`) |

## Risk register

| Risk | Mitigation |
|---|---|
| OAuth in Studio scope creep | Hard rule — never add. Deep-link only. |
| Hung git command | 200ms timeout (AC-US2-06) |
| Shell injection via repo path | `execFile` with argv + explicit cwd (AC-US2-02) |
| Reverse tabnabbing | `noopener,noreferrer` on `window.open` (AC-US1-05) |
| Pop-up blocker swallows action | Fallback toast with clickable anchor (AC-US2-08) |
| Telemetry leaks PII | repoUrl is consensual (user clicked Submit); no IP / UA stored (enforced by 0716 schema) |
| 0716 not deployed yet | MSW handler returns 204 during parallel build (AC-US3-05) |

## Success Criteria

- All ACs green with TDD red→green→refactor evidence in tasks.md.
- Playwright spec asserts: click in nav → new tab opens with correct URL containing `?repoUrl=https://github.com/<owner>/<repo>` for a workspace with a github remote; in a non-github workspace, URL has no `?repoUrl=`; telemetry POST observed.
- No OAuth, no token storage, no auth UI introduced anywhere.

## Dependencies

- [0716-studio-search-api-and-telemetry](../0716-studio-search-api-and-telemetry/) — provides `/api/v1/studio/telemetry/submit-click`. MSW mock unblocks parallel build.
- [0717-studio-find-ui](../0717-studio-find-ui/) — owns the `SubmitDeepLink` component file (stub). This increment binds behavior.
- Existing Studio backend Next.js API routes (workspace context already exposed for other endpoints).
- `verified-skill.com/submit` — already deployed and accepts `?repoUrl=` query param.
