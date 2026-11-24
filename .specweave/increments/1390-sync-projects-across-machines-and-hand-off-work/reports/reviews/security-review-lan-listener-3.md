DESIGN CHANGES FIRST
Verdict: fix first

# Security design review: 1390 T-17, round 3

Reviewed umbrella commit: `4c99fd3098967af5023bfd6aad36e7e5d7b445cb`. Fresh static review of S-6 / D-09 only. No listener exists; this is not a finding against a running service.

**Round 2 HIGH: partly closed.** AC-25 and AC-26 now refuse unsafe descendants at final apply, including after fallback to Connect (lines 49–50, 285, 307–311, 467). The remaining gap is above the approved root, not below it.

## Blocking finding

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 3 | 🟠 HIGH | `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/spec.md` | 312–315 | The sticky-directory exception admits an ancestor controlled by another user | 10/10 |

Line 312 permits a sticky ancestor if its next component belongs to the app user, without requiring the **sticky directory itself** to have a trusted owner. On POSIX, the directory owner can rename that child despite the sticky bit. The approved root can therefore resolve somewhere else at final write even when it and every directory below it pass. The post-write identity check cannot guarantee that outside files remained untouched. Both transports use the same apply rule.

**Check-then-write ruling:** Acceptable under the stated threat model once every component is anchored against replacement by other users. The security guarantee comes from preventing replacement, not from making the window short or checking again afterwards. A native helper is not required if apply refuses whenever it cannot establish that guarantee.

## Rulings on the additions

1. **Root anchoring: retain the requirement; strike the sticky exception as written.** Require trusted ownership in both branches. A trusted-owned sticky ancestor may qualify only for an existing, app-user-owned next component whose replacement the filesystem actually prevents. If that cannot be established, refuse. Removing the exception altogether also closes the finding.
2. **Connect compatibility cost: accept.** A reviewed Sync can now skip a previously writable destination and name the folder and reason (lines 314, 320). A switch of transport must not turn a refused write into an allowed one.

## Implementation gates

- On LAN, direct Connect and forced LAN-to-Connect fallback, verify that an unsafe descendant or an untrusted sticky ancestor is named and refused before the affected mutation. Assert outside files are byte-for-byte unchanged, not just that the copy stopped. Include a safe, privately owned tree as a positive control.
- Cover missing targets on Add, effective ACLs (including authority to change permissions), and link or reparse-point checks on each supported OS. Apply the rule to each final mutation, not just the first file in a batch. Keep the post-write identity check for stopping and reporting anomalies.

**Verified:** Read the pinned design, its diff from `02958bc5`, and the round 2 report through Git objects. Checked the current pathname-based rename and directory walk in `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/apply.ts:203–228,250–269`. Rechecked the exception against the local macOS `sticky(7)` manual, which explicitly includes the directory owner among principals allowed to remove or rename entries. No runtime tests were run. Earlier closed findings remain closed.
