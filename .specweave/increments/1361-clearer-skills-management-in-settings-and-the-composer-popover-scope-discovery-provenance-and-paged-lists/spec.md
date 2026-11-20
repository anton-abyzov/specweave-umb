# Clearer skills management in Settings and the composer popover: scope, discovery, provenance and paged lists

## Problem

Two screens answer "which skills does this agent have here" and both leave the answer unclear.

Composer popover (screenshot 2, GitHub Copilot, 12 skills): every row reads `untracked` with an `Agent` badge under a group named "Other". The skills are real: Copilot advertises them as ACP commands (`acp://command/<name>`, scope `agent`), and the popover joins a row to the folder inventory by exact file path, which an advertised command never has. So scope, version and provenance are all lost, and "untracked" reads as "not installed properly". On the machine where this was seen, `obsidian-brain` is a project-scoped vskill install at 1.0.12 with a lock entry; the popover shows none of that.

Settings > Skills, "Across machines" (screenshot 1): a long flat list with no search and no paging; a current-machine cell reads "On this machine" plus "Added"; an unread machine reads "Not checked" with the reason only in a header that scrolls away; a skill built into one agent reads "Not on <machine>" on a machine whose agent does not ship it, a gap nobody can fill.

Underneath both:

- For Gemini CLI and Copilot CLI the server replaces the agent's own list with a scan of the folders that CLI reads. Settings then shows the agent as loading a skill the agent does not list (seen: 13 names in Copilot's folders, 12 listed by Copilot), and drops a skill the agent lists from a folder the app does not scan.
- That scan keeps the first copy of a name, project first, so a separate user-level copy of the same skill is invisible. A person cannot tell "no user-level copy" from "the app did not look".
- Nothing separates "the agent was read and does not have it" from "the agent was not read" at the row level; the provider states sit in a footnote under the table.
- Long inventories (70+ rows with claude.ai and system skills) render in full in both places.

## Scope

In: the composer skills popover and Settings > Skills ("On <machine>" table, "Built into the agent" block, "Across machines" matrix): scope, provider discovery, provenance, machine and unknown-versus-absent made explicit; search over the whole inventory before paging; an additive, optional server field for discovery and for lower-priority copies; focused tests; headless screenshots on synthetic data; a read-only reconciliation report of the real inventory on the machine where the screenshots were taken.

Out: installing, removing, promoting or re-scoping any skill; changes to vskill; the files increment 1360 lists (`ProjectSkillsActions*`, `SkillUpdate*`, `vskillTool*`, `processRunner.ts`); the Skills search/install panel (`SkillSearch`, `SkillUpdatePanel`); mobile; fixing the installed `obsidian-brain` copy.

## Acceptance Criteria

