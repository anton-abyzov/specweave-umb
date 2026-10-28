# Timing and carry-forward validation

Production source `6e8396eff2454c5228cdf85e85393f672bc633b9`, retained visual checks `a94d4b61e2e3b4fad705c92095c14c6700e77357`, PR https://github.com/anton-abyzov/specwithcode-dev/pull/959 . Evidence directory: `/Users/antonabyzov/.specwithcode/m4/evidence/1106-internal-receipts`.

The final scoped timing, metadata, receipt attention, relay and assistant-content suites pass 91 tests in `timing-final-focused.log`. Cases cover subsequent turns/messages, same-run steers, resumed runs with gaps, overlap union, duplicate IDs, queued retained starts, user/tool waits, terminal missing ends, partial/invalid/future timestamps, and verbatim 0957 receipt/result preservation. A broader seven-suite attempt passed 323 tests and failed the numbered-request regression; the repaired matcher passes the final focused suite. That earlier failure is retained, not called green.

Real ThreadMetaRow fixture checks settled/live/tool-wait/queued/watch/missing timing across 1280/light and 390/dark. It validates 1m latest versus 6m recorded, 2m live versus 7m recorded, unknown terminal timing, viewport containment and keyboard Escape dismissal. Standalone browser uses headless Chromium, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never and file screenshots/traces. Native preview returned unavailable; fallback is recorded. DOM activation tests React presentation, not native pointer delivery. Coordinator and worker thread pages share source wiring; compact coordinator Overview has separate status presentation.

The native pointer automation limitation also reproduces against unchanged origin/main components, retained in `pointer-baseline.json`. No claim is made that it fixes installed input blocking. Earlier virtual-row overlap work remains separately described in 1106 overlap reports.

Final production build and exact PR head CI are recorded separately when settled. Installed app remains 1.0.109; no install, restart or release was requested or performed.

Final visual result: 14 cases pass (12 timing states plus two 0957 relay/result cases), 14 PNGs and two traces in `/Users/antonabyzov/.specwithcode/m4/evidence/1106-internal-receipts/timing-headless-final`. The checker initially overselected the timing popover as a relay; scoping its selector to the receipt section corrected the test, with no production change. Exact-head Checks run: https://github.com/anton-abyzov/specwithcode-dev/actions/runs/40737392624 .

Final production web build passed in 2m 36s, exit 0, with production source frozen. Log: `/Users/antonabyzov/.specwithcode/m4/evidence/1106-internal-receipts/final-production-build.log`. All four owned fixture servers were stopped by their exact PIDs; no app/service worker was stopped. 1106 stays active while T-12/T-13/T-16 await exact-head CI and closure verification/review.
