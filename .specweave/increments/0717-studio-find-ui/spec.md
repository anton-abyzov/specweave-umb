---
increment: 0717-studio-find-ui
title: "Local Studio /studio/find page — discovery UI with as-you-type search and pagination"
type: feature
priority: P1
status: planned
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 90
parallel: true
siblings:
  - 0716-studio-search-api-and-telemetry
  - 0718-studio-submit-deeplink
brainstorm: .specweave/docs/brainstorms/2026-04-24-local-studio-discovery-submission.md
---

# Feature: Local Studio /studio/find — discovery UI with as-you-type search and pagination

## Overview

Local Studio gains a discovery surface. Today it only manages local skills. This increment adds a `/studio/find` page that calls the same-origin search proxy from sibling [0716](../0716-studio-search-api-and-telemetry/) with as-you-type debounced queries, AbortController-based stale-request cancellation, client-side caching, ETag/304 reuse, and a LoadMore pagination control. Results render in cards that surface trust, publisher, and threat signals inline — Studio shows *signals*, not whole governance pages (those stay on `verified-skill.com`).

The page is parallel-buildable: during 0716 development we mock `/api/v1/studio/search` via MSW with fixtures derived from the contract document at `.specweave/docs/contracts/studio-search-api-v1.md`. The final integration task swaps mocks for live calls.

## Out of scope

- OAuth / auth (we never authenticate in Studio).
- Submit-flow logic (the SubmitDeepLink component renders here as a stub; behavior is bound by sibling [0718](../0718-studio-submit-deeplink/)).
- Server-side install execution (V1 is clipboard-copy only).
- Filter UI (category / tier / sort) — defer until users ask.
- Infinite scroll — LoadMore is the chosen pattern for accessibility + predictability.
- Porting `/publishers`, `/trust`, `/audits`, `/insights` pages (deep-link to the website).

## User Stories

### US-001: As-you-type search with debounce, abort, and client cache (P1)
**Project**: vskill-platform

**As a** Studio user looking for a skill
**I want** results to update as I type without flicker, slowdowns, or stale flashes
**So that** discovery feels instant and predictable.

**Acceptance Criteria**:
- [x] **AC-US1-01**: Typing in the SearchBar fires the search 200ms after the last keystroke (debounced). Verified by a test that types in rapid succession and asserts only one network call.
- [x] **AC-US1-02**: When a new query supersedes an in-flight one, the older `fetch` is aborted via `AbortController`. Verified by a mock that records signal abort events. Only the latest query's response renders — no flicker of stale results.
- [x] **AC-US1-03**: Client-side LRU cache (50 entries, in-memory per session) keyed by `${q}|${offset}`. Identical queries within session don't refetch. Verified by a mock that asserts zero invocations on the second identical query.
- [x] **AC-US1-04**: Queries shorter than 2 characters do not fire. Whitespace-only is trimmed and treated as empty. Verified by tests for `""`, `"x"`, `"   "`.
- [x] **AC-US1-05**: Loading state appears within 100ms of the debounce settling — skeleton cards (not a spinner) are rendered to keep layout stable.
- [x] **AC-US1-06**: Failed/timed-out request shows ErrorState with a Retry button. Prior results are NOT cleared (resilience under intermittent network).
- [x] **AC-US1-07**: The page is deep-linkable — `/studio/find?q=react` reads `q` from URL on mount and shows the corresponding results. Updating the search bar updates the URL via `replaceState` (not pushState — avoids history pollution per keystroke).
- [x] **AC-US1-08**: Client sends `If-None-Match` header with the last response's ETag; 304 from sibling 0716's proxy results in reuse of cached body without re-parse.
- [x] **AC-US1-09**: Composite as-you-type budget — on cache hit, time from last keystroke to rendered results is under 250ms (debounce 200 + server cache hit <5ms + render <10ms). Measured via a Playwright trace.

---

### US-002: Result cards with trust, publisher, and threat signals (P1)
**Project**: vskill-platform

**As a** Studio user evaluating a skill
**I want** trust, publisher, and threat info inline on each card
**So that** I never have to navigate away to know whether a skill is safe to install.

**Acceptance Criteria**:
- [x] **AC-US2-01**: ResultCard renders skill name, author, description (2-line clamp), TrustBadge, PublisherChip, StatsRow, InstallButton.
- [x] **AC-US2-02**: TrustBadge displays one of: `VERIFIED` (green), `CERTIFIED` (gold), `unknown` (gray). Aria-label describes the tier. Click deep-links to `verified-skill.com/trust` (new tab, `rel="noopener noreferrer"`).
- [x] **AC-US2-03**: PublisherChip renders publisher.name + green checkmark when `publisher.verified === true`; "Unknown publisher" gray chip when `publisher === null`. Click deep-links to `verified-skill.com/publishers/<slug>` (new tab).
- [x] **AC-US2-04**: When `isBlocked === true`, a red ThreatBanner appears above card content showing `threatType` + `severity`. The InstallButton is replaced by a red `Do not install` pill (NOT hidden — explicit signal).
- [x] **AC-US2-05**: StatsRow shows GitHub stars, vskill installs, current version using compact formatting (e.g. `1.2k`).
- [x] **AC-US2-06**: Cards are keyboard accessible — Tab order is name → publisher chip → install button → next card. Enter activates the focused control.
- [x] **AC-US2-07**: All security-sensitive text (name, description) is rendered as React text nodes only; no `dangerouslySetInnerHTML` paths.
- [x] **AC-US2-08**: Description longer than 300 chars or 2 lines is clamped via CSS `line-clamp: 2`; no overflow.

