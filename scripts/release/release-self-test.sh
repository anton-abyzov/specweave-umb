#!/bin/bash
# release-self-test.sh: offline checks for `release.sh cleanup` and verify's desktop_app check.
# Builds a throwaway repo with worktrees, a fixture manifest with no verify
# checks, and stub gh/specweave-studio commands on PATH, then runs cleanup
# --apply against it; then runs verify on fixture desktop_app checks against a
# fake app with stub ssh, PlistBuddy, codesign and spctl. Touches nothing outside its temp folder.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
RELEASE_SH="$HERE/release.sh"

T="$(cd "$(mktemp -d "${TMPDIR:-/tmp}/release-self-test.XXXXXX")" && pwd -P)"
trap 'rm -rf "$T"' EXIT

# What release.sh reads from the environment for the desktop_app check, besides HOME: an inventory
# or tool override exported in the calling shell must not point the fixtures elsewhere.
unset STUDIO_FLEET_HOSTS RELEASE_DESKTOP_APP RELEASE_SSH RELEASE_PLISTBUDDY RELEASE_CODESIGN RELEASE_SPCTL
export HOME="$T/home" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.com GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.com
export RELEASE_MANIFEST="$T/manifest.json" SW_REPOS_BASE="$T/base" RELEASE_STATE_FILE="$T/state.json"
mkdir -p "$HOME" "$T/bin" "$T/base"

cat >"$T/bin/gh" <<'SH'
#!/bin/bash
exit 0
SH
# Stub specweave-studio. `db query --base-dir H` prints H/stub-db.jsonl, a plain
# `db query` prints $STUB_DB_FILE; STUB_DB=fail makes every db query fail. After
# the first db query, $STUB_DB_NEXT (a file, or "fail") replaces $STUB_DB_FILE.
# STUB_OWNERS=1 adds `worktree owners --json`, which prints $STUB_OWNERS_FILE.
cat >"$T/bin/specweave-studio" <<'SH'
#!/bin/bash
printf '%s\n' "$*" >>"$STUB_LOG"
case "$*" in
  "--help") printf 'SUBCOMMANDS\n  db           Read the live database.\n'
    [ "${STUB_OWNERS:-0}" = 1 ] && printf '  worktree     Worktree tools.\n'
    exit 0 ;;
  "worktree --help") [ "${STUB_OWNERS:-0}" = 1 ] && printf 'SUBCOMMANDS\n  owners    List owners.\n'
    exit 0 ;;
  "worktree owners --json") [ "${STUB_OWNERS:-0}" = 1 ] || exit 1; cat "$STUB_OWNERS_FILE" ;;
  "db query --base-dir "*) [ "${STUB_DB:-ok}" = fail ] && exit 1; cat "$4/stub-db.jsonl" ;;
  "db query "*) [ "${STUB_DB:-ok}" = fail ] && exit 1
    calls=$(( $(cat "$STUB_LOG.db" 2>/dev/null || echo 0) + 1 )); echo "$calls" >"$STUB_LOG.db"
    file="$STUB_DB_FILE"; [ "$calls" -gt 1 ] && [ -n "${STUB_DB_NEXT:-}" ] && file="$STUB_DB_NEXT"
    [ "$file" = fail ] && exit 1
    cat "$file" ;;
  *) echo "stub: unexpected call: $*" >&2; exit 9 ;;
esac
SH
chmod +x "$T/bin/gh" "$T/bin/specweave-studio"
export PATH="$T/bin:$PATH" STUB_LOG="$T/stub.log"

cat >"$RELEASE_MANIFEST" <<'JSON'
{"repos": [{"name": "fx", "slug": "example/fx", "path": "repo", "default_branch": "main"}],
 "tracks": {"fx": {"repo": "fx", "release": ["true"]}},
 "groups": {"all": ["fx"]},
 "cleanup": {"protected_globs": ["rel-*"], "min_idle_minutes": 0}}
JSON

FAILS=0
PASSES=0
check() {
  local name="$1" want="$2" got="$3"
  if [ "$got" = "$want" ]; then
    PASSES=$((PASSES + 1)); printf 'ok   %s\n' "$name"
  else
    FAILS=$((FAILS + 1)); printf 'FAIL %s: want [%s], got [%s]\n' "$name" "$want" "$got"
  fi
}

