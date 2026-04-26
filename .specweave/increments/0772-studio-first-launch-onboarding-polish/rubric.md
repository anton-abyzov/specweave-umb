---
increment: 0772-studio-first-launch-onboarding-polish
title: "Studio First-Launch Onboarding Polish"
generated: 2026-04-26
source: hand-written
version: "1.0"
status: active
---

# Quality Contract

This rubric is the per-increment quality contract consumed by closure gates (`/sw:done`). All five user stories share these standards.

## Functional Correctness

- All ACs in `spec.md` map to ≥ 1 test in `tasks.md` (red/green pair).
- `npx vitest run` passes for every new/touched test file.
- Server endpoints' integration tests use real `child_process` (not mocked) where the function under test is the spawn call itself; pure logic tests mock at the `spawnSync` boundary.
- UI component tests render via React Testing Library and assert visible text, accessible roles, and dispatched events — never internal implementation details.

## Code Quality

- No `any` in new TypeScript code. New props/interfaces are explicit and documented.
- No new top-level files larger than 400 LOC. Split if exceeded.
- New components consume the existing `var(--color-*)` token system; no inline hex colors.
- New strings live in `src/eval-ui/src/strings.ts` (or its companion files) — never inline literals in components — exception: per-instance dynamic content (computed commands, paths).
- Reuse existing helpers (`parseGithubRemote`, `scanInstalledPluginSkills`, `redactKey`, `fetchJson`) instead of re-implementing.

## Cross-Cutting Concerns

- **Cross-platform**: Onboarding detection and `github-status` work on macOS, Linux, Windows. Tests must mock the platform branch when asserting per-OS behavior.
- **Performance**: First-launch onboarding total CLI overhead ≤ 50 ms median. `/api/project/github-status` 95p ≤ 100 ms.
- **Backward compatibility**: Server `AgentScopeEntry.pluginSkillCount` is optional in client adapter (`?? 0`). 409 string-match path stays alongside the new structured payload so older servers don't break the new client.
- **Accessibility**: New CTA buttons + hint card pass `axe` (no critical/serious violations). All buttons have visible focus rings, descriptive `aria-label`s where text is icon-only.

## Closure Gates

- [ ] `vitest run` clean for affected suites.
- [ ] No new ESLint warnings.
- [ ] `tsc --noEmit` clean.
- [ ] `sw:code-reviewer` produces no critical/high/medium findings.
- [ ] `simplify` finds no duplication or premature abstraction (the create-flow fix should NOT introduce new abstraction layers).
- [ ] `sw:grill` writes `grill-report.json` confirming all five user stories' acceptance criteria are satisfied by visible code paths (not just tests).
- [ ] `judge-llm` confirms each AC is observably true in the running studio (snapshot test or screenshot acceptable for UI ACs).
- [ ] Living docs synced via `specweave sync-living-docs 0772-...`.

## Manual Verification (User Gate)

The user MUST manually verify these flows before closure (per CLAUDE.md "Manual Verification Gates"):

1. Fresh project, no claude binary, no API keys → `npx vskill@latest studio` → onboarding prompt fires with softened wording.
2. Fresh project, claude binary present → onboarding silent, studio launches.
3. Project with no skills → right pane shows "Browse marketplaces" + "Create new skill" CTAs; both work.
4. Click Create Skill → fill form → success → right pane navigates to the new skill's overview page.
5. Click Create Skill again with the same name → no red error; "Skill already existed — opened it" inline note; navigates to existing skill.
6. Fresh project (no `.git`) → after creating a skill, the GitHub bootstrap hint appears with `gh repo create ...`. Copy button copies command. Dismiss hides it for the project.
7. Agent badge total reads `(N · G · P)`; hover tooltip says "project · personal · plugins". Adding/removing a plugin skill updates the count after the 30 s cache TTL.

Any failure in steps 1-7 blocks closure.
