# 0858 — Hybrid regression scheduling

## Problem

Increment 0857 built a deterministic `npm run verify` harness that proves the golden path **create-skill → install → run-with-a-non-default-model** never regresses. But nothing runs it on a schedule. Anton's requirement: *"a reliable set of tasks which we could run regularly — once or twice a day — consider routines or a separate GitHub workflow."*

The catch (verified in 0857/CLI investigation): the **default** eval provider is local `claude-cli` (spawns a local `claude` binary, no API key) and other real providers are `lm-studio`/`ollama` on localhost. **GitHub-hosted runners cannot run the local-model leg.** A naive CI-only setup would silently SKIP the model step; a naive Mac-only setup silently skips whenever the laptop is closed. Hence a **hybrid**.

## User Stories

### US-001 — Always-on CI backstop
As the maintainer, I want the golden-path verify to run automatically twice a day on GitHub, so a regression in create/install/run-with-model is caught even when my Mac is off.

- **AC-US1-01**: A GitHub Actions workflow runs `npm run verify` (hermetic stub lane) on a twice-daily cron and on `workflow_dispatch`.
- **AC-US1-02**: It also runs `npm run verify:matrix` so an all-SKIP run fails (loud-skip gate), never reads green.
- **AC-US1-03**: It builds both bundles (`build` + `build:eval-ui`) before verifying, so the studio leg uses fresh code.
- **AC-US1-04**: It needs NO secrets for the core lane; an optional `anthropic/haiku` lane runs only when `ANTHROPIC_API_KEY` is set, skip-loud and non-blocking.
- **AC-US1-05**: On failure, an optional Slack alert fires when `SLACK_WEBHOOK_URL` is set; GitHub's scheduled-failure email is the always-on fallback.

### US-002 — Authoritative local-model leg
As the maintainer, I want a Mac-local scheduled task that runs the verify against the **real** `claude-cli` default + a local model twice a day, since only my Mac can execute that leg.

- **AC-US2-01**: A `mcp__scheduled-tasks` task `vskill-regression-daily` runs `npm run verify` in the vskill repo on a twice-daily local-time schedule.
- **AC-US2-02**: It asserts provider availability first, so "model not loaded" is a FAIL/alert, not a silent skip.

## Out of scope (follow-ups)
- The >30h staleness guard that cross-checks the Mac run from CI.
- The desktop SEA-sidecar parity verify target.
