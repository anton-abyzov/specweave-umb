---
increment: 0701-studio-provider-pricing-and-model-identity
title: "Studio provider pricing and model identity"
type: feature
priority: P1
status: planned
created: 2026-04-24
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio provider pricing and model identity

## Overview

Skill Studio's AgentModelPicker (vskill eval-ui) misleads users in three small ways: Claude Code model rows hide which concrete model will actually serve the session, Anthropic-API models show `$0.00 / $0.00 per 1M tokens`, and LM Studio's "Start service" CTA confuses "start the app I already have" with "start LM Studio's HTTP server." This increment fixes all three so the picker can be trusted for routing, cost estimation, and setup guidance.

## Problem

1. **Generic Claude Code aliases** — `api-routes.ts` PROVIDER_MODELS lists `sonnet`/`opus`/`haiku` generics with no hint at the resolved model ID. A Pro/Max user cannot tell whether `opus` routes to Opus 4.7 or 4.6 until the session starts.
2. **Zero-dollar Anthropic API pricing** — `useAgentCatalog.toAgentEntry` never populates `pricing` for `anthropic`, so `ModelList.formatMetadata` renders `$0.00 / $0.00 per 1M tokens`. This makes the picker useless for cost comparison.
3. **Confusing "Start service" CTA for LM Studio** — users with loaded models see "Start service →" and assume they must install/boot the *app itself*, when in fact they only need to start LM Studio's built-in OpenAI-compatible HTTP server (Developer → Start Server, port 1234).

## Goal

Make the picker tell the truth about what will run, what it costs, and what the user must do to unlock local providers.

## User Stories

### US-001: Resolved Claude Code model identity
**Project**: vskill

**As a** vskill user on a Pro/Max Claude Code subscription
**I want** to see the exact model ID my Claude Code session will route to
**So that** I can reason about capability, context window, and quota impact before running

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `/api/config` response includes a `resolvedModel` field on the `claude-cli` provider populated from `~/.claude/settings.json` `model` key (supports full IDs like `claude-opus-4-7[1m]` and aliases like `sonnet`).
- [ ] **AC-US1-02**: When `~/.claude/settings.json` is missing, malformed, or unreadable, `resolvedModel` is `null`; the UI renders the generic label only (no crash, no misleading text).
- [x] **AC-US1-03**: The Studio picker's Claude Code model rows render the resolved ID as secondary metadata when present (e.g. "Claude Opus" heading + "routing to claude-opus-4-7[1m]" sub-line).
- [ ] **AC-US1-04**: Resolution is re-read on each `/api/config` request (no extra caching beyond filesystem read) so a user who toggles `/model` in Claude Code sees the change on the next picker open.

### US-002: Real Anthropic API pricing
**Project**: vskill

**As a** vskill user deciding between API-keyed Anthropic models
**I want** to see accurate per-1M-token input/output prices
**So that** I can estimate cost without leaving the picker

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `PROVIDER_MODELS["anthropic"]` entries in `api-routes.ts` carry `pricing: { prompt, completion }` matching the public rate card — Opus 4.7 & 4.6: 15/75, Sonnet 4.6: 3/15, Haiku 4.5: 1/5 USD per 1M tokens.
- [ ] **AC-US2-02**: `/api/config` response propagates `pricing` on each Anthropic model entry (shape identical to OpenRouter's).
- [x] **AC-US2-03**: `useAgentCatalog.toAgentEntry` copies `pricing` from the server response so `ModelList.formatMetadata` renders e.g. `$3.00 / $15.00 per 1M tokens` for Claude Sonnet 4.6.
- [ ] **AC-US2-04**: A dated source comment in `api-routes.ts` points to `https://www.anthropic.com/pricing` and records the last-checked date (2026-04-24) so maintainers know when to re-verify.

### US-003: Accurate LM Studio CTA copy
**Project**: vskill

**As a** vskill user with models loaded in LM Studio but the local HTTP server not running
**I want** the picker to tell me to start the LM Studio *server* (not the app)
**So that** I don't waste time re-installing software I already have

**Acceptance Criteria**:
- [x] **AC-US3-01**: `strings.providers.lmStudio.startServiceCta` changes from `"Start service →"` to `"Start LM Studio server →"`.
- [ ] **AC-US3-02**: A new `strings.providers.lmStudio.startServiceTooltip` with value `"Open LM Studio → Developer tab → Start Server (default port 1234)."` is exported from `strings.ts`. **String is exported, but NOT wired into `LockedProviderRow` as `title=` attribute per T-009 acceptance test — only partially delivered.**
- [x] **AC-US3-03**: Ollama's CTA stays `"Start service →"` (single command `ollama serve`, no app/server split to explain).

## Out of Scope

- Live Anthropic pricing via API (no public pricing endpoint exists — hardcoded + dated comment is acceptable).
- Changing Claude Code's routing behavior (we only surface what it already decides).
- Resolving model IDs for Cursor/Codex/Gemini CLI (separate config paths, separate increment).
- Cache read/write pricing display (only base input/output for this increment).
- Redesigning the LM Studio setup drawer flow — copy change only.
- Reading project-local `.claude/settings.json` overrides (global-only resolution for v1).

## Dependencies

- Anthropic public pricing page (https://www.anthropic.com/pricing) — snapshot taken 2026-04-24.
- Existing `/api/config` + `/api/openrouter/models` routes in `vskill/src/eval-server/api-routes.ts`.
- Existing `useAgentCatalog` hook + `ModelList` component in `vskill/src/eval-ui/`.
