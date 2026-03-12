---
id: FS-420
title: "Vendor Skill Freshness"
type: feature
status: completed
priority: P1
created: "2026-03-03T00:00:00.000Z"
lastUpdated: 2026-03-07
tldr: "14 of 16 official Anthropic skills from `anthropics/skills` are missing from vskill search results."
complexity: medium
stakeholder_relevant: true
---

# Vendor Skill Freshness

## TL;DR

**What**: 14 of 16 official Anthropic skills from `anthropics/skills` are missing from vskill search results.
**Status**: completed | **Priority**: P1
**User Stories**: 2

## Overview

14 of 16 official Anthropic skills from `anthropics/skills` are missing from vskill search results. The discovery pipeline's 30-day dedup TTL prevents re-scanning vendor repos for new skills, and the cron job excludes `vendor-orgs` from its discovery sources. When Anthropic (or any vendor org) adds new skills, they remain invisible until an admin manually triggers a force re-import.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0420-vendor-skill-freshness](../../../../../increments/0420-vendor-skill-freshness/spec.md) | ✅ completed | 2026-03-03T00:00:00.000Z |

## User Stories

- [US-001: Vendor skills bypass discovery dedup (P0)](./us-001-vendor-skills-bypass-discovery-dedup-p0.md)
- [US-002: Vendor discovery runs on cron schedule (P1)](./us-002-vendor-discovery-runs-on-cron-schedule-p1.md)