- [ ] AC-01: In the popover, a skill whose file path the agent reported (Claude, Codex and others) shows that file's scope, version and lock. A skill the agent only advertises as a command (`acp://` path) is matched to the files the app found for the same agent instance under that name, compared without regard to case so that two files differing only in case show as several matching files instead of one, and the row says so: "Matching file · v1.0.12" with the lock source when a lock of that scope lists it, else "no lock entry". The word "untracked" and the "Agent" badge are gone.
- [ ] AC-02: In the popover, an advertised skill with no matching file reads "Location unknown" and has no Settings link; it is never shown as absent or given a scope. With more than one matching file the row reads "2 matching files" and names each scope; it never picks one. While the folder inventory is loading rows read "Checking…"; after it failed they carry no scope claim.
- [ ] AC-03: No screen claims an agent does not list a skill. A copy the app found by scanning an agent's folders (Gemini CLI, Copilot CLI) is marked "found in a scanned folder" on its agent badge in Settings, with the hint that the agent's own list is not checked per folder. The popover's source line says, for an agent with one machine-wide list, that the list is the agent's own for this machine and is not checked for this folder.
- [ ] AC-04: A second file with the same name in a lower-priority folder (for example a user-level copy behind a project copy) is reported, not dropped: Settings names every scope on the row and the detail hint lists the other files as "also found", stating that the order is the app's scan order and that the agent does not report which copy it uses. Extra copies change no status, attention, drift, lock or copy count. With one copy, nothing extra appears.
- [ ] AC-05: Popover header states the agent, the machine and the folder, and one line says where the list comes from.
- [ ] AC-06: Popover search matches against every skill, then the result is paged (20 per page) with "a–b of n", Previous and Next; group headings show the group's total, not the page's slice; a new query returns to page 1; a rescan that shrinks the list clamps the page.
- [ ] AC-07: Settings "On <machine>" table: search and chips filter the whole inventory, then rows are paged (25 per page, with 50 and 100 offered); the summary states matches and the visible range; the "Built into the agent" block is paged the same way; changing a filter returns to page 1; a skill linked from the popover opens its sheet whatever page or filter it sits behind.
- [ ] AC-08: Settings shows, above the table, the machine and the read time, and one line per agent that was not fully read (timed out, failed, cached, partly read) or that keeps one machine-wide list, with what that means for absence. The Scope column names each level a copy sits at; the Source column reads "No lock entry" for a skill no vskill lock lists, instead of a dash.
- [ ] AC-09: "Across machines": a search box filters every skill before paging (25 per page); every machine's cell, the current one included, reads its version or "Installed" with its scope, and no "Added"; an unread machine's cells carry the reason (Offline, Reading…, No project there, Could not be read, Scan incomplete, Needs sign-in), not "Not checked"; a skill built into an agent reads "Not reported here" on a machine without it, never "Not on <machine>".
- [ ] AC-10: Version skew is safe both ways: a payload without the new optional fields renders as before with no discovery wording, and a payload with them decodes on the current schemas. A folder scan the app could not finish for an agent marks that agent's read incomplete, so absence there reads unknown on old and new clients.
- [ ] AC-11: A reconciliation report for the machine in the screenshots records, read-only: the lock entry, each on-disk copy and its hash, every user-level root as "folder absent" or "folder present, skill not in it", which Copilot instance uses which home, and what stays unverified. Nothing is installed, removed or moved.
- [ ] AC-12: Focused web and server tests cover AC-01 to AC-10; headless screenshots of both screens on synthetic data (neutral machine and skill names) are saved and opened; an independent adversarial review by codex `gpt-6.2-sol` covers this design and then the final patch, with findings rechecked.

## Approach

Work happens in a scratch clone of the app on branch `1361-clearer-skills-management` from `origin/main`; the shared checkout stays on 1360's branch untouched.

1. Contracts (`projectSkills.ts`, `server.ts`), all optional and display-only, no existing field or enum value changes:
   - `discovery: "folder-scan"` on `ServerProviderSkill` and `ProjectSkillPresence`: the app found this file by scanning the folders this agent reads; the agent did not report it. Absent: the agent's own report, or an older machine.
   - `otherCopies: { path, scope }[]` on both: files with the same name the scan found in lower-priority folders.
2. Server: `scanSkillRoots` also returns the copies it used to drop (`shadowed`), without changing `skills`. `applyNativeSkillSwitches` (Gemini, Copilot) tags scanned skills, attaches `otherCopies`, and reports a scan that could not finish; the service then sets the existing `incomplete` flag on that agent's state. `buildProjectSkillRows` copies the two fields onto the presence and uses them in no calculation.
3. Web logic, pure and tested first: a shared `paginate` helper (`lib/pagination.ts`); `ComposerSkillsPopover.logic.ts` gains the confirmed-path join, the same-instance name match (case-insensitive) shown as matching files, provenance and paging; `ProjectSkillsSettings.logic.ts` gains scope and discovery labels and the agent read-state lines; `SkillMachineMatrix.logic.ts` gains cell reasons, scope, the built-in rule and search.
4. Web components: popover rows become two lines (name and badges; version, provenance, note). Settings table, built-in block and matrix get a shared `SkillsPager`. `ProjectSkillsSettings.tsx` is at 1,330 of 1,500 lines, so the table and its cells move to `components/skills/SkillsTable.tsx` before anything is added.
5. Evidence: a new headless fixture `apps/web/tests/skills-clarity` (popover and Settings, synthetic data, 70+ skills) with a `verify.mjs` that waits for animations, asserts the texts and writes PNGs outside the repository; extend `skills-machines` for the matrix.

Rejected: a "not listed by the agent" claim (design review round 1: an ACP agent's command list is instance-wide, probed at the server's own folder, and can be partial, so nothing proves what it lists for a folder); showing advertised skills without a file as Settings rows (no file, so no detail target); adding lower-priority copies as presences (they would feed lock selection, drift and status); removing the folder scan for Copilot (versions and switches depend on it).

Risks: a name match is not proof of the copy an agent uses, so matches are labelled as matches and never resolved; older machines send no field (AC-10).

## Decisions

