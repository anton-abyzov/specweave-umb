# 0934 Skills consolidation and Studio skills view

## Problem

Claude loads 228 skill entries in this project and real use sits in about 25 (400 Skill-tool calls in 90 days, 42 distinct, top 10 = 75%). 104 entries come from a claude.ai-synced "sw" 1.0.0 plugin dated 2026-03-30 that has served zero invocations, shadows the sw 3.x descriptions, and whose hooks.json calls the removed `specweave hook` command 2,220 times across 91 transcripts. Grok's 124 includes 9 skills from `~/.claude/skills/.trash`, 7 Codex command files and 12 bare-name copies of the sw plugin. SpecWithCode Settings > Skills reproduces its counts exactly (Claude 78, Codex 92, Grok 124, 158 rows, 35 flags) but 17 of the 35 flags are false positives: 6 from Grok `userInvocable:false` mapped to disabled (apps/server/src/provider/Drivers/GrokSkills.ts:85) and 11 from `vskill doctor` redundant-link findings about Cursor, Gemini and OpenCode folders merged by name (apps/server/src/project/projectSkillsInventory.ts:374, 402). 16 SKILL.md files show as 2 or 3 rows (17 phantom rows). The Version column shows the lock version (16 of 17 say 1.0.0) not the SKILL.md version. The 4 "duplicate" rows are sw version skew (Claude 3.0.12 in a folder named 2.1.0, Codex 3.0.20, source 3.0.23). apify-data-gathering is flagged because doctor's NAME_RE rejects the `marketing/` namespaced name the installer writes by design. Plan and evidence: https://claude.ai/artifact/Hto9NvYYpvDDFuGo5SwwxF.

## Scope

In: the Studio skills view fixes, the machine hygiene (plugins off, trash moved, sw plugin updated, umbrella skill copies refreshed, legacy lock entries removed, apify and html-report fixed), the merge map (asc 15 to 9, three single merges, ten video workflows removed, five deprecations) after a 90-day Codex re-check, trigger phrases for 14 skills, republish and relock of edited skills, AGENTS.md trimmed. Out: changing the specweave plugin generator (it forbids a `name:` field by design), the doctor NAME_RE change (0932 T-05), removing any skill with Codex use in the last 90 days.

## Acceptance Criteria

- [ ] AC-01: Studio joins presences by canonical file (realpath) before name, so apify-data-gathering, nanobanana and the 12 sw plugin skills each show as one row with the other providers' names as aliases; the phantom-row count on the specweave cwd is 0.
- [ ] AC-02: Doctor findings count toward attention only when their agents or paths belong to a provider in the snapshot; Grok `userInvocable:false` keeps `enabled: true` with a `userInvocable` flag; entries under a dot-segment path (`/.trash/`, `/.root-owned-*`) and non-SKILL.md command files are dropped from provider catalogs; Studio's identical-copy rule and doctor's agree.
- [ ] AC-03: The Skills table shows the SKILL.md version beside the lock version with a "lock out of date" hint when they differ, and for plugin presences the plugin manifest version per provider; "duplicate" with different versions reads "different versions"; Level is normalised by path (`*/plugins/cache/*` is Plugin) and Bundled and System have labels; legacy-lock entries with nothing on disk show as "stale lock entry" without attention.
- [ ] AC-04: Running the repro script (`scratchpad/studio-skills-ui/repro.ts`, moved into the repo as a test fixture runner) on the specweave cwd reports at most 12 attention rows, all real.
- [ ] AC-05: On this Mac the synced "sw", marketing and cowork-plugin-management org plugins and the three org skill copies are off, `~/.claude/skills/.trash` is outside the skills tree, the Claude sw plugin is 3.0.23, the umbrella `.claude/skills` entries are symlinks to `.agents/skills` with the retired sw-brainstorm and sw-team gone, the two legacy lock entries are removed, and `vskill doctor --json` reports no bad-name, bad-description or identical-copy finding.
- [ ] AC-06: A 90-day Codex re-check (find -L over ~/.codex/sessions, including the external archive) is recorded per candidate; only candidates with zero Claude calls and zero Codex reads are removed; the removals, merges and deprecations from the merge map are applied, each merged skill's content is folded into its target with the target's trigger phrase extended, and `vskill doctor` is clean afterwards.
- [ ] AC-07: The 14 user skills without a "Use when" trigger have one, remotion-best-practices has a real description, html-report's description is at most 1,024 characters; obsidian-brain, social-media-posting and every edited skill are republished through vSkill and relocked (lock sha equals disk); personal forks are relocked without republishing (D-03).
- [ ] AC-08: Umbrella AGENTS.md has no "Available Subagent Types" section, the Jev table is at most 6 rows, and the SpecWeave procedure text is at most 1.2k tokens measured by `wc -c` divided by 4.

