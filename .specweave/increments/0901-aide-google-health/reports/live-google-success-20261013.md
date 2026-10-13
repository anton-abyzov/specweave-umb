# Real Aide Google verification

Passed on 2026-10-13 at 12:13:39Z (08:13:39 America/New_York), installed service and desktop 1.0.8, source `291f919c24b600e400b8c64e9f3dd383795f33a6`.

The 0904 installer cleared this verification window after independent runtime and native About readbacks. The guarded update receipt has phase `verified`, complete database continuity, and verified appended-activity/heartbeat row preservation. Desktop native About reported `SpecWithCode Version 1.0.8 (291f919c24b6)` with the new process opening the audited ASAR. These are separate from the Google result below.

Fresh local status confirmed the bundled Studio client, connected Google account and all three Aide grants. The official CLI issued only the temporary scopes required by each phase, preserving the normal HOME and account configuration.

Aide coordinator run 6 completed successfully through its native Google tools:

| Tool | Persisted outcome |
| --- | --- |
| studio_google_status, checkConnection=true | Gmail, Calendar and Drive all `ok`; connection `verified` |
| studio_google_gmail_search, newer_than:30d, maxResults=1 | 1 real item |
| studio_google_calendar_events, October 2026, maxResults=1 | 1 real item |
| studio_google_drive_search, maxResults=1 | 1 real item |

Exactly four Google calls ran. Health completed before the three reads. There were no additional dynamic/native tools, delegation, provider failures, content writes, account changes or retries. The receipt excludes returned identities and contents. Both owned temporary sessions were revoked, all prior active sessions were preserved, and no unowned session was added. The runner exited 0 at 12:13:44Z, and the independent receipt validator exited 0.

Evidence: `live-google-status-20261013T1214.json`, `live-google-native-20261013T1214.json`, and `live-google-verified-20261013T1214.json`. Filename timestamps are labels; the actual recorded times are authoritative.

Historical failures remain separate. The original screenshot failed to open an exhausted Claude worker before reaching Google. The later 1.0.7 verification run 4 failed Codex route admission before any Google tool. A human calendar request in run 5 completed at 06:34:30Z with status and Calendar only, before the 1.0.8 service started; it did not prove Gmail or Drive. The successful run 6 above proves all three on the installed 1.0.8 source without rewriting those failures.

The Morning briefing and Theme cancellation fixes are included in 1.0.8. The two chat-linked editor fixes and expanded navigation runner are included in the separately owned 1.0.9 candidate; publication/installation of that follow-up is still pending. No all-fixes-shipped claim is made here.
