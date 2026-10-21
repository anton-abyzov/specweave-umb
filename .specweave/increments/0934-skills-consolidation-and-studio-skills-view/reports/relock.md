---
title: 0934 T-06 triggers, descriptions, republish and relock (AC-07)
date: 2026-10-19
---

# Triggers, descriptions, republish and relock

## Trigger phrases

The October 18 inventory flagged 14 user-level entries without a "Use when" trigger. State now:

| Skill | Result |
|---|---|
| frontend-design | trigger added (local; source anthropics/skills via the `skills` CLI) |
| webapp-testing | trigger added (local; source anthropics/skills) |
| unslop | trigger added (local; source cursor/plugins; the skill sets `disable-model-invocation: true`) |
| jev-browser-use | trigger added (local; source wy-coliney/jev-browser-use) |
| motion-graphics | upstream heygen copy now opens with "Use when"; no edit needed |
| remotion-best-practices | real description with a "Use when" trigger (was "Router for all Remotion skills", 30 characters) |
| asc-whats-new-writer | restored October 20 (2 Codex reads in 90 days, see merge-map-applied.md); "Use when writing or localizing App Store release notes or What's New text." added to its own description |
| music-to-video, pr-to-video, remotion-to-hyperframes, slideshow, talking-head-recut | removed (zero Claude calls and zero Codex reads in 90 days, see codex-90d.md) |
| import-memory | claude.ai built-in synced skill, not editable here (Grok-only listing) |
| postiz:postiz | Grok plugin entry, not a user skill file |

A fresh scan of every SKILL.md under `~/.agents/skills`, `~/.claude/skills` and `~/.codex/skills` finds a trigger phrase in each description except reverse-engineer-anything, which REA's installer owns (see merge-map-applied.md).

## Descriptions

- html-report: `vskill update html-report --global --agent claude-code --agent codex` brought the published 1.1.3 (description 983 characters, limit 1,024). The plain update failed on `~/.gemini/antigravity/skills`, a symlink to `~/.gemini/config/skills` that vSkill refuses to write through.
- remotion-best-practices: description rewritten (254 characters).
- social-media-posting: the owner's name removed from the description ("Anton's single skill" to "One skill").

## Republish and relock

Lock: `~/.agents/vskill.lock`. "match" compares the lock `sha` with sha256 of the normalised SKILL.md on disk, the value vSkill writes at install.

| Skill | Published before | Action | Lock sha equals disk |
|---|---|---|---|
| social-media-posting | public repo anton-abyzov/social-media-posting-skill (registry `anton-abyzov/social-media-posting-skill/social-media-posting-skill`, CERTIFIED 1.2.2); the disk folder is a checkout of that repo | commit 2b25fe6 pushed to that repo's main (version 1.3.1, description scrubbed); `vskill submit anton-abyzov/social-media-posting-skill --skill social-media-posting-skill --path SKILL.md`; lock entry repointed from the generic vskill copy to that repo | yes (a3d5c75a) |
| html-report | public anton-abyzov/vskill | updated to the published 1.1.3, no local edit left | yes (3cc9fb0d) |
| webapp-testing | third party, anthropics/skills | `version: "1.0.0"` added (disk version was unreadable), lock sha set to disk, `pinnedVersion: "1.0.0"` so `vskill update` keeps the local trigger | yes (659c196e) |
| unslop | third party, cursor/plugins | same as webapp-testing | yes (c2f69a3a) |
| rea, dcfc-inquiry-replies | unchanged | none | yes |
| apify-data-gathering | public anton-abyzov/vskill | not edited; the lock holds the upstream sha and the installer rewrites `name:` to `marketing/apify-data-gathering` by design | lock equals upstream |
| obsidian-brain | public anton-abyzov/vskill (generic template, registry 1.0.13) | not republished (personal fork, see below); lock sha set to disk, version and `pinnedVersion` 1.1.0, so `vskill update` keeps the fork | yes (e0710892) |
| kie-gemini-omni | public anton-abyzov/vskill (registry 1.0.1); not in any lock | not republished (personal fork, see below) | not locked |

