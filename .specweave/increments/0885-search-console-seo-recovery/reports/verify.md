# Verify — 0885-search-console-seo-recovery

PASS · 2026-10-07T19:04:47.401Z · commands from explicit

## Commands

### `python3 .specweave/increments/0885-search-console-seo-recovery/scripts/verify-mail-inventory.py` → exit 0 (0s)

```
PASS: 88 complete decoded notices from verified admin mailbox; no tracking links retained
```

### `python3 .specweave/increments/0885-search-console-seo-recovery/scripts/verify-release-artifacts.py` → exit 0 (1s)

```
PASS: 120 public checks, 32 design cases, Help deployment/playback, current owner-preserving EasyChamp readback, Verified Skills authenticated rollout/config/cache observation/31 public/3 uncached/6 headless, archive hashes and 174 text artifacts; global coverage and Google indexing gates remain explicit
```

## Acceptance criteria

7/7 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | All 88 matching Search Console emails are read and summarized without secrets or tracking URLs; current and historical findings have dispositions. |
| AC-02 | x (tasks) | spec-weave.com sitemap excludes robots-blocked utility URLs and matches public canonical URLs; affected static site build and regression checks pass. |
| AC-03 | x (tasks) | verified-skill.com public routes have consistent canonical/social metadata, available social images, published video schema and thumbnails; unfinished/operational routes are excluded; sitemap contains only eligible URLs. Public publisher listings and search return correct records/totals on uncached requests within the existing database timeout. |
| AC-04 | x (tasks) | EasyChamp's supported source and live pages are checked against Event image/location and Video date/thumbnail notices; remaining verified source defects are corrected and tested, with current owners preserved. |
| AC-05 | x (tasks) | Independent review resolves critical/high findings; each changed repo is pushed and deployment identity plus public/headless evidence proves the released behavior; remaining Google validation limitations are recorded. |
| AC-06 | x (tasks) | Documentation links retain the shared olive identity and readable contrast in both themes; deployed headless checks prove at least 4.5:1 for normal text and 3:1 for large text. |
| AC-07 | x (tasks) | Every Help tutorial video has an accessible, visible player in initial HTML without a user click; player URLs agree with structured data, remain responsive and do not autoplay. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-seo-coordinator | python3 .specweave/increments/0885-search-console-seo-recov… |  |
| T-02 | done | codex-specweave-seo | PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PA… |  |
| T-03 | done | codex-vskill-seo | Merged source 4e4690cad68bc3b19e4fdf17ba774f4cd46f52ce; rev… | Functional T03/AC03 met; T05 remains pending restored Cloud… |
| T-04 | done | codex-easychamp-seo | UIKit5982da9 and ce3b8fd; Landingea31431 mergedf77de0be; Ar… |  |
| T-05 | done | codex-seo-coordinator | Observed commands: verify-live-seo.py --site all --crawl-sp… |  |
| T-06 | done | codex-seo-coordinator | 385b569cadb32e296a7e3d201f9e705e7c46685d; merge6a2dd672da77… |  |
| T-07 | done | codex-easychamp-seo | Final head1cf2f06; npm test -- --maxWorkers=4 exit0,5745pas… |  |

7/7 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