# fresh_repo: origin + main checkout at $T/base/repo, with one commit on main.
fresh_repo() {
  rm -rf "$T/origin.git" "$T/base/repo" "$T/wt" "$HOME/.specwithcode"
  : >"$STUB_LOG"; rm -f "$STUB_LOG.db"
  git init -q --bare -b main "$T/origin.git"
  git clone -q "$T/origin.git" "$T/base/repo" 2>/dev/null
  git -C "$T/base/repo" checkout -q -b main
  git -C "$T/base/repo" commit -q --allow-empty -m init
  git -C "$T/base/repo" push -q origin main
  mkdir -p "$T/wt"
}
add_wt() { git -C "$T/base/repo" worktree add -q -b "$2" "$1" main; }
has_branch() { git -C "$T/base/repo" rev-parse -q --verify "refs/heads/$1" >/dev/null && echo yes || echo no; }
run_cleanup() { bash "$RELEASE_SH" cleanup fx --apply 2>"$T/cleanup.err" >"$T/cleanup.json" || true; }
action_of() { jq -r --arg p "$1" '.worktrees[] | select(.path == $p) | .action' "$T/cleanup.json"; }
reason_of() { jq -r --arg p "$1" '.worktrees[] | select(.path == $p) | .reason' "$T/cleanup.json"; }
exists() { [ -d "$1" ] && echo yes || echo no; }
# row <k> <p> <b> <archived>: one db query row; "null" means JSON null.
row() { jq -cn --arg k "$1" --arg p "$2" --arg b "$3" --argjson a "$4" '{k: $k, p: (if $p == "null" then null else $p end), b: (if $b == "null" then null else $b end), archived: $a}'; }


# ---- 1. db query bindings: bound worktree kept, unbound removed, recorded branch kept
fresh_repo
add_wt "$T/wt/bound" bound
add_wt "$T/wt/group/inner" inner
add_wt "$T/wt/free" free
add_wt "$T/wt/recorded" recorded
add_wt "$T/wt/archived" archived-wt
add_wt "$T/wt/project" project-root
add_wt "$T/wt/session" session-cwd
add_wt "$T/wt/outer/nested" nested
add_wt "$T/wt/back\\slash" backslash
ln -s "$T/wt" "$T/wt-link"
export STUB_DB_FILE="$T/db.jsonl"
# The bound folder is recorded through a symlink; "group" holds a nested worktree;
# "recorded" is a branch whose thread folder lives elsewhere and is archived;
# "archived-wt" is the folder of an archived thread, so it is not bound. A project
# root and a running session sit inside two worktrees; "outer" is a project root
# that only contains a worktree, which does not hold it.
{
  row thread "$T/wt-link/bound" bound 0
  row thread "$T/wt/group" null 0
  row thread "$T/elsewhere" recorded 1
  row thread "$T/wt/archived" null 1
  row project "$T/wt/project" null 0
  row session "$T/wt/session/sub" null 0
  row project "$T/wt/outer" null 0
  row thread "$T/wt/back\\slash" null 0
} >"$STUB_DB_FILE"
run_cleanup
check "db: bound worktree kept" "keep|bound to a SpecWithCode thread" "$(action_of "$T/wt/bound")|$(reason_of "$T/wt/bound")"
check "db: bound worktree folder still there" yes "$(exists "$T/wt/bound")"
check "db: bound worktree branch kept" yes "$(has_branch bound)"
check "db: worktree nested in a thread folder kept" keep "$(action_of "$T/wt/group/inner")"
check "db: unbound merged worktree removed" removed "$(action_of "$T/wt/free")"
check "db: unbound merged worktree folder gone" no "$(exists "$T/wt/free")"
check "db: unbound merged branch deleted with -d" no "$(has_branch free)"
check "db: branch recorded by a thread: worktree removed" removed-worktree "$(action_of "$T/wt/recorded")"
check "db: branch recorded by a thread kept" yes "$(has_branch recorded)"
check "db: archived thread folder is not bound" removed "$(action_of "$T/wt/archived")"
check "db: project root worktree kept" "keep|a SpecWithCode project or running agent session uses it" "$(action_of "$T/wt/project")|$(reason_of "$T/wt/project")"
check "db: running session folder kept" keep "$(action_of "$T/wt/session")"
check "db: worktree inside a project root removed" removed "$(action_of "$T/wt/outer/nested")"
check "db: path with a backslash kept" keep "$(action_of "$T/wt/back\\slash")"
check "db: every query asks only for non-deleted rows" 0 "$(grep '^db query' "$STUB_LOG" | grep -vc 'deleted_at IS NULL' | tr -d ' ')"
check "db: bindings read again before each of 4 removals" 5 "$(grep -c '^db query' "$STUB_LOG" | tr -d ' ')"

