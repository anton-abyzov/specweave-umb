# Shared helpers for scripts/release/*.sh. Source it; do not run it.
# Bash 3.2 compatible: no associative arrays, no mapfile, no ${var,,}.

RELEASE_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UMB="$(cd "$RELEASE_LIB_DIR/../.." && pwd)"
MANIFEST="${RELEASE_MANIFEST:-$UMB/.specweave/release/manifest.json}"
TIMING_PY="$RELEASE_LIB_DIR/timing.py"
RELEASE_STATE="${RELEASE_STATE_FILE:-$UMB/.specweave/state/release-run.json}"

log() { printf '%s\n' "$*" >&2; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }
now_epoch() { date -u +%s; }
now_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }

require_tools() {
  local t
  for t in "$@"; do
    command -v "$t" >/dev/null 2>&1 || die "missing tool: $t"
  done
}

# mf <jq filter> [jq args...]: query the manifest, raw output.
mf() {
  local filter="$1"
  shift
  [ -s "$MANIFEST" ] || die "manifest not found: $MANIFEST"
  jq -r "$@" "$filter" "$MANIFEST"
}

# Directory that holds repositories/: this checkout, or the main worktree
# when this is a linked worktree (repositories/ is not tracked).
repos_base() {
  if [ -n "${SW_REPOS_BASE:-}" ]; then
    printf '%s\n' "$SW_REPOS_BASE"
    return 0
  fi
  if [ -d "$UMB/repositories" ]; then
    printf '%s\n' "$UMB"
    return 0
  fi
  local common
  common="$(cd "$UMB" && git rev-parse --git-common-dir 2>/dev/null)" || {
    printf '%s\n' "$UMB"
    return 0
  }
  (cd "$UMB" && cd "$common/.." && pwd)
}

# repo_field <repo name> <field>
repo_field() {
  mf '.repos[] | select(.name == $n) | .[$f] // empty | if type == "object" or type == "array" then tojson else . end' \
    --arg n "$1" --arg f "$2"
}

repo_abs_path() {
  local rel
  rel="$(repo_field "$1" path)"
  [ -n "$rel" ] || die "unknown repo: $1"
  printf '%s/%s\n' "$(repos_base)" "$rel"
}

# track_field <track> <field>
track_field() {
  mf '.tracks[$t][$f] // empty | if type == "object" or type == "array" then tojson else . end' \
    --arg t "$1" --arg f "$2"
}

track_exists() {
  [ "$(mf '.tracks | has($t)' --arg t "$1")" = "true" ]
}

# expand_tracks <name>: a track id or a group name -> track ids, one per line.
expand_tracks() {
  if track_exists "$1"; then
    printf '%s\n' "$1"
    return 0
  fi
  local out
  out="$(mf '.groups[$g] // empty | .[]' --arg g "$1")"
  [ -n "$out" ] || die "unknown track or group: $1 (see: release.sh tracks)"
  printf '%s\n' "$out"
}

# Known-noise check names (one per line).
noise_checks() {
  mf '.known_noise_checks[]?.name'
}

# Expand a leading ~ in a path.
expand_home() {
  case "$1" in
    "~") printf '%s\n' "$HOME" ;;
    "~/"*) printf '%s/%s\n' "$HOME" "${1#\~/}" ;;
    *) printf '%s\n' "$1" ;;
  esac
}

# Highest version among release tags of <slug> with <prefix> (prefix stripped).
latest_release_version() {
  local slug="$1" prefix="$2"
  gh api "repos/$slug/releases?per_page=50" --jq '.[] | select(.draft == false) | .tag_name' 2>/dev/null |
    awk -v p="$prefix" 'index($0, p) == 1 { v = substr($0, length(p) + 1); if (v ~ /^[0-9]+\.[0-9]+\.[0-9]+$/) print v }' |
    sort -V | tail -1
}

# Version in <file> on the default branch of <slug>.
default_branch_version() {
  local slug="$1" branch="$2" file="$3"
  gh api "repos/$slug/contents/$file?ref=$branch" --jq '.content' 2>/dev/null |
    tr -d '\n' | base64 --decode 2>/dev/null | jq -r '.version // empty' 2>/dev/null
}

next_patch() {
  printf '%s\n' "$1" | awk -F. 'NF == 3 { printf "%d.%d.%d\n", $1, $2, $3 + 1 }'
}

# state_set <track> <phase> [waiting_on] [log] [result]
# Updates .specweave/state/release-run.json (ephemeral, gitignored). Tracks run
# in parallel, so the read-modify-write holds an exclusive lock.
state_set() {
  mkdir -p "$(dirname "$RELEASE_STATE")"
  python3 - "$RELEASE_STATE" "$@" <<'PY'
import fcntl, json, os, sys, tempfile, time
path, track, phase = sys.argv[1], sys.argv[2], sys.argv[3]
extra = sys.argv[4:] + [None] * 3
waiting_on, log_path, result = extra[0], extra[1], extra[2]
now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
lock = open(path + '.lock', 'a')
fcntl.flock(lock, fcntl.LOCK_EX)
try:
    with open(path) as f:
        state = json.load(f)
    if not isinstance(state, dict):
        state = {}
except (OSError, ValueError):
    state = {}
state.setdefault('started_at', now)
tracks = state.setdefault('tracks', {})
entry = tracks.setdefault(track, {})
if entry.get('phase') != phase:
    entry['phase_started_at'] = now
entry['phase'] = phase
entry['updated_at'] = now
if waiting_on is not None:
    entry['waiting_on'] = waiting_on
if log_path:
    entry['log'] = log_path
if result:
    entry['result'] = result
state['updated_at'] = now
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
with os.fdopen(fd, 'w') as f:
    json.dump(state, f, indent=2)
    f.write('\n')
os.replace(tmp, path)
PY
}