## Approach

Studio work in one worktree off main (one PR): `projectSkillsInventory.ts` groups by `realPath` from `input.files` and picks the display name (Claude folder or plugin name, else lock key, else frontmatter), `parseVskillDoctorReport` keeps `kind`, `agents` and `paths`, `buildProjectSkillRows` filters findings to snapshot providers, `GrokSkills.ts` maps `userInvocable`, `projectSkillsScan.ts readSkillFileFacts` parses the frontmatter version and reads a sibling plugin.json, `ProjectSkillsSettings.tsx` renders the extra columns, `ProjectSkillsSettings.logic.ts` normalises Level. Machine hygiene and the merge map run on this Mac in the umbrella, recorded in `reports/`. Rejected: adding `name:` to the plugin source (generate-skills.mjs throws on it). Risk: turning off the synced plugin is a claude.ai org setting; EasyChamp's closure flow uses an older local cache plugin, not the synced one, so it is unaffected.

## Decisions

- D-01 Removals are deletions on this Mac, approved by the owner on 2026-10-18 (D3); every removed skill is reinstallable through vSkill or the hyperframes router.
- D-02 sw-team and sw-brainstorm are retired in the catalog and never recommended.
- D-03 AC-07's republish clause excludes the personal forks obsidian-brain and kie-gemini-omni: they hold the owner's email, vault paths and private workflow. The owner delegated the call on October 20, 2026 and the safe default was taken: they stay unpublished, obsidian-brain is relocked to its disk copy and pinned at 1.1.0, kie-gemini-omni is in no lock (see reports/relock.md).

## Open questions

- Which tool rewrote three heygen SKILL.md files on 2026-10-14 without updating the lock (check `vskill doctor` after relock).

## Tasks

### T-01 Join by file, filter doctor, Grok flags, junk filter
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/project/projectSkillsInventory.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/projectSkillsScan.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/Drivers/GrokSkills.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/projectSkills.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/__tests__/projectSkillsInventory.test.ts | Test: cd repositories/anton-abyzov/specweave-studio && npx vitest run apps/server/src/project/__tests__/projectSkillsInventory.test.ts

### T-02 Versions, levels and labels in the table
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/project/projectSkillsScan.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/projectSkills.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProjectSkillsSettings.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProjectSkillsSettings.logic.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProjectSkillsSettings.logic.test.ts | Test: cd repositories/anton-abyzov/specweave-studio && npx vitest run apps/web/src/components/settings/ProjectSkillsSettings.logic.test.ts

### T-03 Attention count on the specweave cwd
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/server/scripts/skills-attention-report.ts, .specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/attention-after.md | Test: cd repositories/anton-abyzov/specweave-studio && npx tsx apps/server/scripts/skills-attention-report.ts ../specweave | grep -qE 'attention ([0-9]|1[0-2])$'

### T-04 Machine hygiene
- AC: AC-05 | Files: .specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/hygiene.md, .claude/skills/, .agents/skills/ | Test: vskill doctor --json | jq -e '[.issues[]|select(.kind=="bad-name" or .kind=="bad-description" or .kind=="identical-copy")]|length==0' && test ! -d ~/.claude/skills/.trash

### T-05 Codex re-check and the merge map
- AC: AC-06 | Files: .specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/codex-90d.md, .specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/merge-map-applied.md | Test: vskill doctor --json | jq -e '.issues|length==0' && test ! -d ~/.agents/skills/asc-build-lifecycle

### T-06 Triggers, descriptions, republish and relock
- AC: AC-07 | Files: .specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/relock.md | Test: cd ~/.agents && vskill outdated --json | jq -e '[.[]|select(.warning)]|length==0'

### T-07 Trim AGENTS.md
- AC: AC-08 | Files: AGENTS.md | Test: ! grep -q 'Available Subagent Types' AGENTS.md && test $(wc -c < AGENTS.md) -lt 9000
