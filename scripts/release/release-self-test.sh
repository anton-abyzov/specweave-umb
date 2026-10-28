#!/bin/bash
# release-self-test.sh: offline checks for `release.sh cleanup`, the tag_drift
# verify check and the order of a group ship.
# Builds a throwaway repo with worktrees, a fixture manifest with no verify
# checks, and stub gh/specweave-studio commands on PATH, then runs cleanup
# --apply against it. Touches nothing outside its temp folder.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
RELEASE_SH="$HERE/release.sh"

T="$(cd "$(mktemp -d "${TMPDIR:-/tmp}/release-self-test.XXXXXX")" && pwd -P)"
trap 'rm -rf "$T"' EXIT

export HOME="$T/home" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.com GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.com
export RELEASE_MANIFEST="$T/manifest.json" SW_REPOS_BASE="$T/base" RELEASE_STATE_FILE="$T/state.json"
mkdir -p "$HOME" "$T/bin" "$T/base"

# Stub gh: `gh api repos/<slug>/releases...` prints $STUB_RELEASES (tag names,
# as the real call's --jq filter would); everything else prints nothing.
cat >"$T/bin/gh" <<'SH'
#!/bin/bash
case "$1 $2" in
  "api repos/"*"/releases"*) [ -z "${STUB_RELEASES:-}" ] || printf '%s\n' $STUB_RELEASES ;;
esac
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

# ---- 8. tag_drift: commits under the watched paths after the newest tag fail verify
fresh_repo
cat >"$T/manifest-drift.json" <<'JSON'
{"repos": [{"name": "fx", "slug": "example/fx", "path": "repo", "default_branch": "main"}],
 "tracks": {"desk": {"repo": "fx", "release": ["true"], "expect_version": "latest_tag:desk-v",
   "verify": [{"name": "drift", "kind": "tag_drift", "tag_prefix": "desk-v", "paths": ["app/", "src/studio*", "package.json"]}]}},
 "groups": {"all": ["desk"]}}
JSON
R="$T/base/repo"
commit_file() { mkdir -p "$R/$(dirname "$1")"; echo "$2" >"$R/$1"; git -C "$R" add "$1"; git -C "$R" commit -q -m "$2"; }
run_drift() { RELEASE_MANIFEST="$T/manifest-drift.json" bash "$RELEASE_SH" verify desk 2>"$T/drift.err" >"$T/drift.json" && echo 0 || echo $?; }
drift_of() { jq -r ".checks[0].$1" "$T/drift.json"; }
commit_file app/main.rs v1
git -C "$R" tag desk-v1.0.1
commit_file docs/readme.md "docs only"
git -C "$R" push -q origin main --tags
export STUB_RELEASES="v9.9.9 desk-v1.0.0 desk-v1.0.1"
check "drift: only unwatched paths changed passes" "0|pass" "$(run_drift)|$(drift_of status)"
check "drift: pass names the tag" yes "$(drift_of detail | grep -q '^current: desk-v1.0.1; 1 commits' && echo yes || echo no)"
commit_file app/ui.ts "touch app"
commit_file src/studio-runtime/x.ts "touch studio"
commit_file package.json "bump package"
commit_file docs/more.md "more docs"
git -C "$R" push -q origin main
git -C "$R" update-ref refs/remotes/origin/main "$(git -C "$R" rev-parse HEAD~4)"
check "drift: watched commits after the tag fail verify" "1|fail" "$(run_drift)|$(drift_of status)"
check "drift: detail counts watched commits and names the tag" yes "$(drift_of detail | grep -q '^stale: 3 of 5 commits on origin/main since newest tag desk-v1.0.1' && echo yes || echo no)"
check "drift: detail names the newest watched commit" yes "$(drift_of detail | grep -q 'newest [0-9a-f]* [0-9-]* bump package' && echo yes || echo no)"
check "drift: counts from origin, not the stale local origin/main" yes "$(drift_of detail | grep -qv 'local refs' && echo yes || echo no)"
check "drift: private fetch refs removed" 0 "$(git -C "$R" for-each-ref refs/release-drift | wc -l | tr -d ' ')"
check "drift: local origin/main left alone" "$(git -C "$R" rev-parse HEAD~4)" "$(git -C "$R" rev-parse refs/remotes/origin/main)"
git -C "$R" tag desk-v1.0.2
git -C "$R" push -q origin --tags
STUB_RELEASES="desk-v1.0.1 desk-v1.0.2"
check "drift: a new tag at the tip passes" "0|pass" "$(run_drift)|$(drift_of status)"
git -C "$R" remote set-url origin "$T/missing.git"
git -C "$R" update-ref refs/remotes/origin/main HEAD
check "drift: fetch failure falls back to local refs" "0|pass|yes" "$(run_drift)|$(drift_of status)|$(drift_of detail | grep -q 'local refs (fetch failed)' && echo yes || echo no)"
STUB_RELEASES=""
check "drift: no release tag fails" "1|fail" "$(run_drift)|$(drift_of status)"
unset STUB_RELEASES

# ---- 9. group ship: a failed track skips the next ones unless they run after a failure
fresh_repo
R="$T/base/repo"
printf '#!/bin/bash\n# accepts --dry-run\nexit 3\n' >"$R/fail.sh"
printf '#!/bin/bash\n# accepts --dry-run\necho "$RELEASE_TRACK" >>"%s/ran"\n' "$T" >"$R/ok.sh"
cat >"$T/manifest-ship.json" <<'JSON'
{"repos": [{"name": "fx", "slug": "example/fx", "path": "repo", "default_branch": "main"}],
 "policy": {"release": true},
 "tracks": {
   "first": {"repo": "fx", "release": ["bash", "fail.sh"], "dry_run_flag": "--dry-run"},
   "dependent": {"repo": "fx", "release": ["bash", "ok.sh"], "dry_run_flag": "--dry-run"},
   "independent": {"repo": "fx", "release": ["bash", "ok.sh"], "dry_run_flag": "--dry-run", "after_failure": "run"}},
 "groups": {"all": ["first", "dependent", "independent"], "grp": ["first", "dependent", "independent"]}}
JSON
rm -f "$T/ran"
ship_rc=0
RELEASE_MANIFEST="$T/manifest-ship.json" bash "$RELEASE_SH" ship grp --dry-run >"$T/ship.out" 2>"$T/ship.err" || ship_rc=$?
check "ship: group still fails when its first track fails" 1 "$ship_rc"
check "ship: independent track runs after the failure" independent "$(cat "$T/ran" 2>/dev/null)"
check "ship: dependent track skipped" yes "$(grep -q '\[dependent\] skipped: first failed' "$T/ship.err" && echo yes || echo no)"
check "ship: failure reported for the repo" yes "$(grep -q 'ship: failed for: fx' "$T/ship.err" && echo yes || echo no)"

printf '\n%d passed, %d failed\n' "$PASSES" "$FAILS"
[ "$FAILS" -eq 0 ]
