# Slash-command guard performance — T-32

Commit: `3a41c2882ecbe71a7510c1f8b476ab20583c2de1` in `/tmp/specweave-0877-guard-performance`, based on `59fd2c4d5`.

The AST guard computed source positions for all 17,275 output literal visits, although only 12 visits contained command matches. It now matches decoded literal text first and computes locations only when needed. The two possible bare-command regexes are reused; `matchAll` clones them and does not advance their stored `lastIndex`. Namespaced matches still precede bare matches for each literal, and duplicate hits from nested output calls remain intact.

Only `tests/unit/cli/slash-command-hints.test.ts` changes. The full source-tree walk, TypeScript parsing, parent links, AST traversal, output-callee/returner rules, exemptions, shipped-skill lookup, ordered hits, test assertions, and timeout are unchanged. The entire `describe` block was also compared byte-for-byte. No runtime code, skipped tests, narrowed file coverage, or increased timeout.

## Evidence

- Parent reported the unchanged guard exceeded its 10-second timeout twice in full CI at `59fd2c4d5`, with the other 16,494 tests passing. The timeout did not reproduce in this isolated local run; the optimization targets demonstrated redundant work, not a relaxed performance threshold.
- Original focused run: 2 tests pass; guard 1787 ms. Optimized focused run: the same 2 tests pass; guard 1307 ms. Logs: `slash-guard-before.log`, `slash-guard-after.log`.
- Independent temporary-module comparison on all **849 source files**: **22 ordered hits**, identical token/file/line tuples, including duplicates. SHA-256 of ordered hits: `31e3fdddeb20b54e3b757cc882b50082b7c5db72053b784cc793011bb0206c3b`.
- Both versions visit **17,275 literal occurrences**. Instrumented source-location lookups fall from **17,275 to 12**. Hoisting regexes does not change their text or flags.
- Disposable fixtures produce **25 identical ordered hits**. They include Unicode/hex escaped slashes, escaped newlines, template heads/middles/tails, excluded bare commands immediately after interpolation, nested output calls, instruction returns, duplicates, ignored input strings, and ordinary URL/prose strings. The escaped-literal line additionally asserts the exact expected three tokens.
- The initial alternating in-memory proposal benchmark was old 1035/959 ms versus candidate 691/691 ms. The final instrumented comparison was old 593/470 ms versus new 383/519 ms. These local samples vary; they are not a CI timing guarantee. The reduced operation count and ordered equivalence are deterministic evidence.

Run `slash-guard-equivalence-probe.mjs <worktree> <output.json>` with Node 22 and `--expose-gc` to compare the committed implementation against `59fd2c4d5`. It extracts the same guard, adds only scan-root/counter instrumentation to temporary modules, and deletes the temporary fixture directory afterward. Evidence: `slash-guard-proposal.json`, `slash-guard-equivalence.json`, `slash-guard-equivalence.log`.

No browser was used. Full combined-suite CI must confirm whether the original timeout is resolved under its actual contention and coverage conditions.
