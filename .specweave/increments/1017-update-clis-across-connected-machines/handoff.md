# Completed checkpoint: October 27, 2026

1017 is completed. This checkpoint supersedes the historical continuation instructions below. PR #631 merged at 05fa77b27d7b8d3652dcf6da36745ba359affbc2 and is included in installed app/service 1.0.105, source 0b680c88224a92d5b154a364b0332e1e01b68139. Authenticated headless Providers fleet and selected-provider acceptance is recorded. All seven temporary local acceptance sessions were revoked. No installer, remote grant, restart or release was performed during acceptance.

T-04 is done; verification passed 6/6 ACs, 5/5 tasks and 100 focused checks. Fresh review SHIP, with nonblocking popover overlap and fleet screenshot timing limitations retained in /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1017-update-clis-across-connected-machines/reports/review.md. Complete exited 0 without override. Closure hooks reported no resolvable JIRA issue key or ADO work item ID; zero external items changed. No retry or invented tracker association.

Remote execution on M1, M3, Anna Air and Ministorm remains unknown: existing grants are required. This is separate from accepted local installed behavior. Receipt: /Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/installed-acceptance.md.

## Historical handoff (superseded)

## Superseding Astra sweep checkpoint

October 23, 2026: #631 merged at `05fa77b27d7b8d3652dcf6da36745ba359affbc2`. Former worktree is absent; branch and tested commit remain. Bundle reports `1.0.74`, shell CLI `1.0.75`; running service inclusion is unproven. Current release owner is Complete screenshot sessions, replacing the older 1015 routing below. T-04 remains open. Current exact acceptance and next action: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/installed-acceptance.md`. No remote grant or installer mutation performed.

# 1017 Release and postrelease handoff

## Where I left off

Increment: `1017-update-clis-across-connected-machines`. Source repository: `https://github.com/anton-abyzov/specwithcode-dev`.

Source worktree: `/Users/antonabyzov/.specwithcode/m4/worktrees/provider-cli-fleet-update`.

Branch: `feat/provider-cli-fleet-update`. Source commit: `4c25c1effd1f5dd57d6125b9072b0c17d33f37bf`. Worktree was clean at this handoff. PR: https://github.com/anton-abyzov/specwithcode-dev/pull/631 . Its open head matches this commit.

Planning root: `/Users/antonabyzov/Projects/github/specweave-umb`. Spec: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1017-update-clis-across-connected-machines/spec.md`.

Implementation/acceptance owner: this thread, `thread:delegated-task:command%3Amcp%3Af9b6f93f-2383-4a68-8fb1-0a0bb9d73b36%3Adelegate-task%3Aprovider-cli-fleet-update-20261023`.

CI, merge, inclusion and rollout owner: 1015, `thread:delegated-task:command%3Amcp%3Af9b6f93f-2383-4a68-8fb1-0a0bb9d73b36%3Adelegate-task%3Aprepare-five-hour-release-20261023`. The parent already has the PR watch. No duplicate watcher, merge, release, worker or restart.

## Effect-aware repair receipt

The seven introduced CI diagnostics on `26904bba4ad6b06462cda4f78eee1ccb19d59eb5` were repaired using specific tagged failure channels. The matching local Effect-aware gate now passes all 15 packages with zero new diagnostics against the unchanged repository baseline. Web passes this gate. All 74 focused behavior checks and fresh review pass. The earlier plain TypeScript result was insufficient; do not reuse it as evidence of Effect-aware verification. No suppressions or baseline edits were added.

Current repair report: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/effect-repair/report.md`.

1015 retains CI/watch/merge/inclusion for the new head. Installed UI and live remote acceptance remain unproven. No live installer was executed during this repair.

## Done / Pending

T-01, T-02, T-03 and T-05 are recorded done with commit/evidence. T-04 and AC-06 remain open. The earlier verification ran its focused command successfully, then failed closure coverage at 5/6 ACs and 3/4 tasks. A later source-repair task T-05 is now also done; T-04 is still open. No completion override was used. This handoff does not change acceptance state.

Already covered, do not repeat without a source change or a new failure:

- 100 focused tests, production web/server builds, server typecheck and fresh review. The reviewer found and re-verified the Node-entrypoint/renamed-binary idle-check repair.
- Headless source fixture: selected local instance only by default; explicit connected-peer selection; offline and unauthorized rows disabled; exact environment/instance RPC routing; verified and busy outcomes; desktop and 390px layouts without horizontal overflow.
- Real local M4 Codex side-by-side update: `0.162.1` to `0.164.0`. Old entrypoint hash and auth hash unchanged; no app/service restart. This was helper/real-installer verification, not a click through the installed new app UI.
- Additional postreceipt fixture checks: Tab focus stays in the dialog, Escape closes an idle dialog, and closing sends no installer RPC. No passed suite was repeated.

Exact remaining acceptance:

1. **Release inclusion and installed identity.** 1015 supplies the merge/inclusion SHA, release version and independently observed installed app/service version and SHA. Source/CI/release success alone does not prove installed behavior.
2. **Installed UI, AC-06/T-04.** In the installed release, open Settings > Providers and the selected CLI update plan. Verify exact selected instance and machine default; explicit opt-in for other machines; current/target version and owning installer; actionable skipped rows; cancellation of queued work and independent per-machine results; no app/service restart. Retain screenshots and the actual outcome. Codex is already `0.164.0` on M4: do not downgrade, reinstall a busy executable or invent an outdated state merely to expose the button. If an honestly outdated eligible instance is unavailable, record that acceptance remains unproven.
3. **Live remote execution.** Before dispatch, read authoritative existing destination `providers:manage` permission for this connection, destination identity, configured executable/real path, installer ownership, installed/target version and active-session safety. Worker inventory status is not the Providers UI grant. Only execute on an already-authorized eligible destination, and only if staging preserves active releases or the in-place executable is idle. Verify destination version and individual outcome afterward. If no safe authorized destination exists, retain the unproven gate; do not widen permissions or call a denial an execution pass. The last inventory reported `needs_grant` for five peers, and no remote installer was executed.
4. **CI/typecheck disposition.** 1015 owns #631 checks. Local web typecheck reported the exact error below in unchanged source. Do not claim a baseline pass; use the PR owner's current disposition, and fix a real scoped regression if one is established.

`/Users/antonabyzov/.specwithcode/m4/worktrees/provider-cli-fleet-update/apps/web/src/lib/newThreadWorkspaceDefault.ts(14,17): error TS2883: The inferred type of 'observeNewThreadIsRepo' cannot be named without a reference to 'EnvironmentRegistry' from '../../node_modules/@specweave-studio/client-runtime/src/connection/registry'. This is likely not portable. A type annotation is necessary.`

## Decisions

- Keep 1017 open until the remaining gates are proven. Do not silently defer a gate to make verification green.
- No new remote grants, auth/account changes, paid turns, session kills, busy in-place replacements, forced app/service restarts, downgrades or competing release actions.
- Preserve installer provenance and configured paths. Staged Codex uses its owning Node/npm with an exact stable version and a new directory; Homebrew/native/global/custom installations retain their own boundary. An unverifiable wrapper stays manual.
- The in-place safety guard observes host processes by configured/real executable paths, provider names and npm package identities. An external process can still start between that observation and installer launch. Do not claim an atomic drain/admission lock.
- The fleet batch is client-side, at most two concurrent items, and is not durable across app closure/service restart. Cancel affects queued items only.
- All browser checks must explicitly use `headless: true`, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`, report open `never` and file-backed evidence.
- Never directly access `userdata/statev2.sqlite` or its sidecars. Use the supported database CLI if a future read is necessary.

## Files touched and evidence

The latest continuation repaired the two runner files and fast-forward pushed PR #631 to `4c25c1effd1f5dd57d6125b9072b0c17d33f37bf`. The full source inventory is `git show --stat` for that commit in the source worktree above.

Evidence report: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/report.md`.

Visual report: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/report.html`.

Additional fixture/source receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/postreceipt-checks.json`.

Real local installer receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/live-local-update.json`.

Version-source receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/versions.json`.

Fleet inventory limit: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/fleet-inventory.json`.

Full web typecheck error: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/web-typecheck.log`.

Close-gate output: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/specweave-verify.log`.

Next installed receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/installed-acceptance.md` (not yet created; never treat this planned path as evidence).

## Next steps

1015 returns exact inclusion/installed identity and UI receipt to this thread. This owner checks the receipt against each gate above, performs only new safe checks, records T-04 done only when AC-06 is proven, and then runs `specweave verify 1017`, fresh review if new changes warrant it, and `specweave complete 1017` without an override.

If authoritative remote permission or idle proof is absent, do not execute a remote update. Keep that limitation visible and the applicable gate open.

## Resume

Read this handoff and current owners before claiming T-04. Do not run pickup or apply any snapshot in the dirty umbrella/shared checkout. The source branch already exists in the isolated worktree, and PR #631 is managed by 1015.

The CLI handoff was recorded with `--no-push`. Explicit `--workspace` made its generated Git header describe the umbrella, not the app source. Retrying from the app worktree with `SPECWEAVE_WORKSPACE` was refused: `Working directory is not a member of workspace /Users/antonabyzov/Projects/github/specweave-umb: /Users/antonabyzov/.specwithcode/m4/worktrees/provider-cli-fleet-update`. This hand-written document is the authoritative source/owner handoff. The generated diff copy of unrelated umbrella work was removed; no original files or owner work was changed, committed, stashed or pushed.

The sync README could not be read: `gh: No commit found for the ref claude-project-sync (HTTP 404)` from the configured SpecWeave umbrella repository. No branch/grant/registration was created to bypass that boundary. The local spec/ledger and this document carry the portable continuation state.

Verify and close 1017 only after its remaining acceptance is proven.
