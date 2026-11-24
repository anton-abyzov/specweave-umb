<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=839c1f775b70d66401609491866f49af0b7c791f at=2026-11-19T16:17:30.451Z -->
FIX FIRST
Verdict: fix first

AC-18/AC-41 remains open (high): apps/server/src/handoff/HandoffSetMoves.ts:1011-1028 follows a dangling symlink, maps ENOENT to absent, and skips the existing link. Lines 1033 and 1051 exclude or allow that same secret path, so retry can delete the edited entry. Reject symlinks before digesting. Absolute and .. paths now refuse cleanup. No separate new blocker.

Evidence: 5f7b395b3 is tests-only and asserts that a directory replacing the copied file survives retry; tests not run. Reviewed 839c1f775b70d66401609491866f49af0b7c791f.
