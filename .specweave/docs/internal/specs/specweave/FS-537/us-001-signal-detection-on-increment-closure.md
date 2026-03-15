---
id: US-001
feature: FS-537
title: Signal Detection on Increment Closure
status: not_started
priority: P1
created: 2026-03-15
tldr: "**As a** SpecWeave user."
project: specweave
external_tools:
  jira:
    key: SWE2E-270
  ado:
    id: 194
---

# US-001: Signal Detection on Increment Closure

**Feature**: [FS-537](./FEATURE.md)

**As a** SpecWeave user
**I want** recurring patterns to be silently detected when increments close
**So that** the system builds awareness of my project's conventions without interrupting my workflow

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given an increment is closing via `LifecycleHookDispatcher.onIncrementDone()`, when living docs output exists at `.specweave/docs/internal/`, then the signal collector reads module overviews, API surface files, ADR directory, and skill-memories files
- [ ] **AC-US1-02**: Given the collector identifies a pattern, when no matching signal exists in `.specweave/state/skill-signals.json`, then a new signal entry is created with fields: id, pattern, category, description, incrementIds, firstSeen, lastSeen, confidence, evidence, suggested, declined, generated
- [ ] **AC-US1-03**: Given a pattern matches an existing signal by category slug, when the increment ID is not already in `incrementIds`, then the existing signal is updated with the new increment ID appended and `lastSeen` refreshed
- [ ] **AC-US1-04**: Given `.specweave/state/skill-signals.json` does not exist, when the collector runs for the first time, then the file is created with `{"version": "1.0", "signals": []}`
- [ ] **AC-US1-05**: Given the signal collector encounters an error (missing files, parse failure), when the error occurs, then it logs a warning and exits without blocking increment closure

---

## Implementation

**Increment**: [0537-project-skill-gen-docs](../../../../../increments/0537-project-skill-gen-docs/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-022**: Wire signal collection + suggestion engine into LifecycleHookDispatcher.onIncrementDone()
- [ ] **T-030**: Full pipeline integration test — signal detection through suggestion
