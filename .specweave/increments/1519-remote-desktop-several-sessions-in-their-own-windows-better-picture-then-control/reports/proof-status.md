# 1519 proof status, November 28, 2026

## Shipped

| PR | Merge commit | Released in |
|---|---|---|
| #1019, several sessions in their own windows, view count, picture | `ea7668757b3cca5ecb7e3c6e2568ba05d3e03927` | v1.0.465 |
| #1028, control (helper, grant, banner, input rules) | `51d234aec0957f088ff7825a9ad064ec381b7290` | v1.0.466 |

Both were confirmed with `bash scripts/release/request-release.sh --released <commit>`.

## Security review of #1028

Reviewer: Muse Wonder Full 1.0 (meta), reasoning effort high. It ran instead of Gemini 4 Neon and GPT-6.2 Sol, and `spec.md` (Review) records why.

| Round | Commit read | Verdict |
|---|---|---|
| 1 | `0881e4543`, in three slices | helper fix first, session ship, viewer fix first |
| 2 | `8f5989a92` | fix first |
| 3 | `4e2def6b7` | fix first |
| 4 | `6415bb98a` | fix first |
| 5 | `8222aff35` | ship |

Every finding was checked against the code and fixed before the next round. Records are in `reports/reviews/`. CI was green on the merged head, `3b9be8c26` (31 checks). One earlier failure was a LAN timing test that the diff does not touch.

## Not verified yet

The machine-level proofs need M5 unlocked. They are not done.

- **Not done:** the two-window screenshot (m1 plus a machine that shows "off").
  - Why: `CGSSessionScreenIsLocked` read 1 at every check from 06:45 to 08:35 EST.
  - Why: window capture returns nothing while the screen is locked.
- **Not done:** the before and after measurements over Connect from M5 to m1 (AC-07, `reports/picture-measurements.md`).
  - Measurements to take: frames per second, KB per frame, and capture-to-confirm time.
- **Not done:** the control request from M5 to m1.
  - Needs M5 unlocked and on v1.0.466.
  - Needs m1 on v1.0.466 or later.
  - Then the owner approves at m1: Touch ID for "Always allow control", plus the Accessibility grant if macOS asks.
- **Not done:** installing v1.0.466 on M5.
  - M5 has v1.0.465.
  - The app updates itself at a quiet moment, and no update was forced.
