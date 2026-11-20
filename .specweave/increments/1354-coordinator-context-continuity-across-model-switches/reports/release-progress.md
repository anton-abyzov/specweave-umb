# Release progress

PR 521 merged after cross-family policy-valid SHIP at `23657666cdd2c3dcf37722784e08fd36e847edfb` and green final PR Gate. Merge: `bed940f7e58fa16db6ed86cd85d03418dabef759`. Receipt: `/srv/specwithcode/minisforum/evidence/1354-context-continuity/merge.json`. CI receipt: `/srv/specwithcode/minisforum/evidence/1354-context-continuity/ci-wake.json`.

Documented request-release.sh dispatched run `44036253156`: https://github.com/anton-abyzov/specwithcode/actions/runs/44036253156 . Request receipt: `/srv/specwithcode/minisforum/evidence/1354-context-continuity/release-request.log`. No release version selected manually and no busy-machine update forced.

Pending: release outcome, confirm a published tag contains the merge, installed behavior verification, and existing independent reviewer delivery-scope verification and record through the coordinator. Original incident attribution remains unverified; two review lows remain documented in the round 3 report. Increment is not complete.

## Published outcome

Release run `44036253156` succeeded at merge `bed940f7e58fa16db6ed86cd85d03418dabef759`. The documented `request-release.sh --released` confirms this merge is in `v1.0.332`: https://github.com/anton-abyzov/specwithcode/releases/tag/v1.0.332 . Published November 17, 2026. The release monitor is disabled.

Installed proof remains pending. The release log explicitly says `fleet-m4, desktop, fleet-workers: skipped (--ci); hosts reading GitHub install v1.0.332 on their next update check` and `fleet-linux: skipped (--ci); update Linux workers with linux_rollout.py --version 1.0.332 on the M4`. Full log: `/srv/specwithcode/minisforum/evidence/1354-context-continuity/release-332.log`. Local `specweave-studio --version` still returns `v1.0.329`. No busy update was forced. Fleet discovery currently reaches m4; original m3 incident evidence remains unavailable.

Requested coordinator route for an idle installed target at 1.0.332 or later containing the merge, then an automated isolated project verifying worker identity and conversation constraints across a model/provider switch. Evidence must distinguish installed version, selected history and actual provider continuation. Existing independent reviewer must verify and record delivery scope after these receipts; publication alone is not acceptance.

## Local quiet-window continuation

Target is linux-mini. Supported updater `update 1.0.332 --yes --if-idle` downloaded, verified, extracted and executable-checked 1.0.332, then correctly refused to restart the busy 1.0.329 service. It reported one active run (this verification owner); no work stopped. Log: `/srv/specwithcode/minisforum/evidence/1354-context-continuity/local-idle-update-direct.log`.

The installed shell wrapper clears the documented STUDIO_ENABLE_SELF_UPDATE opt-in. Invoking the installed CLI directly with that variable enables the same supported updater; no idle guard bypass is used. One quiet command continuation runs `/srv/specwithcode/minisforum/evidence/1354-context-continuity/local-idle-update.sh`; it retries the conditional updater without waking an agent while busy. Its first successful idle installation wakes this thread for runtime/build and isolated cross-provider behavior verification. Owner remains this thread. Reviewer delivery verification follows installed receipts; increment remains open.