# ---- 2. worktree owners adds folders; branches still come from db query
fresh_repo
add_wt "$T/wt/owned" owned
add_wt "$T/wt/deleted-owner" deleted-owner
add_wt "$T/wt/recorded" recorded
export STUB_OWNERS=1 STUB_OWNERS_FILE="$T/owners.json"
# The shape the research suggests for `worktree owners`: no branch field.
cat >"$STUB_OWNERS_FILE" <<JSON
[{"path":"$T/wt/owned","realPath":"$T/wt/owned","threadId":"t1","archived":false,"deleted":false,"kind":"thread"},
 {"path":"$T/wt/deleted-owner","realPath":"$T/wt/deleted-owner","threadId":"t2","archived":false,"deleted":true,"kind":"thread"}]
JSON
row thread "$T/wt/recorded-old" recorded 1 >"$STUB_DB_FILE"
run_cleanup
check "owners: folder it lists kept" keep "$(action_of "$T/wt/owned")"
check "owners: deleted thread does not bind" removed "$(action_of "$T/wt/deleted-owner")"
check "owners: branch from db query kept" yes "$(has_branch recorded)"
check "owners: db query still used" yes "$(grep -q '^db query' "$STUB_LOG" && echo yes || echo no)"

# ---- 3. owners output in an unknown shape is ignored; db query still decides
for shape in \
  "{\"worktrees\":[{\"worktreePath\":\"$T/wt/x\",\"branch\":\"x\"}]}" \
  "{\"owners\":[{\"cwd\":\"$T/wt/x\"}]}" \
  "[{\"folder\":\"$T/wt/x\",\"branchName\":\"x\"}]" \
  "[]"; do
  fresh_repo
  add_wt "$T/wt/db-bound" db-bound
  add_wt "$T/wt/x" x
  printf '%s\n' "$shape" >"$STUB_OWNERS_FILE"
  row thread "$T/wt/db-bound" db-bound 0 >"$STUB_DB_FILE"
  run_cleanup
  check "owners unknown shape $shape: db binding kept" keep "$(action_of "$T/wt/db-bound")"
  check "owners unknown shape $shape: warning logged" yes "$(grep -q 'worktree owners gave output cleanup cannot read' "$T/cleanup.err" && echo yes || echo no)"
done
unset STUB_OWNERS

# ---- 4. every SpecWithCode home is read; a home with no database fails closed
fresh_repo
SW="$HOME/.specwithcode"
mkdir -p "$SW/userdata" "$SW/m4/userdata" "$SW/worktrees" "$SW/m4/worktrees" "$SW/m4/scratch" "$SW/other/worktrees"
touch "$SW/userdata/statev2.sqlite" "$SW/m4/userdata/statev2.sqlite"
add_wt "$SW/worktrees/root-bound" root-bound
add_wt "$SW/m4/worktrees/m4-bound" m4-bound
add_wt "$SW/m4/scratch/free" scratch-free
add_wt "$SW/other/worktrees/unread" unread
row thread "$SW/worktrees/root-bound" null 0 >"$SW/stub-db.jsonl"
row thread "$SW/m4/worktrees/m4-bound" null 0 >"$SW/m4/stub-db.jsonl"
run_cleanup
check "homes: thread in the root home keeps its worktree" keep "$(action_of "$SW/worktrees/root-bound")"
check "homes: thread in another home keeps its worktree" keep "$(action_of "$SW/m4/worktrees/m4-bound")"
check "homes: unbound scratch worktree removed" removed "$(action_of "$SW/m4/scratch/free")"
check "homes: home with no database fails closed" "keep|thread bindings unavailable" "$(action_of "$SW/other/worktrees/unread")|$(reason_of "$SW/other/worktrees/unread")"
check "homes: both homes queried" 2 "$(grep '^db query --base-dir' "$STUB_LOG" | awk '{ print $4 }' | sort -u | wc -l | tr -d ' ')"
check "homes: root home queried" yes "$(grep -q "^db query --base-dir $SW " "$STUB_LOG" && echo yes || echo no)"
fresh_repo
mkdir -p "$SW/userdata" "$SW/m4/userdata" "$SW/m4/worktrees"
touch "$SW/userdata/statev2.sqlite" "$SW/m4/userdata/statev2.sqlite"
add_wt "$SW/m4/worktrees/m4-free" m4-free
add_wt "$T/wt/outside" outside
row thread null null 0 >"$SW/m4/stub-db.jsonl"
# The root home has no stub-db.jsonl, so its query fails.
run_cleanup
check "homes: one home unreadable keeps managed worktrees" "keep|thread bindings unavailable" "$(action_of "$SW/m4/worktrees/m4-free")|$(reason_of "$SW/m4/worktrees/m4-free")"
check "homes: one home unreadable keeps every branch" yes "$(has_branch outside)"

