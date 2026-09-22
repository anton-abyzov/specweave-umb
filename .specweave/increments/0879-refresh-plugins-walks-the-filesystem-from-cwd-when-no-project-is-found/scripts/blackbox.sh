#!/usr/bin/env bash
# Black-box proof for 0879: `specweave refresh-plugins` must stop fast (exit 1,
# clear message, no writes) outside a SpecWeave project, and keep working inside one.
# Uses the locally built CLI (bin/specweave.js -> dist/), so run `npx tsc` first.
set -u
UMB=/Users/antonabyzov/Projects/github/specweave-umb
REPO=$UMB/repositories/anton-abyzov/specweave
BIN=$REPO/bin/specweave.js
TMP=$(mktemp -d "${TMPDIR:-/tmp}/sw-0879-XXXXXX")
trap 'rm -rf "$TMP"' EXIT
fail=0
now() { date +%s; }

# The old code walked the cwd tree following symlinks; this link reproduced a
# 9.6 s run (7.8 s system time) with the published 2.2.2 binary.
mkdir -p "$TMP/noproj/deep"
ln -s /System/Library "$TMP/noproj/escape"

echo "== 1. no project: cwd=$TMP/noproj (holds escape -> /System/Library), 20 s timeout"
t0=$(now)
( cd "$TMP/noproj" && timeout 20 node "$BIN" refresh-plugins ) > "$TMP/noproj.log" 2>&1
code=$?
el=$(( $(now) - t0 ))
cat "$TMP/noproj.log"
echo "exit=$code elapsed=${el}s"
[ "$code" -eq 1 ] || { echo "FAIL: expected exit 1"; fail=1; }
[ "$el" -le 2 ] || { echo "FAIL: expected <= 2 s"; fail=1; }
grep -q "No SpecWeave project found" "$TMP/noproj.log" || { echo "FAIL: message missing"; fail=1; }
grep -q "\.specweave/config\.json" "$TMP/noproj.log" || { echo "FAIL: config.json hint missing"; fail=1; }
grep -q "specweave init" "$TMP/noproj.log" || { echo "FAIL: remedy missing"; fail=1; }
for stray in .claude vskill.lock skills-lock.json .specweave; do
  [ ! -e "$TMP/noproj/$stray" ] || { echo "FAIL: wrote $stray into cwd"; fail=1; }
done

echo "== 2. no project, --quiet: no output, still exit 1"
( cd "$TMP/noproj" && timeout 20 node "$BIN" refresh-plugins --quiet ) > "$TMP/quiet.log" 2>&1
code=$?
[ "$code" -eq 1 ] || { echo "FAIL: expected exit 1 (got $code)"; fail=1; }
[ ! -s "$TMP/quiet.log" ] || { echo "FAIL: expected no output:"; cat "$TMP/quiet.log"; fail=1; }

echo "== 3. inside a project: umbrella root, 60 s timeout"
t0=$(now)
( cd "$UMB" && timeout 60 node "$BIN" refresh-plugins ) > "$TMP/umb.log" 2>&1
code=$?
el=$(( $(now) - t0 ))
cat "$TMP/umb.log"
echo "exit=$code elapsed=${el}s"
[ "$code" -eq 0 ] || { echo "FAIL: expected exit 0"; fail=1; }
grep -Eq "sw: (active|installed)" "$TMP/umb.log" || { echo "FAIL: sw not reported"; fail=1; }
[ "$el" -le 15 ] || { echo "FAIL: expected <= 15 s"; fail=1; }

echo "== 4. inside a project: nested repo dir (root resolves upward), 60 s timeout"
t0=$(now)
( cd "$REPO" && timeout 60 node "$BIN" refresh-plugins ) > "$TMP/nested.log" 2>&1
code=$?
el=$(( $(now) - t0 ))
tail -4 "$TMP/nested.log"
echo "exit=$code elapsed=${el}s"
[ "$code" -eq 0 ] || { echo "FAIL: expected exit 0"; fail=1; }
grep -Eq "sw: (active|installed)" "$TMP/nested.log" || { echo "FAIL: sw not reported"; fail=1; }

if [ "$fail" -eq 0 ]; then echo "BLACKBOX: PASS"; else echo "BLACKBOX: FAIL"; fi
exit $fail
