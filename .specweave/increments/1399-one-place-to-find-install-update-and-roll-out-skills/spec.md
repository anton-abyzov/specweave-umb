# One place to find, install, update and roll out skills

## Problem

Anton cannot answer "where is skill X, which version is it, and does every machine have it" from one place. His skills on m4 come from four sources and two package managers. M5 has almost none. The Skills page in Settings has a filter bug and a scope label that suggests more than it does.

Evidence, gathered November 18, 2026. The full map is in `reports/2026-11-18-where-skills-live-and-how-to-manage-them-edf624-937ca7.md`.

- **m4 storage.** `~/.agents/skills` holds 59 skill folders, and 52 of them are symlinked into `~/.claude/skills`. Two lockfiles track them:
  - `~/.agents/vskill.lock` tracks 11, from `anton-abyzov/vskill`, `anton-abyzov/anton-personal-skills` (private), `anton-abyzov/social-media-posting-skill`, `anthropics/skills`, `cursor/plugins`, and one `hosted-private:` verified-skill.com source.
  - `~/.agents/.skill-lock.json`, written by the `npx skills` CLI, tracks 29: hyperframes (19), app-store-connect (9), marketingskills and others. One skill appears in both locks.
  - 19 folders are tracked by neither: hand copies such as `gws`, `kie-gemini-omni`, `tax-filing`, `precocity-invoicing`, `video-pipeline` and `tauri-desktop-release`. No command updates them.
- **Other skill folders on m4.**
  - `~/.claude/skills` also holds five real folders and `synced/`, which contains claude.ai skills.
  - `~/.codex/skills` holds two.
  - Claude plugins: `sw` 3.1.23, `codex` and `stripe`. Marketplaces: official, `obsidian-skills` (kepano), `marketingskills`, `openai-codex` and a local `specweave`.
- **Authoring sources.**
  - `repositories/anton-abyzov/vskill` (public) carries 10 plugins with 25 skills under `plugins/*/skills`, plus 10 under `skills/`. `obsidian-brain` lives in `plugins/personal`.
  - `~/Projects/github/anton-personal-skills` (private) carries 4.
- **M5 (user `anton`, a separate home).** There are no user skills for Claude or Codex, no `~/.agents`, no plugins, no vskill lock, no `vskill` on PATH and no Obsidian vault.
  - `~/.claude/skills/synced` holds 35 claude.ai-synced skills that Claude Code loads.
  - Codex has only its 6 `.system` skills, which is exactly the "6 skills" in the screenshot.
- **Filter bug.**
  - `ComposerSkillsPopover.tsx:215` links to Settings > Skills with `agent=<instanceId>` taken from the thread's provider, for example `claudeAgent`.
  - `ProjectSkillsSettings.tsx:752` seeds the Agent filter from it.
  - On M5 no row has a Claude copy, so `projectSkillFacets` offers only Codex. `FacetGroup` (`ProjectSkillsSettings.tsx:602-627`) renders options only, so the active `claudeAgent` filter is invisible. The result is "showing 0" and an unselected "Codex 6" chip.
- **"Claude 0" on M5 is mostly true.** Nothing is installed for Claude there. The page still hides the 35 claude.ai-synced skills Claude does load, because `discoverClaudePluginSkills` skips `@synced` by design (`apps/server/src/provider/Drivers/ClaudeSkills.ts:708`). It also gives no hint about how to get skills onto M5.
- **"All environments" on the Skills page is a single-machine read.**
  - `settingsScope.ts:150` makes scope kind `all`. `ProjectSkillsSettings.tsx:101-121` then renders the user-level view of `machine ?? primaryEnvironmentId`, which is the window's own machine.
  - It does not combine machines and never writes anywhere. Writes to other machines happen only through the 1248/1125 "Install on all" / "Push to machines" flow. That flow runs `vskill install <owner/repo/name>@X.Y.Z` on each target over Connect (`apps/server/src/fleet/fleetSkills.ts`), so it fails on a machine without vskill, such as M5 today.

Skills are files on each machine, so "apply to all environments" can only ever mean "copy the same source and version to each machine and report each one".

## Scope

In:

- One Skills page that searches installed skills, connected repos and Obsidian notes.
- Connect a skill repo, public or private.
- Version and Update for each skill, with honest "Use now" readiness.
- An explicit "Also add on" rollout from one source, with "Keep updated on these machines" and a result row for each machine (wording shared with Integrations, 1400).
- Adopting untracked and `npx skills` installs into one lock.
- A generated Obsidian catalog note.
- Fixes for the filter bug, the empty-agent explanation and the misleading "All environments" option on the Skills page.

Out:

- Auto-publishing to verified-skill.com.
- Copying GitHub tokens between machines.
- Changing Usage's "All environments" scope.
- Plugin bundle publishing.
- Editing the claude.ai-synced skills, which are managed on claude.ai.

