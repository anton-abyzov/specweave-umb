# 0858 — Plan

## Component A — GitHub Actions workflow (CI backstop)

`repositories/anton-abyzov/vskill/.github/workflows/golden-path-nightly.yml`

- Triggers: `schedule` cron `0 6,18 * * *` (twice daily, off US business hours), `workflow_dispatch`, and `pull_request` on the model/install/create/harness paths (`src/eval/**`, `src/eval-server/**`, `src/commands/**`, `test/verify/**`).
- `concurrency` group per-ref with cancel-in-progress.
- Job `verify` on `ubuntu-latest`, 15-min timeout, secrets mapped to job-level env (`ANTHROPIC_API_KEY`, `SLACK_WEBHOOK_URL`) so step `if:` can read them.
- Steps: checkout → setup-node 22 (npm cache) → `npm ci` → `npm run build && npm run build:eval-ui` → `npm run verify` (stub lane) → `npm run verify:matrix` (loud-skip gate) → optional real `anthropic/haiku` lane (`if env.ANTHROPIC_API_KEY != ''`, `continue-on-error`) → upload `test/verify/reports/` artifact (always) → optional Slack on failure.

Modeled on the existing `e2e-live-nightly.yml` (Node 22, checkout@v4, setup-node@v4) but single-repo (no vskill-platform / Postgres).

## Component B — Mac-local scheduled task (local-model leg)

`mcp__scheduled-tasks` task `vskill-regression-daily`, twice-daily local time. Prompt: cd to the vskill repo, assert provider availability, run `npm run verify` against the real `claude-cli` default + one local model (lm-studio/ollama), alert on FAIL. Mirrors the established `obsidian-brain-daily` Mac-scheduled pattern (fires while Claude.app is open).

## Why hybrid (not one or the other)
- GitHub cron = always-on, hermetic, but cannot run `claude-cli`/`lm-studio` (no local binary/server on hosted runners).
- Mac task = the only place the local-model leg can run, but skips silently when the laptop is closed.
- Together: CI guarantees the create/install/run-with-model wiring never regresses; the Mac task adds authoritative real-local-model coverage.
