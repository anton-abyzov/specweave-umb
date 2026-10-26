#!/bin/bash
# release-self-test.sh: offline checks for `release.sh cleanup`.
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

cat >"$T/bin/gh" <<'SH'
#!/bin/bash
exit 0
SH
# Stub specweave-studio. STUB_OWNERS=1 adds `worktree owners --json` (prints
# $STUB_OWNERS_FILE); STUB_DB=fail makes `db query` fail, else it prints $STUB_DB_FILE.
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
  "db query "*) [ "${STUB_DB:-ok}" = fail ] && exit 1; cat "$STUB_DB_FILE" ;;
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

# ---- 1. db query bindings: bound worktree kept, unbound removed, recorded branch kept
fresh_repo
add_wt "$T/wt/bound" bound
add_wt "$T/wt/group/inner" inner
add_wt "$T/wt/free" free
add_wt "$T/wt/recorded" recorded
add_wt "$T/wt/archived" archived-wt
ln -s "$T/wt" "$T/wt-link"
export STUB_DB_FILE="$T/db.jsonl"
# The bound folder is recorded through a symlink; "group" holds a nested worktree;
# "recorded" is a branch whose thread folder lives elsewhere and is archived;
# "archived-wt" is the folder of an archived thread, so it is not bound.
cat >"$STUB_DB_FILE" <<EOF
{"p":"$T/wt-link/bound","b":"bound","archived":0}
{"p":"$T/wt/group","b":null,"archived":0}
{"p":"$T/elsewhere","b":"recorded","archived":1}
{"p":"$T/wt/archived","b":null,"archived":1}
EOF
: >"$STUB_LOG"
run_cleanup
check "db: bound worktree kept" "keep|bound to a SpecWithCode thread" "$(action_of "$T/wt/bound")|$(reason_of "$T/wt/bound")"
check "db: bound worktree folder still there" yes "$([ -d "$T/wt/bound" ] && echo yes || echo no)"
check "db: bound worktree branch kept" yes "$(has_branch bound)"
check "db: worktree nested in a thread folder kept" keep "$(action_of "$T/wt/group/inner")"
check "db: unbound merged worktree removed" removed "$(action_of "$T/wt/free")"
check "db: unbound merged worktree folder gone" no "$([ -d "$T/wt/free" ] && echo yes || echo no)"
check "db: unbound merged branch deleted with -d" no "$(has_branch free)"
check "db: branch recorded by a thread: worktree removed" removed-worktree "$(action_of "$T/wt/recorded")"
check "db: branch recorded by a thread kept" yes "$(has_branch recorded)"
check "db: archived thread folder is not bound" removed "$(action_of "$T/wt/archived")"
check "db: query asks only for non-deleted threads" 1 "$(grep -c 'deleted_at IS NULL' "$STUB_LOG" | tr -d ' ')"

# ---- 2. worktree owners preferred when the command exists
fresh_repo
add_wt "$T/wt/owned" owned
add_wt "$T/wt/deleted-owner" deleted-owner
export STUB_OWNERS=1 STUB_DB=fail STUB_OWNERS_FILE="$T/owners.json"
cat >"$STUB_OWNERS_FILE" <<EOF
[{"worktreePath":"$T/wt/owned","branch":"owned","archived":false,"deleted":false},
 {"worktreePath":"$T/wt/deleted-owner","branch":"deleted-owner","deleted":true}]
EOF
: >"$STUB_LOG"
run_cleanup
check "owners: bound worktree kept" keep "$(action_of "$T/wt/owned")"
check "owners: deleted thread does not bind" removed "$(action_of "$T/wt/deleted-owner")"
check "owners: db query not used" 0 "$(grep -c '^db query' "$STUB_LOG" | tr -d ' ')"
unset STUB_OWNERS STUB_DB

# ---- 3. no bindings: keep SpecWithCode folders and every branch
fresh_repo
mkdir -p "$HOME/.specwithcode/m4/worktrees" "$HOME/.specwithcode/m4/scratch"
add_wt "$HOME/.specwithcode/m4/worktrees/managed" managed
add_wt "$HOME/.specwithcode/m4/scratch/note" note
add_wt "$T/wt/outside" outside
export STUB_DB=fail
run_cleanup
check "unavailable: managed worktree kept" "keep|thread bindings unavailable" "$(action_of "$HOME/.specwithcode/m4/worktrees/managed")|$(reason_of "$HOME/.specwithcode/m4/worktrees/managed")"
check "unavailable: scratch worktree kept" keep "$(action_of "$HOME/.specwithcode/m4/scratch/note")"
check "unavailable: outside worktree removed" removed-worktree "$(action_of "$T/wt/outside")"
check "unavailable: outside branch kept" yes "$(has_branch outside)"
unset STUB_DB

# ---- 4. dry run reports and touches nothing
fresh_repo
add_wt "$T/wt/recorded" recorded
printf '{"p":null,"b":"recorded","archived":0}\n' >"$STUB_DB_FILE"
bash "$RELEASE_SH" cleanup fx 2>"$T/cleanup.err" >"$T/cleanup.json" || true
check "dry run: would remove, branch noted" "remove|no commits outside origin/main; branch recorded will be kept: a SpecWithCode thread records it" "$(action_of "$T/wt/recorded")|$(reason_of "$T/wt/recorded")"
check "dry run: folder untouched" yes "$([ -d "$T/wt/recorded" ] && echo yes || echo no)"

printf '\n%d passed, %d failed\n' "$PASSES" "$FAILS"
[ "$FAILS" -eq 0 ]
