# Decision: automatic local checkpoints, explicit handoff

SpecWeave 3.0.3 treated plan usage at 90% as a reason to force a model continuation, hand off and stop. Plan percentages can reach 100% while paid credits remain. Full handoff also releases ownership and performs Git network pushes. Those effects are inappropriate for automatic saving during parallel sessions.

The replacement queues a bounded local worker after hook events, at most once per five minutes per canonical worktree/session. Hooks return strict empty JSON immediately. They do not read quota transcripts, request model work, push Git refs, change claims, or update the explicit handoff pointer. Four worker slots bound resource use; an eight-second supervisor deadline cleans up its own POSIX process group. Atomic snapshot generations preserve the preceding successful checkpoint on Git/write/scrub failure and allow retry. Existing enabled settings migrate through the unchanged usage-guard command. Explicit handoff remains available for intentional ownership and cross-machine transfer.

## Released proof

Source PR #1983 merged as 10969cdf6d4d8f28db5cde0b0fb1b31964946c9f, with a tree identical to independently reviewed 7c8288e5cf486fdfcbfc966296b0bb70dc4e315e. The user authorized completion of the pending administrator merge; all required test/build/docs/package checks were green, and the independent fresh review returned SHIP. The Claude review bot failed before producing a review. Upstream 3.0.5 provider and monotonic release-guard changes were preserved.

Release 3.0.6 workflow 37737968263 succeeded. The public npm manifest reports gitHead 10969cdf6d4d8f28db5cde0b0fb1b31964946c9f; SHA512/SHA1 integrity matched the downloaded tarball. Clean installation and all nine installed-package checkpoint scenarios passed, with hook responses of 44–184 ms. A guarded atomic launcher update activated the immutable public 3.0.6 package while preserving 3.0.3 files and existing hook settings. The real enabled profile returned strict {} in 51 ms and wrote a fresh checkpoint. Proxy PID 883, Switch PID 887 and Tailscale PIDs 916/969 stayed unchanged and healthy, without restart or configuration changes.

Final Node 22 CI passed 9,983 tests across 494 files, with 77 existing skips. Coverage: statements 70.71%, branches 63.28%, functions 72.77%, lines 71.6%. Targeted affected-code coverage was 87.8% lines and 75.81% branches. The integration suite passed 328 tests; build, TypeScript, manifest validation, release preflight, lint and package verification passed. Earlier failures and unchanged successful retries remain in the reports. No tests were weakened or removed.

Production documentation deployed from the release merge; all 12 public routes expose the new behavior. Stronger visual inspection found a pre-existing desktop CSS cascade defect hiding the active story panel. PR #1986 fixed the selector specificity, with fresh SHIP review, green test/docs CI and a merged tree identical to reviewed source. Deployment 37739794208 published merge 55abf329cd0f59190c41042e0a3d1ef9d20752ed. The live site passed 32 panel states plus six pricing cases at 320/390/1440 widths, light/dark themes and desktop reduced motion, with visible panels and no page errors or horizontal overflow. Representative public screenshots are retained in this report directory.

## Boundaries

Snapshots refresh after hook events, not continuously inside a long turn. They are local recovery evidence, not a remote backup; pickup does not automatically apply them. Recovery must inspect current work and owners. Windows hook smoke passed, but full Windows process cleanup was not exercised on a Windows machine. No Tailscale/proxy settings changed.
