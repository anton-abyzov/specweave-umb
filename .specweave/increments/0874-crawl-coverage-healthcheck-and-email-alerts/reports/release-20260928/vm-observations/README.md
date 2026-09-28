# T029 per-VM source observations

Candidate `1687ce4837c5a430321e5e1c2fbafb4d860716de` from merged `789f423b102d728cac91e808b8369d40e27d9e53`, clean isolated worktree `0874-vm-observations`, branch `codex/0874-vm-observations`. Ten source/test files are bound by the manifest. Root independently ran 141 focused tests and matched all ten hashes; the additional EasyChamp reviewer is completing a separate review. Draft PR creation is authorized; merge/deploy remain gated on final review and required CI.

Installed and registry SpecWeave are both 3.0.3. Authenticated shared context `0a7b2a80291892de697cad4d85b4ed9218b99929` (19:47:41Z) was read; later root merge/runtime receipts supersede its pending status. No overlapping changed task files were found in existing worktrees; original owners and checkouts remain preserved. T029 was claimed through the CLI in the existing0874 ledger.

The baseline regression reproduced interleaved/simultaneous heartbeats erasing per-VM observations. Canonical scoped records now persist first with explicit failure status; compatibility writes cannot erase them. Readers preserve separate VM/source identity, bounded data and fetch concurrency, server receive times, strict absence-only legacy fallback and explicit missing/malformed/error diagnostics. Observations use SUBMISSIONS_KV; baselines/histories stay in ALERTS_KV, proven with distinct namespaces. Registered body IP plus a shared internal key remains trusted-fleet authentication, not per-VM attestation.

Focused tests: 141/141. Full platform: 5,986 passed and 14 existing skips. Node22.20 Worker build and queue-health contract passed. Actual generated-count artifact input was recorded before restoring only the incidental source change. Typecheck is NOT green: exact base and candidate both produce the same 314 diagnostics after normalizing checkout path and line coordinates; no new diagnostics.

No VM, crawler, checkpoint, credential, database or schedule was changed. Runtime proof requires naturally scheduled heartbeats after a separately reviewed Worker-only deployment. T028's release is managed independently by root.
