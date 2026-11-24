# 0932 scoped verification

PASS on October 21, 2026, at 2:50 AM EDT. The actual `specweave verify 0932` invocation ran all six explicit commands from `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/scoped-verify-20261021-final-command-manifest.json`. This is the task-scoped verification, not the umbrella aggregate.

- Full vskill suite: 678 files passed; 7,132 tests passed and two repository-defined tests skipped.
- Platform task paths: 29 files and 331 tests passed.
- VM scanner content transport: four tests passed.
- npm/global vskill 1.2.10, active tenant plus successful nightly run 39383673080, and published sw-do 3.1.0 checks passed.
- Ledger: 13/13 tasks done, 13/13 acceptance criteria met, no task skips or open claims, no malformed ledger events.

The first scoped attempt failed two unchanged CLI performance assertions at 1,100 ms and 1,863 ms against the existing 1,000 ms limits. Both entire files then passed all 161 tests in 894 ms in an isolated recheck. The subsequent full six-command run passed without exclusions, assertion edits or increased limits. The failed report and recheck output remain in `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/scoped-verify-20261021-timing-failure.md` and `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/scoped-verify-20261021-timing-recheck.log`.

The vskill checkout stayed at `36c5c532dbc105463cf89906bb632fdd775e1dbc`. The platform checkout advanced from `e86907bfa521f6f9ea0bc0aaf86a7c5aaaa9f0d2` to `58e2eb892e5868ee1010da6a8a2eb6edbc4bf4d3` during this run. A direct Git diff contains only `/Users/antonabyzov/Projects/github/wt-0932-0934/platform-finalize/package.json`: its worker-build flag and explanatory comment. Tested source and tests were unchanged. Node 22.20.0, at most two Vitest workers, isolated Git global/system configuration, and unset SPECWEAVE_WORKSPACE were used. No browser was launched and no source files were edited.

The source tests and operational readbacks above do not establish deployment of PR #176 or restoration of the social-media-posting registry document. The parent owns those remaining live checks and final completion.

Verify and close 0932.
