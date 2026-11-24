#!/usr/bin/env bash
# 0879 follow-up: living-docs, save and gc must refuse a non-project cwd; greenfield
# detection must not follow symlinks; the discovery directory count must be depth-bounded.
# Runs the nested repo's bin against its emitted dist (npx tsc -p tsconfig.json first).
set -uo pipefail
UMB=$(cd "$(dirname "$0")/../../../.." && pwd -P)
SW="$UMB/repositories/anton-abyzov/specweave"
BIN="$SW/bin/specweave.js"
[ -f "$SW/dist/src/cli/commands/living-docs.js" ] || { echo "dist not built: run npx tsc -p tsconfig.json in $SW"; exit 1; }
T=$(cd "$(mktemp -d "${TMPDIR:-/tmp}/sw-0879-sib-XXXXXX")" && pwd -P); trap 'rm -rf "$T"' EXIT
fail=0; ok() { echo "  ok: $1"; }; bad() { echo "  FAIL: $1"; fail=1; }

# Synthetic "home": bare .specweave/ (like ~/.specweave), a symlink into a 12^3 tree,
# a symlink into a dir with a .js file, and a 30-deep directory chain.
node -e '
const fs=require("fs"),p=require("path");const root=process.argv[1];let n=0;
(function mk(d,l){if(!l)return;for(let i=0;i<12;i++){const q=p.join(d,`d${l}_${i}`);fs.mkdirSync(q,{recursive:true});n++;mk(q,l-1);}})(root,3);
console.log("bigtree dirs:",n);' "$T/bigtree"
mkdir -p "$T/home/.specweave" "$T/home/Documents" "$T/src/pkg"; echo 'console.log(1)' > "$T/src/pkg/app.js"
ln -s "$T/bigtree" "$T/home/escape"; ln -s "$T/src" "$T/home/escape2"
d="$T/home/Documents"; for i in $(seq 1 30); do d="$d/l$i"; done; mkdir -p "$d"

echo "== 1. living-docs from a non-project cwd (bare .specweave/ present), 20 s timeout =="
out=$(cd "$T/home" && timeout 20 node "$BIN" living-docs </dev/null 2>&1); rc=$?
echo "$out" | sed 's/^/  | /'
[ $rc -eq 1 ] && ok "exit 1" || bad "exit $rc"
echo "$out" | grep -q "No SpecWeave project found: no .specweave/config.json in $T/home or any parent directory" && ok "message names cwd and config.json" || bad "message"
echo "$out" | grep -q "specweave init" && ok "remedy" || bad "remedy"

echo "== 2. gc from a non-project cwd =="
out=$(cd "$T/home" && timeout 20 node "$BIN" gc 2>&1); rc=$?
[ $rc -eq 1 ] && ok "exit 1" || bad "exit $rc"
echo "$out" | grep -q "No SpecWeave project found" && ok "message" || bad "message"
out=$(cd "$T/home" && timeout 20 node "$BIN" gc --json 2>&1); rc=$?
if [ $rc -eq 1 ] && printf '%s' "$out" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const j=JSON.parse(s);process.exit(/No SpecWeave project found/.test(j.error)?0:1)})'; then ok "--json: {error} object, exit 1"; else bad "--json (exit $rc)"; fi

echo "== 3. save --dry-run from a non-project cwd holding two nested git repos, 60 s timeout =="
mkdir -p "$T/umb/a/r1" "$T/umb/a/r2"
for r in r1 r2; do git -C "$T/umb/a/$r" init -q && git -C "$T/umb/a/$r" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init; done
out=$(cd "$T/umb" && timeout 60 node "$BIN" save --dry-run --no-push 2>&1); rc=$?
echo "$out" | sed 's/^/  | /'
[ $rc -eq 1 ] && ok "exit 1" || bad "exit $rc"
echo "$out" | grep -q "Not inside a git repository: $T/umb" && ok "message names cwd" || bad "message"
echo "$out" | grep -q "Scanning for repositories" && bad "scanned anyway" || ok "no repository scan"

echo "== 3b. save --dry-run inside an umbrella child repo whose .specweave/ has no config.json =="
mkdir -p "$T/umb2/.specweave"; echo '{}' > "$T/umb2/.specweave/config.json"
git -C "$T/umb2" init -q && git -C "$T/umb2" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
for r in a b; do mkdir -p "$T/umb2/repositories/org/$r/.specweave/state"; git -C "$T/umb2/repositories/org/$r" init -q && git -C "$T/umb2/repositories/org/$r" -c user.email=t@t -c user.name=t commit -q --allow-empty -m init; done
out=$(cd "$T/umb2/repositories/org/a/.specweave" && timeout 60 node "$BIN" save --dry-run --no-push 2>&1); rc=$?
echo "$out" | grep -v "Malware\|malware" | sed 's/^/  | /' | head -6
[ $rc -eq 0 ] && echo "$out" | grep -q "Mode: Workspace (1 repository)" && ok "child repo saved alone" || bad "exit $rc / not single-repo"
echo "$out" | grep -q "Auto-detected" && bad "fanned out to sibling repos" || ok "no fan-out from a child"
out=$(cd "$T/umb2" && timeout 60 node "$BIN" save --dry-run --no-push 2>&1); rc=$?
echo "$out" | grep -q "Auto-detected 2 nested repositories" && ok "umbrella root still fans out" || bad "umbrella root did not fan out (exit $rc)"

echo "== 4. greenfield detection does not follow symlinks (dist) =="
out=$(node -e "import('$SW/dist/src/cli/helpers/init/greenfield-detection.js').then(m=>{const t=Date.now();const r=m.isGreenfieldDetailed('$T/home');console.log(JSON.stringify(r),(Date.now()-t)+'ms');process.exit(r.isGreenfield?0:1)})"); rc=$?
echo "  | $out"
[ $rc -eq 0 ] && ok "greenfield despite escape2 -> app.js and escape -> bigtree" || bad "followed a symlink"

echo "== 5. discovery directory count bounded to the scan depth (dist), 60 s timeout =="
out=$(timeout 60 node -e "import('$SW/dist/src/core/living-docs/discovery.js').then(async m=>{let total=0;const r=await m.runDiscovery('$T/home',[],(_c,t)=>{total=t});console.log('counted',total,'scanned',r.codebaseStats.totalDirs);process.exit(total===r.codebaseStats.totalDirs&&total===16?0:1)})"); rc=$?
echo "  | $out"
[ $rc -eq 0 ] && ok "counted == scanned == 16 (root + 15 levels of the 30-deep chain)" || bad "count/scan mismatch"

echo "== 6. positive: gc --json from the umbrella root (dry run), 120 s timeout =="
out=$(cd "$UMB" && timeout 120 node "$BIN" gc --json 2>&1); rc=$?
if [ $rc -eq 0 ] && echo "$out" | grep -q '"stateDir"'; then ok "runs inside a project"; else bad "exit $rc"; fi

if [ $fail -eq 0 ]; then echo "BLACKBOX-SIBLINGS: PASS"; else echo "BLACKBOX-SIBLINGS: FAIL"; exit 1; fi
