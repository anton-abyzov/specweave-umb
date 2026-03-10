---
id: US-001
feature: FS-455
title: "Eval Server Command (P1)"
status: completed
priority: P1
created: 2026-03-08T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 16
    url: https://github.com/anton-abyzov/vskill/issues/16
---

# US-001: Eval Server Command (P1)

**Feature**: [FS-455](./FEATURE.md)

**As a** skill developer
**I want** to run `vskill eval serve [--port 3457] [--root ./plugins]` to launch a local eval UI
**So that** I can access the eval editor and benchmark tools from a browser

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the vskill CLI is installed globally, when I run `vskill eval serve`, then a Node.js HTTP server starts on port 3457 (default) and prints the local URL
- [x] **AC-US1-02**: Given the server is running, when I open `http://localhost:3457` in a browser, then the React SPA loads from bundled `dist/eval-ui/` assets
- [x] **AC-US1-03**: Given I pass `--port 4000 --root ./my-plugins`, when the server starts, then it binds to port 4000 and scans `./my-plugins` for skills instead of the default `plugins/` directory
- [x] **AC-US1-04**: Given the server is running, when I press Ctrl+C, then the server shuts down gracefully

---

## Implementation

**Increment**: [0455-skill-eval-ui](../../../../../increments/0455-skill-eval-ui/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Implement eval server HTTP foundation (router, SSE helpers, static serving)
- [x] **T-002**: Implement CLI `vskill eval serve` command
