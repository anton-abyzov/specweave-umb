---
id: US-002
feature: FS-466
title: "Real Markdown Preview in EditorPanel"
status: completed
priority: P1
created: 2026-03-09T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 50
    url: https://github.com/anton-abyzov/vskill/issues/50
---

# US-002: Real Markdown Preview in EditorPanel

**Feature**: [FS-466](./FEATURE.md)

**As a** skill author
**I want** the SKILL.md editor preview pane to render the markdown body as formatted HTML
**So that** I can visually verify my skill documentation looks correct while editing

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a SKILL.md with markdown body content, when the preview pane is visible (Side-by-Side or Preview mode), then the body renders as formatted HTML (not raw monospace text) using dangerouslySetInnerHTML with the renderMarkdown utility
- [x] **AC-US2-02**: Given the user is typing in the raw editor, when the content changes, then the preview pane updates in real time to reflect the rendered markdown
- [x] **AC-US2-03**: Given a SKILL.md with frontmatter fields and allowed-tools, when the preview pane renders, then the frontmatter cards and allowed-tools pills remain unchanged and appear above the rendered body
- [x] **AC-US2-04**: Given a SKILL.md with no body content (frontmatter only), when the preview pane renders, then no body section appears and no errors occur

---

## Implementation

**Increment**: [0466-skill-builder-preview-history](../../../../../increments/0466-skill-builder-preview-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-005**: Replace raw pre block with renderMarkdown in EditorPanel preview
- [x] **T-006**: Verify frontmatter cards and allowed-tools pills unaffected
