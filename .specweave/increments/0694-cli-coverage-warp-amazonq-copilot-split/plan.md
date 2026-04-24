---
increment: 0694-cli-coverage-warp-amazonq-copilot-split
status: active
---

# Architecture Plan

## Summary

Pure data + interface change in `vskill/src/agents/agents-registry.ts` plus a tiny UI gate in Studio. No new modules, no schema migrations, no DB. The blast radius is one TypeScript file and two React components, with parity test files for each.

## Decisions

### D-1: Don't delete `github-copilot` — rename + alias
**Decision**: Rename `github-copilot` → `github-copilot-ext` and add a `LEGACY_AGENT_IDS = { 'github-copilot': 'github-copilot-ext' }` map consumed by `getAgent(id)`.

**Why**: Anyone with installed skills under the old id (lockfiles, scripts, `vskill add github-copilot`) shouldn't break. Renaming preserves install history; the alias makes the rename invisible to consumers.

**Alternative rejected**: Add `copilot-cli` and silently leave `github-copilot` ambiguous. Rejected because the existing entry's `detectInstalled: 'which github-copilot'` is wrong (the binary is named `copilot`) and the path `.github/copilot/skills` only matches the VS Code extension.

### D-2: `isRemoteOnly` is a soft flag, not entry removal
**Decision**: Keep Devin / bolt.new / v0 / Replit in the catalog, mark them `isRemoteOnly: true`, and gate install affordances + show "Remote" badge in Studio.

**Why**: Catalog completeness — users searching for "Devin" should still find the entry and learn it's web-only. Removing them silently would be worse UX than a clear "Remote" label.

### D-3: Verify paths via WebFetch at implementation time
**Decision**: For Warp + Amazon Q + Copilot CLI, fetch the cited vendor docs in T-005/T-006/T-004 to confirm the skills dir convention. If a doc is unreachable, use the documented community defaults and tag the entry with a `// VERIFY` comment.

**Why**: These tools went GA recently; docs may have moved. Hard-coding without verification risks shipping wrong paths.

## File Changes

| File | Change |
|---|---|
| `vskill/src/agents/agents-registry.ts` | +4 entries, rename 1, +`isRemoteOnly?` field, +`LEGACY_AGENT_IDS`, +`getInstallableAgents()`, update `getAgent()` |
| `vskill/src/agents/agents-registry.test.ts` | +tests for new entries, alias resolution, isRemoteOnly filter |
| `vskill/src/eval-ui/src/components/AgentScopePicker.tsx` | Render Remote badge when `isRemoteOnly` |
| `vskill/src/eval-ui/src/components/AgentScopePicker.Popover.tsx` | Same badge in popover |
| `vskill/src/commands/add.ts` | Reject install on remote-only agent with typed error |
| `vskill/src/commands/add.test.ts` | Test for rejection |

## Coordination with Parallel Agent

`impl-registry-dry` is also editing `agents-registry.ts` (adding `NON_AGENT_CONFIG_DIRS` export). Plan: complete all our entry edits + helper additions through T-008, send `CONTRACT_READY: agents-registry.ts edits done`, then they layer their export at the end of the file. Their edits append-only (new export), ours are interspersed (entry rename + new entries) — sequencing prevents merge conflicts.

## Test Strategy

- Unit (Vitest): every new entry asserts shape; alias map asserts `getAgent('github-copilot') === getAgent('github-copilot-ext')`; `getInstallableAgents()` returns 49 (53 total − 4 remote-only).
- Component (Vitest + Testing Library or snapshot): AgentScopePicker renders Remote badge for `isRemoteOnly` rows.
- Integration: round-trip `getAgent(id) → resolve install path` for each new agent.
- Detection: mock `which copilot|warp|q` succeeding → `detectInstalledAgents()` includes them.
