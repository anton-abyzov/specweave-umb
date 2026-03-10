---
id: US-004
feature: FS-459
title: "Skill Dependency Visibility (MCP + Skill-to-Skill)"
status: completed
priority: P1
created: 2026-03-09T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
---

# US-004: Skill Dependency Visibility (MCP + Skill-to-Skill)

**Feature**: [FS-459](./FEATURE.md)

**As a** skill developer
**I want** to see which MCP servers and other skills my skill depends on, based on tool patterns and skill references in SKILL.md
**So that** I can ensure proper MCP configuration and prerequisite skills are installed before testing and deploying

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given a SKILL.md that references tool patterns matching known MCP servers (slack_*, github_*, linear_*, gws_*, drive_*, gmail_*, sheets_*, calendar_*, chat_*), when the SkillDetailPage loads, then detected MCP dependencies are shown in a dedicated section with server name, matched tools, and MCP server URL
- [x] **AC-US4-02**: Given the `allowed-tools` YAML frontmatter field lists tool names, when parsed, then those tool names are also matched against the known MCP pattern registry for dependency detection
- [x] **AC-US4-03**: Given a detected MCP dependency, when the user clicks "Copy Config", then a Claude Code `.mcp.json` configuration snippet is copied to the clipboard (e.g., `{ "mcpServers": { "slack": { "type": "http", "url": "https://mcp.slack.com/mcp" } } }`)
- [x] **AC-US4-04**: Given the backend endpoint `GET /api/skills/:plugin/:skill/dependencies`, when called, then it returns both detected MCP servers (names, URLs, matched tool patterns, setup instructions) and detected skill-to-skill dependencies (skill names referenced in SKILL.md content via patterns like `/skill-name`, `use the ... skill`, or explicit `dependencies` frontmatter)
- [x] **AC-US4-05**: Given a SKILL.md with no MCP tool patterns or skill references detected, when the page loads, then the dependencies section shows an appropriate empty state (e.g., "No dependencies detected")
- [x] **AC-US4-06**: Given a SKILL.md that references other skills by name (e.g., "use the scout skill" or "chains with social-media-posting"), when the dependencies section renders, then referenced skills are listed with their names and links to their detail pages if they exist in the current plugin set

---

## Implementation

**Increment**: [0459-skill-eval-enhancements](../../../../../increments/0459-skill-eval-enhancements/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
