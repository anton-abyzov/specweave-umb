# 1493 Release

- PR https://github.com/anton-abyzov/specwithcode/pull/966 squash-merged as `c8701bd9e688d64377fe220d255c9b6a309ac981` on head `7686efabab10a2a4b306be22a7c3523467865923`. That head had a GPT-6 Sol SHIP (`review-gpt-6-sol-round-8.md`) and 28 green checks.
- Released in v1.0.447: `request-release.sh --released c8701bd9e` printed "is released in v1.0.447". Release run: https://github.com/anton-abyzov/specwithcode/actions/runs/45930488087.
- `SpecWithCode-1.0.447-arm64.zip` passed `SHA256SUMS`. Its `app.asar` contains "This form was closed." (`FORM_CLOSED`, new in 1493) and "Enter a date and time.".
- Strict `specweave verify 1493` passed in the gated checks copy at the merge commit: 8 of 8 commands, ACs 14/14, tasks 2/2 (`reports/verify.md`).
- The installed app updates at its next quiet moment; nothing was forced.

## Review rounds

Rounds 2 to 8 were run by GPT-6 Sol on Codex. Rounds 2 to 6 returned NO-SHIP, and every finding was fixed (`review-gpt-6-sol-response.md`). Round 7 returned SHIP at `30f63b76a`. Round 8 returned SHIP at `7686efaba`: that round added one test-only commit fixing a race in `apps/server/src/terminal/Manager.test.ts` that CI hit twice (`manager-race.txt`).
