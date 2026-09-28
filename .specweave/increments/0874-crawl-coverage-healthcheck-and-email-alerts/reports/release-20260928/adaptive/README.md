# T027 resumable adaptive discovery

Source: `757278503c2d18f4ff9b00129c635e2b076a8fa1`, base `a066df378c8f42ef6e5515d906d7feb996c2d475`. Isolated worktree `0874-adaptive-resume`, branch `codex/0874-adaptive-resume`. All 14 source files are bound by the retained manifest. Independent root review and required CI are pending. Production adaptive mode remains OFF.

Node 22.20.0 full crawler suite: 235 passed, zero failed, one existing optional live API guard skipped because GITHUB_TEST_TOKEN is absent. Focused visibility/planner/scheduler suite: 32 passed. Gitleaks scanned 111.62KB with no findings; repository malware and secret pre-commit checks also passed.

The durable versioned plan drains each validated leaf before the next count probe. Fresh processes resume pending pages using stored public repo/path payloads; SIGKILL and changed-pagination tests prove accepted inputs avoid resubmission and unresolved inputs remain replayable. Same-name collisions cannot share incomplete receipts. Private/internal and unknown-visibility search results are excluded before intake and identity proof; unknown visibility keeps coverage incomplete. GitHub documents repository.private in its REST search-code response example: https://docs.github.com/en/rest/search/search#search-code .

A bounded exact natural-key union (first 10,000) is kept only in mode 0600 runtime checkpoint/completed files. Exports contain count, saturation, sweep/config identity and checksum only. Encounter counters are explicitly not global distinct counts. Capped tails remain represented and never turn into full-coverage success. Configuration/schema mismatch is non-destructive in either adaptive-mode direction. Partial results do not emit dead-man success or count as completed runs.

Read-only privacy trace: the bulk route authenticates content probes and creates submissions without GitHub privacy metadata. The existing publishSkill guard rejects explicit tenant/private intent, but does not independently check source repository visibility. The public crawler now fails closed on this boundary. No actual historical leak was established; no historical data was changed.

Initial release T025 is done with the retained seven-root runtime receipt. T017 full-breadth acceptance remains open; a millions-of-matches sweep can take days at GitHub quota. No full-corpus completion is claimed from this local test suite.


## Final reviewed source

Final head: `ebc6c4ad4b8ad13ea5a90acc3b734cbb6c6003d3`, draft PR https://github.com/anton-abyzov/vskill-platform/pull/75 . Follow-up validation rejects malformed/incomplete responses and coarse 422 without advancing. Typed permanent policy receipts preserve legacy error fields and carry an explicit original path; only four closed validation codes can settle rejection, and rejected identities never warm accepted-key cache. Missing content and transient failures remain retryable. All bulk details carry original input paths, including fallback probes.

Full final crawler suite: 250 passed, zero failed, one optional live-GitHub-token skip. Platform: 5904 passed, 14 existing skips. Bulk producer: 46/46. Independent root review: 70/70 consumer plus 46/46 producer, no critical/high blocker. Worker build and queue-health contract passed with exact Node 22.20.0 and isolated dependencies. The first build with a symlinked dependency tree failed during OpenNext bundling; it is superseded by the isolated successful build, not hidden. Actual generated public-count input/hash is retained before restoring source drift.

All production changes remain gated on exact-head CI, root merge/authorization and fresh idle/identity checks. The approved plan requires Worker producer first, then crawler-only adaptive enable, runtime continuation with one stable sweep ID, and honest partial intake/coverage evidence. No schema 2 checkpoint may be removed to make rollback to an incompatible coarse reader appear successful.