---

### US-003: Install action via clipboard copy (P1)
**Project**: vskill-platform

**As a** Studio user who found a skill
**I want** one click to copy the install command to my clipboard
**So that** I can paste it into my terminal without typing or memorizing.

We chose clipboard over server-side shell-out (security: server can't reach `~/.claude/`) and over direct fs writes (drift: would duplicate 0670's install logic).

**Acceptance Criteria**:
- [x] **AC-US3-01**: Clicking InstallButton writes `vskill install <name>` to the clipboard via `navigator.clipboard.writeText()`. The skill name is sanitized to `/^[a-zA-Z0-9._-]+$/` before composition (defense-in-depth).
- [x] **AC-US3-02**: A toast confirms the copy and includes the hint "Run `vskill install <name>` in your terminal." Toast auto-dismisses after 3.5s.
- [x] **AC-US3-03**: Telemetry POST to `/api/v1/studio/telemetry/install-copy` (from sibling 0716) with `{ skillName, q, ts: Date.now() }`. Fire-and-forget — UI never blocks on the response.
- [x] **AC-US3-04**: Hidden / replaced when `isBlocked === true` (per AC-US2-04).
- [x] **AC-US3-05**: Clipboard API unavailable (older browser, insecure context) — fallback to a copyable readonly input + a "Select all" button. Verified by a test that mocks `navigator.clipboard` as undefined.

---

### US-004: LoadMore pagination (P1)
**Project**: vskill-platform

**As a** Studio user with many search results
**I want** a clear "Load more" control instead of infinite scroll
**So that** I have predictable navigation, accessibility, and a clear "no more results" signal.

**Acceptance Criteria**:
- [x] **AC-US4-01**: Initial query fetches 20 results (`offset=0&limit=20`). Subsequent LoadMore clicks advance offset by 20.
- [x] **AC-US4-02**: LoadMore appends new results to the existing list — no full-grid rerender. Scroll position preserved.
- [x] **AC-US4-03**: LoadMore is disabled (and labeled "All results loaded") when `offset + currentList.length >= total`. `total` comes from sibling 0716's response envelope (AC-US1-03 of 0716).
- [x] **AC-US4-04**: Result count line above grid: `Showing N of M results`. Updates on every fetch and LoadMore append.
- [x] **AC-US4-05**: Editing the search bar resets offset to 0 (new query starts fresh).
- [x] **AC-US4-06**: If `total` drifts down between requests (e.g. a result was blocklisted) and `offset >= total`, the page auto-resets `offset=0` and refetches.

## Functional Requirements

### FR-001: Mock harness for parallel build
Until 0716 ships, MSW handlers at `vskill-platform/src/test-fixtures/studio-search.handlers.ts` serve canonical fixtures from `vskill-platform/src/test-fixtures/studio-search.json`. Fixtures cover: 1 verified+certified result, 1 verified-only, 1 unknown publisher, 1 blocked, 1 with `total > limit` for LoadMore tests. Once 0716 deploys, an integration task swaps MSW for live calls.

### FR-002: SubmitDeepLink stub
A `SubmitDeepLink` component renders the "Submit your skill" CTA above the result grid AND in the Studio nav. It accepts a `repoUrl?` prop and an `onClick` handler. The default behavior is `window.open('https://verified-skill.com/submit', '_blank')` — sibling 0718 binds the workspace-info resolver and telemetry POST to this component.

### FR-003: Accessibility
WCAG 2.1 AA. Keyboard nav, ARIA labels on badges, focus rings preserved, reduced-motion respected for skeleton transitions.

## Performance budgets

| Path | Budget |
|---|---|
| Debounce | 200ms |
| Cache-hit render (cached body, no fetch) | <250ms perceived |
| Cache-miss render (against 0716 cache miss + 0715 edge fast path) | <300ms perceived |
| LoadMore append | <250ms perceived for cache hit, <300ms for miss |
| Skeleton appears within | 100ms after debounce settle |

## Risk register

| Risk | Mitigation |
|---|---|
| Stale flicker on rapid typing | AbortController per request, only latest renders (AC-US1-02) |
| Network jitter degrades UX | ErrorState retains prior results + retry (AC-US1-06) |
| Blocked skill accidentally installed | Install button replaced with red pill (AC-US2-04 + AC-US3-04) |
| Clipboard API unavailable | Fallback readonly input (AC-US3-05) |
| 0716 not landed in time | MSW mocks unblock parallel build (FR-001) |
| Description XSS | React text nodes only, no `dangerouslySetInnerHTML` (AC-US2-07) |

## Success Criteria

- All ACs green with TDD red→green→refactor evidence in tasks.md.
- Playwright spec covers golden path: type → debounce → results → keyboard nav card → click Install → clipboard contains `vskill install <name>` → telemetry POST observed.
- Composite as-you-type budget met (AC-US1-09) measured by a Playwright trace.
- Integration: switching MSW off and pointing at 0716's live endpoints requires zero code change beyond the MSW disable flag (FR-001).

## Dependencies

- [0716-studio-search-api-and-telemetry](../0716-studio-search-api-and-telemetry/) — provides `/api/v1/studio/search` and `/api/v1/studio/telemetry/install-copy`. Build proceeds against MSW mocks until 0716's contract doc is published.
- Existing TanStack Query / SWR provider in Studio (no new package).
- [0715-search-perf-edge-first-and-cache](../0715-search-perf-edge-first-and-cache/) — relied on transitively (0716's proxy sits on top of 0715).
