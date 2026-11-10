# Skills management follow-up

Authorized by Anton on November 6, 2026. Implement after PR #1430 merges, from fresh main in a separate PR and increment. Preserve Skills counts/filter ownership and reconcile overlapping files before editing. This scope does not expand PR #1430 or imply acceptance of its pending CI/release.

## Entry and navigation

Keep composer Skills search. Every skill row opens Skills settings with that skill selected, scoped to the originating machine and agent. The copies-differ label is a separate deep link directly to that skill's comparison view. Preserve project context and composer draft. Show actionable missing/offline states if the destination cannot be read.

## Detail view

Render descriptions as Markdown with inline code, links and line breaks. Lead with a short summary and when to use, with full text behind Show more. Render the SKILL.md body with headings where useful. Give version and status clear meaning. Group Loaded by agents sharing a path, show the path once, retain per-agent toggles. Match existing design system.

## Edit and resolve

Expose differing copies with a readable diff, provenance, machine, agent, path and version. Let the user pick the intended copy explicitly; preview affected destinations and preserve conflict/stale protection. From the selected detail, edit, bump version and explicitly publish to the chosen private or public vskill registry destination. Never silently overwrite a copy, switch visibility or publish.

## Create and distribute

Provide a clear New skill entry in Settings Skills. Flow: describe or paste, choose agents and scope, review and publish, apply. Available on machine chips show actual installed versions/status for M1, Ministorm, the Duo and other connected machines. Install on all previews selected destinations/agents and performs guarded version-pinned installs or updates through existing fleet and vskill boundaries. Report per-machine success, conflict, offline, access refusal and retry states. An offline/unknown machine is not absent or installed. Keep active sessions intact.

## Verification and delivery

After #1430 merges, give Anton two or three lines of exact clicks matching the released screen, distinguishing merged source from installed availability. Verify light/dark, wide/narrow with headless before/after screenshots, saved to an owned evidence folder. Run focused behavior tests and relevant production builds, fresh review and applicable CI, then use the sole release dispatcher for merge/release. Report the follow-up PR link and screenshot paths briefly, and send Anton one-line status when the PR is up.

Create the follow-up increment with concrete file ownership and tasks before code changes. Its checklist must end with Verify and close followed by its assigned increment number.

## References

- Authoring PR: https://github.com/anton-abyzov/specwithcode-dev/pull/1430
- Detail screenshot: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-b74fb90b-0c91-4c98-8efa-f9ba6eae68c4.png`
- Settings screenshot: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-451b7e8f-198d-4722-97ef-ec428cb560b8.png`
- Composer screenshot: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-8c931a47-dc0d-4116-ba13-c39c8746ff87.png`

Review hardening: add root-fixpoint refusal to SkillPublishingAdapter ancestor traversal for unavailable UNC roots, plus a regression test. See /Users/antonabyzov/.specwithcode/m4/evidence/1209-final/review-3397802386.md.
