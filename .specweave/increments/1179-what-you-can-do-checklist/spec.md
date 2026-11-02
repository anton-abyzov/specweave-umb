---
increment: 1179-what-you-can-do-checklist
title: What you can do checklist
status: completed
---

# What you can do checklist

## Problem

The first-run wizard covers setup, then nothing shows people what else the product does: routines and other machines stay undiscovered. The user chose a dismissible checklist over a guided tour.

## Scope

In: a checklist card on Overview, ticked from real state, with a setting to bring it back.

Out: a guided tour, mobile, per-machine progress.

## Acceptance criteria

- [x] AC-01 Overview shows five items: connect an agent, add a project, start a session, set up a routine, add another machine.
- [x] AC-02 Each tick comes from real state; opening a page or link ticks nothing.
- [x] AC-03 The card stays hidden until that state is known, and goes away when dismissed or finished.
- [x] AC-04 Settings > General brings it back, and settings search finds it.
- [x] AC-05 Each open item has one action that goes to the place to do it.
- [x] AC-06 It has no horizontal overflow at 1100 and 390 px, in light and dark.

## Approach

A saved client setting holds the dismissal. Overview passes what it already knows; the card reads providers and routines itself and stops reading routines once dismissed.

## Tasks

### T-01 Checklist logic, card and setting
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: apps/web/src/components/studio/whatYouCanDo.logic.ts, apps/web/src/components/studio/WhatYouCanDo.tsx, apps/web/src/components/studio/StudioOverview.tsx, apps/web/src/components/settings/SettingsPanels.tsx, packages/contracts/src/settings.ts | Test: pnpm exec vp test run apps/web/src/components/studio/whatYouCanDo.logic.test.ts apps/web/src/components/studio/StudioOverview.test.tsx

### T-02 Visual check
- AC: AC-06 | Files: apps/web/tests/what-you-can-do | Test: node apps/web/tests/what-you-can-do/verify.mjs

### T-03 Verify and close 1179
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1179-what-you-can-do-checklist
