# 1080 live continuation — 2026-10-26

## Ownership and paths
This chat owns increment1080 and source/docs publication. Persistent umbrella worktree: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-1080, branch codex/specwithcode-independent. The previous /tmp checkouts were removed externally; committed branches were restored without touching other owners' work.

App checkout: repositories/anton-abyzov/specweave-studio, branch codex/independent-product, head 9d9361e8224c83550ae6b63592ba152df2fc041b. App PR https://github.com/anton-abyzov/specwithcode-dev/pull/786 remains open awaiting new-head CI. It now integrates released main1.0.89 and the owner-merged #787 status fix. One package.json conflict was resolved as version1.0.89 + UNLICENSED. No history rewrite.

CLI/docs checkout: repositories/anton-abyzov/specweave, branch codex/1080-source-terms-guides, head c050250be57fa07b33e5f16e5d24ed4b5372a7d4. Initial PR #2153 merged at ece5e2842aa99fb3bcbcbd5bf36ba650e32f91f7. Its deployment run40274523536 succeeded. Follow-up #2154 corrects four remaining guide claims; docs/SEO build and fresh review pass, CI pending.

Public clone: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-1080-public. Prepared sanitized snapshot commit28564b63 (full SHA in git), version1.0.89, source9d9361e822, parent public39b0a05fdf625fd06cef5c2fbe30de87ed3da96f. NOT PUSHED. Before publication: confirm #786 merged, fetch private main, compare its tree to9d9361e822; verify public main still the parent and fast-forward only. Never reset public history or change release tags/assets. Regenerate if merged main differs.

## Coordination
Anton explicitly authorized coordination. Peer chat01a17670-ba14-74d1-8617-d43c7bddf5f8 (Fix blocked items shown as idle) owns app1.0.90 canonical release candidate/build/test trees. Peer merged #791/#787, confirmed live1.0.89; no public-source write from that lane until our publication completes. Peer is preparing1.0.90 through drafts only, will merge latest main after #786, retain1.0.90 + UNLICENSED and rerun affected gates, then mirror after our completion message. Send publication SHA when done. Do not change peer's branch or release trees.

## Passing verification
- App source terms audit4/4, exact inherited MIT bytes preserved.
- Runtime/npm packaging8/8 after final merge.
- Full fleet suite48/48, exit0, 170s, after isolated frozen scripts dependency installation. Same existing2 acceptance-proof skips asCI. Log fleet-final.log.
- New fixture fix eeeea79265 makes only formatting-insensitive lookup while retaining exact record path/schema/version/newline and copy→write→hash ordering. 30 refresh tests pass; fresh reviewer approved and tested8 negative fixtures. Final merge reviewed again: ship, no findings.
- Initial CLI CI all green:535 passing unit files;10447 tests passed,78 skipped. Coverage72.69% statements,65.92% branches,75.11% functions,73.44% lines; all exceed unit60 target. Receipt coverage-ci.json.
- Local isolated guard/project-root17/17 and checkpoint19/19 pass unchanged. Supported unit coverage run had one local helper-start timing race; its complete19-test file passed on isolated rerun. No test or threshold relaxed.
- A broad all-test audit also exposed42 legacy integration failures outside projectCI; kept coverage-resume.log. Do not misrepresent it as all-green. The supported coverage script is npm run test:unit; actual cleanCI passes it above targets.
- Docs builds/SEO pass, both initial and4-guide follow-up. Headless live-site verifier is running/available in reports/verify-live-site.mjs; use --guides after #2154 deploys. Save Chrome headless receipts/screenshots.

## Tasks and next steps
T01/T02/T04/T05/T06 are done; T03 (publication) is claimed and pending. All work is authorized; no permission request needed for green merges/publication. Continue waiting with scripts/release/ci-wait.sh bounded540s, no error ignoring. Merge #786 when required checks + fleet are green and no completed check fails; merge #2154 when green (develop review requirement may use authorized admin merge, same as #2153). Verify docs deploy, public source and actual GitHub contents. Then task done T03, specweave verify with real scoped commands, final fresh review if needed and complete1080. Do not claim complete while publication remains pending.

Verification scripts in reports: verify-publication.mjs (GitHub source/notice/identity/author/version checks) and verify-live-site.mjs (Chrome headless; --guides adds4 guides).
