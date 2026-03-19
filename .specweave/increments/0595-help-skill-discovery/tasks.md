---
increment: 0595-help-skill-discovery
---

# Tasks

### T-001: Create /sw:help SKILL.md
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [x] completed

Create `plugins/specweave/skills/help/SKILL.md` with:
- Frontmatter with description and trigger phrases
- Context gathering via `specweave status --json` and `specweave analytics --since 30d --json`
- Skills organized by workflow stage with one-liner descriptions
- Contextual next actions for active increments
- Getting started guidance for new users
- Graceful degradation when data unavailable

**Test Plan**: Given SKILL.md exists → When frontmatter is parsed → Then description contains trigger phrases "help", "what can I do", "show commands"

---

### T-002: Register help skill in plugin.json
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [x] completed

Add `"help"` to the `provides.skills` array in `plugins/specweave/.claude-plugin/plugin.json`.

**Test Plan**: Given plugin.json is read → When provides.skills is checked → Then "help" is in the array

---

### T-003: Clean up framework terminology in public docs
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed

Replace "framework" with "tool"/"SpecWeave" in:
- `docs-site/docs/overview/introduction.md` (line 5)
- `docs-site/docs/overview/philosophy.md` (line 3)
- `docs-site/docs/integrations/generic-ai-tools.md` (lines 3, 59, 225)
- `docs-site/docs/overview/plugins-ecosystem.md` (line 12)

Preserve tech stack references ("React framework", "Next.js framework").

**Test Plan**: Given docs are edited → When grep for "framework" runs on edited files → Then only tech stack references remain

---

### T-004: Create help.md docs page
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

Create `docs-site/docs/commands/help.md` documenting the `/sw:help` command following existing command page patterns.

**Test Plan**: Given help.md exists → When page is read → Then it documents skill usage, output sections, and examples
