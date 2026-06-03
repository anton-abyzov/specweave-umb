---
increment: 0869-hook-wiring-audit
title: Hook wiring audit + recurrence guard (6 dead hooks)
type: bug
priority: P1
status: completed
created: 2026-06-03T05:30:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug: 6 of 10 SpecWeave hooks are silently dead (router/hooks.json mismatch)

## Overview

The plugin `plugins/specweave/hooks/hooks.json` invokes 10 distinct `specweave hook <X>`
commands, but the Node hook-router (`src/core/hooks/handlers/hook-router.ts`) registers only
**4** event keys. The other **6** — `session-start`, `post-tool-use`, `post-tool-use-analytics`,
`stop-reflect`, `stop-auto`, `stop-sync` — resolve to "unknown event type" and return the safe
default, running **no handler and no side effect**. Because the failure mode is a *safe default*,
the hooks look healthy while doing nothing.

**Root cause (commit-level):** `0f81519b1` ("rework hooks: remove shell-based handlers,
consolidate to CLI-first") removed those router keys and deleted their handler files but left
`hooks.json` calling them; `0867` later re-added only `pre-compact` + `stop`. Full evidence in
`reports/hook-wiring-audit-2026-06-03.md`.

**Most serious casualty:** `stop-auto` — `/sw:auto`'s autonomous loop depends on the Stop hook
returning `decision:block` (`auto.ts:532`); dead ⇒ autonomous mode never continues.

## Problem

A whole class of bug (a `hooks.json` entry whose event the router doesn't register) is
**invisible** — no test asserts parity between the call-sites (`hooks.json`) and the dispatch
(`HANDLERS`). 0868 fixed one instance (`stop`) by hand; nothing stops the next one.

## Scope of THIS increment

Ship the **recurrence guard** (executable parity invariant) + the audit. The actual
restoration of the 6 dead handlers is a deliberate follow-up (each is a REGISTER-or-REMOVE
product decision, and `stop-auto` needs careful loop logic) — see report fix plan.

## User Stories

### US-001: A test makes the hooks.json↔router mismatch impossible to ship silently (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** a test that fails when any `hooks.json` hook command targets an event the router
does not register (unless explicitly allowlisted as known-dead)
**So that** a hook can never again be wired in `hooks.json` but silently no-op in the router.

**Acceptance Criteria**:
- [x] **AC-US1-01**: A test parses the plugin `hooks.json`, extracts every `specweave hook <X>` event name, and asserts each is either a key in the router `HANDLERS` map OR in an explicit `KNOWN_UNROUTED` allowlist.
- [x] **AC-US1-02**: `KNOWN_UNROUTED` is exactly the 6 currently-dead names (`session-start`, `post-tool-use`, `post-tool-use-analytics`, `stop-reflect`, `stop-auto`, `stop-sync`), each annotated; the test asserts the allowlist has **no stale entries** (every allowlisted name still appears in `hooks.json`), so restoring a hook forces its removal from the list.
- [x] **AC-US1-03**: The test asserts the 4 known-good events (`user-prompt-submit`, `pre-tool-use`, `pre-compact`, `stop`) ARE registered — so a regression that drops one (like 0867/0868) fails loudly.
- [x] **AC-US1-04**: The audit report (`reports/hook-wiring-audit-2026-06-03.md`) documents all 10 hooks, the root-cause commit, the connected places (plugin cache drift, project `settings.json` shell hooks), and the per-hook restoration plan.

## Out of Scope

- Restoring/registering the 6 dead handlers (follow-up increment; `stop-auto` is critical).
- Cleaning up the stale installed plugin caches (handled by republish + `refresh-plugins`).

## Success Criteria

- `npx vitest run` for the new guard test passes (GREEN) and fails if a hook is added
  unregistered, a dead hook is restored but left allowlisted, or an allowlisted name is removed.

## Dependencies

- `plugins/specweave/hooks/hooks.json`, `src/core/hooks/handlers/hook-router.ts`.
