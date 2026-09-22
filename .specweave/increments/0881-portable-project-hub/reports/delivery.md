> Historical RC snapshot. Stable release supersedes it: [2.3.0 delivery](stable-release.md).

# Portable project hub — delivery

Installed locally: **SpecWeave 2.3.0-rc.1**, built from `d43b766a58ece6a5f294baa39cdb32c4b7d37115`. Previous global CLI was 2.2.3. Stable npm release remains unpublished. Draft PR: https://github.com/anton-abyzov/specweave/pull/1953, stacked on published-2.2.3 delivery PR #1952.

## Decision

The video demonstrates useful coordination patterns: one project brief, delegated work, shared artifacts and repeatable routines. Those fit SpecWeave without tying its state to Claude. Implement them as portable files over the existing intent/evidence stores. Leave native execution, schedules, mobile/voice, design editing and billing with the host. Hidden conversation state is not a cross-tool synchronization API. A generated worker brief is an explicit snapshot.

This is an additive **2.3 minor** capability. No breaking major migration is needed. Native Codex skills use `.agents/skills/sw-*`; old `.codex/skills` and unnamespaced custom skills remain intact. Changed managed installations are backed up before copying. Every project verifies its own installed files and companion resource modes.

## Delivered

- `specweave project` initializes ordinary folders and existing umbrellas, updates goal/context, reuses intent work, stores file/HTTPS artifact references and routine definitions, and exports coordinator or worker briefs.
- Project hub dashboard supports desktop, tablet and phone. Revision conflicts retain the draft and require explicit retry against the current revision. Artifact files download as attachments.
- Project storage uses validated schemas, bounded reads, exclusive write locks, optimistic revisions and atomic replacement. Managed initialization rejects symlinked destinations. Briefs use existing secret scrubbing.
- This umbrella now has a shared project brief, an intent linked to increment 0881, the video-analysis artifact and all 12 native core Codex skills. Existing config is byte-for-byte unchanged; original AGENTS content is preserved before the added hub pointer.

## Evidence

Node 22.20.0. Full source suite passed: **746 files; 16,793 tests; 159 existing skips**. Build, dashboard TypeScript, skill lint and docs-reference lint passed. Targeted new-code coverage: **95.61% lines, 86.08% branches, 90.24% functions, 92.55% statements**.

The actual tarball was installed into an isolated prefix and globally. CLI init/work/artifact/routine/brief flows passed. Actual packaged refresh installed all 12 native Codex skills, preserved a custom same-name unnamespaced skill and passed a second refresh. Chromium used `headless: true` at 1440, 820 and 390 pixels; editing, work creation, artifact/routine flows, file download and persistence passed with no runtime errors or horizontal overflow. Independent review verified five fixes and reports no remaining confirmed findings.

See `verify.md`, `review-independent.md`, `install-receipt.json`, `packaged-e2e.log`, `native-install-smoke.log`, and screenshots under `artifacts/packaged/` and `artifacts/installed/`. Source-gates records the earlier full pass before install/acceptance checkboxes were finalized. No tests were weakened or skipped to obtain a pass.

## Use

Run `specweave project show`, `specweave project brief --harness codex`, or `specweave dashboard` from the umbrella. For another project, run `specweave project init --name "Project name" --goal "Desired outcome"` in that folder. New native skills are discoverable in subsequent Codex sessions; this task's already-loaded plugin tool catalog is not claimed to have hot-reloaded.

Saving a routine does not create an active schedule. Use native host automation after authorization. No external posts/messages, cloud deployments or billing changes were made.

## Remaining gate

Manual UI acceptance is required before increment closure by umbrella AGENTS.md: "Ask user for manual acceptance: new UI, auth, payments, data migrations". Automated checks and local installation are complete independently of this acceptance. The increment remains active; do not invoke complete or claim stable publication yet.

Rollback if requested: `npm install -g specweave@2.2.3 --ignore-scripts`; original umbrella instructions/config and prior native skill copies are preserved in the recorded backup paths. Keep project data unless the user asks to remove it.
