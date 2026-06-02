---
status: completed
---
# 0866 — External-sync & release stabilization

## Goal
Make the **from-scratch install → first increment → external-tool sync** path reliably work, and bring npm/GitHub releases back into a consistent state. Diagnosis was done in the 2026-06-01 session; this increment executes the fixes and **proves** them with a live round-trip, the way a brand-new user would experience it.

## Diagnosis (verified 2026-06-01)
| # | Finding | Status |
|---|---|---|
| F1 | `specweave init` / `auto` "Next steps" printed a non-existent `specweave increment` command (real command is `create-increment`). | ✅ Fixed in source (`next-steps.ts`, `auto.ts`) — needs to ship. |
| F2 | `sync-health` ADO check reported false "missing credentials" on the **global** CLI (1.0.585) because it looked for legacy `ADO_*` vars; `.env` uses `AZURE_DEVOPS_*`. | ✅ Already fixed in local **1.0.586** (0865 `ADO_PAT_ALIASES`/`AZURE_DEVOPS_*`) — needs to ship. |
| F3 | Create-path `.env` loading was alleged broken by an audit agent. **Disproved**: `CredentialsManager.loadFromEnv()` already merges `.env`→`process.env` on construction. Sync create works from the repo root without manual export. | ✅ No action (verified working). |
| F4 | JIRA project **SWE2E is missing the "Story" issue type** → multi-user-story increments 400 at closure. (Single-US increments map US→Epic and are unaffected.) | ⚠️ Open. |
| F5 | Release drift: local **1.0.586 never published** (tag unpushed, never CI-built); npm **1.0.585 has no GitHub release**; GitHub "Latest" mislabeled on **v1.0.583**; stray local tag **v1.0.58**. | ⚠️ Open. |

## User Stories

### US-001 — Onboarding command is correct and shipped
- [x] **AC-US1-01**: `specweave init` "Next steps" shows a command that actually exists (`specweave create-increment`), verified by running it from a fresh temp dir on the shipped build.
- [x] **AC-US1-02**: A unit test asserts the init next-steps output contains `create-increment` and does NOT contain the string `specweave increment "`.

### US-002 — Releases are consistent
- [x] **AC-US2-01**: `specweave` **1.0.586** is published to npm (`npm view specweave@1.0.586 version` succeeds) and includes the F1/F2 fixes.
- [x] **AC-US2-02**: GitHub releases exist for **v1.0.585** and **v1.0.586**, and the **"Latest"** badge is on **v1.0.586** (not v1.0.583).
- [x] **AC-US2-03**: Stray local tag `v1.0.58` deleted; `v1.0.586` tag pushed to origin.

### US-003 — External sync proven by a live round-trip
- [x] **AC-US3-01**: A throwaway **single-user-story** test increment is created and `sync-progress` creates a real **GitHub issue** in `anton-abyzov/specweave`; the URL is written back into the increment's `metadata.json`.
- [x] **AC-US3-02**: The same run creates a real **Jira** Epic in `SWE2E` and a real **ADO** work item in `EasyChamp/SpecWeaveSync`; both links are written back to `metadata.json`. (Run from the repo root so `.env` auto-loads; isolate providers with `--no-*` if needed.)
- [x] **AC-US3-03**: After verification, **all created external items are cleaned up** (GitHub issue closed, Jira epic deleted, ADO work item deleted) and the test increment is abandoned/removed. No registry pollution remains.

### US-004 — JIRA Story type resolved
- [x] **AC-US4-01**: Either the **"Story"** issue type is added to SWE2E's issue-type scheme (so multi-US increments sync), **or** SpecWeave is configured to map user stories to an available type — and `sync-health` reports JIRA issue types ✓ (no "Missing issue types: Story" warning).

## Out of scope
- Re-recording or editing the SpecWeave intro video (handled separately; script delivered to `SPECWEAVE-VIDEO-SCRIPT.md`).
- vskill npm (already in sync at 1.0.19; optional non-Latest source-tag backfill only).

## Notes for executor
- **Use the local bin** for any sync test until 1.0.586 is published: `node repositories/anton-abyzov/specweave/bin/specweave.js …` (global PATH is 1.0.585). Build first: `cd repositories/anton-abyzov/specweave && npm run rebuild`.
- **npm publish caveat**: CI `release.yml` fails with EOTP (granular token can't bypass 2FA). Publish locally with an OTP recovery code from Obsidian (`obsidian-cli`/`obsidian-brain` skill, search "npm recovery codes"). If a code can't be obtained safely, STOP and report — do not burn codes guessing.
- **Cleanup is mandatory** for US-003 — the test creates real items in three live trackers.
