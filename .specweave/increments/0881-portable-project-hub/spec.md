# 0881 — Portable project hub

## Problem
Riley Brown's 2026-09-21 video demonstrates a project coordinator, worker threads, shared context, artifacts and routines. SpecWeave 2.2.2 already has intents, ledger evidence, sessions and handoffs, but lacks a durable project brief and artifact/routine library usable outside code. Codex setup still targets a legacy skills directory and contains obsolete product guidance.

## Scope
In: additive project hub for any local folder (no Git requirement), reusable project brief, shared context, existing intent work items as worker assignments, artifact references, routine definitions and explicit preparation, CLI plus dashboard, current Codex skill discovery, documented native execution boundaries, packaged local installation.
Out: proprietary design editor, mobile/cloud runtime, a second agent runtime, copying hidden conversation memory, background scheduler, automatic publication, billing guesses. Native tools execute work and schedules; SpecWeave carries inspectable context and evidence.

## Acceptance Criteria
- [x] AC-01: A non-Git folder and an existing umbrella can hold editable project name, goal and shared context without replacing existing config or instructions.
- [x] AC-02: Worker briefs combine current shared context, an existing intent and linked artifact references; remain usable by Codex, Claude Code and generic tools; never claim a native task was launched.
- [x] AC-03: Artifacts are associated with intent IDs; local references stay inside the project and HTTPS references are safe; reusable routines produce explicit worker briefs and accurately state scheduling status.
- [x] AC-04: Concurrent/stale updates cannot silently overwrite project data; invalid/corrupt data fails visibly; portable output is bounded and secret-scrubbed.
- [x] AC-05: Dashboard provides usable brief editing, work links, artifact/routine creation and copyable worker briefs on desktop/tablet/mobile with headless evidence.
- [x] AC-06: Codex adapter installs skills in .agents/skills, preserves existing user data and documents native skills and explicit CLI fallback; new project skill is portable.
- [x] AC-07: Regression tests, build, skill/docs lint, targeted coverage and packaged-install smoke pass; release classification and actual installed version are recorded.

- [x] AC-08: Dashboard and website consume shared brand tokens; paper, ink, accent, surfaces, type and controls match the current public website with responsive headless comparison evidence.
- [ ] AC-09: Stable npm version is published from pushed source, installed from the registry on this machine, and passes full source and installed-package checks; implementation and umbrella evidence are pushed.

## Approach
Reuse existing IntentStore for assignments and execution history; do not create a competing task ledger. Add optional .specweave/project/hub.json with optimistic revisions, exclusive cross-process locking and atomic replacement. Artifact files remain in place; store references only. Project context is explicit user-maintained text, not transcript mining. Prepare fresh worker briefs on demand so snapshot staleness is explicit. Routines store cadence/instructions and export briefs for native scheduling; no scheduler is implied. Add project CLI and dashboard route/tab. Correct Codex adapter path and guidance, retaining legacy files. Keep umbrella config and increment placement unchanged. Additive capability merits 2.3.0 (no breaking migration). Deliver 2.3.0-rc.1 locally first; stable publication and UI closure remain separate from install proof.

Existing ADR 0142 describes historical per-repo increments; current umbrella instructions supersede that aspect. ADR 0845 separates installability from binary detection, which remains valid for Codex setup. Isolated source: /tmp/specweave-0881-root initially from origin/develop 49cb4de1a, rebased onto published npm 2.2.3 gitHead a8b4fd0d49a606fbf891cd462f78a53417cf10ee after that release appeared during this task. Preserve dirty umbrella and unrelated 0879 source branch.

## User acceptance and release authorization
On 2026-09-22 the user accepted the UI, required exact alignment with the current website design system, and explicitly authorized pushing all task work, publishing the latest stable release, installing locally and full testing. This resolves the manual acceptance gate; complete the requested design alignment and automated checks before closure. No further permission request is needed.

## Stable release integration
Final candidate 193f9f6c3 includes exact merged ancestry of sibling scan fixes (#1950, #1951, #1954), preserves version 2.3.0 and adds their bounded-discovery behavior to the release. Full source tests and package preflight run on this combined tree.