The social-media-posting submission returned the existing May 14 submission (state PUBLISHED, version 1.2.2) instead of scanning 1.3.1; the registry does not rescan a repo it already knows. That is the 0932 vSkill publish loop, not a setting.

Skills edited locally whose source belongs to someone else and that only the `skills` CLI tracks (`~/.agents/.skill-lock.json`): frontend-design, remotion-best-practices, jev-browser-use, asc-cli-usage (asc-id-resolver merge), asc-whats-new-writer (trigger), kie-gemini-omni's nanobanana section. asc-metadata-sync, asc-release-flow and asc-shots-pipeline went back to their pre-merge text on October 20. There is no vSkill lock entry to relock, and the same-place rule rules out publishing them under the owner's account. A `npx skills update` would overwrite these edits.

## Not republished: obsidian-brain and kie-gemini-omni

Both disk copies are the owner's personal forks of skills published publicly in anton-abyzov/vskill. obsidian-brain's fork carries the owner's email address, vault paths and credentials-folder path (`references/user-preferences.md`, the Config block); the published copy is a placeholder template with evals. kie-gemini-omni's fork is a rewrite with the merged nanobanana content (Apache-2.0, resciencelab/opc-skills). The only place they were published is the public vskill repo, so republishing means making the personal versions public. The owner told the agent to settle the open items itself (October 20); the agent took the safe default: the forks stay private, AC-07's republish clause excludes them, and obsidian-brain is relocked to its disk copy and pinned.

## Test

`cd ~/.agents && vskill outdated --json | jq -e '[.[]|select(.warning)]|length==0'` prints `true`, exit 0.

## October 20 recheck

`cd ~/.agents && vskill outdated --json | jq -e '[.[]|select(.warning)]|length==0'` prints `true` (vskill 1.2.10). Lock sha equals disk for social-media-posting, webapp-testing, rea, dcfc-inquiry-replies, html-report and unslop. obsidian-brain is now relocked to its disk copy too (lock and disk both e0710892, version and `pinnedVersion` 1.1.0), so every edited skill's lock sha equals disk and T-06 is done under D-03.


## October 21 final live publication

The authorized resubmission of `anton-abyzov/social-media-posting-skill/social-media-posting-skill` returned submission `sub_92092aad-2a4c-42d8-b186-8304f7c84397`, which reached PUBLISHED at 1:42 PM EDT on October 21, 2026. This receipt supersedes the earlier unfinished publication statement above.

The registry version remains `1.2.3` under its existing auto-version content deduplication policy. The source declares `1.3.1`; no versioning-policy change was made. The previously missing version document now contains all 21,975 bytes of the published source at commit `2b25fe6ebf3bcc6a477db02d2bb3f76fd1bab236`. Its SHA-256 is `a3d5c75a015c5f12cee2037823dcf754b5e7c84bd6cb893508a23ab3b748bf97`, matching both the local canonical document and lock. The one-file manifest has the same hash and byte count; tree hash is `fca0012b4b0c3b9228b2b23d7f7007a7d3557647b77cb7dc301faa5e2c8270c5`.

The registry description now begins “One skill for” and exactly matches the publisher's whitespace-normalized, 500-character-capped source-description contract (499 characters after trimming the cut boundary and appending the ellipsis). The full original description remains in the byte-identical stored document. The first verification attempt incorrectly required the untruncated frontmatter description; that failed output is retained at /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/publication-description-contract-failure-20261021.log. Only that expectation was corrected after inspecting the existing publisher contract; document, hash, commit, lock and manifest equality checks remain exact.

Live acceptance receipt: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/publication-after-20261021.json. Executable check: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/publication-check-20261021.py. Before-state evidence: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/publication-before-20261021.json.

Platform source, CI and deployment are established separately by PR https://github.com/anton-abyzov/vskill-platform/pull/176 and /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/release-production-20261021-receipt.json. All three crawler hosts completed their rollout before this resubmission, as recorded at /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-rollout-20261021.md. No rollout was repeated.
