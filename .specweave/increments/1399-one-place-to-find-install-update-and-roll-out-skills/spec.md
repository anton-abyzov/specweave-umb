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
- **"Claude 0" on M5 is mostly true.** Nothing is installed for Claude there. The page still hides the 35 claude.ai-synced skills Claude does load, because the user-skill scan reads only `~/.claude/skills/<name>/SKILL.md`, one level deep (`apps/server/src/provider/Drivers/ClaudeSkills.ts:866`), so `synced/<id>/<name>` is never reached. Separately, `@synced` plugins are skipped by design (`ClaudeSkills.ts:708`). It also gives no hint about how to get skills onto M5.
- **"All environments" on the Skills page is a single-machine read.**
  - `settingsScope.ts:150` makes scope kind `all`. `ProjectSkillsSettings.tsx:101-121` then renders the user-level view of `machine ?? primaryEnvironmentId`, which is the window's own machine.
  - It does not combine machines and never writes anywhere. Writes to other machines happen only through the 1248/1125 "Install on all" / "Push to machines" flow. That flow runs `vskill install <owner/repo/name>@X.Y.Z` on each target over Connect (`apps/server/src/fleet/fleetSkills.ts`). On a machine without vskill, such as M5 today, it falls back to `npx --yes vskill@latest` (`fleetSkills.ts:269`). That needs Node and network on the target, and the target runs whatever vskill is latest.

Skills are files on each machine, so "apply to all environments" can only ever mean "copy the same source and version to each machine and report each one".

## Scope

In:

- One Skills page that searches installed skills, connected repos and Obsidian notes.
- Connect a skill repo, public or private.
- Version and Update for each skill, with honest "Use now" readiness.
- An explicit "Also add on" rollout from one source, with "Keep updated on these machines" and a result row for each machine (wording shared with Integrations, 1402 D-03).
- Adopting untracked and `npx skills` installs into one lock.
- A generated Obsidian catalog note.
- Fixes for the filter bug, the empty-agent explanation and the misleading "All environments" option on the Skills page.

Out:

- Auto-publishing to verified-skill.com.
- Copying GitHub tokens between machines.
- Changing Usage's "All environments" scope.
- Plugin bundle publishing.
- Editing the claude.ai-synced skills, which are managed on claude.ai.

Gate: Anton approved everything on November 18, 2026 (D-01, D-03, D-06, D-07), so every AC may ship. AC-01 to AC-03 are local and read-only. The review of November 18, 2026 (`reports/review-muse-wonder-full-1.0.md`, verdict SHIP after listed fixes) is folded in below. AC-04 to AC-07 change only the machine they run on. AC-08 to AC-11 write to other machines over Connect and wait for Anton's acceptance of this spec (D-01, D-03).

## Acceptance Criteria

- [ ] AC-01: An Agent, Level or Tier filter value with no matching option on this machine still renders as a selected chip with count 0, so one click clears it. With a filter seeded from the composer link (`?agent=claudeAgent`) on a machine with only Codex skills, the page shows a selected "Claude 0" chip next to "Codex 6", never a hidden filter. The chip uses the agent's display name ("Claude"), never the raw id (`claudeAgent`). The filter row also renders when the machine has zero rows but a filter is active, since today it is gated on `rows.length > 0` (`ProjectSkillsSettings.tsx:975`). Clear filters restores all rows.
- [ ] AC-02: When an agent the machine has reports zero skills, the footer names it and says why, for example "Claude: no skills installed on M5". Skills Claude loads from claude.ai sync are listed read-only with the source "claude.ai", and no toggle or edit is offered. On M5 this shows the 35 synced skills instead of "Claude 0".
- [ ] AC-03: The Skills page shows exactly one machine, with one picker for the whole page and none inside sections. The picker is the shared `SettingsScopeSentence.tsx`, so it needs a per-page option that hides "All environments" for Skills only. The scope line reads "Set up for [firstproject v] on [M5 v]" (Skills is project-scoped in `settingsPageScope.ts`; the user level reads "Set up for [All projects v] on [M5 v]"), captioned "Each machine keeps its own. Changes here only affect M5." Copy says "machine", never "environment". "All environments" is gone from the Skills page and stays on Usage. A read-only view labelled "Across machines" replaces it. It shows one row per skill and one column per reachable machine, with the version or a status chip in each cell and the time each machine was read. It reuses the per-machine reads behind 1248's "Available on" and does not add a second fleet read. It has no toggles that write to every machine, and it never reports unknown as missing.
- [ ] AC-03a: Each skill uses the status chips shared with Integrations (1402, D-03): "On this machine", "Not on M5", "Needs sign-in" (a private repo with no GitHub access) and "Offline". Skills add one more, "Update available x.y.z". Claude.ai-synced and Codex system skills sit in a "Built into the agent" block, which is never installable or editable.
- [ ] AC-04: One search box on the Skills page returns three groups:
  - Installed (any agent, this machine);
  - Available in a connected repo (not installed), with that repo's version;
  - Notes, matching notes in the Obsidian vault when this machine has one.

  Each result opens its detail. A repo result offers Install. A note result opens the note in Obsidian or the file viewer. Nothing is installed by searching.
