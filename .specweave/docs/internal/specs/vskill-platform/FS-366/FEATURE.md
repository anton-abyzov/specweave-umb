---
id: FS-366
title: "Orphan cleanup on re-submission + install tracking phone-home"
type: feature
status: planned
priority: P1
created: 2026-02-24
lastUpdated: 2026-02-24
complexity: medium
stakeholder_relevant: true
project: vskill-platform
external_tools:
  github:
    type: milestone
    id: 142
    url: https://github.com/anton-abyzov/specweave/milestone/142
---

# Orphan cleanup on re-submission + install tracking phone-home

## TL;DR

**What**: Clean up orphaned/stale submissions when a skill is re-submitted, and add install tracking phone-home so vskill CLI reports installs to the platform.
**Status**: planned | **Priority**: P1
**User Stories**: 2

## Overview

Two related improvements: (1) When a skill is re-submitted, automatically deprecate the previous Skill record using the existing `isDeprecated` field. (2) The vskill CLI sends a fire-and-forget POST to the platform after each successful `vskill install`, incrementing `Skill.vskillInstalls`.

## User Stories

- [US-001: Orphan Skill Cleanup on Re-submission](./us-001-orphan-skill-cleanup-on-re-submission.md)
- [US-002: Install Tracking Phone-Home from CLI](./us-002-install-tracking-phone-home-from-cli.md)
