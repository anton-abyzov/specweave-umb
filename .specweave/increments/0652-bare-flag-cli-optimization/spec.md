---
increment: 0652-bare-flag-cli-optimization
title: Add --bare flag to Claude CLI subprocess spawns
type: feature
priority: P1
status: completed
created: 2026-03-30T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Add --bare flag to Claude CLI subprocess spawns

## Overview

SpecWeave spawns Claude CLI subprocesses (`claude -p` / `claude --print`) for LLM calls across three modules: the main provider, auto-mode completion evaluator, and plugin intent detector. These subprocesses currently load hooks, plugins, CLAUDE.md files, MCP servers, and other auto-discovered context that they never use (each call provides its own explicit system prompt and model). Adding the `--bare` flag skips this unnecessary discovery, yielding ~14% faster startup per subprocess invocation.

## User Stories

### US-001: Faster LLM Provider Calls (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the Claude Code provider subprocess to start without loading unnecessary context
**So that** every LLM analysis call (structured and unstructured) executes faster

**Acceptance Criteria**:
- [x] **AC-US1-01**: `ClaudeCodeProvider.executeClaudeCommand()` passes `--bare` flag to the spawned `claude` process
- [x] **AC-US1-02**: Existing `--system-prompt`, `--model`, `--output-format json` flags continue to work alongside `--bare`
- [x] **AC-US1-03**: `getStatus()` health check call also uses `--bare`

---

### US-002: Faster Auto-Mode Completion Evaluation (P1)
**Project**: specweave

**As a** SpecWeave user running auto mode
**I want** completion evaluation subprocess calls to skip auto-discovery
**So that** each evaluation cycle completes faster

**Acceptance Criteria**:
- [x] **AC-US2-01**: `executeClaudeCli()` in completion-evaluator.ts passes `--bare` flag for all LLM evaluation calls
- [x] **AC-US2-02**: `extractSuccessCriteria()` also uses `--bare` for Haiku-based criteria extraction

---

### US-003: Faster Plugin Intent Detection (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the Haiku-based intent detection subprocess to use `--bare` instead of `--setting-sources ""`
**So that** every user prompt's plugin detection runs with minimal overhead

**Acceptance Criteria**:
- [x] **AC-US3-01**: `executeClaudeCli()` in llm-plugin-detector.ts passes `--bare` flag
- [x] **AC-US3-02**: The `--setting-sources ""` workaround is replaced by `--bare` (which subsumes it)

## Functional Requirements

### FR-001: --bare flag placement
The `--bare` flag must be the first argument in the args array, before `-p`/`--print` and all other flags, to ensure it is processed before any auto-discovery begins.

### FR-002: No behavioral change
Adding `--bare` must not change the output format, model selection, system prompt injection, or error handling of any subprocess call.

## Success Criteria

- All existing unit tests pass unchanged (behavioral equivalence)
- New tests verify `--bare` is present in spawned args
- No regressions in auto-mode, plugin detection, or LLM provider functionality

## Out of Scope

- Team agent spawning (`team.ts`) -- needs full Claude environment for teammate mode
- Hook scripts -- they ARE hooks, cannot skip themselves
- Benchmarking actual wall-clock improvement (environment-dependent)

## Dependencies

- Claude CLI v2.1+ (supports `--bare` flag)
