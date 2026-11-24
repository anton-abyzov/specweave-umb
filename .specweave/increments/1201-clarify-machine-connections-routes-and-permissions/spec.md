# Clarify machine connections, routes and permissions

## Problem

Settings > Connections uses an unlabeled purple switch beside a connected machine and update controls that look enabled despite missing permission. M1 also lists M4's Tailscale address alongside its own. Users cannot distinguish connectivity, update authority, worker grants, or which machine a route reaches.

## Scope

In: source-grounded explanation and diagram, accessible machine and route presentation, explicit update availability and scope, diagnosis of the apparent wrong-machine route and regression coverage for truthful route presentation, headless visual evidence, reviewed PR, merge and normal deployment.

Out: changing existing grants or automatic-update preferences, merging the whole Settings information architecture, interrupting live sessions, bypassing the release owner.

## Acceptance Criteria

- [ ] AC-01: A linked report explains Environment, each shown control, permission gates and route selection from source, with a diagram and a verified mockup or screenshot.
- [ ] AC-02: Connection availability, update permission and worker grants are visibly separate; unavailable update actions explain their requirement without looking actionable; the connection toggle has a visible scope label.
- [ ] AC-03: Routes identify the intended machine, current route and preference/fallback meaning; a wrong-machine endpoint cannot be advertised or used as verified evidence of reaching the intended machine. The M4-under-M1 cause is evidenced or explicitly bounded as unknown.
- [ ] AC-04: Focused behavior tests and production builds pass; headless desktop/mobile light/dark captures show readable controls without overflow. Exact-head review and applicable CI pass before merge; deployment inclusion is verified.

## Approach

Inspect `ManagedUpdatesSection.tsx`, `ConnectionsSettings.tsx`, `EnvironmentRoutesList.tsx`, runtime route learning/identity validation and server `DirectEndpoints.ts`. Preserve the worker-help owner's unrelated edits. Use the existing app tokens and typography, quiet grouped status rows, explicit action labels and inline reasons rather than more status-colored switches. Record design and diagnosis under this increment's `reports/` before implementing. Verify only through isolated fixtures with `headless: true`, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never` and file-backed evidence. Coordinate a safe checkout and the single release dispatcher.

## Decisions

### Asked
- User requested implementation through PR, merge and deploy, plus M1 route diagnosis in this same increment.

### Defaulted
- Retain connection/grant semantics and existing Settings pages; improve the current page instead of implementing the earlier unselected information architecture proposal.
- Never infer endpoint identity from a hostname alone. Distinguish an intended destination from a verified connected identity. Live readback proved the M4 8443 endpoint reaches M1 through the existing proxy; preserve that working path instead of deleting it.
- Use normal release activation; preserve running work and all existing grants.

### Open
- none

## Tasks

### T-01 Explain controls and design the machine presentation
- AC: AC-01 | Files: reports/explanation.md, reports/design.html | Test: source-linked report review and headless rendered mockup inspection

### T-02 Clarify connection, update and route controls; preserve endpoint identity
- AC: AC-02, AC-03 | Files: apps/web/src/components/settings/ManagedUpdatesSection.tsx, apps/web/src/components/settings/ManagedUpdatesSection.test.tsx, apps/web/src/components/settings/ConnectionsSettings.tsx, apps/web/src/components/settings/EnvironmentRoutesList.tsx, apps/web/src/components/settings/EnvironmentRoutesList.test.tsx | Test: focused settings and route presentation regression suites

### T-03 Verify, review, merge and deploy
- AC: AC-04 | Files: reports/verification.md, reports/review.md, reports/delivery.md, apps/web/tests/connection-clarity | Test: focused tests, production web/server builds, headless fixture, exact-head review, GitHub checks and deployment receipt

### T-04 Verify and close 1201
- AC: AC-01, AC-02, AC-03, AC-04 | Files: reports/closure.md | Test: specweave verify 1201 and fresh-context review, then specweave complete 1201
