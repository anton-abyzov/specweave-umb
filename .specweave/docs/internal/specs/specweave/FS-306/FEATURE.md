---
id: FS-306
title: Fix Marketplace Skill Loss - Restore KV Enumeration + Prisma Migration
type: feature
status: planning
priority: P0
created: 2026-02-21
lastUpdated: 2026-02-21
tldr: Fix Marketplace Skill Loss - Restore KV Enumeration + Prisma Migration
complexity: medium
auto_created: true
external_tools:
  github:
    type: milestone
    id: 118
    url: "https://github.com/anton-abyzov/specweave/milestone/118"
---
# Fix Marketplace Skill Loss - Restore KV Enumeration + Prisma Migration

## TL;DR

**What**: Fix Marketplace Skill Loss - Restore KV Enumeration + Prisma Migration
**Status**: planning | **Priority**: P0
**User Stories**: 7

## Overview

Fix Marketplace Skill Loss - Restore KV Enumeration + Prisma Migration

## Implementation History

| Increment | Status |
|-----------|--------|
| [0306-fix-marketplace-skill-loss](../../../../../increments/0306-fix-marketplace-skill-loss/spec.md) | planning |

## User Stories

- [US-001: KV Enumeration Fallback for Published Skills](./us-001.md)
- [US-002: Write Published Skills to Prisma Skill Table](./us-002.md)
- [US-003: Migrate getSkills() to Prisma-Primary](./us-003.md)
- [US-004: Rebuild Published Index from Surviving KV Keys](./us-004.md)
- [US-005: Fix addToPublishedIndex Race Condition](./us-005.md)
- [US-006: Fix Discovery Cron DATABASE_URL in Worker Context](./us-006.md)
- [US-007: Marketplace Health Monitoring Endpoint](./us-007.md)
