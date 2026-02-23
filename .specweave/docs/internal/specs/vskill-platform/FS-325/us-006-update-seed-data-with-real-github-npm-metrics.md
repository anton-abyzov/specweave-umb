---
id: US-006
feature: FS-325
title: Update Seed Data with Real GitHub/NPM Metrics
status: not-started
priority: P1
created: 2026-02-22
project: vskill-platform
---
# US-006: Update Seed Data with Real GitHub/NPM Metrics

**Feature**: [FS-325](./FEATURE.md)

visitor viewing individual skill pages
**I want** to see real GitHub stars, forks, npm downloads, and version numbers
**So that** per-skill metrics reflect verifiable reality instead of fabricated values

---

## Acceptance Criteria

- [ ] **AC-US6-01**: All skills sharing a `repoUrl` show the same `githubStars` and `githubForks` values (the real repo values)
- [ ] **AC-US6-02**: `specweave` skill shows `githubStars: 69`, `githubForks: 7`, `npmDownloads: 20002`, `currentVersion: "1.0.313"`
- [ ] **AC-US6-03**: `anthropics/skills` group (16 skills) shows `githubStars: 73059`, `githubForks: 7481`
- [ ] **AC-US6-04**: `openai/skills` group (32 skills) shows `githubStars: 9280`, `githubForks: 518`
- [ ] **AC-US6-05**: `google-gemini/gemini-cli` group shows `githubStars: 95246`, `githubForks: 11474`
- [ ] **AC-US6-06**: `google-gemini/gemini-skills` group shows `githubStars: 1766`, `githubForks: 115`
- [ ] **AC-US6-07**: `google-labs-code/stitch-skills` group shows `githubStars: 1873`, `githubForks: 213`
- [ ] **AC-US6-08**: `google-labs-code/jules-skills` group shows `githubStars: 7`, `githubForks: 1`
- [ ] **AC-US6-09**: `firebase/agent-skills` group shows `githubStars: 123`, `githubForks: 2`
- [ ] **AC-US6-10**: `coreyhaines31/marketingskills` group shows `githubStars: 8701`, `githubForks: 1135`
- [ ] **AC-US6-11**: Community skills from fictional repos (e.g., `devops-community/skill-*`) have `githubStars: 0`, `githubForks: 0`
- [ ] **AC-US6-12**: All `vskillInstalls` values in seed data are set to `0`
- [ ] **AC-US6-13**: NPM downloads for the 6 real packages use actual npm registry values

---

## Implementation

**Increment**: [0325-homepage-metrics-accuracy](../../../../../increments/0325-homepage-metrics-accuracy/spec.md)