Gate: AC-01 to AC-03 are local and read-only and may ship now. AC-04 to AC-07 change only the machine they run on. AC-08 to AC-11 write to other machines over Connect and wait for Anton's acceptance of this spec (D-01, D-03).

## Acceptance Criteria

- [ ] AC-01: An Agent, Level or Tier filter value with no matching option on this machine still renders as a selected chip with count 0, so one click clears it. With a filter seeded from the composer link (`?agent=claudeAgent`) on a machine with only Codex skills, the page shows a selected "Claude 0" chip next to "Codex 6", never a hidden filter. Clear filters restores all rows.
- [ ] AC-02: When an agent the machine has reports zero skills, the footer names it and says why, for example "Claude: no skills installed on M5". Skills Claude loads from claude.ai sync are listed read-only with the source "claude.ai", and no toggle or edit is offered. On M5 this shows the 35 synced skills instead of "Claude 0".
- [ ] AC-03: The Skills page shows exactly one machine, with one picker for the whole page and none inside sections. The scope line reads "Set up on [M5 v]", captioned "Each machine keeps its own. Changes here only affect M5." Copy says "machine", never "environment". "All environments" is gone from the Skills page and stays on Usage. A read-only view labelled "Across machines" replaces it. It shows one row per skill and one column per reachable machine, with the version or a status chip in each cell and the time each machine was read. It has no toggles that write to every machine, and it never reports unknown as missing.
- [ ] AC-03a: Each skill uses the status chips shared with Integrations (1400): "On this machine", "Not on M5", "Needs sign-in" (a private repo with no GitHub access) and "Offline". Skills add one more, "Update available x.y.z". Claude.ai-synced and Codex system skills sit in a "Built into the agent" block, which is never installable or editable.
- [ ] AC-04: One search box on the Skills page returns three groups:
  - Installed (any agent, this machine);
  - Available in a connected repo (not installed), with that repo's version;
  - Notes, matching notes in the Obsidian vault when this machine has one.

  Each result opens its detail. A repo result offers Install. A note result opens the note in Obsidian or the file viewer. Nothing is installed by searching.
- [ ] AC-05: "Connect a skill repo" accepts `owner/repo` or a GitHub URL, detects public or private, and lists its skills with `metadata.version` and the source commit.
  - A private repo uses only this machine's existing GitHub sign-in (`gh` or `vskill auth`). Without one, it says "Sign in to GitHub on <machine> to read <repo>", and nothing is sent to verified-skill.com.
  - `anton-abyzov/vskill` and `anton-abyzov/anton-personal-skills` are suggested on first use.
  - Connected repos are saved per machine and listed with Disconnect.
- [ ] AC-06: Each skill row shows the installed version as `metadata.version` plus the short source commit, and the latest version in its source. Two copies with the same version and different content count as different.
  - Update installs the latest from the recorded source with vskill and reads the version back from the lock.
  - Update all updates every outdated, tracked skill on this machine and lists each result.
- [ ] AC-07: After Install or Update, the composer offers the skill at once (`$name`) without restarting the app. Each agent shows a readiness that is read back from that agent's own skill list, never assumed: Loaded now, Next message, or Next session.
- [ ] AC-08 (gated): Rolling out is an explicit action after an install or update, never a scope. The action reads "Also add on: [ ] m4 [ ] linux-mini [ ] m1", the same wording as Integrations. The source is one connected repo at one version. Each checked machine gets that exact version over Connect, through the existing guarded fleet path extended to GitHub sources (owner/repo/name@version and commit), not only registry ones. Skills add an option, "Keep updated on these machines". When it is on, a later Update of the source offers the same machines again, pre-checked, behind one confirmation. Nothing rolls out without that click.
- [ ] AC-09 (gated): Rollout shows one result row per machine: "Added x.y.z", "Updated to x.y.z", "Offline, not added", "No access" (no GitHub access to a private repo), "vskill missing", or "Failed" with the error text. An offline machine is never queued silently. Retry failed skips verified successes. A machine without vskill offers "Install vskill on <machine>" as its own confirmed step.
- [ ] AC-10 (gated): "Adopt" on an untracked or `npx skills`-tracked skill records it in `vskill.lock` with its source when the folder matches a connected repo's skill byte for byte. Otherwise it offers "Add to anton-personal-skills" as a pull request. Adopt never deletes the folder or the old lock entry until the vskill entry reads back.
- [ ] AC-11 (gated): On machines with the vault, a generated note `003 Resources/AI Skills/Skills catalog.md` lists each skill with source repo, version, agents and machines in sync. It is regenerated after installs and marked "generated, edit the source repo instead". Obsidian is an index, never the source.
- [ ] AC-12: Focused tests cover filters, empty-agent states, compare, search groups, repo connect refusal paths, update readback and fleet partial failure. Headless light and dark screenshots at 1440px and 390px cover each new state. `ProjectSkillsSettings.tsx` and `fleetSkills.ts` stay under 1,500 lines by splitting new parts into their own files.

