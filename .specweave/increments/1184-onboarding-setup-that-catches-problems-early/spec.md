---
increment: 1184-onboarding-setup-that-catches-problems-early
title: Onboarding setup that catches problems early
---

# Onboarding setup that catches problems early

## Problem

A clean-state headless run on November 2, 2026 (main at `7793e50e9a`, evidence in `~/.specwithcode/m4/evidence/onboarding-rethink-20261102/`) shows setup lets a new person finish with nothing working:

- The Agents step's Continue looks the same with no agent ready, and says nothing about chats failing later.
- An agent reading "Unavailable" or "Needs attention" has no action, only the same word repeated. Signing in from another terminal has no re-check; a person must leave the step.
- The Agents step lists only Codex and Claude and never says others exist.
- "SpecWithCode Connect / Loading sign-in…" never resolves when Clerk does not load, and nothing says Connect is optional. The stage named "Connect" shares its word with that product.
- A brand new, empty Overview says "Partial observations; some hosts are not current", which is false.

A fresh Windows install recently failed at Claude sign-in (1171) and at Connect publishing (1174). Those server messages exist now; setup must show them at the moment they can be acted on.

## Scope

In: the Agents and Computers steps of the web wizard, the empty Overview summary, a headless walk, and a design page recommending the wider flow.

Out: reordering the wizard, a first-task step, contextual concept hints and iOS changes. Those wait on the user's decision on the design page. No release dispatch.

## Acceptance Criteria

- [ ] AC-01: The Agents step states a verdict from real provider state: checking, ready (names what is ready and where), unconfirmed, a machine with nothing ready, or nothing ready at all.
- [ ] AC-02: With nothing ready anywhere the primary button reads "Continue without an agent" and the step says chats will not start until one is ready; once anything is ready it reads "Continue".
- [ ] AC-03: Providers other than Codex and Claude count toward the verdict, and the step says others can be added later in Settings > Providers.
- [ ] AC-04: Each machine has "Check again", which re-probes its providers and shows it is working.
- [ ] AC-05: An agent needing attention whose sign-in is not confirmed offers a terminal with its login command typed and not run, and its status word is not repeated. The server's message, including the signed-out Windows text, shows in full.
- [ ] AC-06: The Connect row says it is optional. If sign-in has not loaded after 10 seconds it says so, offers Retry and tells the person setup continues without it.
- [ ] AC-07: The first stage is named "Computers".
- [ ] AC-08: An empty workspace's Overview does not claim partial observations.
- [ ] AC-09: A headless walk on clean private state at desktop and phone widths has no horizontal overflow and captures each step, in no-CLI and CLI-could-not-be-verified states.

## Approach

`apps/web/src/onboarding/agentReadiness.logic.ts` holds the verdict, using `providerCanRunWork` so setup and the Overview checklist agree on what can run. `useAgentReadiness.ts` subscribes per machine like `useProjectScans`. `WelcomeWizard.tsx` renders it. Retry reloads the page, since Clerk has no reload call and this is the first stage. Rejected: blocking Continue with no agent, because a person may add a provider later or just look around; a separate summary screen, because catching the problem in place needs no extra click.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A warning with sign-in unknown still counts as able to run, matching the checklist, and reads as "could not be confirmed" → reversible.
- D-02 Sign-in load timeout of 10 seconds → reversible.
### Open
- D-03 Reorder to Agents, Projects, First task with Connect last: left to the user on the design page.

## Tasks

### T-01 Agents step verdict and no dead ends
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/agentReadiness.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/agentReadiness.logic.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/useAgentReadiness.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.terminal.test.tsx | Test: `pnpm exec vp test run apps/web/src/onboarding/agentReadiness.logic.test.ts apps/web/src/components/onboarding/WelcomeWizard.terminal.test.tsx`

### T-02 Connect row says optional and reports a failed load
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.machineRole.test.tsx | Test: `pnpm exec vp test run apps/web/src/components/onboarding/WelcomeWizard.machineRole.test.tsx`

### T-03 Empty Overview summary
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/StudioOverview.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/StudioOverview.test.tsx | Test: `pnpm exec vp test run apps/web/src/components/studio/StudioOverview.test.tsx`

### T-04 Headless walk and design page
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/setup-checks/walk.mjs | Test: `node apps/web/tests/setup-checks/walk.mjs <origin> <token> <out> <playwright-core>`

### T-05 Verify and close 1184
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: none | Test: `specweave verify 1184-onboarding-setup-that-catches-problems-early`
