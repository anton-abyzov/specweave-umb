---
increment: 0729-versions-empty-state-guidance
title: "Versions tab empty-state guidance"
type: feature
priority: P1
status: active
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# 0729 — Versions Tab Empty-State Guidance

## Overview

The Versions tab in the studio shows "No version history available" when a local skill has never been submitted to verified-skill.com. This is technically correct but unhelpful — users don't know why it's empty or what to do. Replace the generic message with an empty state that explains the situation and offers a clear next step.

## Problem

Local skills authored in the studio (`origin: "source"`) never appear on verified-skill.com unless explicitly submitted. The platform-fed Versions tab will always be empty for them. Users repeatedly ask "why don't I see versions for the skill I just edited?" because the current empty state gives no context.

## User Stories

### US-001: Local skills explain why the Versions tab is empty
**Project**: vskill

**As a** skill author who has saved/regenerated a local skill several times
**I want** the Versions tab to explain that local-only skills have no platform-tracked history and to point me at the submit flow
**So that** I understand the difference between local saves and published versions and can decide whether to submit

**Acceptance Criteria**:
- [x] **AC-US1-01**: When versions array is empty AND `skill.origin === "source"`, the Versions tab renders explanatory text ("This skill is local-only — no published versions yet") plus a primary CTA button labelled "Submit on verified-skill.com"
- [x] **AC-US1-02**: When versions array is empty AND `skill.origin !== "source"` (installed plugin/global), keep the legacy "No version history available" message — no submit CTA (user doesn't own the skill)
- [x] **AC-US1-03**: The CTA button opens `https://verified-skill.com/submit?repo=<encoded-repoUrl>` (or `https://verified-skill.com/submit` if no repoUrl is known) in a new tab with `target="_blank"` + `rel="noopener noreferrer"`
- [x] **AC-US1-04**: The empty-state component is reachable via a stable `data-testid="versions-empty-state-local"` (source skills) or `data-testid="versions-empty-state-installed"` (installed) so end-to-end tests can assert which branch rendered

## Out of Scope (Follow-ups)

- **Local-drift indicator** — when local SKILL.md content differs from latest published version, badge it with "Local changes." Requires content-hash computation in studio + comparison with platform's `contentHash`. Defer to follow-up increment 0730.
- **Local version history (Option D)** — append-only JSONL ledger for every save, merged into the Versions tab. Defer to follow-up increment 0731.

## Dependencies

- Existing `WorkspaceContext.state.skill` already exposes `origin` (typed as `"source" | "plugin" | "global"`) and the route params (`plugin`, `skill`)
- Existing `SkillInfo` type at `src/eval-ui/src/types.ts` already has `origin` + optional `homepage`/`repoUrl` fields
- No new API endpoint, no new server route, no new platform call
