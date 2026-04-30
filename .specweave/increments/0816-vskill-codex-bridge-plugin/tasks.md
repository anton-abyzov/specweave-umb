# Tasks: vskill `codex-bridge` plugin

### T-001: Author plugin manifests (.claude-plugin + .codex-plugin)
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given the new plugin dir, When `jq . plugins/codex-bridge/.claude-plugin/plugin.json` runs, Then it parses cleanly with `name`, `version`, `description`, `author`, `keywords`
- Given the new plugin dir, When `jq . plugins/codex-bridge/.codex-plugin/plugin.json` runs, Then it parses cleanly with `name` (kebab-case), `version` (semver), `description`, `skills[]` containing `./skills/agents-md-author`

### T-002: Author demo skill (SKILL.md + references)
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given `agents-md-author/SKILL.md`, When YAML frontmatter is parsed, Then keys equal exactly `{name, description}` (strict-mode)
- Given `references/agents-md-spec.md`, When opened, Then it documents the cross-vendor SKILL.md / AGENTS.md / CLAUDE.md conventions concisely

### T-003: Author plugin README
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given `plugins/codex-bridge/README.md`, When opened, Then it documents the file layout, the strict-mode frontmatter rule, and how to author a similar dual-target plugin

### T-004: Add top-level Codex marketplace
**User Story**: US-003 | **AC**: AC-US3-02 | **Status**: [x] completed
**Test Plan**:
- Given `.agents/plugins/marketplace.json`, When `jq '.plugins | length' .agents/plugins/marketplace.json` runs at vskill root, Then output is `1`
- Given the file, When `jq -r '.plugins[0].name'` runs, Then output is `codex-bridge`

### T-005: Register in .claude-plugin/marketplace.json
**User Story**: US-003 | **AC**: AC-US3-01 | **Status**: [x] completed
**Test Plan**:
- Given updated `.claude-plugin/marketplace.json`, When `jq '.plugins | length'` runs, Then output is `9`
- Given the file, When `jq '.plugins[] | select(.name=="codex-bridge")'` runs, Then a non-empty entry is returned with `source: "./plugins/codex-bridge"`

### T-006: Test A — vskill install (dual-target)
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-04 | **Status**: [x] completed — installed to 15 agents incl. .claude/skills/codex-bridge/agents-md-author/SKILL.md and .codex/skills/codex-bridge/agents-md-author/SKILL.md (byte-identical, score 100/100)
**Test Plan**:
- Given an empty `/tmp/codex-bridge-test`, When `npx vskill install --repo <vskill> --plugin codex-bridge` runs, Then `.claude/skills/agents-md-author/SKILL.md` and `.codex/skills/agents-md-author/SKILL.md` both exist
- Given those two files, When `diff` runs, Then they are byte-identical

### T-007: Test B — codex plugin marketplace add
**User Story**: US-002 | **AC**: AC-US2-02, AC-US2-03 | **Status**: [x] completed — `[marketplaces.vskill]` registered in ~/.codex/config.toml; `codex exec` with -c plugins."codex-bridge@vskill".enabled=true ran the skill and produced a 5-section AGENTS.md outline. Schema bugs caught and fixed: source.type→source.source, installation enum→AVAILABLE, authentication enum→ON_USE, category PascalCase→Engineering.
**Test Plan**:
- Given the vskill repo root with `.agents/plugins/marketplace.json`, When `codex plugin marketplace add <vskill-path>` runs, Then exit code is 0 and the plugin is discoverable
- Given the cache dir, When `ls ~/.codex/plugins/cache/` runs, Then a marketplace dir containing `codex-bridge` exists

### T-008: Test C — strict frontmatter check
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [x] completed — keys = {description, name}; description length 434 (under Codex's 1024 cap)
**Test Plan**:
- Given `agents-md-author/SKILL.md`, When a YAML parser extracts the frontmatter keys, Then the set is exactly `{name, description}`

### T-009: Test D — schema conformance vs OpenAI spec
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed — name=codex-bridge (kebab), version=0.1.0 (semver), category=Engineering (PascalCase), capabilities=[Read,Write], all skill paths resolve
**Test Plan**:
- Given `.codex-plugin/plugin.json`, When validated against OpenAI's documented field requirements, Then `name` is kebab-case, `version` is valid semver, all paths in `skills[]` resolve to real directories under the plugin root

### T-010: Test E — marketplace registry integrity
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed — claude marketplace=9 plugins, codex marketplace=1; existing 'skills' plugin still installs cleanly (scout/SKILL.md materialized, no regression)
**Test Plan**:
- Given the modified registries, When jq counts run, Then claude=9 plugins, codex=1 plugin
- Given vskill install of an existing plugin (e.g., `skills`), When run, Then no regression — `.claude/skills/scout/SKILL.md` materializes as before

### T-011: Test F — cleanup
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed — /tmp tmpdirs removed; `codex plugin marketplace remove vskill` confirmed
**Test Plan**:
- Given the test artifacts, When `rm -rf /tmp/codex-bridge-test` and `codex plugin marketplace remove vskill` run, Then both succeed and no test residue remains

### T-012: Sync living docs + commit
**User Story**: All | **AC**: All | **Status**: [x] completed
**Test Plan**:
- Given a clean working tree, When `git add` + `git commit` run for the new files, Then commit succeeds with one-line message under 72 chars