# ---- 5. no bindings: keep SpecWithCode folders and every branch
no_studio_path="$(printf '%s' "$PATH" | tr ':' '\n' | while IFS= read -r d; do [ -x "$d/specweave-studio" ] || printf '%s:' "$d"; done)"
for mode in fail unknown missing; do
  fresh_repo
  mkdir -p "$HOME/.specwithcode/m4/worktrees" "$HOME/.specwithcode/m4/scratch" "$HOME/.specwithcode/worktrees"
  add_wt "$HOME/.specwithcode/m4/worktrees/managed" managed
  add_wt "$HOME/.specwithcode/m4/scratch/note" note
  add_wt "$HOME/.specwithcode/worktrees/root" root
  add_wt "$T/wt/outside" outside
  case "$mode" in
    fail) STUB_DB=fail run_cleanup ;;
    unknown) printf '%s\n' "{\"rows\":[{\"p\":\"$T/wt/outside\"}]}" '{"cwd":"/x/a"}' >"$STUB_DB_FILE"; run_cleanup ;;
    missing) PATH="${no_studio_path%:}" run_cleanup ;;
  esac
  check "unavailable ($mode): managed worktree kept" "keep|thread bindings unavailable" "$(action_of "$HOME/.specwithcode/m4/worktrees/managed")|$(reason_of "$HOME/.specwithcode/m4/worktrees/managed")"
  check "unavailable ($mode): scratch worktree kept" keep "$(action_of "$HOME/.specwithcode/m4/scratch/note")"
  check "unavailable ($mode): root home worktree kept" keep "$(action_of "$HOME/.specwithcode/worktrees/root")"
  check "unavailable ($mode): outside worktree removed" removed-worktree "$(action_of "$T/wt/outside")"
  check "unavailable ($mode): outside branch kept" yes "$(has_branch outside)"
done
check "unavailable (missing): stub never called" 0 "$(grep -c . "$STUB_LOG" | tr -d ' ')"

# ---- 6. a thread that binds a worktree during cleanup keeps it
fresh_repo
add_wt "$T/wt/late" late
add_wt "$T/wt/late-fail" late-fail
: >"$STUB_DB_FILE"
row thread "$T/wt/late" null 0 >"$T/db-next.jsonl"
STUB_DB_NEXT="$T/db-next.jsonl" run_cleanup
check "second read: newly bound worktree kept" "keep|bound to a SpecWithCode thread" "$(action_of "$T/wt/late")|$(reason_of "$T/wt/late")"
check "second read: its branch kept" yes "$(has_branch late)"
fresh_repo
add_wt "$T/wt/late-fail" late-fail
: >"$STUB_DB_FILE"
STUB_DB_NEXT=fail run_cleanup
check "second read failed: worktree kept" "keep|thread bindings unavailable on the second read" "$(action_of "$T/wt/late-fail")|$(reason_of "$T/wt/late-fail")"
check "second read failed: folder still there" yes "$(exists "$T/wt/late-fail")"

