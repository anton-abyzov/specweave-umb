# T029 independent review

Verdict: no blocking finding in the bounded ten-file change at `1687ce4837c5a430321e5e1c2fbafb4d860716de` (tree `d5b923c6a8c545ab508847115d18cf398c0a810e`, base `789f423b`). The worktree remained clean and all ten source/test manifest hashes matched after review and testing.

The reader uses configured registered identities, limits keys/concurrency/record size, retains each VM's source row and scopes detector history, high-water marks and alert dedup independently. Legacy records retain their old state keys and are read only on true canonical absence; malformed/read-error scoped records remain explicitly degraded. Canonical source writes precede heartbeat metadata, and a failed compatibility write reports its partial result without discarding persisted per-VM data. Separate SUBMISSIONS_KV source records and ALERTS_KV detector state are covered by actual route tests.

Independent validation: 141 focused tests passed across five files. Seven additional probes loaded the actual TypeScript source modules with only in-memory storage, synthetic Cloudflare bindings and a clock: authentication/registration denial; concurrent duplicate-source writes and safe metadata; separate detector baselines/dedup; source-write and subsequent heartbeat-write failure; compatibility-write failure; actual TTL expiry; malformed scoped data refusing a healthy aggregate fallback. All passed; no network requests or repository edits occurred.

Author evidence inspected: 5,986 platform tests pass with 14 existing skips, Node22 Worker build and queue contract pass. TypeScript is not green: the exact base/head comparison has the same 314 diagnostics and no additions. These pre-existing errors remain explicit.

Shared fleet-key authentication is not individual VM attestation. Legacy free-form aggregate behavior is deliberately preserved while new per-VM records carry sanitized metadata. Native/store/assistant activation are outside this review. Exact-head hosted CI and natural scheduled production heartbeat readback are still deployment verification gates; no production action was performed here.

See `t029-parity-review.json` for exact source hashes, context ref, evidence paths and probe details.