- [ ] AC-05: "Connect a skill repo" accepts `owner/repo` or a GitHub URL, detects public or private, and lists its skills with `metadata.version` and the source commit.
  - A private repo uses only this machine's existing GitHub sign-in through `gh`. `vskill auth` signs in to verified-skill.com and is not a GitHub read path. Without one, it says "Sign in to GitHub on <machine> to read <repo>", and nothing is sent to verified-skill.com.
  - `anton-abyzov/vskill` and `anton-abyzov/anton-personal-skills` are suggested on first use.
  - Connected repos are saved per machine and listed with Disconnect.
- [ ] AC-06: Each skill row shows the installed version as `metadata.version` plus the short source commit, and the latest version in its source. Two copies with the same version and different content count as different.
  - Update installs the latest from the recorded source with vskill and reads the version back from the lock.
  - Update all updates every outdated, tracked skill on this machine and lists each result.
- [ ] AC-07: After Install or Update, the composer offers the skill at once (`$name`) without restarting the app. Each agent shows a readiness, never assumed: Loaded now, Next message, or Next session. Codex is read back from its app-server skills probe (`CodexDriver.ts:331`). Claude has no live probe, because the app mirrors its folders (`ClaudeSkills.ts:16`), so Claude shows "Next session" unless a running session reports the skill. This extends 1248 AC-06's installed-versus-ready readback and does not replace it.
- [ ] AC-08: Rolling out is an explicit action after an install or update, never a scope. The action reads "Also add on: [ ] m4 [ ] linux-mini [ ] m1", the same wording as Integrations. The source is one connected repo at one version. Each checked machine gets that exact version over Connect, through the existing guarded fleet path. That path is extended to GitHub sources, which today pass only the registry gate (`ProjectSkillsFleet.ts:148`). A GitHub source carries `expectedHash`, the normalized content hash the destination already checks (`fleetSkills.ts:68`), plus the source commit as a new contract field. The destination refuses unless the same repo is connected there. The argv stays fixed. Skills add an option, "Keep updated on these machines". It is stored on the machine that made the change, as one record per skill (source repo, skill, scope user or project, machine list), in that machine's SpecWithCode settings, and is never pushed to the other machines. When it is on, a later Update of the source offers the same machines again, pre-checked, behind one confirmation. Nothing rolls out without that click.
- [ ] AC-09: Rollout shows one result row per machine: "Added x.y.z", "Updated to x.y.z", "Offline, not added", "No access" (no GitHub access to a private repo), "Added via npx vskill" (vskill not installed; ran `npx --yes vskill@latest`), "vskill and npx missing", or "Failed" with the error text. An offline machine is never queued silently. Retry failed skips verified successes. Installing vskill on another machine is out of scope until Anton decides it (D-06).
- [ ] AC-10: "Adopt" on an untracked or `npx skills`-tracked skill records it in `vskill.lock` with its source when the folder matches a connected repo's skill under the same normalized content match the fleet path uses (`fleetSkills.ts:68`). That way, legitimate `--copy` installs with Claude-only fields stripped still match. After the vskill entry reads back, Adopt removes that skill's entry from `~/.agents/.skill-lock.json`, so only one CLI owns the folder. It never deletes the folder. A skill that matches nothing offers "Add to anton-personal-skills", which opens a pull request: an outward GitHub write that needs its own confirmation each time (D-07).
- [ ] AC-11: On machines with the vault, a generated note `003 Resources/AI Skills/Skills catalog.md` lists each skill with source repo, version, agents and machines in sync. It is regenerated after installs and marked "generated, edit the source repo instead". Obsidian is an index, never the source.
- [ ] AC-12: Focused tests cover filters, empty-agent states, compare, search groups, repo connect refusal paths, update readback and fleet partial failure. Headless light and dark screenshots at 1440px and 390px cover each new state. `ProjectSkillsSettings.tsx` and `fleetSkills.ts` stay under 1,500 lines by splitting new parts into their own files.

## Approach

**Single source of truth, recommended.**

- **Every skill is authored in a GitHub repo.**
  - Public, reusable skills go in `anton-abyzov/vskill` (`plugins/<plugin>/skills/<name>`, flat folders, name equals folder, `metadata.version`).
  - Private ones go in `anton-abyzov/anton-personal-skills`.
  - Third-party skills stay in their own repos.
