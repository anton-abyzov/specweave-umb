# Verify — 0896-hosted-private-skill-publishing

PASS · 2026-10-17T01:52:31.226Z · commands from none detected

## Commands

_No verification commands found. Set `testing.commands` in .specweave/config.json._
## Acceptance criteria

8/8 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | A private skill submitted by an entitled tenant is stored, queued, scanned and published with its tenant and PRIVATE visibility preserved at every step, and never appears on public routes, search or publisher stats. |
| AC-02 | x (tasks) | Private repository reads use only the tenant's scoped GitHub installation credentials; platform credentials are never used for private content. |
| AC-03 | x (tasks) | Public and private publish sandboxes both pass in one automated run (moved from 0847 AC-US3-06). |
| AC-04 | x (tasks) | `HOSTED_PRIVATE_PUBLISHING_AVAILABLE` is turned on only after AC-01..AC-03 and AC-05..AC-08 pass, and turning it off again restores the current safe rejection. |
| AC-05 | x (tasks) | With the gate open, a Studio private publish by an entitled user sends the selected tenant's `tenantId` (from every caller that renders `PublishButton`: the Overview tab via `PublishStatusRow` and the Edit tab via `EditorPanel`), so the platform never answers 400 `missing_tenant`; with the gate closed, Studio still omits `tenantId`. (0874 acceptance step 8: no Studio caller passes `tenantId`.) |
| AC-06 | x (tasks) | The Studio eval-server submission guard follows the gate: while closed it refuses every private repository with 422 `private_repository` as today; while open, a private-repo skill with private intent and a `tenantId` goes to the tenant-scoped private path, and public intent for a private repo is still refused. (0874 acceptance: the guard refuses every private repo whatever the gate says.) |
| AC-07 | x (tasks) | Before AC-04 opens the gate, production `VSKILL_FREE_PRIVATE_SKILL_LIMIT` matches a recorded owner decision. Today `vskill-platform/wrangler.jsonc` `vars` sets it to `"50"`, overriding the code default of 0 in `src/lib/tenant-caps.ts` (`FREE_PRIVATE_SKILL_LIMIT_DEFAULT`), so free tenants would get 50 private skills, not the 0874 "paid unlocks private" paywall. A test pins the shipped value to the decision, and a free tenant past it gets 402 `TENANT_LIMIT_REACHED`. |
| AC-08 | x (tasks) | The real publish pipeline never drops private intent: Submission persistence carries privacy and tenant, and a private-intent `POST /api/v1/submissions` is either carried PRIVATE and tenant-scoped through scan and publish or rejected; it is never stored or published as PUBLIC. (0874 acceptance: the Submission table has no privacy or tenant column, so private intent for a public repo entered the public pipeline with 201; private publish only worked through the tenant route.) |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-0896-platform | Platform1b002187; task-scope388tests passed/1existing skip … |  |
| T-02 | done | codex-0896-tests | Platform 8ef2818f47fee1547af494056010f5f0eb480156: observed… |  |
| T-03 | done | codex-0896-platform | UNDEPLOYED platform activation adfa8e12c9af108d9c042b82107c… |  |
| T-04 | done | codex-0896-studio | vskill e11b58b,0532a60,798eae5,ce15608: live tenant selecti… |  |
| T-05 | done | codex-0896-studio | vskill e11b58b and0532a60: gate-aware tenant-private submis… |  |
| T-06 | done | codex-0896-platform | Platform1b002187; free allowance0 in code+wrangler; tenant-… |  |
| T-07 | done | codex-0896-platform | Platform1b002187; additive PrivateSubmission+PrivateSkillAr… |  |
| T-08 | done | codex-0896-tests | Platform 8ef2818f47fee1547af494056010f5f0eb480156: observed… |  |
| T-09 | done | claude@antons-macbook-m4max | git diff --check → exit 0 log: .specweave/increments/0896-h… |  |
| T-10 | done | codex-0896-lead | cd /Users/antonabyzov/.codex/worktrees/hosted-private-publi… |  |
| T-11 | done | codex-0896-studio | vskill f7e6b9c,0532a60: authenticated private submit/instal… |  |
| T-12 | done | codex-0896-lead | 767ce0a2 plus fa29b1e7 fixture correction: public-only stat… |  |
| T-13 | done | codex-0896-lead | 2abc1b51,92f7bae2,695bafe9: tenant-lock revocation, process… |  |
| T-14 | done | codex-0896-studio | vskill 4f9d129: retained per-agent managed inventories acro… |  |
| T-15 | done | codex@antons-macbook-m4max | edf3f1b3: public-only problem report attachment and redacti… |  |
| T-16 | done | codex-0896-studio | 512df507 integrated as f60cc8d9: authenticated init-to-GitH… |  |
| T-17 | done | codex-0896-lead | 1a20957: actual blocklist fixture tests 7/7 pass in /tmp/08… |  |
| T-18 | done | codex-0896-studio | vskill 8cd6181817b795e81e0826ba3ba7e2200d223895 pushed to c… |  |
| T-19 | done | codex-0896-platform | Platform fd173ea6: test-only activation fixture repair afte… |  |

19/19 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