## Approach

**Single source of truth, recommended.**

- **Every skill is authored in a GitHub repo.**
  - Public, reusable skills go in `anton-abyzov/vskill` (`plugins/<plugin>/skills/<name>`, flat folders, name equals folder, `metadata.version`).
  - Private ones go in `anton-abyzov/anton-personal-skills`.
  - Third-party skills stay in their own repos.
- **Every machine installs with vskill.** The canonical folder is `~/.agents/skills`, with Claude links in `~/.claude/skills`. Codex already reads `~/.agents/skills`. One `~/.agents/vskill.lock` records source, version and commit.
- **Obsidian holds a generated catalog**, so search works there too. It is never edited by hand as a source.
- **The Skills page drives the lifecycle**, through vskill and Connect: find, install, update, use now, roll out.

Order of work:

1. T-01, the filter fix, in `ProjectSkillsSettings.tsx`. It is UI only and adds no new phrase.
2. Local read-only gaps: AC-02 and AC-03.
3. Local management: AC-04 to AC-07.
4. Gated fleet work: AC-08 to AC-11.

Reuse the 1248 detail sheet, Available on, Install on all and Compare. Reuse the 1125 `fleet skills` executor. Do not build a second installer. Fleet installs pass a fixed argv. Destinations recheck grants and the expected commit.

Rejected alternatives:

- **Syncing `~/.agents/skills` folders between machines directly** (rsync or Connect file copy). It bypasses the lock, cannot report versions and copies private content blindly.
- **Obsidian as the source.** M5 has no vault, and notes are not installable packages.
- **"All environments" as a write-to-all switch.** Skills are per machine, and a hidden fan-out write is the opposite of what Anton expects.

Risks:

- Claude Code may need a new session for a new skill. AC-07 reports that honestly instead of promising "now".
- Private repo reads on other machines need GitHub auth there (D-03).
- `npx skills` and vskill both write `~/.agents/skills`. Adopt must not fight the other CLI.

## Decisions

### Asked
- none yet (Anton reviews this spec before the gated work)

### Defaulted (change any before sw-do)
- D-02: Install location → `~/.agents/skills` canonical with agent links, the current vskill layout (reversible).
- D-04: "All environments" → removed from the Skills page only and replaced by the read-only "Across machines" view. Usage keeps it. Wording matches 1400: "machine", never "environment".
- D-05: Version → `metadata.version` plus source commit, because vskill installs read GitHub main and the version alone can hide changes.

### Open
- D-01 (Anton): Accept the model "author in two GitHub repos, install with vskill on each machine, sync per skill" before AC-08 to AC-11 start. Recommended: yes.
- D-03 (Anton, auth): Private repo access on other machines. Recommended: sign in to GitHub once on each machine (`gh auth login`), with no token copying. Alternative: publish private skills as `hosted-private` on verified-skill.com and install from there.

## Tasks

### T-01 Show hidden filter values as selected chips
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.test.tsx | Test: from apps/web, `node ../../node_modules/vite-plus/bin/vp test run src/components/settings/ProjectSkillsSettings.logic.test.ts src/components/settings/ProjectSkillsSettings.test.tsx`

### T-02 Explain empty agents and list claude.ai-synced skills read-only
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/ClaudeSkills.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/projectSkillsScan.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.tsx | Test: focused server and web tests with a fixture home that holds only `~/.claude/skills/synced/<id>/<skill>`

### T-03 One machine per page, "Set up on", status chips and the Across machines view
- AC: AC-03, AC-03a | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsScope.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillMachineMatrix.tsx | Test: web tests prove Usage still offers All environments and Skills does not; matrix shows Offline as unknown

### T-04 Unified search and Connect a skill repo
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillRepoSources.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillSearch.tsx, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectSkills.ts | Test: public repo lists skills; private repo without auth refuses with the sign-in message; no request to verified-skill.com for a private repo

### T-05 Version, Update, Update all and Use now readiness
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectSkillsActions.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillDetailPanel.tsx | Test: update reads the new version and commit back from the lock; readiness comes from each agent's list

### T-06 "Also add on" rollout with a result row per machine (gated on D-01, D-03)
- AC: AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/fleetSkills.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/fleetSkillsGithubSource.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectSkillsFleet.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillAvailability.tsx | Test: fleet partial failure, vskill missing, no repo access, retry failed only

### T-07 Adopt untracked skills and generate the Obsidian catalog (gated on D-01)
- AC: AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillAdopt.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillCatalogNote.ts | Test: adopt keeps the folder until the lock reads back; catalog note regenerates and carries the generated marker

### T-08 Verify and close 1399
- AC: AC-12 | Files: .specweave/increments/1399-one-place-to-find-install-update-and-roll-out-skills/reports/ | Test: `specweave verify 1399`, headless screenshots, fresh review, `specweave complete 1399`