# ---- 7. dry run reports and touches nothing
fresh_repo
add_wt "$T/wt/recorded" recorded
row thread null recorded 0 >"$STUB_DB_FILE"
bash "$RELEASE_SH" cleanup fx 2>"$T/cleanup.err" >"$T/cleanup.json" || true
check "dry run: would remove, branch noted" "remove|no commits outside origin/main; branch recorded will be kept: a SpecWithCode thread records it" "$(action_of "$T/wt/recorded")|$(reason_of "$T/wt/recorded")"
check "dry run: folder untouched" yes "$(exists "$T/wt/recorded")"

# ---- 8. verify kind desktop_app: the app's version and signature, on this Mac and over the fleet ssh
# Stub PlistBuddy prints the app's Info.plist (here just the version). Stub codesign fails a bundle
# that has Contents/_bad_signature, prints Contents/_requirement as its designated requirement
# (implicit, "# designated => ...", for an ad hoc cdhash one) and satisfies -R=<requirement> only
# when that is it; stub spctl rejects a bundle that has Contents/_rejected. Stub ssh logs its
# arguments and runs the remote /bin/bash -s here, or fails as an unreachable host does for the
# host named in $STUB_SSH_DOWN.
REQ='identifier "com.specweave.studio" and anchor apple generic and certificate 1[field.1.2.840.113635.100.6.2.6] /* exists */ and certificate leaf[field.1.2.840.113635.100.6.1.13] /* exists */ and certificate leaf[subject.OU] = NMCB2JZ7QG'
cat >"$T/bin/fake-plistbuddy" <<'SH'
#!/bin/bash
for last; do :; done
cat "$last" 2>/dev/null || { echo 'Print: Entry, ":CFBundleShortVersionString", Does Not Exist' >&2; exit 1; }
SH
cat >"$T/bin/fake-codesign" <<'SH'
#!/bin/bash
printf '%s\n' "$*" >>"$STUB_LOG.codesign"
for last; do :; done
[ -d "$last" ] || { echo "$last: No such file or directory" >&2; exit 1; }
req="$(cat "$last/Contents/_requirement")"
if [ "$1" = -d ]; then
  echo "Executable=$last/Contents/MacOS/SpecWithCode" >&2
  case "$req" in cdhash*) echo "# designated => $req" ;; *) echo "designated => $req" ;; esac
  exit 0
fi
[ ! -e "$last/Contents/_bad_signature" ] || { echo "$last: a sealed resource is missing or invalid" >&2; exit 1; }
for arg; do
  case "$arg" in
    -R=*) [ "${arg#-R=}" = "$req" ] || { echo "$last: test-requirement: code failed to satisfy specified code requirement(s)" >&2; exit 3; } ;;
  esac
done
SH
cat >"$T/bin/fake-spctl" <<'SH'
#!/bin/bash
printf '%s\n' "$*" >>"$STUB_LOG.spctl"
for last; do :; done
[ ! -e "$last/Contents/_rejected" ] || { echo "$last: rejected" >&2; exit 3; }
echo "$last: accepted" >&2
SH
cat >"$T/bin/fake-ssh" <<'SH'
#!/bin/bash
printf '%s\n' "$*" >>"$STUB_LOG.ssh"
for arg; do case "$arg" in *@*) dest="$arg" ;; esac; done
if [ -n "${STUB_SSH_DOWN:-}" ] && [ "${dest#*@}" = "$STUB_SSH_DOWN" ]; then
  echo "ssh: connect to host $STUB_SSH_DOWN port 22: Connection refused" >&2
  exit 255
fi
exec /bin/bash -s
SH
chmod +x "$T/bin/fake-plistbuddy" "$T/bin/fake-codesign" "$T/bin/fake-spctl" "$T/bin/fake-ssh"
APP="$T/Applications/SpecWithCode.app"
FLEET="$HOME/.local/share/specweave/fleet"
mkdir -p "$FLEET"
cat >"$FLEET/hosts.json" <<'JSON'
{"m1": {"host": "m1.example", "user": "tester", "home": "/Users/tester"},
 "m3": {"host": "-oProxyCommand=false", "user": "tester", "home": "/Users/tester"}}
