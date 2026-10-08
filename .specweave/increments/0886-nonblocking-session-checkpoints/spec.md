# 0886 Nonblocking session checkpoints

## Problem
SpecWeave 3.0.3 forces a model continuation at 90% plan usage, instructs it to hand off and stop, and records a marker before success. Plan percentages can reach 100% while paid credits remain. Full handoff pushes Git refs and releases ownership, which is inappropriate for automatic saving during parallel proxy/Tailscale sessions.

## Scope
In: silent local background checkpoints, per-session/worktree isolation, discovery, migration of existing hook behavior, regression proof and npm release. Out: changing proxy/Tailscale configuration, account switching, taking over other sessions, changing explicit handoff semantics.

## Acceptance Criteria
- [ ] AC-01: Stop and rate-limit hooks emit strict empty JSON and never ask the model to stop or continue, regardless of reported usage or credits.
- [ ] AC-02: Enabled hooks refresh an atomic local checkpoint at most once per five minutes per canonical worktree/session; failures preserve previous evidence and remain retryable.
- [ ] AC-03: Automatic saves never push, release claims, change user Git index/refs, or overwrite another session or the explicit handoff pointer. Ambiguous increments do not choose an owner.
- [ ] AC-04: Actual CLI regression tests cover duplicate startup warnings, parallel sessions, unavailable network/proxy and slow Git; hook return stays under two seconds.
- [ ] AC-05: Fresh review, meaningful coverage/build/lint and public npm tarball verification pass for the released version; existing Tailscale and proxy remain healthy.

## Approach
Replace quota-triggered model instructions with one detached, bounded, offline worker. Reuse the scrubbed handoff builder in checkpoint mode with an isolated destination and the actual working directory for Git capture. Publish a receipt only after successful writing; preserve the previous generation on failure. Existing auto-handoff settings enable the new behavior automatically, and --at remains accepted for compatibility but no longer gates saving. Explicit handoff remains the ownership-transfer/network action. Status exposes the local checkpoint directory. No daemon, scheduler, network probe or model request is necessary. Source: origin/develop 6a2dd672d; installed/public starting version 3.0.3. Hook semantics checked against https://learn.chatgpt.com/docs/hooks.

## Tasks

### T-01 Background checkpoint engine
- AC: AC-02, AC-03 | Files: src/core/session/session-checkpoint.ts, src/core/session/checkpoint-worker.ts, src/core/session/work-handoff.ts, src/core/session/handoff-git-state.ts, src/core/session/handoff-doc-format.ts, src/core/session/handoff-doc-format.test.ts, src/core/session/work-handoff.test.ts, tests/unit/core/session/session-checkpoint.test.ts | Test: npx vitest run --config vitest.unit.config.ts tests/unit/core/session/session-checkpoint.test.ts

### T-02 Nonblocking hook integration and documentation
- AC: AC-01, AC-02 | Files: src/core/session/usage-guard.ts, src/cli/commands/auto-handoff.ts, bin/specweave.js, bin/startup-check.js, tests/unit/core/session/usage-guard.test.ts, tests/unit/core/session/grok-limit-handoff.test.ts, README.md, docs-site/docs/guides/auto-handoff.md, docs-site/docs/guides/cross-tool-handoff.md, docs-site/docs/guides/claude-code-vs-codex.md, docs-site/docs/guides/claude-code-usage-limit.md, docs-site/docs/guides/specweave-3.md, docs-site/docs/workflows/overview.md, docs-site/docs/reference/commands.md, docs-site/docs/guides/switch-claude-code-to-codex.md, docs-site/docs/overview/how-it-works.md, docs-site/src/pages/pricing.tsx, docs-site/src/components/landing/content.tsx, docs-site/static/llms.txt, src/templates/AGENTS.md.template, src/templates/CLAUDE.md.template, skills/sw-handoff/SKILL.md, CHANGELOG.md, package.json, package-lock.json, plugins/specweave/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, scripts/completions/*, plugins/specweave/skills/handoff/SKILL.md | Test: npx vitest run --config vitest.unit.config.ts tests/unit/core/session/usage-guard.test.ts tests/unit/core/session/grok-limit-handoff.test.ts

### T-03 Real CLI parallel and network regression
- AC: AC-03, AC-04 | Files: scripts/e2e/session-checkpoints.mjs | Test: node scripts/e2e/session-checkpoints.mjs

### T-04 Review, release and evidence
- AC: AC-05 | Files: reports/*, docs-site/blog/2026-02-21-toxicskills-why-your-ai-agent-skills-need-verification.md | Test: npm --prefix /Users/antonabyzov/.codex/worktrees/usage-checkpoint/specweave run release:preflight
