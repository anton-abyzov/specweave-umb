---
increment: 0876-studio-dynamic-local-models-and-openrouter-crash
title: "Skill Studio: real local model list + OpenRouter hover-crash fix"
type: feature
priority: P1
status: completed
created: 2026-06-17
completed: 2026-06-17
structure: user-stories
test_mode: TDD
coverage_target: 90
repos:
  - repositories/anton-abyzov/vskill
---

# Feature: Skill Studio: real local model list + OpenRouter hover-crash fix

## Overview

The Skill Studio (Tauri desktop app, currently v1.0.56) model picker has two
user-reported defects:

1. The local-provider (Ollama) list shows **hardcoded models that aren't installed**
   (`Llama 3.1 8B / Qwen 2.5 32B / Gemma 2 9B / Mistral 7B`). The real models on the
   machine are whatever `GET /api/tags` reports (here: `qwen3-coder:30b`, `qwen2.5:14b`).
2. **Hovering "OpenRouter" crashes the app.**

This increment makes the picker show the *real* list of locally-available models
(dynamic, never hardcoded) and makes OpenRouter hover crash-proof against malformed
catalog responses.

## Requirements Source

User-reported, direct-quote direction: *"for all Llama, it seems like there are some
hard codes, so you must use dynamic … have a real list of models that are available on
local machines. Also, when I hover over OpenRouter, it just crashes."* Root causes were
verified at the line level (see plan.md). Increment 0875 explicitly left the model-picker
selection logic out of scope; this increment closes that gap.

## User Stories

### US-001: Real local model list — no hardcoded fallback (P1)
**Project**: vskill

**As a** Skill Studio user choosing a local model,
**I want** the Ollama/LM Studio lists to show exactly the models actually installed on my
machine (and nothing when the runtime is down),
**So that** I never see and accidentally pick a model that isn't there.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `PROVIDER_MODELS["ollama"]` is `[]` (parity with `lm-studio`); the
  picker never seeds Ollama with hardcoded model names.
- [x] **AC-US1-02**: `probeOllama()` returns `{ available: false, models: [] }` when the
  `/api/tags` probe throws, times out, or returns a non-OK / bad body — i.e. an
  unreachable Ollama yields an empty list, not the old four Llama-family models.
- [x] **AC-US1-03**: When `/api/tags` responds OK with models, `probeOllama()` returns
  `{ available: true, models }` reflecting exactly those names (filtering blank names),
  e.g. `qwen3-coder:30b`, `qwen2.5:14b` on this machine.
- [x] **AC-US1-04**: The probe timeout for both `probeOllama()` and `probeLmStudio()` is
  raised from 500ms to 2000ms so a cold sidecar start no longer falls back to "offline".
- [x] **AC-US1-05**: When a local provider is unavailable, the existing `start-service`
  CTA is shown (no behavior regression); LM Studio behavior is unchanged except the timeout.

### US-002: OpenRouter hover never crashes (P1)
**Project**: vskill

**As a** Skill Studio user,
**I want** hovering (or searching within) the OpenRouter provider to never crash the app,
even when the OpenRouter catalog response is malformed,
**So that** I can browse OpenRouter models reliably.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `hydrateOpenRouter()` guards the response shape — if `data.models`
  is not an array it is treated as empty (no throw), and each model's display name is
  `m.name ?? m.id` (rows with neither id nor name are dropped).
- [x] **AC-US2-02**: `rankFiltered()` in `ModelList.tsx` is null-safe: filtering and
  sorting use `(m.displayName ?? m.id ?? "")` so a model with a null/missing display name
  cannot throw `TypeError: …toLowerCase` when the user types in the OpenRouter search box.
- [x] **AC-US2-03**: Regression tests reproduce the crash inputs (a model with
  `name: null`, and a response missing the `models` array) and assert no throw + graceful
  render.
- [x] **AC-US2-04**: `ModelList` runs an identical hook sequence on every render — the
  OpenRouter empty-card early return must sit *after* all hooks (`useMemo`/`useVirtualList`),
  so switching the displayed agent from an available provider to OpenRouter-without-a-key
  cannot throw React #300 ("rendered fewer hooks than expected"). This is the second,
  pre-existing hover crash (surfaced by the e2e run), distinct from AC-US2-02. A
  re-render-across-agent-switch regression test reproduces it (RED → GREEN verified).

## Out of Scope

- Adding new providers/runtimes (llama.cpp, Jan, vLLM, GPT4All).
- Redesigning the picker UI or the OpenRouter pricing/caching pipeline.
- Changes to the publish drawer (covered by 0875).

## Success Metrics

- Picker shows 0 non-installed local models in any probe state.
- 0 crashes on OpenRouter hover/search across malformed-response fixtures.
- Shipped as desktop v1.0.57 with green CI.