JSON
# make_app <version> [bad|adhoc|other-team|rejected]: the fake app on every Mac (one path: the stub
# ssh runs here), signed with the release's requirement unless an ad hoc or another team's signature.
make_app() {
  rm -rf "$APP"
  mkdir -p "$APP/Contents"
  printf '%s\n' "$1" >"$APP/Contents/Info.plist"
  case "${2:-}" in
    adhoc) printf '%s' 'cdhash H"4b875ae6a9aaacdc06ace70c099c02314025eb66"' >"$APP/Contents/_requirement" ;;
    other-team) printf '%s' "${REQ%NMCB2JZ7QG}ABCDE12345" >"$APP/Contents/_requirement" ;;
    *) printf '%s' "$REQ" >"$APP/Contents/_requirement" ;;
  esac
  [ "${2:-}" != bad ] || touch "$APP/Contents/_bad_signature"
  [ "${2:-}" != rejected ] || touch "$APP/Contents/_rejected"
}
# verify_app <host> [version] [requirement]: `release.sh verify` on a track with one desktop_app
# check and desktop_app.requirement (default $REQ; "none" leaves it out); sets APP_RC, APP_STATUS
# and APP_DETAIL.
verify_app() {
  jq -n --arg host "$1" --arg req "${3:-$REQ}" '{repos: [{name: "fx", slug: "example/fx", path: "repo", default_branch: "main"}],
    tracks: {apps: ({repo: "fx", release: ["true"], fleet: {ssh_key: "~/.local/share/specweave/fleet/id_ed25519"},
      verify: [{name: "app", kind: "desktop_app", host: $host}]} + (if $req == "none" then {} else {desktop_app: {requirement: $req}} end))}}' \
    >"$T/manifest-apps.json"
  : >"$STUB_LOG.ssh"
  : >"$STUB_LOG.codesign"
  : >"$STUB_LOG.spctl"
  APP_RC=0
  RELEASE_MANIFEST="$T/manifest-apps.json" RELEASE_DESKTOP_APP="$APP" RELEASE_SSH="$T/bin/fake-ssh" \
    RELEASE_PLISTBUDDY="$T/bin/fake-plistbuddy" RELEASE_CODESIGN="$T/bin/fake-codesign" RELEASE_SPCTL="$T/bin/fake-spctl" \
    bash "$RELEASE_SH" verify apps --version "${2:-1.2.3}" >"$T/verify.json" 2>"$T/verify.err" || APP_RC=$?
  APP_STATUS="$(jq -r '.checks[0].status' "$T/verify.json" 2>/dev/null)" || APP_STATUS=""
  APP_DETAIL="$(jq -r '.checks[0].detail' "$T/verify.json" 2>/dev/null)" || APP_DETAIL=""
}
PASS_DETAIL="SpecWithCode.app 1.2.3, signed with the release's designated requirement, accepted by Gatekeeper"
make_app 1.2.3
verify_app local
check "app: this Mac on the release passes" "0|pass|$PASS_DETAIL" "$APP_RC|$APP_STATUS|$APP_DETAIL"
check "app: codesign checks deep and strict" 1 "$(grep -cxF -- "--verify --deep --strict $APP" "$STUB_LOG.codesign" | tr -d ' ')"
check "app: codesign checks the release's requirement" 1 "$(grep -cxF -- "--verify -R=$REQ $APP" "$STUB_LOG.codesign" | tr -d ' ')"
check "app: Gatekeeper assesses it" "-a -t exec $APP" "$(cat "$STUB_LOG.spctl")"
check "app: this Mac is not read over ssh" 0 "$(grep -c . "$STUB_LOG.ssh" | tr -d ' ')"
make_app 1.2.2
verify_app local
check "app: another version fails" "1|fail|SpecWithCode.app on this Mac is 1.2.2, want 1.2.3" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3 bad
verify_app local
check "app: a bad signature fails" "1|fail|SpecWithCode.app 1.2.3 on this Mac fails codesign --verify --deep --strict: $APP: a sealed resource is missing or invalid" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3 adhoc
verify_app local
check "app: an ad hoc build of the release fails" "1|fail|SpecWithCode.app 1.2.3 on this Mac is not signed with the release's designated requirement (it has: none)" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3 other-team
verify_app local
check "app: another team's build of the release fails" "1|fail|SpecWithCode.app 1.2.3 on this Mac is not signed with the release's designated requirement (it has: ${REQ%NMCB2JZ7QG}ABCDE12345)" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3 rejected
verify_app local
check "app: a build Gatekeeper rejects fails" "1|fail|SpecWithCode.app 1.2.3 on this Mac is not accepted by Gatekeeper (spctl -a -t exec): $APP: rejected" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3
verify_app local 1.2.3 none
check "app: a track that names no requirement fails" "1|fail|track apps names no desktop_app.requirement, the designated requirement its app is signed with" "$APP_RC|$APP_STATUS|$APP_DETAIL"
rm -rf "$APP"
verify_app local
check "app: a missing app fails" "1|fail|no $APP on this Mac" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3
verify_app m1
check "app: a worker on the release passes over ssh" "0|pass|$PASS_DETAIL" "$APP_RC|$APP_STATUS|$APP_DETAIL"
check "app: the worker is read over the pinned fleet ssh" \
  "-F /dev/null -i $FLEET/id_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$FLEET/known_hosts -o ConnectTimeout=10 tester@m1.example /bin/bash -s" \
  "$(cat "$STUB_LOG.ssh")"
