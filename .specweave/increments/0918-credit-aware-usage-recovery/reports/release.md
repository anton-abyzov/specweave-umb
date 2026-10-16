# 1.0.14 release evidence

Public release: https://github.com/anton-abyzov/specwithcode/releases/tag/v1.0.14

Independent GitHub readback on 2026-10-14 confirmed publishedAt `2026-10-14T13:33:25Z`, `isDraft: false`, and 11 release assets.

Reviewed product commit `d8d0422d5f87290a429369479adc100a8ae0e4d5` is an ancestor of combined release source `939a796c4635feae9495292ddc5d29e7eee7a311`. Private main merge: `267bbe15a19428daa83c385eeff8ec7e334cd747`. Sanitized public source: `62fa60ab84d075193ddace4ed87ad0a75d03fb6f`.

The release owner reports independent combined review approval and 394 tests across 11 suites. Signed desktop and standalone runtime passed artifact checks; runtime verified 7,482 files. Anonymous full-content readback passed all 11 public payloads and the latest versionless DMG.

Publication receipt: `/Volumes/SanDisk APFS/SpecWithCodeReleases/0907-114/publication-939a-2/receipt.json` (owner-reported location).
Anonymous readback: `/Volumes/SanDisk APFS/SpecWithCodeReleases/0907-114/anonymous-939a-1/receipt.json`, SHA256 `07699a99d84e461b455fdefa9e1d1d3f40e495aadae8123eeb4257e15ea336a2`.

UI previews were explicitly accepted by Anton. M1 and M3 deployment receipts were independently read: both report phase `verified`, source `939a796c4635feae9495292ddc5d29e7eee7a311`, runtime archive SHA256 `c41a1136db2bffdc518acb965f33fff05cb38e2df5f95042dc9b6da70efddf04`, preserved rows/auth/identity, and verified complete database continuity. No inference was executed.

Receipts are under `/Volumes/SanDisk APFS/SpecWithCodeReleases/0907-114/worker-install-939a-1/remote-execution-{m1,m3}-root-939a-1/readback-receipts-final-1/install-attempt-1/update.json`. Their final guarded results both exit 0 with `guardedReceiptVerified: true`.

Local Mac `/Applications/SpecWithCode.app/Contents/Info.plist` independently reports `CFBundleShortVersionString: 1.0.14`. The release owner reports successful installation and relaunch through the normal updater after explicit user authorization. Full local-service continuity and six-route handoff acceptance remain owned by increment 0907; they are not asserted by 0918.

`python3 .specweave/increments/0918-credit-aware-usage-recovery/reports/verify-release.py` passed: published release with 11 assets, sealed anonymous-download receipt, sealed M1/M3 installed-version readbacks, and local Mac app version. No live paid turn is claimed.
