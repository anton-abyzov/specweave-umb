---
id: US-001
feature: FS-394
title: Unified sw-* Plugin Installation via --repo
status: complete
priority: P2
created: 2026-03-01
project: specweave
external:
  github:
    issue: 1455
    url: https://github.com/anton-abyzov/specweave/issues/1455
---
# US-001: Unified sw-* Plugin Installation via --repo

**Feature**: [FS-394](./FEATURE.md)

SpecWeave user
**I want** sw-* plugins (sw-github, sw-jira, etc.) to install from GitHub via `--repo anton-abyzov/specweave`
**So that** plugin installation works without requiring a local marketplace directory at `~/.claude/plugins/marketplaces/specweave`

---

## Acceptance Criteria

- [x] **AC-US1-01**: `install_plugin_via_vskill()` function in `user-prompt-submit.sh` uses `npx vskill install --repo anton-abyzov/specweave --plugin <name>` instead of `--plugin-dir ~/.claude/plugins/marketplaces/specweave`
- [x] **AC-US1-02**: The function no longer checks for or depends on `~/.claude/plugins/marketplaces/specweave` directory existence
- [x] **AC-US1-03**: The scope guard migration code (lines ~297-304) also uses the --repo path for sw-* reinstallation
- [x] **AC-US1-04**: sw-* plugins install successfully when triggered by lazy-loading keyword detection or LLM detection

---

## Implementation

**Increment**: [0394-unified-plugin-install-via-repo](../../../../../increments/0394-unified-plugin-install-via-repo/spec.md)

