# vskill

## F01 [slow-step] real=True safe=True save=150->140 :: Rust cache never restores on desktop-v* tag builds, so every release compiles all dependencies cold
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/notarize-dryrun.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src-tauri/rust-toolchain.toml
EVIDENCE: rust-cache logs 'No cache found' on all three legs today (keys v0-rust-build-Linux-x64-01b81e85-610aea19, v0-rust-build-Darwin-arm64-fc985acc-610aea19, v0-rust-build-Windows_NT-x64-e70cdc14-610aea19), and also on v1.0.64 (37905199652) and v1.0.63 (33687220308). The caches it saves are scoped to refs/tags/desktop-v1.0.65 (497/473/430 MB). The next tag can never read them; a tag run can only read its own ref and main. The only main-branch Rust cache is v0-rust-dryrun-Darwin-arm64-fc985acc-610aea19 from the nightly dry-run, under a different prefix ('dryrun' job id vs 'build'). Its env hash fc985acc is identical to the release macOS leg, so only the key name blocks reuse. Warm-cache evidence: the dry-run Tauri step took 236s/269s on cache hits (10-14, 10-15) and 387s on today's miss. Today's miss came from rustc moving to 1.99.1 (hash e59a64c1 -> fc985acc), because dtolnay/rust-toolchain@stable floats. Repo cache usage is 11.24 GB in 50 entries, above the 10 GB cap, so unusable tag and PR caches are evicting useful ones. Dependency phase measured from the first to the last dependency 'Compiling' line: linux ~143s, mac ~140s, win ~215s. Post-job saves that are never reused: 11/40/37s.
CHANGE: 1. desktop-release.yml 'Cache Cargo': keep `workspaces: src-tauri -> target` and add `shared-key: desktop-${{ matrix.target }}` plus `save-if: false`. Tags never save.
2. notarize-dryrun.yml 'Cache Cargo': set `shared-key: desktop-aarch64-apple-darwin`. It already does a release aarch64 build on main every night, so the macOS release leg will restore it.
3. Add Linux and Windows main-branch writers with `shared-key: desktop-x86_64-unknown-linux-gnu` and `desktop-x86_64-pc-windows-msvc` (see F18). They should run the same `tauri build --target <t>` with GITHUB_OAUTH_CLIENT_ID set, so dependency artifacts and the env hash match.
4. Pin Rust. Create src-tauri/rust-toolchain.toml with `[toolchain] channel = "1.99.1"` and the three targets. Replace `dtolnay/rust-toolchain@stable` with `dtolnay/rust-toolchain@master` and `toolchain: 1.99.1` in desktop-release.yml, notarize-dryrun.yml and sidecar-smoke.yml, so a new stable no longer invalidates every cache overnight. Bump the pin deliberately.
RISK: Low. A stale or poisoned cache can only affect dependency artifacts; cargo still rebuilds anything whose fingerprint changed. Pinning delays Rust updates until someone bumps the pin.
VERIFIER: Confirmed: 'No cache found' on all three legs. The tag caches live under refs/tags/desktop-v1.0.65, repo cache usage is 11.24 GB in 50 entries, and the only main Rust cache is v0-rust-dryrun-Darwin-arm64-fc985acc-610aea19 (env hash identical to the release mac leg). A warm cache helps: the dry-run Tauri step took 236-309s on hits and 387-410s on misses. The saving is overstated without writers, though. On its own (steps 1, 2 and 4) only the macOS leg can restore, and macOS (544s) is not on the critical path, so the wall-clock gain is just the tag-ref post-save on Linux: 11s today, 37s on Windows once F02 makes Windows critical. With Linux and Windows writers (F18), the Windows leg loses deps 215s + crate download 25s + post-save 37s, minus about 25s for restore, so about 250s. Release wall: about 140s off without F02 (Linux 872 to about 733), and Windows 701 to about 450 with F02. Do not add src-tauri/rust-toolchain.toml as well as pinning the action. dtolnay does not read the file, so rustup would install a second toolchain named '1.99.1' next to 'stable' (15-30s per job, and on Anton's machines). Pick one mechanism.
IMPL: desktop-release.yml lines 57-65: `uses: dtolnay/rust-toolchain@<SHA of master>` with `toolchain: 1.99.1` and `targets: ${{ matrix.rustup_targets }}`. Then `Swatinem/rust-cache@v2` with `workspaces: src-tauri -> target`, `shared-key: desktop-${{ matrix.target }}` and `save-if: false`.
notarize-dryrun.yml lines 33-42: same toolchain pin, `shared-key: desktop-aarch64-apple-darwin`, save left on (schedule runs on main).
Linux and Windows writers come from F18.
Keep CARGO_*/RUST* env identical between writer and reader jobs; rust-cache hashes them into the key (today: CARGO_HOME, CARGO_INCREMENTAL, CARGO_TERM_COLOR).
There is no stale-signed-artifact risk: rust-cache keeps only deps/build/.fingerprint and deletes bundle/.

## F02 [slow-step] real=True safe=True save=170->None :: RPM bundling takes about 5 minutes on the Linux leg, which is the release critical path
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src-tauri/tauri.conf.json, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: Linux 'Bundling Skill Studio-…rpm' to the next bundle took 321s today (14:56:24->15:01:45), 304s on v1.0.64 and 305s on v1.0.63. The .deb of the same payload (130 MiB SEA sidecar + binary) takes 3s, and both packages are about 51.6 MB, which matches tauri-utils 2.10.1's documented RPM default ('Defaults to Gzip with level 6'). Linux was the slowest leg in every recent release: 872s, 852s and 938s, against at most 701s for Windows and 552s for macOS. Publish starts only after Linux finishes. Downloads across 20 GitHub desktop releases: .rpm 53, .deb 46, .AppImage 606 (the updater uses the AppImage).
CHANGE: 1. tauri.conf.json `bundle.linux.rpm`: add `"compression": {"type": "zstd", "level": 3}`. Time it against `{"type": "none"}` with a local or CI `npx tauri build --target x86_64-unknown-linux-gnu --bundles rpm`.
2. If the time does not drop well below 60s, take RPM off the critical leg. Set the linux matrix row to `bundles: deb,appimage` and add a 4th row (`os: ubuntu-22.04`, `platform: linux-rpm`, `bundles: rpm`, same target). It runs in parallel and shares the F01 cache. Extend the upload-artifact paths and the sign-linux-artifacts call to it.
3. Alternatively drop RPM entirely, given the download numbers.
RISK: A zstd payload needs rpm 4.14 or newer (RHEL 8+, Fedora 31+). 'none' makes the RPM about 3x larger. A separate RPM job costs one more Linux runner.
VERIFIER: Confirmed: 321s (14:56:24.75 to 15:01:45.82). Linux is the critical leg. The compression rationale is contradicted by the evidence. The .rpm (51,579,101 B) and .deb (51,580,210 B) are the same size, so the RPM already uses gzip-6 (the tauri-utils 2.10.1 default), and the deb gzips the same payload in 3s. Compression level is therefore not the explained cost, and zstd-3 may save nothing. The separate-leg option is also weaker than claimed. A cold RPM-only leg costs about 175s setup + 260s compile + 321s RPM, roughly 760-780s, which is longer than Windows (701s), so it saves only about 95-110s unless F01 makes it warm. Dropping RPM gives the full gain: Linux falls to about 551s, Windows (701s) becomes critical, and the run is about 171s shorter. Downloads across the last ~20 releases: rpm 45, deb 38, AppImage 318.
IMPL: Preferred: desktop-release.yml line 42 `bundles: deb,appimage`. Optionally remove "rpm" from tauri.conf.json bundle.targets.
sign-linux-artifacts.sh already skips missing rpm/*.rpm (`[ -f "$f" ] || continue`).
The upload-artifact, publish-manifest and softprops *.rpm globs can stay: upload-artifact errors only when nothing matches at all.
To keep RPM, first time `npx tauri bundle --target x86_64-unknown-linux-gnu --bundles rpm --config '{"bundle":{"linux":{"rpm":{"compression":{"type":"none"}}}}}'` on an ubuntu-22.04 runner via workflow_dispatch. Adopt it only if the step drops below about 60s.

## F03 [slow-step] real=True safe=True save=90->50 :: Fat LTO with codegen-units=1 and the unused staticlib/cdylib crate types makes the final link 2-3.5 minutes that no cache can skip
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src-tauri/Cargo.toml
EVIDENCE: src-tauri/Cargo.toml has `[lib] crate-type = ["staticlib", "cdylib", "rlib"]` and `[profile.release] lto = true, codegen-units = 1, opt-level = "s"`. Time from the last dependency 'Compiling' line to 'Finished release': linux 117s (14:54:24->14:56:21), mac 168s (14:54:05->14:56:53), win 207s (14:55:36->14:59:03). Even with a warm cache the macOS dry-run compile still took about 162s on 10-15 (03:04:20->03:07:02). src-tauri/gen holds only schemas (no android or apple projects), so the mobile-only staticlib and cdylib outputs are unused. Under lto=true each of them gets its own whole-program LTO link.
CHANGE: 1. Change `[lib] crate-type` to `["rlib"]`. Keep `#[cfg_attr(mobile, tauri::mobile_entry_point)]` in lib.rs; it is harmless.
2. Measure `lto = "thin"` with the default codegen-units (16) against the current settings. Compare build time and the .app/.exe/.AppImage sizes.
3. If size matters, keep fat LTO for releases but add `[profile.release]` overrides only after the measurement.
RISK: Thin LTO with more codegen units can grow the binary by an estimated 5-15%. If mobile builds are ever added, staticlib and cdylib must come back for those targets.
VERIFIER: Confirmed: crate-type [staticlib, cdylib, rlib] with lto=true, cgu=1, opt-level s. Only main.rs uses vskill_desktop_lib, and src-tauri/gen has no mobile projects. Measured split from the logs:
- Lib step (last dep to '(lib) generated warnings'): linux 59s, windows 114s.
- Bin LTO after that: linux 58s, windows 93s.
Removing staticlib/cdylib lets cargo emit bitcode only for the lib, skipping its object codegen and the cdylib/staticlib link and archive. That saves part of the lib step, an estimated 40-80s on Windows and 25-45s on Linux; not measured. Today this is 0 wall-clock, because Linux is critical and limited by RPM. It counts only after F02. The thin-LTO part must be measured for size and perf before adopting.
IMPL: src-tauri/Cargo.toml: `[lib] name = "vskill_desktop_lib"` with `crate-type = ["rlib"]`. Leave [profile.release] unchanged in the same PR.
Compare the 'Build Tauri' step and the gap from the last 'Compiling' line to 'Finished' on the next Desktop Build nightly (F18) or a workflow_dispatch of notarize-dryrun.
Try `lto = "thin"` as a separate change only after comparing .app/.exe/.AppImage sizes.

## F04 [wait-gap] real=True safe=True save=520->520 :: The desktop release waits on a version-bump PR even though CI stamps the version from the tag
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/release-desktop.sh, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/.claude/skills/tauri-desktop-release/SKILL.md
EVIDENCE: desktop-release.yml step 'Derive desktop version from git tag + sync into Cargo.toml + tauri.conf.json' rewrites Cargo.toml, tauri.conf.json and Cargo.lock from GITHUB_REF_NAME (log: 'Desktop version: 1.0.65', cargo update --precise). Today the bump went through PR #181. It was created at 14:40:14, its slowest check (Sidecar Smoke rust-windows, 517s) finished at 14:48:58, the agent waited 361s (14:43:05-14:49:06), and the tag was only pushed at 14:49:23. If the tag had gone on main at about 14:40 the desktop release would have finished about 9 minutes earlier. The skill text the agent updated still says 'a release can be just a bump PR + tag'.
CHANGE: 1. release-desktop.sh: remove step 3 (sed bump) and step 4's commit and push to main. Tag the fetched origin/main HEAD directly: `git tag desktop-v$V <origin/main sha> && git push https://github.com/anton-abyzov/vskill.git desktop-v$V`.
2. desktop-release.yml publish job: add a final step, after the R2 manifest and GitHub release succeed, that commits the three version files back to main with the built-in token. permissions is already write-all, and a GITHUB_TOKEN push does not trigger CI. Commit message: 'release: desktop $V'.
3. Update SKILL.md to say 'tag main; CI stamps the version; the publish job commits the bump'.
RISK: main's Cargo.toml shows the previous version for about 15 minutes. A push from Actions to main can conflict with a concurrent merge; retry with a rebase, or open a PR instead.
VERIFIER: Confirmed. desktop-release.yml lines 148-171 stamp Cargo.toml, tauri.conf.json and Cargo.lock from GITHUB_REF_NAME. PR #181 (bump plus script) was created at 14:40:13. Its rust-windows check ended at 14:48:57, it merged at 14:49:17, and the tag was pushed at 14:49:23. Nothing before the stamp step (the sidecar and eval-ui builds) reads the desktop version.
The saving is an estimate, not a measurement. Tagging origin/main at about 14:40:14 would have saved about 549s, and about 730s if tagged together with v1.2.8 (see missed M1).
The commit-back step is optional and adds risk: an unreviewed GITHUB_TOKEN push to main that triggers no CI, and races with merges. main is unprotected (branch protection 404, no rulesets), so it would work, but it is simpler to let main's Cargo.toml lag, since only dev builds show it, or bump it in the next normal PR.
IMPL: release-desktop.sh:
- Delete steps 3-4.
- Then run `git fetch -q https://github.com/anton-abyzov/vskill.git main && SHA=$(git rev-parse FETCH_HEAD) && git tag "desktop-v$VERSION" "$SHA" && git push https://github.com/anton-abyzov/vskill.git "desktop-v$VERSION"`.
desktop-release.yml build job, first step after checkout (fetch-depth 0 is already there): `git merge-base --is-ancestor "$GITHUB_SHA" origin/main || { echo '::error::tag is not on main'; exit 1; }`.
SKILL.md line 26: replace 'a release can be just a bump PR + tag' with 'tag origin/main; CI stamps the version from the tag; no bump PR'.

## F05 [discovery-gap] real=True safe=True save=150->120 :: The 'one-command' release script was stale, so the agent hand-rolled the desktop release; there is no npm release script
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/release-desktop.sh, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/release-npm.sh, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/RELEASING.md
EVIDENCE: At 14:38:24 the agent read a 347-line release-desktop.sh whose steps 6-7 regex-edited vskill-platform files and redeployed the platform. Those steps had been dead since the manifest moved to R2 on 2026-09-03. It spent 14:38:20-14:40:14 rewriting them, hand-bumping versions with sed (including `sed -i '' '5086s/1.0.64/1.0.65/' src-tauri/Cargo.lock`), and running only step 1 via `head -n $N`. The first rsign check failed ('Missing untrusted comment', because rsign reads the password from a tty) and had to be retried through a pty. In the end the agent never ran the script: tag, poll and verify were all done by hand (14:49:21, 14:50:12-15:05:47, 15:05:52-15:06:10). The current script still has problems:
- Step 2 re-uploads TAURI_SIGNING_PRIVATE_KEY/PASSWORD with `gh secret set` on every run.
- Step 4 pushes straight to main.
- Step 5 does a single `gh run list` after `sleep 8`, which races the run's creation.
- It never verifies the downloaded bundle's signature. The agent did this by hand at 15:06:00.
npm side: the agent had to work out the convention (git show v1.2.7, npm-release.yml) and poll the registry by hand.
CHANGE: Rewrite release-desktop.sh as `release-desktop.sh [<version>] [--dry-run] [--rotate-secrets]`:
(a) Default version: the patch after `git tag -l 'desktop-v*' --sort=-v:refname | head -1`.
(b) Preflight with no side effects:
- `gh auth status`.
- ~/.config/skill-studio-release/{minisign.key,minisign.pub,minisign.passphrase} exist.
- ~/.cargo/bin/rsign sign and verify through the existing pty helper.
- The pubkey in tauri.conf.json equals base64(minisign.pub).
- `gh secret list -R anton-abyzov/vskill` contains TAURI_SIGNING_PRIVATE_KEY, TAURI_SIGNING_PRIVATE_KEY_PASSWORD, APPLE_CERTIFICATE, APPLE_ID, CLOUDFLARE_R2_* and GPG_PRIVATE_KEY. Check names only, never values.
- The latest 'Notarize Dry-Run (nightly)' and 'Sidecar Smoke' runs on main succeeded.
(c) Run `gh secret set` only with --rotate-secrets.
(d) Fetch https://github.com/anton-abyzov/vskill.git main, tag origin/main and push the tag over https (F04).
(e) Look up the run with a retry loop: `gh run list -R … --workflow desktop-release.yml --branch $TAG --json databaseId`, for up to 120s. Then `gh run watch $RUN -R … --exit-status --interval 30`.
(f) Verify:
- assets include .app.tar.gz.sig, x64-setup.exe.sig and .AppImage.sig;
- https://verified-skill.com/desktop/latest.json?ts=… returns x-manifest-source: r2 and version=$V;
- download the darwin-aarch64 URL from the manifest, base64-decode its signature and run `rsign verify -p minisign.pub -x`.
(g) Promote the release and clean up drafts.
Add release-npm.sh:
- check that package.json version is not yet a tag;
- tag v$V on origin/main and push over https;
- `gh run watch` the npm Release run;
- poll `curl -fsS https://registry.npmjs.org/vskill/$V` until 200 (max 5 min);
- `npx -y --prefer-online vskill@$V --version`.
Add RELEASING.md at the repo root listing both commands, the key paths and what each verifies. Point the tauri-desktop-release skill at it.
RISK: Low. The script automates what the agent did by hand. --dry-run lets it be tested without a tag.
VERIFIER: Confirmed from the transcript:
- At 14:38:24 the agent read the old script.
- 14:38:47: rsign failed with 'Missing untrusted comment'.
- 14:38:52: retry through a pty.
- Sed bumps, including `5086s/1.0.64/1.0.65/` on Cargo.lock.
- 14:39:55: step 1 run via `head -n $N`.
- Tag, polling and rsign verify all done by hand.
The merged 225-line script still re-sets both signing secrets on every run (TAURI_SIGNING_PRIVATE_KEY was last set 2026-06-03, so nobody has run it since), pushes to main, and does a single `gh run list` after `sleep 8`. Not mentioned by the profiler: step 8 runs `gh release delete --cleanup-tag`, which also deletes the git tags of stale drafts. The saving is mostly the agent's discovery time (~114s), and it is the enabler for F04.
IMPL: Keep the existing pty rsign block (lines 70-102).
Gate step 2 behind `--rotate-secrets`.
Replace steps 3-4 with F04.
Step 5: `for i in $(seq 1 24); do RUN_ID=$(gh run list -R "$REPO" --workflow desktop-release.yml --branch "$TAG" --event push --json databaseId -q '.[0].databaseId'); [ -n "$RUN_ID" ] && break; sleep 5; done; gh run watch "$RUN_ID" -R "$REPO" --exit-status --interval 15`.
After step 7, add the agent's check: decode `platforms["darwin-aarch64"].signature` from latest.json, download the URL, and run `rsign verify -p minisign.pub -x`.
Step 8: drop `--cleanup-tag`.
New scripts/release/release-npm.sh: poll `https://registry.npmjs.org/vskill/$V` (the per-version document updates faster than the packument the agent polled for 130s), then `npx -y --prefer-online vskill@$V --version`.
Add RELEASING.md.

## F06 [redundant-work] real=True safe=True save=100->0 :: npm Release re-runs the whole test suite on a commit CI is already testing
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/npm-release.yml
EVIDENCE: npm Release 38917182229 ran 'Test the full package' for 157s (661 files, 6957 tests, Duration 156.08s) on SHA a5fa1a04. CI run 38917170476 on the same SHA started 6s earlier and ran the same suite (unit-full, 176s). Test time is 69% of the 227s release job. The trend is the same: 148-227s across v1.2.0-v1.2.8.
CHANGE: In npm-release.yml:
1. Add `actions: read` to permissions.
2. Replace 'Test the full package' with a step that finds the CI run for the tagged commit: `ID=$(gh run list -R $GITHUB_REPOSITORY --workflow ci.yml --commit $GITHUB_SHA --event push --json databaseId -q '.[0].databaseId')`, retried for up to 90s.
3. Run `gh run watch $ID -R $GITHUB_REPOSITORY --exit-status`, and fail the release if CI fails.
4. If no CI run exists (a tag on a non-main commit), fall back to `npm test -- --maxWorkers=4`.
5. Run checkout and npm ci before the wait, so setup overlaps it.
RISK: The release becomes coupled to CI's job set. If unit-full is ever removed from ci.yml, the release would gate on less. Keep a comment that ties them together.
VERIFIER: The redundancy is real: npm Release (14:36:51) and CI (14:36:45) both ran on a5fa1a04. The saving does not hold on its own, though. CI unit-full took 213s (finished 14:40:22), while the npm job's own test phase took 13+157s (done about 14:39:47). Waiting on CI would have put the publish at about 14:40:22 + 24s, roughly 10s later than today's 14:40:37. The finding pays off only with F08: sharded CI at about 110s gives about 65s.
IMPL: Land F08 first.
npm-release.yml: `permissions: { contents: write, actions: read }`. Replace lines 28-32 with a step that loops for up to 90s on `gh run list -R "$GITHUB_REPOSITORY" --workflow ci.yml --commit "$GITHUB_SHA" --event push --json databaseId -q '.[0].databaseId'`, then runs `gh run watch "$ID" -R "$GITHUB_REPOSITORY" --exit-status`. If no ID is found, fall back to `npm test -- --maxWorkers=4`. Set env GH_TOKEN: ${{ github.token }}.

## F07 [redundant-work] real=True safe=True save=20->20 :: npm Release builds twice (an explicit step, then prepublishOnly)
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/npm-release.yml
EVIDENCE: In job 117027545075, 'Build and validate both published artifacts' ran build + build:eval-ui + release:preflight from 14:39:47 to 14:40:07 (20s). `npm run release` (= `npm publish --ignore-scripts=false`) then ran prepublishOnly, which is build + build:eval-ui + sync-readme-badges + git diff README + release:preflight, again from 14:40:07 to 14:40:29.
CHANGE: Delete the 'Build and validate both published artifacts' step. The publish step's prepublishOnly already builds both artifacts and runs the preflight guard, which ci.yml publish-guard tests.
RISK: A build failure now surfaces inside the publish step, which aborts before upload because prepublishOnly fails first.
VERIFIER: Confirmed. The explicit build ran 14:39:47 to 14:40:07, and prepublishOnly rebuilt everything again 14:40:07 to 14:40:29. `npm run release` passes --ignore-scripts=false, so prepublishOnly does run despite .npmrc ignore-scripts=true.
IMPL: npm-release.yml: delete lines 33-34 ('Build and validate both published artifacts'). prepublishOnly still runs build, build:eval-ui, the badge sync and README diff, and release:preflight before upload.

## F08 [slow-step] real=True safe=True save=110->100 :: CI's full Vitest suite runs on one runner and sets the wall time of every PR, including release PRs
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/ci.yml
EVIDENCE: In CI 38917170476, unit-full took 213s, of which 'Full unit suite' was 176s; every other job finished in 90s or less. CI wall time was 197-224s over the last 15 runs. Vitest timing from the npm job: tests 227.96s, environment 125.18s, prepare 74.79s, collect 53.19s (summed across workers), 156s wall on 4 workers. vitest 3.2.7 supports --shard.
CHANGE: In ci.yml unit-full:
1. Add `strategy: { fail-fast: false, matrix: { shard: [1, 2, 3] } }` and name the job `unit-full (${{ matrix.shard }}/3)`.
2. Run `npx vitest run --reporter=dot --shard=${{ matrix.shard }}/3`.
3. If branch protection or F06 needs a single check name, add a tiny `unit-full` job with `needs: unit-full-shards` that only reports.
Optionally fold the four per-OS jobs (diff-smoke, unit, keys-store-cli, install-smoke) into one job per OS. That removes 9 repeated `npm ci && npm run setup && npm run build` passes of 20-54s each and cuts Windows/macOS runner queueing.
RISK: Shards rebalance as files are added. Tests with hidden cross-file ordering dependencies may surface; that is a real bug, not a regression.
VERIFIER: Confirmed. unit-full took 213s (176s suite) against 90s or less for every other job, and vitest 3.2.7 supports --shard. Each shard keeps about 35-40s of setup (npm ci, setup, build), plus uneven split and per-shard collect overhead, so 3 shards come to about 105-115s. CI wall drops by about 100s. This is not on the desktop release path; it gates PR merges and F06. main has no required checks, so job renames are safe.
IMPL: ci.yml unit-full (lines 116-132):
- Add `name: unit-full (${{ matrix.shard }}/3)` and `strategy: { fail-fast: false, matrix: { shard: [1, 2, 3] } }`.
- Keep `npm run build`, since some tests may import dist/.
- Change the suite step to `npx vitest run --reporter=dot --shard=${{ matrix.shard }}/3`.
Every file still runs in exactly one shard, which keeps the comment's 'nothing can rot unnoticed' guarantee.

## F09 [slow-step] real=True safe=True save=250->220 :: Sidecar Smoke rust-windows runs a redundant cargo check and is always cold; it is the long pole of every release PR
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/sidecar-smoke.yml
EVIDENCE: Job 117029116749 (PR #181) took 517s: cargo check 141s, then `cargo test --no-run` 166s, which rebuilds everything in the test profile and reuses nothing from check's rmeta output, then `cargo test` 32s, which recompiles vskill-desktop again ('Finished test in 29.99s'), plus a 47s cache save. rust-cache logged 'No cache found' for v0-rust-rust-windows-Windows_NT-x64-e70cdc14-610aea19. sidecar-smoke.yml never runs on main, so PR refs have no base cache. Each PR or branch ref saves its own 750 MB cache that nothing reuses: refs/pull/181/merge, fix/e2e-live-platform-token, fix/global-update-and-sort, refs/pull/174/merge and others. This job was what the agent waited on for 361s before it could tag.
CHANGE: In rust-windows:
1. Delete the 'cargo check' and 'cargo test --no-run' steps. Keep one `cargo test --locked -- --nocapture` (RUST_BACKTRACE=1).
2. Add `push: { branches: [main], paths: [same list as pull_request] }` to the triggers so main writes a cache PRs can restore.
3. Set Swatinem `shared-key: rust-windows-debug` and `save-if: ${{ github.ref == 'refs/heads/main' }}`.
4. Pin the toolchain as in F01.
RISK: The `cargo check` step goes away. `cargo test` compiles the same crate plus tests, so no coverage is lost.
VERIFIER: Confirmed: 517s = cargo check 141s + `cargo test --no-run` 166s + `cargo test` 32s (which recompiled vskill-desktop: 'Compiling vskill-desktop' at 14:47:33, 'Finished test in 29.99s') + a 47s cache save. src-tauri has no cfg(not(test)) code, so cargo check finds nothing that cargo test misses.
Cold, without a cache: about 218s saved (141 + ~30 + 47).
With a main-written cache: about 300s saved.
On the release path this overlaps F04, which removes the bump PR, so do not add the two savings together. On ordinary src-tauri PRs it is the long pole.
IMPL: sidecar-smoke.yml lines 140-161: replace the three steps with one step, `cargo test --locked -- --nocapture`, with env CARGO_TERM_COLOR=always and RUST_BACKTRACE=1. Rename the job to 'cargo test src-tauri (windows-latest)'.
Triggers: replace `push: branches: ['fix/**']` (F10) with `push: { branches: [main], paths: [<same 4 paths as pull_request>] }`.
rust-cache: `shared-key: rust-windows-debug` and `save-if: ${{ github.ref == 'refs/heads/main' }}`.
Toolchain pin as in F01. Also see missed M3 (stub prerequisites, about -80s).

## F10 [redundant-work] real=True safe=True save=536->0 :: Sidecar Smoke push trigger on fix/** has no path filter and duplicates the PR run; no workflow cancels superseded runs
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/sidecar-smoke.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/ci.yml
EVIDENCE: These commits ran Sidecar Smoke twice (push + pull_request): 38fdc4ce and c557428e on fix/private-skill-privacy-1.2.1. Today ae6f288e, which only changed .github/workflows/e2e-live-nightly.yml, still ran a full 536s Sidecar Smoke (38917372125) through the unfiltered `push: fix/**` trigger. The pull_request trigger is path-filtered and correctly skipped it. The 60-minute outlier 38857682375 was also push-triggered on fix/global-update-and-sort. ci.yml has no concurrency group: merging #180 and #181 4 seconds apart started two full 13-job CI runs on main (38918864782, 38918874111) and both ran to completion.
CHANGE: 1. sidecar-smoke.yml: remove `push: branches: ['fix/**']`, or give it the same `paths:` list as pull_request. Add `concurrency: { group: sidecar-smoke-${{ github.event.pull_request.number || github.ref }}, cancel-in-progress: true }`.
2. ci.yml: add `concurrency: { group: ci-${{ github.event.pull_request.number || github.ref }}, cancel-in-progress: ${{ github.event_name == 'pull_request' }} }`. Main runs are kept so every merge commit gets a result. On main, also cancel when the newer commit contains the older one; this is optional.
3. Add `timeout-minutes: 15` to the diff-smoke, unit, keys-store-cli and install-smoke jobs. They currently default to 360 minutes.
RISK: Cancelling PR runs hides results for intermediate pushes, which is intended.
VERIFIER: Confirmed. ae6f288e changed only e2e-live-nightly.yml, yet the push trigger ran a full Sidecar Smoke (38917372125, 532s rust-windows), and it showed up in PR #180's checks. ci.yml has no concurrency group (05f5b9a9 and 0eec9613 both ran in full).
The 536s figure is runner time, not release wall-clock. Today it was 0 on the critical path, because PR #181's own rust-windows check finished 106s later. On a fix/** PR that does not touch src-tauri, it removes a ~9-minute check from what the agent waits on.
A concurrency group alone would not dedupe push against pull_request, since they compute different group keys. Removing the push trigger is the real fix.
IMPL: sidecar-smoke.yml: delete lines 21-23 (push fix/**). Add `concurrency: { group: sidecar-smoke-${{ github.event.pull_request.number || github.sha }}, cancel-in-progress: ${{ github.event_name == 'pull_request' }} }`.
ci.yml: add `concurrency: { group: ci-${{ github.event.pull_request.number || github.sha }}, cancel-in-progress: ${{ github.event_name == 'pull_request' }} }`.
Add `timeout-minutes: 15` to diff-smoke, unit, keys-store-cli and install-smoke.

## F11 [reliability-gap] real=True safe=True save=361->0 :: Flaky Windows settings tests caused the 60-minute Sidecar Smoke 'outlier'
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src-tauri/src/preferences/settings.rs
EVIDENCE: Run 38857682375 was two attempts, not a hang (job timeouts are 30/60 min). Attempt 1 (05:48:14-05:55:23) failed in rust-windows:
- test_debounced_writes_collapse_within_250ms (settings.rs:814, left 'system', right 'dark-9');
- test_studio_lifecycle_default_persists_round_trip (settings.rs:981, left 'ask', right 'use-existing').
Attempt 2, started by hand 47 minutes later at 06:42:36, passed in 361s. Wall time was 3628s. Cause: `flush_for_test` only sleeps DEBOUNCE_MS+100 ms (350 ms) on the #[tokio::test] runtime. spawn_debouncer runs on tauri::async_runtime, a different runtime, and writes after its own 250 ms sleep. With 168 tests in parallel on a 4-core Windows runner, that write can land after the assert.
CHANGE: Make the flush deterministic:
1. Add a write counter to SettingsStore: `writes: Arc<tokio::sync::watch::Sender<u64>>` (cfg(test), or always; it is cheap). Pass it into spawn_debouncer and call `send_modify(|n| *n += 1)` after each atomic_write.
2. In flush_for_test, record the current count. Then `tokio::time::timeout(Duration::from_secs(10), rx.wait_for(|n| *n > before)).await.expect("debounced write")`.
Simpler alternative: flush_for_test does `let s = self.state.lock().await.clone(); atomic_write(&self.path, &s).unwrap();`. This keeps the final-value assertions meaningful but no longer proves that the debouncer itself wrote.
RISK: Low. Test-only behavior. The watch channel adds one Arc to the store.
VERIFIER: Confirmed. Attempt 1 (05:48:17-05:55:22) failed with settings.rs:814 and :981 (166 passed, 2 failed). Attempt 2 started at 06:42:40 and passed. It was not a hang and no timeout was missing. flush_for_test sleeps 350ms on the test runtime, while spawn_debouncer runs on tauri::async_runtime.
The proposed counter recipe has a race. If the debounced write lands before flush_for_test reads `before`, then wait_for(n > before) waits for a write that never comes, hits the 10s timeout, and fails spuriously. Wait on a request generation instead.
The typical wall saving is 0. The value is removing flaky reruns: about 425s of runner time plus human latency (47 minutes here).
IMPL: src-tauri/src/preferences/settings.rs (tokio 1.52.2, so watch::Receiver::wait_for is available):
1. Add `requested: Arc<AtomicU64>` and `written: watch::Sender<u64>` (or an Arc of it) to SettingsStore.
2. Change write_tx to `UnboundedSender<u64>`.
3. In set_key, while still holding the state lock: `let g = self.requested.fetch_add(1, SeqCst) + 1; let _ = self.write_tx.send(g);`.
4. spawn_debouncer: track `max_g` from recv plus drained try_recv values, snapshot, atomic_write, then `written.send_replace(max_g)`.
5. flush_for_test: `let target = self.requested.load(SeqCst); let mut rx = self.written.subscribe(); tokio::time::timeout(Duration::from_secs(10), rx.wait_for(|w| *w >= target)).await.expect("debounced write").expect("debouncer alive");`.
reset() writes directly and is unaffected.

## F12 [redundant-work] real=True safe=True save=16->16 :: The desktop sidecar step rebuilds tsc and vite that the previous step just built
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/notarize-dryrun.yml
EVIDENCE: desktop-release.yml runs `npm run build && npm run build:eval-ui`, then build-sidecar*.sh without SKIP_UPSTREAM_BUILD, so each script runs both builds again. The log line '==> Building upstream artifacts (tsc + vite)...' costs linux 16s (14:51:30->14:51:46), mac 16s and win 21s. sidecar-smoke.yml already sets SKIP_UPSTREAM_BUILD=1 for the same scripts. notarize-dryrun.yml has the same duplication.
CHANGE: Add `env: { SKIP_UPSTREAM_BUILD: '1' }` to these steps:
- 'Build sidecar (macOS/Linux)' and 'Build sidecar (Windows)' in desktop-release.yml;
- 'Build sidecar' in notarize-dryrun.yml.
RISK: None. dist/ is built in the immediately preceding step of the same job.
VERIFIER: Confirmed: '==> Building upstream artifacts (tsc + vite)...' at linux 14:51:30 to 14:51:46 (16s), mac 14:51:09 to 14:51:25 (16s) and win 14:51:08 to 14:51:29 (21s). All three scripts honor SKIP_UPSTREAM_BUILD. beforeBuildCommand is empty, so tauri-action does not rebuild the frontend a third time.
IMPL: desktop-release.yml: add `env: { SKIP_UPSTREAM_BUILD: '1' }` to 'Build sidecar (macOS/Linux)' (line 117) and 'Build sidecar (Windows)' (line 127).
notarize-dryrun.yml: add the same env to 'Build sidecar' (line 74).

## F13 [slow-step] real=True safe=False save=35->0 :: Linux apt install costs 24-58s on the critical-path leg
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: 'Install Linux build deps' took 58s today, 39s on v1.0.64 and 24s on v1.0.63. It runs `apt-get update` and installs webkit2gtk-4.1, gtk3, appindicator, rsvg, patchelf, libfuse2, rpm and gnupg, then downloads minisign. Linux is the critical path (F02).
CHANGE: Replace the apt block with `awalsh128/cache-apt-pkgs-action@v1.4.3`, using `packages: libwebkit2gtk-4.1-dev libsoup-3.0-dev libjavascriptcoregtk-4.1-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev patchelf libfuse2 rpm` and `version: 1`. Keep the minisign 0.12 download, but cache /usr/local/bin/minisign with actions/cache keyed on the version. Use the same block in the F18 nightly Linux leg.
RISK: Cached .debs can lag security updates; bump the cache `version` monthly.
VERIFIER: 58s today, but 24-39s on prior releases. The breakdown is apt-get update 18s, download 10s, and unpack/setup plus man-db triggers 24s. After F02, Linux is no longer the critical leg, so the wall saving is about 0. awalsh128/cache-apt-pkgs-action restores files without running maintainer scripts. It is also an extra third-party action inside a `permissions: write-all` workflow that holds Apple, minisign, GPG and R2 secrets, which is not a good trade for about 30s.
IMPL: Lower-risk alternatives for desktop-release.yml lines 67-80:
- Prefix the install with `sudo rm -f /var/lib/man-db/auto-update` (skips man-db triggers).
- Drop `gnupg`, which is preinstalled.
- Drop `rpm` if F02 removes RPM. tauri-bundler writes RPMs with the rpm crate; check this with one run.
- Or start the apt install in the background as the first step (`(sudo apt-get update && sudo apt-get install -y ...) > /tmp/apt.log 2>&1 & echo $! > /tmp/apt.pid`) and wait on it right before tauri-action, so it overlaps npm ci and the sidecar build (~57s).

## F14 [redundant-work] real=True safe=True save=15->15 :: Assets go to the GitHub release twice (tauri-action in every build job, then softprops in publish), and the first upload has failed releases
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: tauri-action uploads to a draft release in each build job: linux 15:03:22-15:03:37 (~15s, on the critical path), mac 14:58:22-14:58:28, win 15:00:20-15:00:25. The publish job's softprops/action-gh-release then uploads the same files again (11s) and renames the release ('Skill Studio …' becomes 'vSkill Desktop …'). Run 33685939907 (v1.0.63) built all three platforms (421-632s) and then all three failed at tauri-action's upload with 'Bad credentials', wasting 776s plus a re-run.
CHANGE: 1. In the tauri-action step, keep only `with: args: --target … --bundles …`. Remove tagName, releaseName, releaseDraft, prerelease and includeUpdaterJson; without tagName or releaseId, tauri-action only builds. Drop GITHUB_TOKEN from that step's env.
2. In the publish job's softprops `files:`, add `release-artifacts/**/*.app.tar.gz` so the GitHub mirror keeps the macOS updater bundle.
3. Keep `draft: false` there. Release creation now happens in exactly one place, after R2 succeeds.
RISK: The GitHub release appears only after all builds finish, not as an early draft. release-desktop.sh's draft cleanup becomes mostly a no-op.
VERIFIER: Confirmed: Linux uploads 15:03:22 to 15:03:37, on the critical leg today. softprops then re-uploads the same assets and renames the release. The live latest.json points only at verified-skill.com/desktop/v1.0.65/* (R2), so changing the GitHub mirror asset names does not affect the updater. One name changes: tauri-action uploads 'Skill.Studio_aarch64.app.tar.gz', while softprops would upload 'Skill.Studio.app.tar.gz'. The gain is about 15s now, and about 5s once Windows is critical.
IMPL: desktop-release.yml lines 296-302: keep only `args: --target ${{ matrix.target }} --bundles ${{ matrix.bundles }}`. Remove tagName, releaseName, releaseDraft, prerelease, includeUpdaterJson, and GITHUB_TOKEN (line 265).
softprops files (lines 482-490): add `release-artifacts/**/*.app.tar.gz`.
release-desktop.sh step 6's `\.app\.tar\.gz\.sig$` pattern still matches. Step 8's draft promotion becomes a no-op.

## F15 [slow-step] real=True safe=True save=40->35 :: The serial publish tail spends 23s installing tools the runner already has and uploads to R2 one file at a time
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/publish-manifest.sh
EVIDENCE: In job 117040178095, 'Install jq + aws-cli + git-cliff' took 23s: apt-get update, then awscli 1.22.34 from jammy, which pulls ghostscript, fonts, python3-botocore and more. 'Publish to Cloudflare R2' took 40s. Its 13 `aws s3 cp` calls run one after another in publish-manifest.sh (upload_with_cache loops at lines ~183-196). The 125 MB AppImage is uploaded twice, at 15:04:55 and again at 15:05:03, because it is both the user-facing file and the updater bundle. This job starts only when the last build finishes, so every second is on the critical path.
CHANGE: 1. desktop-release.yml publish: delete `sudo apt-get update && sudo apt-get install -y jq awscli`. ubuntu-22.04 images ship AWS CLI v2 and jq; add `aws --version; jq --version` as a guard. Keep the git-cliff curl, or cache it.
2. publish-manifest.sh: keep a bash associative array of destination keys already uploaded and skip duplicates in the second loop. Run the uploads in the background: `upload_with_cache … &`, collect PIDs, then `for p in $PIDS; do wait $p || exit 1; done` before 'Step 3 — Assemble latest.json'. Keep the 4a/4b/4c manifest promotion after that, so it stays atomic.
RISK: Parallel uploads must still fail the job if any one fails, which waiting on each PID handles. AWS CLI v2 and v1 flags are compatible for `s3 cp`.
VERIFIER: Confirmed. The apt install took 23s (awscli 1.22.34 plus fonts and ghostscript). PATH on ubuntu-22.04 puts /usr/local/bin (preinstalled AWS CLI v2) ahead of /usr/bin, so the apt v1 install was likely never used. The binary uploads ran serially from 15:04:42.8 to 15:05:13.6 (31s), and the AppImage was uploaded twice to the same key (15:04:55 and 15:05:03). Realistic saving: about 23s + 15-20s.
IMPL: desktop-release.yml lines 451-457: delete `sudo apt-get update && sudo apt-get install -y jq awscli` and add `aws --version; jq --version` as a guard; keep the git-cliff install.
publish-manifest.sh:
- Add `declare -A UPLOADED` and wrap upload_with_cache in `[[ -n "${UPLOADED[$dest]:-}" ]] && return 0; UPLOADED[$dest]=1`.
- Background each upload in Step 2 (`upload_with_cache ... & PIDS+=($!)`).
- Before Step 3, run `for p in "${PIDS[@]}"; do wait "$p" || exit 1; done`.
- Keep steps 4a-4c serial, after the wait.

## F16 [reliability-gap] real=True safe=False save=4000->None :: Credentials fail late or in unused steps; v1.0.62 took 12 attempts over 70 minutes
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: v1.0.62 (run 28981050488): attempts 1-11 (22:47-23:54) all failed at 'macOS — store notarytool credentials'. That step stores an App Store Connect API key profile 'vskill' which tauri-action never uses; it notarizes with APPLE_ID, APPLE_PASSWORD and APPLE_TEAM_ID. Attempt 12 succeeded at 23:57. v1.0.63 (33685939907) failed only after full builds, with 'Bad credentials'. The only signing-key check today is 'secret is non-empty'. Historically, bad keys and passphrases (v1.0.13-v1.0.28) surfaced only at the end of tauri-action, 7-12 minutes in. The 'Diagnose passphrase encoding' step prints SHA-256 hashes of TAURI_SIGNING_PRIVATE_KEY_PASSWORD to the job log.
CHANGE: 1. Add a `preflight` job on ubuntu-22.04 (timeout 5 min) and set `build: needs: preflight`. It:
- strips whitespace from TAURI_SIGNING_PRIVATE_KEY and TAURI_SIGNING_PRIVATE_KEY_PASSWORD (moving the current cleanup here);
- runs `npx -y @tauri-apps/cli@2.12.1 signer sign -k "$KEY" -p "$PW" probe.txt` and verifies the result against the pubkey in tauri.conf.json (base64-decode plugins.updater.pubkey, then `minisign -Vm probe.txt -P`);
- runs `aws s3 ls s3://vskill-desktop/desktop/ --endpoint-url https://$CLOUDFLARE_R2_ACCOUNT_ID.r2.cloudflarestorage.com`;
- base64-decodes APPLE_CERTIFICATE and runs `openssl pkcs12 -in cert.p12 -noout -passin env:APPLE_CERTIFICATE_PASSWORD` to prove the password;
- runs `gh api repos/$GITHUB_REPOSITORY/releases -q length` with GITHUB_TOKEN.
2. Delete the 'Diagnose passphrase encoding' step.
3. Either delete 'macOS — store notarytool credentials' from the build job, or (if F23 is adopted) switch tauri-action to APPLE_API_KEY, APPLE_API_ISSUER and APPLE_API_KEY_PATH, drop APPLE_ID and APPLE_PASSWORD, and validate the key in preflight with `xcrun notarytool history --key … --key-id … --issuer …` on macOS. One Apple credential path, checked up front.
RISK: Preflight adds about 30-40s, but it runs before the matrix and fails fast. The signer CLI version must match the bundler's minisign format; it does, since it is the same @tauri-apps/cli 2.12.1.
VERIFIER: Evidence confirmed. v1.0.62 attempts 1-11 failed at 'macOS — store notarytool credentials' and attempt 12 succeeded. The ASC_* secrets were last set on 2026-05-07, so the failure was transient (the step validates against Apple), and the step is unused because tauri-action notarizes with APPLE_ID/APPLE_PASSWORD. 31 of the last 60 Desktop Release runs failed.
The change as described would break signing:
- GITHUB_ENV is per job, so a separate preflight job cannot hand the whitespace-cleaned key or passphrase to the matrix.
- 'Diagnose passphrase encoding' is also the step that exports the cleaned TAURI_SIGNING_PRIVATE_KEY_PASSWORD. tauri-action deliberately does not re-pull it (lines 273-280), so deleting the step drops the passphrase.
- A serial preflight job also adds about 40-60s (runner pickup plus probes) to every release's critical path.
Typical per-release saving is 0. The 4000s figure is one historical tail event.
IMPL: In each build leg:
- In 'Diagnose passphrase encoding', delete only the SHA-256 echo lines (225-226 and 230). Keep the strip and the GITHUB_ENV export, and rename the step 'Clean signing passphrase'.
- Right after it, add 'Probe updater signing key': `echo probe > /tmp/probe.txt && npx tauri signer sign /tmp/probe.txt`. It uses the local @tauri-apps/cli 2.12.1 and reads TAURI_SIGNING_PRIVATE_KEY/_PASSWORD from env, so no secrets go on argv.
- Then verify with minisign against the base64-decoded plugins.updater.pubkey (Linux has minisign; on mac/win, verify on Linux only or skip). This runs in parallel and fails before the compile.
- Delete 'macOS — store notarytool credentials' (lines 97-108) unless F22 keeps a profile.
Optionally add an R2 `aws s3 ls` probe early in the Linux leg.

## F17 [scan-gap] real=True safe=True save=58->58 :: Nightly signals fail for weeks without anyone being alerted, so release-day agents rediscover them
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/nightly-health.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/release-desktop.sh
EVIDENCE: E2E Live (nightly) failed 100 of 100 runs; the agent counted them at 14:37:49. It now fails explicitly with 'Secret VSKILL_PLATFORM_TOKEN is not set' (38918889741), and that secret does not exist in `gh secret list`. Notarize Dry-Run failed 53 of its last 60 runs; 10-07 to 10-11 died in 17-22s with "component 'rust-std' for target 'universal-apple-darwin' is unavailable". Lighthouse CI failed 22/30 and E2E Lifecycle (nightly) 7/30. Nothing opens an issue or warns before a release; notarize-dryrun only alerts on a duration above 4h.
CHANGE: 1. Add nightly-health.yml with `on: workflow_run: { workflows: ["E2E Live (nightly)", "Notarize Dry-Run (nightly)", "Lighthouse CI", "E2E Lifecycle (nightly)", "Golden Path (regression)", "Sidecar Smoke"], types: [completed] }` and `permissions: issues: write`. On `conclusion == 'failure'` and branch main, open or comment on one issue per workflow (title '<workflow> red on main', label nightly-red) with the run URL and the first ##[error] line from `gh run view --log-failed`. On success, close it.
2. In release-desktop.sh preflight (F05), refuse to tag when the latest main run of notarize-dryrun.yml or sidecar-smoke.yml failed, unless --force.
3. Human action for E2E Live: Anton creates a fine-grained PAT with Contents: read on anton-abyzov/vskill-platform and runs `gh secret set VSKILL_PLATFORM_TOKEN -R anton-abyzov/vskill`. Alternatively, mint an installation token with actions/create-github-app-token from a GitHub App installed on vskill-platform.
RISK: Possible issue noise. One issue per workflow, closed automatically on green, keeps it bounded.
VERIFIER: Confirmed:
- E2E Live failed 60 of the last 60 runs, and the VSKILL_PLATFORM_TOKEN secret does not exist (secret list checked by name only).
- Notarize Dry-Run: 53 failures, 6 successes, 1 cancelled of 60.
- Lighthouse: 52 failures of 60.
- E2E Lifecycle: 9 failures of 60.
Creating the PAT or secret is Anton's action. Sidecar Smoke never runs on main today, so listing it in the workflow_run filter has no effect until F09 adds push:main.
IMPL: New .github/workflows/nightly-health.yml:
- `on: workflow_run: { workflows: [...exact `name:` values...], types: [completed] }`.
- `if: github.event.workflow_run.head_branch == 'main'`.
- `permissions: { issues: write, actions: read }`.
- Dedupe with `gh issue list --label nightly-red --search "\"$NAME red on main\" in:title"`. Comment on failure; close on success.

## F18 [scan-gap] real=True safe=True save=0->0 :: Linux and Windows release builds and bundlers run only at tag time; one nightly would catch breakage early and warm the release cache
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/notarize-dryrun.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: The only release-profile Tauri build on main is the macOS-only notarize-dryrun. Linux bundling (rpm, AppImage via linuxdeploy downloads from GitHub) and Windows bundling (WiX 3.14, NSIS 3.11, nsis_tauri_utils and the WebView2 bootstrapper from go.microsoft.com) are exercised only by a desktop-v* tag. They downloaded 6 external tool archives during today's release, any of which can break the release at minute 10+. Without a main-branch Linux or Windows release build, F01's cache has no writer for those targets. macOS ships aarch64 only: publish-manifest warns every release 'no *x86_64*.app.tar.gz … skipping darwin-x86_64', so Intel Macs receive no updates.
CHANGE: Turn notarize-dryrun.yml into a 3-leg nightly (keep the name or rename it to 'Desktop Build (nightly)'). Keep the macOS leg as is, with shared-key desktop-aarch64-apple-darwin. Add two legs:
- ubuntu-22.04: x86_64-unknown-linux-gnu, deb,rpm,appimage;
- windows-2022: x86_64-pc-windows-msvc, msi,nsis.
Each new leg runs the same install, sidecar (SKIP_UPSTREAM_BUILD=1) and smoke steps as desktop-release.yml, then `npx tauri build --target <t> --bundles <b> --config '{"bundle":{"createUpdaterArtifacts":false}}'` (the pattern from scripts/release/macos-build.sh:77), with GITHUB_OAUTH_CLIENT_ID set and no signing secrets. Use Swatinem `shared-key: desktop-<target>` and `save-if: true`. Also trigger it on push to main for paths src-tauri/** and src-tauri/Cargo.lock. If Intel Macs matter, add a parallel `macos-13` x86_64-apple-darwin leg to desktop-release.yml and set MACOS_ARCH per leg in publish-manifest. A parallel leg costs no wall time; a universal build would need an x64 SEA sidecar plus lipo and doubles macOS compile time.
RISK: About 25 extra runner-minutes per night, mostly on Windows and Linux. Windows and macOS minutes count more on private plans; vskill is public.
VERIFIER: Real gap, and it is the cache writer that F01 needs. The Intel-Mac point is mostly moot: the only DMG is aarch64, so Intel Macs cannot install the app at all. Adding an x86_64 leg would need an x64 SEA sidecar. A push-to-main trigger should run only the Linux and Windows legs, to avoid a notary submission on every push. No direct saving.
IMPL: notarize-dryrun.yml: add jobs `build-linux` (ubuntu-22.04) and `build-windows` (windows-2022) that mirror desktop-release.yml's install, sidecar (SKIP_UPSTREAM_BUILD=1) and smoke steps.
Then run `npx tauri build --target <t> --bundles <b> --config '{"bundle":{"createUpdaterArtifacts":false}}'` with GITHUB_OAUTH_CLIENT_ID: Ov23li6H8OpvPfuhyDEt.
Use rust-cache `shared-key: desktop-<target>` and `save-if: ${{ github.ref == 'refs/heads/main' }}`, with the same pinned toolchain as F01 and no extra CARGO_/RUST env.
Add `push: { branches: [main], paths: ['src-tauri/**'] }` gated to those two jobs (`if: github.event_name != 'push' || matrix.platform != 'macos'`, or use separate jobs).

## F19 [scan-gap] real=True safe=True save=0->0 :: No timing-regression detection; the permanent Rust cache miss and the 5-minute RPM step went unnoticed
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/timing-report.mjs, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/npm-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/notarize-dryrun.yml
EVIDENCE: Desktop Release wall time across releases: 753, 828, 1025, 908, 1006, 1081, 898, 1022, 888, 1519 (2 attempts), 4747 (12 attempts), 776 (failed), 1054, 935, 966s. Every one compiled cold ('No cache found' in v1.0.63/64/65 logs) and every Linux leg spent about 305s in RPM, with nothing flagging either. Notarize Dry-Run records NOTARIZE_DURATION_SECONDS but alerts only above 14400s.
CHANGE: Add scripts/release/timing-report.mjs (zero dependencies, uses `gh api`). It:
- reads `repos/$REPO/actions/runs/$RUN_ID/jobs` for the current run;
- reads the last 5 successful runs of the same workflow file (`gh run list -w <file> --status success -L 6 --json databaseId`);
- compares each job's and each key step's duration with the median (steps: 'Build Tauri app + sign + (macOS) notarize', 'Install Linux build deps', 'Test the full package', 'Full unit suite');
- greps each job log (`gh api repos/$REPO/actions/jobs/<id>/logs`) for rust-cache 'No cache found' and for 'Bundling' timestamps to get per-bundle durations;
- writes a markdown table to $GITHUB_STEP_SUMMARY;
- emits `::warning::` when a value is above 1.3x the median or above a budget (desktop run 600s, Build Tauri 420s, npm release 180s, rpm bundle 60s) or when a cache miss is seen.
Run it as a final job `timing` in desktop-release.yml (`needs: publish`, `if: always()`, actions: read) and as a last step in npm-release.yml. In notarize-dryrun.yml, add a 900s warning budget next to the 4h issue.
RISK: Duration noise from runner variance; the median over 5 runs and a 1.3x threshold keep false alarms low. Warnings are non-blocking.
VERIFIER: Accurate: every recent release compiled cold and spent about 305s in RPM, and nothing flagged either. No direct saving. Keep warnings non-blocking.
IMPL: Implement as described. Run it as a `timing` job with `needs: publish`, `if: always()` and `permissions: { actions: read }`. Parse step durations from `gh api repos/$REPO/actions/runs/$RUN_ID/jobs` rather than downloading full logs where possible; logs are only needed for the 'No cache found' and 'Bundling' timestamps.

## F20 [reliability-gap] real=True safe=True save=0->0 :: The Homebrew cask step fails on every release and the failure is hidden
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/update-brew-cask.sh
EVIDENCE: Publish log 15:05:29: 'Unknown flag: 1.0.65', '##[error]Process completed with exit code 1', masked by `continue-on-error: true`. The workflow calls `update-brew-cask.sh "${GITHUB_REF_NAME#desktop-v}"` positionally, but the script requires `--version --url --sha256`, and without `--tap-dir` it only prints the cask to stdout. It has never updated a tap.
CHANGE: Either delete the 'Update Homebrew Cask (staging tap)' step, or wire it properly:
1. `V=${GITHUB_REF_NAME#desktop-v}; DMG=$(ls release-artifacts/macos-14-artifacts/dmg/*.dmg)`.
2. Run `bash scripts/release/update-brew-cask.sh --version $V --url "https://verified-skill.com/desktop/v$V/Skill%20Studio_${V}_aarch64.dmg" --sha256 $(sha256sum "$DMG" | cut -d' ' -f1) --tap-dir tap`.
3. Before that, check out the tap repo with a token; afterwards commit and push.
4. Remove continue-on-error, so a broken tap update is visible.
RISK: None if deleted. If wired, a tap token becomes another credential to keep valid.
VERIFIER: Confirmed: 'Unknown flag: 1.0.65' and '##[error]Process completed with exit code 1' at 15:05:29, hidden by continue-on-error. Without --tap-dir the script only prints the cask to stdout. Deleting the step is the right call.
IMPL: desktop-release.yml: delete lines 492-500. Leave update-brew-cask.sh in place for a future tap.

## F21 [reliability-gap] real=True safe=True save=0->0 :: The vskill npm publish uses a long-lived NPM_TOKEN, not OIDC trusted publishing
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/npm-release.yml
EVIDENCE: npm-release.yml has `permissions: contents: write` (no `id-token: write`) and `NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}` (the secret was created 2026-09-14). `npm view vskill@1.2.8 dist.attestations` is empty and _npmUser is 'aabyzov', so the publish was token-based with no provenance. The task brief assumed OIDC. An expired or revoked token fails only at the publish step, after about 3.5 minutes of tests.
CHANGE: 1. Add `id-token: write` to permissions.
2. On npmjs.com, add a Trusted Publisher for package vskill: GitHub, anton-abyzov/vskill, workflow npm-release.yml.
3. After setup-node, add `npm install -g npm@11`; trusted publishing needs npm 11.5.1 or newer, and Node 22 bundles npm 10.
4. Remove NODE_AUTH_TOKEN. npm publish then emits provenance automatically.
5. Until then, add `npm whoami --registry https://registry.npmjs.org` right after setup-node, so a dead token fails in about 2s instead of after tests.
6. Bump `actions/setup-node@v4` to v7 to match the other workflows.
RISK: The Trusted Publisher must be configured before the token is removed, or the next release fails at publish. Do it in one PR plus one npmjs.com setting.
VERIFIER: Confirmed: `npm view vskill@1.2.8` shows _npmUser aabyzov and no dist.attestations. The NPM_TOKEN secret was set 2026-09-14, and the workflow has no id-token permission. The track brief's 'OIDC trusted publishing' is wrong for vskill; memory already notes 'vskill still needs its own Trusted Publisher'. specweave's release.yml is the proven template: npm 12.0.2 pinned and no NODE_AUTH_TOKEN, because a stale token makes npm prefer token auth and fail with 401.
IMPL: First, Anton adds the Trusted Publisher on npmjs.com (package vskill, GitHub Actions, anton-abyzov/vskill, workflow npm-release.yml).
Then in npm-release.yml:
- `permissions: { contents: write, id-token: write }`.
- `actions/setup-node@v7` keeping `registry-url`.
- Add a step `npm i -g npm@12.0.2`.
- Remove `NODE_AUTH_TOKEN` from the publish step (lines 37-38).
package.json repository.url (https://github.com/anton-abyzov/vskill) already matches, as provenance requires. Delete the NPM_TOKEN secret after the first green OIDC publish.

## F22 [scan-gap] real=True safe=True save=0->0 :: macOS signing verification never fails the job, and the dry-run tests a different notarization flow than the release
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/notarize-macos.sh
EVIDENCE: The release step 'Verify code signing (macOS)' runs `spctl … "$DMG" || true`. Today it printed 'source=Unnotarized Developer ID' for the shipped DMG, and the job passed. Only the .app inside was notarized (42s) and stapled. The nightly dry-run instead notarizes and staples the DMG too, through scripts/release/notarize-macos.sh (03:09:48->03:10:37, 49s), and gets 'Notarized Developer ID'. So the canary passes on a flow the release never runs.
CHANGE: 1. In desktop-release.yml macOS, after tauri-action, run `bash scripts/release/notarize-macos.sh "$DMG"`. It uses the notarytool profile 'vskill', so keep the store-credentials step and validate it in F16's preflight.
2. Replace the verify step with gating checks: `xcrun stapler validate "…/bundle/macos/Skill Studio.app"`, `spctl -a -t exec -vv "…/Skill Studio.app"`, and `spctl -a -t open --context context:primary-signature -vv "$DMG"`, none with `|| true`.
3. Notarize the DMG before the upload-artifact step.
4. Alternatively, make the dry-run match the release, but then the shipped DMG stays unnotarized.
RISK: Adds about 50s to the macOS leg, which is not the critical path (544s vs 872s Linux). Apple notary outages would now block releases instead of shipping an unnotarized DMG.
VERIFIER: Confirmed: spctl printed 'source=Unnotarized Developer ID' for the shipped DMG at 14:58:29, and `|| true` hides it. The .app was notarized (42s) and stapled. As written, the change conflicts with F16. notarize-macos.sh uses the keychain profile 'vskill', which comes from the store-credentials step that flaked 11 times on v1.0.62. Use the same APPLE_ID/APPLE_PASSWORD/APPLE_TEAM_ID path that tauri-action already uses. The extra ~50s lands on macOS (544s), which stays off the critical path unless F01 and F02 both land.
IMPL: desktop-release.yml macOS, after tauri-action and before 'Upload platform artifacts':
1. `DMG=$(ls src-tauri/target/aarch64-apple-darwin/release/bundle/dmg/*.dmg)`
2. `xcrun notarytool submit "$DMG" --apple-id "$APPLE_ID" --password "$APPLE_PASSWORD" --team-id "$APPLE_TEAM_ID" --wait --timeout 30m`
3. `xcrun stapler staple "$DMG"`
Set env from the same secrets as tauri-action.
Then replace lines 358-364 with gating checks, none with `|| true`: `xcrun stapler validate ".../macos/Skill Studio.app"`, `spctl -a -t exec -vv ".../macos/Skill Studio.app"` and `spctl -a -t open --context context:primary-signature -vv "$DMG"`.
Without F14, softprops overwrites the same-named DMG on the release.

## F23 [slow-step] real=True safe=True save=20->25 :: Windows bundling re-downloads WiX, NSIS and WebView2 every run and builds an MSI almost nobody uses; Windows becomes critical once F02 lands
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src-tauri/tauri.conf.json
EVIDENCE: Windows job 117033363262: MSI 14:59:03.98->14:59:30.57 (27s, including the WiX 3.14 download and the WebView2 bootstrapper from go.microsoft.com LinkId=2124703). NSIS 14:59:30.58->15:00:18.69 (48s, including the NSIS 3.11 and nsis_tauri_utils downloads and the WebView2 bootstrapper a second time). The job is 701s, second only to Linux. GitHub downloads across 20 releases: .msi 47 vs -setup.exe 610 (the updater uses NSIS).
CHANGE: 1. Add an actions/cache step on Windows for `C:\Users\runneradmin\AppData\Local\tauri` (where tauri-bundler keeps WixTools314, NSIS and the WebView2 bootstrapper), keyed on `tauri-tools-${{ runner.os }}-${{ hashFiles('package-lock.json') }}`.
2. Consider `bundles: nsis` for the Windows row and dropping the MSI, together with the publish-manifest/softprops globs and the .msi R2 upload.
3. Optionally measure `bundle.windows.nsis.compression: "zlib"` against the default lzma: faster to build, larger installer.
RISK: Dropping the MSI removes an enterprise-friendly installer. zlib makes the installer roughly 30-50% larger (estimate).
VERIFIER: Tool caching barely helps. The downloads take about 1-2s in total (WiX 14:59:03.99 to 04.89; NSIS, nsis_tauri_utils and WebView2 under 0.5s), so caching the tauri tools directory saves about 2s. The time goes to light.exe (~22s) and makensis LZMA (~47s). Dropping the MSI saves about 27s, and only once Windows is the critical leg (after F02). It also needs a verify-step edit: desktop-release.yml lines 342-344 require an MSI .sig and would fail the job. Downloads over the last ~20 releases: msi 39, setup.exe 322.
IMPL: desktop-release.yml:
- line 37: `bundles: nsis`.
- Delete the `require_any_sig "Windows MSI installer"` block (lines 342-344).
The msi globs in upload-artifact, publish-manifest and softprops can stay. Measure NSIS `"compression": "zlib"` in tauri.conf.json bundle.windows.nsis separately.

## F24 [reliability-gap] real=True safe=True save=8->5 :: Small hygiene items on the release path: unpinned npx tsx, lockfile fallback, full-history checkouts, Node patch drift
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/package.json, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: 1. `generate:agents-json` runs `npx tsx`, but tsx is in neither dependencies nor devDependencies (no node_modules/.bin/tsx). Every build in every job, including the release builds, fetches an unpinned tsx from the registry.
2. The desktop version-sync step falls back to `cargo generate-lockfile` if `cargo update -p vskill-desktop --precise` fails. That would silently re-resolve all ~200 crates at release time to versions CI never tested ('197 unchanged dependencies behind latest').
3. All three build legs check out with `fetch-depth: 0`; only publish needs history, for git-cliff.
4. The SEA sidecar embeds the host Node, which differed by patch today: mac 22.23.2, linux/win 22.23.3.
CHANGE: 1. Add `tsx` pinned in devDependencies (with package-lock.json) so `npx tsx` resolves locally.
2. Replace `|| cargo generate-lockfile` with `|| { echo '::error::cargo update --precise failed'; exit 1; }`.
3. Use the default shallow checkout in build jobs; keep fetch-depth: 0 in publish.
4. Pin `node-version: '22.23.3'` in desktop-release.yml, notarize-dryrun.yml and sidecar-smoke.yml, so all three sidecars embed the same Node.
RISK: Low. Pinning Node needs a deliberate bump for security patches.
VERIFIER: All four confirmed:
- `generate:agents-json` = `npx tsx` with no tsx in package.json and no node_modules/.bin/tsx.
- The `|| cargo generate-lockfile` fallback is at line 170.
- fetch-depth: 0 on the build legs (checkouts take 3-7s, so the time gain is about 2-4s).
- Node drift: mac 22.23.2 vs linux/win 22.23.3.
The main value is supply-chain hygiene (an unpinned tsx fetched in signing-secret jobs), not time.
IMPL: package.json: `npm install --save-dev --save-exact tsx@<current>` (commit package-lock.json). desktop-release.yml line 170: `(cd src-tauri && cargo update -p vskill-desktop --precise "${VERSION}") || { echo '::error::cargo update --precise failed'; exit 1; }`. Remove `fetch-depth: 0` from the build job checkout (line 47-49), but keep it if F04's main-ancestry guard is added (or fetch main explicitly there). Pin `node-version: '22.23.3'` in desktop-release.yml, notarize-dryrun.yml and sidecar-smoke.yml.

## MISSED :: Desktop release was serialized behind the npm release, though it does not consume the npm artifact
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/release-desktop.sh, /Users/antonabyzov/.claude/skills/tauri-desktop-release/SKILL.md
EVIDENCE: v1.2.8 was tagged at 14:36:49, but desktop-v1.0.65 not until 14:49:23. In between the agent did npm verification (registry poll 14:40:52-14:43:02), desktop discovery and the bump PR, all in sequence. build-sidecar*.sh bundle dist/ from the checked-out source, not from npm, and beforeBuildCommand is empty. The two releases are independent. The desktop run took 966s, so tagging both together would have finished it at about 14:53 instead of 15:05:31.
CHANGE: In RELEASING.md and the tauri-desktop-release SKILL.md flow, push both tags from the same origin/main commit right after the merge: `git push https://github.com/anton-abyzov/vskill.git v$V desktop-v$D`. Then watch both runs in parallel (`gh run watch` in two background calls). Together with F04 (no bump PR) and F05 (a working script), desktop end-to-end time becomes CI time.

## MISSED :: Desktop Release runs floating third-party action refs with permissions: write-all and every signing secret
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/notarize-dryrun.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/npm-release.yml
EVIDENCE: desktop-release.yml line 20 sets `permissions: write-all`. It uses `dtolnay/rust-toolchain@stable` (a branch, line 58), `Swatinem/rust-cache@v2` (line 63), `tauri-apps/tauri-action@v0` (line 254) and `softprops/action-gh-release@v2` (line 475). The jobs hold APPLE_CERTIFICATE/_PASSWORD, the TAURI_SIGNING key and passphrase, GPG_PRIVATE_KEY and the CLOUDFLARE_R2 keys. Memory records past supply-chain payload incidents in these repos. A silent tauri-action@v0 update can also change upload behavior in the middle of a release.
CHANGE: 1. Set workflow-level `permissions: { contents: read }`. Give `contents: write` to the publish job only, plus the build job until F14 removes tauri-action's uploads.
2. Pin all four actions to full commit SHAs, with the version in a trailing comment. Use dtolnay with `toolchain: 1.99.1` (see F01).
3. Do the same in notarize-dryrun.yml and npm-release.yml.

## MISSED :: Sidecar Smoke rust-windows builds the real frontend and SEA sidecar only to satisfy tauri-build
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/sidecar-smoke.yml
EVIDENCE: Job 117029116749 spent 68s in 'Build frontend + sidecar (prerequisites for tauri-build)' plus 19s in setup-node before any cargo work. That is about 87s of the 517s long pole on release and src-tauri PRs. No Rust source or test reads the real sidecar or frontend (grep for binaries/, eval-ui, include_str and include_bytes in src-tauri/src found none). The real sidecar is still built and run by the same workflow's 'Sidecar runtime smoke (windows-latest)' job.
CHANGE: In sidecar-smoke.yml rust-windows:
- Delete the actions/setup-node step.
- Replace the prerequisites step with `mkdir -p dist/eval-ui src-tauri/binaries && printf '<!doctype html><title>stub</title>' > dist/eval-ui/index.html && : > src-tauri/binaries/vskill-server-x86_64-pc-windows-msvc.exe`.
tauri-build only copies externalBin and generate_context! embeds frontendDist, so compiling and testing work against stubs.

## MISSED :: Tag-triggered workflows save npm caches that no other ref can read, adding to the 10 GB eviction pressure
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/npm-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: `gh cache list` shows node-cache-Linux-x64-npm-* entries (100 MB each) under refs/tags/v1.2.6, v1.2.7 and v1.2.8, plus per-PR node caches (90-134 MB) and 750 MB rust-windows caches on PR refs (refs/pull/167, 174, 181 and branch refs). Repo usage is 11.24 GB, over the 10 GB cap, so the useful main caches get evicted. npm Release 38917182229 saved its cache at 14:40:33-14:40:35, after missing at 14:36:54 because main's key was created at 14:37:18.
CHANGE: In npm-release.yml and desktop-release.yml, set `cache: ''` on setup-node. Add `actions/cache/restore@<sha>` with `path: ~/.npm` and `key: node-cache-${{ runner.os }}-${{ runner.arch }}-npm-${{ hashFiles('package-lock.json') }}`, so tag runs restore from main and never save. Together with F01's `save-if: false` and F09's `save-if: main`, PR and tag refs stop writing caches.

## MISSED :: F16 and F22 compete over macOS notarization credentials; only one Apple credential path should exist
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/notarize-dryrun.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/notarize-macos.sh
EVIDENCE: tauri-action notarizes the .app with APPLE_ID, APPLE_APP_SPECIFIC_PASSWORD and APPLE_TEAM_ID (desktop-release.yml lines 267-272). The separate 'macOS — store notarytool credentials' step (ASC API key) is unused in the release, but it failed 11 times on v1.0.62 (run 28981050488) and passed on attempt 12 with no secret change. notarize-macos.sh and the nightly dry-run depend on that keychain profile 'vskill'. The nightly therefore validates a credential the release never uses, and the release keeps a flaky step that only the nightly needs.
CHANGE: Choose one path.
Option A, keep the Apple ID: delete the store-credentials step from desktop-release.yml. Change notarize-macos.sh to accept `--apple-id/--password/--team-id` from env when NOTARY_PROFILE is unset, and use that in notarize-dryrun.yml and in F22's DMG notarization.
Option B, move to the ASC API key: set APPLE_API_KEY, APPLE_API_ISSUER and APPLE_API_KEY_PATH for tauri-action and the scripts, and drop APPLE_ID and APPLE_PASSWORD.
Either way the nightly then exercises exactly the release's credential.

## MISSED :: Desktop Release has no concurrency guard on the R2 latest.json promotion
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/publish-manifest.sh
EVIDENCE: desktop-release.yml has no `concurrency:` key. publish-manifest.sh promotes desktop/latest.json in steps 4a-4c (15:05:13.8-15:05:16.8 today). Two desktop tags pushed close together, or a re-run of an older tag, can race. An older run finishing last would roll latest.json back. With M1 or F04, tags get pushed faster and more often.
CHANGE: In desktop-release.yml, add a top-level `concurrency: { group: desktop-release-publish, cancel-in-progress: false }`, or put it on the publish job only. In publish-manifest.sh, before step 4b, refuse to promote when the current desktop/latest.json version is newer than $VERSION (`sort -V`), unless FORCE_ROLLBACK=1. desktop-rollback.yml already covers intentional rollbacks.