- **Every machine installs with vskill.** The canonical folder is `~/.agents/skills`, with Claude links in `~/.claude/skills`. On m4, Codex's own skills probe listed 84 skills on October 27, 2026, while `~/.codex/skills` holds 2, so Codex appears to load `~/.agents/skills`. Confirm this on M5 after the first install (T-02 test). If it fails, install with `vskill --agent codex --copy`. Windows and m1 symlink behaviour must be checked before rollout there. One `~/.agents/vskill.lock` records source, version and commit.
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
- D-01 → yes. Anton approved the model on November 18, 2026: author skills in two GitHub repos, install them with vskill on each machine, and roll out with "Also add on". AC-08 to AC-11 are no longer gated.
- D-03 → sign in to GitHub once on each machine (`gh auth login`), with no token copying (Anton, November 18, 2026). Signing in stays Anton's step on each machine.
- D-06 → no. SpecWithCode never installs vskill on another machine. It keeps the `npx --yes vskill@latest` fallback and shows "Added via npx vskill" (Anton, November 18, 2026).
- D-07 → yes. "Add to anton-personal-skills" may open a pull request, with a confirmation each time and no auto-merge (Anton, November 18, 2026).

### Defaulted (change any before sw-do)
- D-02: Install location → `~/.agents/skills` canonical with agent links, the current vskill layout (reversible).
- D-04: "All environments" → removed from the Skills page only and replaced by the read-only "Across machines" view. Usage keeps it. Wording matches 1402 D-03: "machine", never "environment".
- D-05: Version → `metadata.version` plus source commit, because vskill installs read GitHub main and the version alone can hide changes.

### Open
- none

## Tasks

### T-01 Show hidden filter values as selected chips
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.test.tsx | Test: from apps/web, `node ../../node_modules/vite-plus/bin/vp test run src/components/settings/ProjectSkillsSettings.logic.test.ts src/components/settings/ProjectSkillsSettings.test.tsx`

### T-02 Explain empty agents and list claude.ai-synced skills read-only
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/ClaudeSkills.ts (add a `synced/<id>` scan root with source claude.ai), repositories/anton-abyzov/specwithcode/packages/contracts/src/projectSkills.ts (synced source marker), repositories/anton-abyzov/specwithcode/apps/server/src/project/projectSkillsScan.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.tsx | Test: focused server and web tests with a fixture home that holds only `~/.claude/skills/synced/<id>/<skill>`

### T-03 One machine per page, "Set up on", status chips and the Across machines view
- AC: AC-03, AC-03a | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsScope.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/SettingsScopeSentence.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillMachineMatrix.tsx | Test: web tests prove Usage still offers All environments and Skills does not; matrix shows Offline as unknown

### T-04 Unified search and Connect a skill repo
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillRepoSources.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillSearch.tsx, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectSkills.ts | Test: public repo lists skills; private repo without auth refuses with the sign-in message; no request to verified-skill.com for a private repo

### T-05 Version, Update, Update all and Use now readiness
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectSkillsActions.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillDetailPanel.tsx | Test: update reads the new version and commit back from the lock; readiness comes from each agent's list

### T-06 "Also add on" rollout with a result row per machine
- AC: AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/fleetSkills.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/fleetSkillsGithubSource.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectSkillsFleet.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillAvailability.tsx | Test: fleet partial failure, vskill missing, no repo access, retry failed only

### T-07 Adopt untracked skills and generate the Obsidian catalog
- AC: AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillAdopt.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillCatalogNote.ts | Test: adopt keeps the folder until the lock reads back; catalog note regenerates and carries the generated marker

### T-08 Verify and close 1399
- AC: AC-12 | Files: .specweave/increments/1399-one-place-to-find-install-update-and-roll-out-skills/reports/ | Test: `specweave verify 1399`, headless screenshots, fresh review, `specweave complete 1399`

## Delivery lanes (November 18, 2026)

Each lane opens its own PR from its own worktree. Lanes A and B own disjoint new files. Each one rebases on main before merging.

- **Lane A** (T-02, T-03, after T-01 merges): the read-only page. It owns `ProjectSkillsSettings.tsx`, `SettingsScopeSentence.tsx`, `settingsScope.ts`, `ClaudeSkills.ts` and `packages/contracts/src/projectSkills.ts`.
- **Lane B** (T-04, T-05): local management. It owns the new `packages/contracts/src/projectSkillRepos.ts`, `apps/server/src/project/SkillRepoSources.ts`, `apps/web/src/components/skills/SkillSearch.tsx` and `SkillUpdate*`. It mounts its UI with one slot in `ProjectSkillsSettings.tsx` after Lane A merges.
- **Lane C** (T-06, T-07, after Lane B merges): fleet rollout, Adopt and the catalog note. After release it runs live acceptance: it adopts on m4 and adds the vskill skills on M5 with "Also add on".