### Asked
- D-01: Reviewer is exactly codex `gpt-6.2-sol`, for the design and for the final patch; no substitute (user).
- D-02: Reconcile the real inventory read-only; never assume absence, never reinstall or change scope silently (user).
- D-03: Evidence uses synthetic data only (user).
- D-04: 1360 is separate and must be preserved (user).

### Defaulted (change any before sw-do)
- D-05: Work in a scratch clone under the app's scratch folder, because the one shared checkout holds 1360's open branch and worktrees are off for this project. Removed once the PR merges or closes.
- D-06: Page sizes: popover 20; Settings table and matrix 25 (50 and 100 offered in the table); built-in block 25.
- D-07: Skills an agent advertises without a file stay out of the Settings table; the popover shows them as "Location unknown" rows without a Settings link (design review round 1, finding 5).
- D-08: "untracked" is replaced by separate facts: version ("no version" when a file states none) and lock ("No matching lock entry" or the lock's source).
- D-10: "Not listed by the agent" is out of scope until an agent can report a fresh, complete list for a folder (design review round 1, finding 1).
- D-09: No release or merge decision is taken by this increment's worker beyond opening the PR; the repository rule "merge green PRs" applies after review passes.

### Open
- none

## Review
Independent adversarial review: codex/gpt-6.2-sol, explicitly requested, for the design (this spec) and the final patch. No substitution if unavailable.

## Tasks

### T-01 Reconcile the real inventory, read-only
- AC: AC-11 | Files: .specweave/increments/1361-clearer-skills-management-in-settings-and-the-composer-popover-scope-discovery-provenance-and-paged-lists/reports/ | Test: test -s .specweave/increments/1361-clearer-skills-management-in-settings-and-the-composer-popover-scope-discovery-provenance-and-paged-lists/reports/inventory-reconciliation.md

### T-02 Design review by gpt-6.2-sol
- AC: AC-12 | Files: .specweave/increments/1361-clearer-skills-management-in-settings-and-the-composer-popover-scope-discovery-provenance-and-paged-lists/reports/ | Test: test -s .specweave/increments/1361-clearer-skills-management-in-settings-and-the-composer-popover-scope-discovery-provenance-and-paged-lists/reports/sol-design-review.md

### T-03 Discovery and lower-priority copies from the server
- AC: AC-03, AC-04, AC-10 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectSkills.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/CursorSkills.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/projectSkillsNativeOverlay.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/projectSkillsNativeOverlay.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/projectSkillsInventory.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/projectSkillsInventory.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectSkillsService.ts | Test: focused projectSkillsNativeOverlay, projectSkillsInventory and CursorSkills suites

### T-04 Popover: join, discovery, provenance and paging
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/lib/pagination.ts, repositories/anton-abyzov/specwithcode/apps/web/src/lib/pagination.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ComposerSkillsPopover.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ComposerSkillsPopover.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ComposerSkillsPopover.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ComposerSkillsPopover.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillsPager.tsx | Test: focused ComposerSkillsPopover and pagination suites run from apps/web with --project unit

### T-05 Settings table: scope, source, agent read lines and paging
- AC: AC-03, AC-04, AC-07, AC-08, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillsTable.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillsBuiltIn.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillsReadState.tsx | Test: focused ProjectSkillsSettings suites run from apps/web with --project unit

### T-06 Across machines: search, paging, reasons and the built-in rule
- AC: AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillMachineMatrix.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillMachineMatrix.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillMachineMatrix.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillMachineMatrix.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillStatusChip.tsx | Test: focused SkillMachineMatrix suites run from apps/web with --project unit

### T-07 Headless screenshots on synthetic data
- AC: AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/skills-clarity/, repositories/anton-abyzov/specwithcode/apps/web/tests/skills-machines/, .specweave/increments/1361-clearer-skills-management-in-settings-and-the-composer-popover-scope-discovery-provenance-and-paged-lists/reports/ | Test: node apps/web/tests/skills-clarity/verify.mjs writes the PNGs and exits 0

### T-08 Final patch review by gpt-6.2-sol, verify and hand over
- AC: AC-12 | Files: .specweave/increments/1361-clearer-skills-management-in-settings-and-the-composer-popover-scope-discovery-provenance-and-paged-lists/reports/ | Test: test -s .specweave/increments/1361-clearer-skills-management-in-settings-and-the-composer-popover-scope-discovery-provenance-and-paged-lists/reports/sol-patch-review.md
