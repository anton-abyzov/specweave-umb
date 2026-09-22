# 0848 — Plan (authored 2026-06-10, retroactive + remaining)

## Design

Privacy in 0848 means **repo-visibility**: a skill's *source code* lives in a private vs public GitHub repo. The signal is computed by joining `SkillInfo.repoUrl` against the connected-repos list and reading `repo.isPrivate` — no new field on `SkillInfo`.

- **Single source of visibility**: `useSkillRepoVisibility` / `useConnectedRepoLookup` (`vskill/src/eval-ui/src/hooks/`). `resolveSkillRepoVisibility` returns `private | public | unknown` (unknown → treated as public, no chip).
- **Atoms**: `PrivateRepoChip` (amber lock chip on sidebar rows) and the Account cabinet `ConnectedReposTable` private/public `VisibilitySection` split are the visual vocabulary; new surfaces reuse the same amber-lock / neutral-globe language.

## Tasks status (reconciled)

| Task | Where | Status |
|---|---|---|
| T-001 visibility hook | `useSkillRepoVisibility.ts` | landed |
| T-002 chip + SkillRow | `PrivateRepoChip.tsx`, `SkillRow.tsx:207` | landed |
| T-003 sidebar sub-grouping | `Sidebar.tsx`/`SidebarSection.tsx` | done in 0874 (workstream C) |
| T-004 account tiles | `ConnectedReposTable.tsx`, `AccountShell.tsx` | landed |
| T-005 public banner | platform `/skills` | landed |
| T-006 publisher footer | platform `publishers/[name]/page.tsx` | done in 0874 |
| T-007 marketplace private section | `MarketplaceDrawer.tsx` | done in 0874 |

## Relationship to 0874

0874 ("tiered private skills — paid unlocks private") introduces the *publish-visibility* concept (a skill published privately to a tenant/org, gated behind a paid Stripe plan) and a publish-flow chooser + paywall. 0848 stays scoped to repo-visibility presentation; 0874 finishes 0848's three remaining presentation tasks (T-003/T-006/T-007) as part of its workstream C and adds the orphaned `PrivateBadge` to the detail header.

## Verification
- `npx vitest run` (Node 22) for `useSkillRepoVisibility.test.ts`, the new SkillRow chip test, sidebar grouping test, MarketplaceDrawer private-section test, and the platform publisher-footer test.
- `npm run build:eval-ui` clean.
