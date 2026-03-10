---
id: FS-393
title: "Crawl Pipeline Throughput Optimization"
type: feature
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
lastUpdated: 2026-03-10
tldr: "The crawl pipeline currently processes submissions through two paths: Het."
complexity: high
stakeholder_relevant: true
---

# Crawl Pipeline Throughput Optimization

## TL;DR

**What**: The crawl pipeline currently processes submissions through two paths: Het.
**Status**: completed | **Priority**: P1
**User Stories**: 6

## Overview

The crawl pipeline currently processes submissions through two paths: Het

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0393-crawl-pipeline-throughput](../../../../../increments/0393-crawl-pipeline-throughput/spec.md) | ✅ completed | 2026-03-01T00:00:00.000Z |

## User Stories

- [US-001: Reduce Pending Submission Age Filter (P1)](./us-001-reduce-pending-submission-age-filter-p1.md)
- [US-002: Increase CF Queue Concurrency (P1)](./us-002-increase-cf-queue-concurrency-p1.md)
- [US-003: Multi-Token GitHub Support in CF Worker (P1)](./us-003-multi-token-github-support-in-cf-worker-p1.md)
- [US-004: Feature Flag to Skip CF Queue Enqueue (P2)](./us-004-feature-flag-to-skip-cf-queue-enqueue-p2.md)
- [US-005: Re-Scannable Rejected Submissions (P2)](./us-005-re-scannable-rejected-submissions-p2.md)
- [US-006: Per-State Staleness Configuration (P2)](./us-006-per-state-staleness-configuration-p2.md)
