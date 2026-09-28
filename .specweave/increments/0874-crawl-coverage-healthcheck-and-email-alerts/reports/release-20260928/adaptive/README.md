# T027 resumable adaptive discovery

Source: `757278503c2d18f4ff9b00129c635e2b076a8fa1`, base `a066df378c8f42ef6e5515d906d7feb996c2d475`. Isolated worktree `0874-adaptive-resume`, branch `codex/0874-adaptive-resume`. All 14 source files are bound by the retained manifest. Independent root review and required CI are pending. Production adaptive mode remains OFF.

Node 22.20.0 full crawler suite: 235 passed, zero failed, one existing optional live API guard skipped because GITHUB_TEST_TOKEN is absent. Focused visibility/planner/scheduler suite: 32 passed. Gitleaks scanned 111.62KB with no findings; repository malware and secret pre-commit checks also passed.

The durable versioned plan drains each validated leaf before the next count probe. Fresh processes resume pending pages using stored public repo/path payloads; SIGKILL and changed-pagination tests prove accepted inputs avoid resubmission and unresolved inputs remain replayable. Same-name collisions cannot share incomplete receipts. Private/internal and unknown-visibility search results are excluded before intake and identity proof; unknown visibility keeps coverage incomplete. GitHub documents repository.private in its REST search-code response example: https://docs.github.com/en/rest/search/search#search-code .

A bounded exact natural-key union (first 10,000) is kept only in mode 0600 runtime checkpoint/completed files. Exports contain count, saturation, sweep/config identity and checksum only. Encounter counters are explicitly not global distinct counts. Capped tails remain represented and never turn into full-coverage success. Configuration/schema mismatch is non-destructive in either adaptive-mode direction. Partial results do not emit dead-man success or count as completed runs.

Read-only privacy trace: the bulk route authenticates content probes and creates submissions without GitHub privacy metadata. The existing publishSkill guard rejects explicit tenant/private intent, but does not independently check source repository visibility. The public crawler now fails closed on this boundary. No actual historical leak was established; no historical data was changed.

Initial release T025 is done with the retained seven-root runtime receipt. T017 full-breadth acceptance remains open; a millions-of-matches sweep can take days at GitHub quota. No full-corpus completion is claimed from this local test suite.