check "app: the worker's codesign checks the release's requirement" 1 "$(grep -cxF -- "--verify -R=$REQ $APP" "$STUB_LOG.codesign" | tr -d ' ')"
make_app 1.2.2
verify_app m1
check "app: a worker on another version fails" "1|fail|SpecWithCode.app on m1 is 1.2.2, want 1.2.3" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3 bad
verify_app m1
check "app: a worker with a bad signature fails" "1|fail|SpecWithCode.app 1.2.3 on m1 fails codesign --verify --deep --strict: $APP: a sealed resource is missing or invalid" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3 adhoc
verify_app m1
check "app: a worker with an ad hoc build of the release fails" "1|fail|SpecWithCode.app 1.2.3 on m1 is not signed with the release's designated requirement (it has: none)" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3 rejected
verify_app m1
check "app: a worker with a build Gatekeeper rejects fails" "1|fail|SpecWithCode.app 1.2.3 on m1 is not accepted by Gatekeeper (spctl -a -t exec): $APP: rejected" "$APP_RC|$APP_STATUS|$APP_DETAIL"
rm -rf "$APP"
verify_app m1
check "app: a worker without the app fails" "1|fail|no $APP on m1" "$APP_RC|$APP_STATUS|$APP_DETAIL"
make_app 1.2.3
STUB_SSH_DOWN=m1.example verify_app m1
check "app: an unreachable worker fails" "1|fail|m1 unreachable over ssh: ssh: connect to host m1.example port 22: Connection refused" "$APP_RC|$APP_STATUS|$APP_DETAIL"
verify_app m9
check "app: a host missing from the inventory fails" "1|fail|m9 has no host and user in the fleet inventory $FLEET/hosts.json" "$APP_RC|$APP_STATUS|$APP_DETAIL"
verify_app m3
check "app: an inventory host that is not a plain name is refused" "1|fail|m3's host or user in the fleet inventory is not a plain name" "$APP_RC|$APP_STATUS|$APP_DETAIL"
check "app: ...before any ssh" 0 "$(grep -c . "$STUB_LOG.ssh" | tr -d ' ')"
STUDIO_FLEET_HOSTS="$T/no-such-hosts.json" verify_app m1
check "app: no inventory fails" "1|fail|fleet inventory $T/no-such-hosts.json not found, so m1 cannot be reached" "$APP_RC|$APP_STATUS|$APP_DETAIL"
check "app: the studio track checks the M4, M1 and M3 apps" "M4 app=local M1 app=m1 M3 app=m3" \
  "$(jq -r '[.tracks.studio.verify[] | select(.kind == "desktop_app") | "\(.name)=\(.host)"] | join(" ")' "$HERE/../../.specweave/release/manifest.json")"
check "app: ...against the release's designated requirement" "$REQ" \
  "$(jq -r '.tracks.studio.desktop_app.requirement' "$HERE/../../.specweave/release/manifest.json")"

printf '\n%d passed, %d failed\n' "$PASSES" "$FAILS"
[ "$FAILS" -eq 0 ]
