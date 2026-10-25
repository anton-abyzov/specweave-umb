# Snapshot acceptance follow-up

Status: Partial. The live provider image handoff passes. The installed-artifact headless harness passes. Full live native UI acceptance remains open, so increment 1016 was reopened.

## Current source and release state

PR #629 is merged at `5b0e564eb28c65be94338f38daa82fdf134cb96e`, with green checks on candidate `c1003ccea07c1a9b7e156a977ea67a2dc830b5e5`. The merge is an ancestor of `v1.0.76`, `v1.0.77` and the installed source `4446ca4295caa9283029623e3a36f69ab8c82003`. The related but disjoint browser lifecycle PR #630 is merged at `55f392a9715dfad2b69c4916890d3f6c8783e0c3` and is an ancestor of `v1.0.77`.

The installed package at `/Applications/SpecWithCode.app/Contents/Resources/app.asar` reports version `1.0.76` and source `4446ca4295ca`. Its exact main bundle and unchanged picker preload were extracted for a private headless harness. No source-checkout capture code was substituted. The helper declarations were parsed from the installed bundle and evaluated without changing their bodies. The picker preload runs unmodified, including its real component-context lookup and IPC submission.

## Installed-artifact harness

A separate Electron 44.4.2 process used `--headless`, `show: false`, offscreen rendering and a private test home. The real installed picker handled selection, typed comment and Enter submission at 75%, 100% and 150% zoom. Each crop contains the selected green heading. The comment and selected HTML survive unchanged.

A generated 3024 × 1964 text PNG exercised the exact installed `fitMacSnapShot` helper. Its output bytes match the input SHA-256. This is a synthetic Retina-size source, not a real OS capture. The offscreen frame itself is 1000 × 800 and is not claimed as a Retina capture.

At 150% zoom, the original CSS rectangle produces a blank 480-byte PNG. The corrected display-coordinate rectangle produces a readable 14188-byte PNG. At 75%, the original crop is 544 bytes; the corrected crop is 6966 bytes.

This proves installed artifact behavior under a separate headless harness. It does not prove the live installed desktop renderer, foreground-window OS shortcut, clipboard representations or end-to-end native composer interaction.

## Live provider image handoff

The corrected 150% crop was uploaded through the installed app's signed attachment URL. HTTP status was `204`. Stored upload bytes match the captured PNG SHA-256 `3e261273dd2647d29024a3b49c6842c55c6063ca87a85a850e3b57f9015314e4`.

The image was delivered to the existing thread on its existing `codex` / `gpt-6.1-sol` subscription session. The provider visually read the heading as `SELECTED CONTEXT TEXT` and the blue element label as `h1#selected`, before using file-reading or image-view tools. The received attachment's bytes were then independently compared to the captured image and matched. Provider/model/account settings were not changed, and no paid fallback was enabled.

Dispatch message: `mcp:cd85e0c8-d9a6-436b-82f4-cc32187a19ff`.

Run: `run:thread:thread%3Adelegated-task%3Acommand%253Amcp%253Af9b6f93f-2383-4a68-8fb1-0a0bb9d73b36%253Adelegate-task%253Afix-blurry-pasted-snapshot-20261023:ordinal:4`.

The receipt proves this app upload and Codex image delivery, not other providers or the entire native capture-to-composer path.

## Failed attempts and containment

The signed packaged executable ignored a supplied script argument and entered ordinary startup. Its exact newly started PID `17639` was terminated. Existing app/service processes were not stopped. That attempt is not an acceptance pass. Subsequent checks used the separate headless Electron harness.

REA's initial static analysis returned `artifact_integrity_mismatch` for the signed unpacked passkeys native module. A read-only retry with `record-and-continue` hit `provider_timeout` after 15000 milliseconds. No package files or signatures were modified, and no integrity-success claim is made. Direct ASAR member extraction plus hashes provided the bounded artifact evidence instead.

## Open gate

The user requires headless acceptance. The isolated harness cannot exercise the foreground native shortcut and existing desktop annotation UI. A decision card asks Anton to perform that final check manually, or explicitly authorize scoped native UI interaction. No visible automation will proceed without that decision. Stop holds, release ownership, provider configuration, production holds and live database files were preserved. No release, service restart, account switch or billing change was requested or performed.

Scratch evidence and harness: `/Users/antonabyzov/.specwithcode/m4/evidence/snapshot-installed-20261025`.

Portable receipt validation: `python3 /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1016-fix-blurry-pasted-snapshots/evidence/installed-20261025/check.py`.

## Receipt CI

The umbrella repository had no existing workflows. A path-scoped workflow validates the retained receipt hashes and explicit boundaries on changes to this increment. A green receipt job proves those retained records are internally consistent; it does not close the live-native gate.
