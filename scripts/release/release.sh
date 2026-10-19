#!/bin/bash
# release.sh: one entrypoint for every release track in this umbrella.
#
#   release.sh status [--fetch] [--run]        audit every repo: branch, ahead/behind, open PRs,
#                                               default-branch CI, latest tag vs published version
#   release.sh ship <track|group> [--dry-run] [--plan] [-- <track script args>]
#                                               run the track's release script, then verify,
#                                               then cleanup for that track only
#   release.sh verify <track|group> [--version X]   deterministic post-release checks (no agent)
#   release.sh cleanup <track> [--apply]        remove fully merged worktrees of the track's repo,
#                                               only after verify passes (dry run without --apply)
#   release.sh timing [<timing.py args>]        defaults to `timing.py check`
#   release.sh tracks                           list tracks and groups
#
# Tracks, repos, commands and policy come from .specweave/release/manifest.json.
# status prints JSON on stdout and a table on stderr. Exit codes: 0 ok, 1 failure,
# 2 pending (ship/verify/cleanup: something is still rolling out; run verify again).
# ship --dry-run refuses a track script that has no dry-run option.
# Progress for long runs is written to .specweave/state/release-run.json.
set -euo pipefail
. "$(dirname "$0")/lib.sh"

usage() { sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/release-sh.XXXXXX")"
cleanup_work() { rm -rf "$WORK"; }
trap cleanup_work EXIT

with_timeout() {
  local seconds="$1"
  shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$seconds" "$@"
  else
    perl -e 'alarm shift @ARGV; exec @ARGV or die "exec failed\n"' "$seconds" "$@"
  fi
}

# ---------------------------------------------------------------- verify checks

# emit <name> <kind> <blocking> <status> <detail>: one JSON check result.
emit() {
  jq -cn --arg name "$1" --arg kind "$2" --argjson blocking "$3" --arg status "$4" --arg detail "$5" \
    '{name: $name, kind: $kind, blocking: $blocking, status: $status, detail: $detail}'
}

expand() { printf '%s\n' "${1//\{version\}/$2}"; }

check_npm_version() {
  local pkg latest exact
  pkg="$(jq -r '.package' <<<"$CHECK")"
  latest="$(npm view "$pkg" dist-tags.latest --prefer-online 2>/dev/null)" || latest=""
  if [ -z "$VERSION" ]; then
    C_STATUS=pass; C_DETAIL="latest $latest"; return
  fi
  if [ "$latest" = "$VERSION" ]; then
    C_STATUS=pass; C_DETAIL="$pkg@$latest is latest"; return
  fi
  exact="$(npm view "$pkg@$VERSION" version --prefer-online 2>/dev/null)" || exact=""
  if [ "$exact" = "$VERSION" ]; then
    C_STATUS=fail; C_DETAIL="$pkg@$VERSION is published but latest is ${latest:-unknown}"
  else
    C_STATUS=pending; C_DETAIL="$pkg@$VERSION not on the registry yet (latest ${latest:-unknown})"
  fi
}

check_gh_release() {
  local slug tag body glob missing="" name found
  slug="$(jq -r '.repo' <<<"$CHECK")"
  tag="$(expand "$(jq -r '.tag' <<<"$CHECK")" "$VERSION")"
  if ! body="$(gh release view "$tag" -R "$slug" --json tagName,isDraft,isPrerelease,assets 2>/dev/null)"; then
    C_STATUS=fail; C_DETAIL="no release $tag in $slug"; return
  fi
  if [ "$(jq -r '.isDraft' <<<"$body")" = "true" ]; then
    C_STATUS=pending; C_DETAIL="$tag is still a draft"; return
  fi
  while IFS= read -r glob; do
    [ -n "$glob" ] || continue
    found=0
    while IFS= read -r name; do
      # shellcheck disable=SC2254
      case "$name" in $glob) found=1; break ;; esac
    done < <(jq -r '.assets[].name' <<<"$body")
    [ "$found" -eq 1 ] || missing="$missing $glob"
  done < <(jq -r '.assets // [] | .[]' <<<"$CHECK")
  if [ -n "$missing" ]; then
    C_STATUS=fail; C_DETAIL="$tag lacks assets:$missing"
  else
    C_STATUS=pass; C_DETAIL="$tag published with $(jq '.assets | length' <<<"$body") assets"
  fi
}

check_http() {
  local url want field equals contains code body
  body="$(mktemp "$WORK/http.XXXXXX")"
  url="$(expand "$(jq -r '.url' <<<"$CHECK")" "$VERSION")"
  want="$(jq -r '.status // 200' <<<"$CHECK")"
  field="$(jq -r '.json_field // empty' <<<"$CHECK")"
  equals="$(jq -r '.equals // empty' <<<"$CHECK")"
  contains="$(jq -r '.contains // empty' <<<"$CHECK")"
  code="$(curl -s -m 20 -o "$body" -w '%{http_code}' "$url")" || code="000"
  if [ "$code" != "$want" ]; then
    C_STATUS=fail; C_DETAIL="$url answered HTTP $code, want $want"; return
  fi
  if [ -n "$field" ]; then
    local got
    got="$(jq -r --arg f "$field" '.[$f] // empty | tostring' "$body" 2>/dev/null)" || got=""
    if [ "$got" != "$equals" ]; then
      C_STATUS=fail; C_DETAIL="$field is '${got}', want '$equals'"; return
    fi
  fi
  if [ -n "$contains" ] && ! grep -qF -- "$contains" "$body"; then
    C_STATUS=fail; C_DETAIL="body lacks '$contains'"; return
  fi
  C_STATUS=pass; C_DETAIL="HTTP $code${field:+, $field=$equals}"
}

check_latest_json() {
  local url header code got hdr body
  hdr="$(mktemp "$WORK/lj-hdr.XXXXXX")"
  body="$(mktemp "$WORK/lj-body.XXXXXX")"
  url="$(jq -r '.url' <<<"$CHECK")"
  header="$(jq -r '.header // empty' <<<"$CHECK")"
  code="$(curl -s -m 20 -D "$hdr" -o "$body" -w '%{http_code}' "$url?ts=$(now_epoch)")" || code="000"
  if [ "$code" != "200" ]; then
    C_STATUS=fail; C_DETAIL="$url answered HTTP $code"; return
  fi
  got="$(jq -r '.version // empty' "$body" 2>/dev/null)" || got=""
  tr -d '\r' <"$hdr" >"$hdr.lf"
  if [ -n "$header" ] && ! grep -qiF -- "$header" "$hdr.lf"; then
    C_STATUS=fail; C_DETAIL="missing header '$header' (version $got)"; return
  fi
  if [ -n "$VERSION" ] && [ "$got" != "$VERSION" ]; then
    C_STATUS=fail; C_DETAIL="manifest serves $got, want $VERSION"; return
  fi
  C_STATUS=pass; C_DETAIL="serves $got${header:+ with $header}"
}

check_gh_run() {
  local slug wf branch body status conclusion url
  slug="$(jq -r '.repo' <<<"$CHECK")"
  wf="$(jq -r '.workflow' <<<"$CHECK")"
  branch="$(expand "$(jq -r '.branch' <<<"$CHECK")" "$VERSION")"
  if ! body="$(gh run list -R "$slug" -w "$wf" -b "$branch" -L 1 --json status,conclusion,url 2>/dev/null)"; then
    C_STATUS=fail; C_DETAIL="cannot list $wf runs in $slug"; return
  fi
  if [ "$(jq 'length' <<<"$body")" -eq 0 ]; then
    C_STATUS=skip; C_DETAIL="no $wf run on $branch"; return
  fi
  status="$(jq -r '.[0].status' <<<"$body")"
  conclusion="$(jq -r '.[0].conclusion // ""' <<<"$body")"
  url="$(jq -r '.[0].url' <<<"$body")"
  if [ "$status" != "completed" ]; then
    C_STATUS=pending; C_DETAIL="$wf on $branch is $status: $url"
  elif [ "$conclusion" = "success" ]; then
    C_STATUS=pass; C_DETAIL="$wf on $branch: success"
  else
    C_STATUS=fail; C_DETAIL="$wf on $branch: $conclusion $url"
  fi
}

check_wrangler_deployments() {
  local worker bin out
  worker="$(jq -r '.worker' <<<"$CHECK")"
  bin="$(repo_abs_path "$(track_field "$TRACK" repo)")/node_modules/.bin/wrangler"
  if [ ! -x "$bin" ]; then
    C_STATUS=skip; C_DETAIL="wrangler not installed in the platform checkout"; return
  fi
  mkdir -p "$WORK/wrangler"
  # Run outside the checkout so wrangler writes no cache files into it.
  if ! out="$(cd "$WORK/wrangler" && with_timeout 90 "$bin" deployments list --name "$worker" --json 2>/dev/null)"; then
    C_STATUS=fail; C_DETAIL="wrangler deployments list failed (login?)"; return
  fi
  C_STATUS=pass
  C_DETAIL="$(jq -r 'if type == "array" and length > 0 then (max_by(.created_on)) | "latest deployment \(.id // "?") at \(.created_on // "?")" else "no deployments listed" end' <<<"$out" 2>/dev/null)" ||
    C_DETAIL="deployments listed"
}

check_fleet_endpoint() {
  local url state got st_status st_down st_msg
  url="$(jq -r '.url' <<<"$CHECK")"
  state="$(expand_home "$(jq -r '.state_file // empty' <<<"$CHECK")")"
  got="$(curl -s -m 5 "$url" | jq -r '.serverVersion // empty' 2>/dev/null)" || got=""
  if [ -n "$got" ] && { [ -z "$VERSION" ] || [ "$got" = "$VERSION" ]; }; then
    C_STATUS=pass; C_DETAIL="serverVersion $got"; return
  fi
  if [ -n "$state" ] && [ -f "$state" ]; then
    st_status="$(jq -r '.status // ""' "$state" 2>/dev/null)" || st_status=""
    st_down="$(jq -r '.downloadedVersion // ""' "$state" 2>/dev/null)" || st_down=""
    st_msg="$(jq -r '.message // ""' "$state" 2>/dev/null | cut -c1-120)" || st_msg=""
    if [ -n "$VERSION" ] && [ "$st_down" = "$VERSION" ]; then
      C_STATUS=pending; C_DETAIL="serverVersion ${got:-unreachable}; updater $st_status with $VERSION downloaded: $st_msg"; return
    fi
  fi
  if [ -z "$got" ]; then
    C_STATUS=fail; C_DETAIL="$url unreachable"
  else
    C_STATUS=fail; C_DETAIL="serverVersion $got, want $VERSION"
  fi
}

# resolve_version <track>: the version verify should expect.
resolve_version() {
  local track="$1" how repo slug def file
  how="$(track_field "$track" expect_version)"
  repo="$(track_field "$track" repo)"
  slug="$(repo_field "$repo" slug)"
  def="$(repo_field "$repo" default_branch)"
  case "$how" in
    default_branch_version)
      file="$(repo_field "$repo" version_file)"
      default_branch_version "$slug" "$def" "${file:-package.json}" ;;
    latest_tag:*) latest_release_version "$slug" "${how#latest_tag:}" ;;
    *) printf '\n' ;;
  esac
}

# verify_track <track> <version or ''> <quick 0|1>: prints a JSON result.
verify_track() {
  TRACK="$1"
  VERSION="$2"
  local quick="$3" kind blocking results="$WORK/verify-$1.jsonl"
  [ -n "$VERSION" ] || VERSION="$(resolve_version "$TRACK")"
  : >"$results"
  while IFS= read -r CHECK <&3; do
    kind="$(jq -r '.kind' <<<"$CHECK")"
    blocking="$(jq -r 'if .blocking == false then "false" else "true" end' <<<"$CHECK")"
    C_STATUS=skip
    C_DETAIL=""
    if [ "$quick" -eq 1 ]; then
      case "$kind" in gh_run|gh_release|wrangler_deployments) continue ;; esac
    fi
    case "$kind" in
      npm_version) check_npm_version ;;
      gh_release) check_gh_release ;;
      http) check_http ;;
      latest_json) check_latest_json ;;
      gh_run) check_gh_run ;;
      wrangler_deployments) check_wrangler_deployments ;;
      fleet_endpoint) check_fleet_endpoint ;;
      *) C_STATUS=fail; C_DETAIL="unknown check kind $kind" ;;
    esac
    emit "$(jq -r '.name' <<<"$CHECK")" "$kind" "$blocking" "$C_STATUS" "$C_DETAIL" >>"$results"
  done 3< <(mf '.tracks[$t].verify // [] | .[] | tojson' --arg t "$TRACK")
  jq -s --arg track "$TRACK" --arg version "$VERSION" '
    {track: $track, version: $version, checks: .,
     result: (if any(.[]; .blocking and .status == "fail") then "fail"
              elif any(.[]; .blocking and .status == "pending") then "pending"
              else "pass" end)}' "$results"
}

print_verify_table() {
  jq -r '"\(.track) \(if .version == "" then "" else .version end): \(.result | ascii_upcase)",
         (.checks[] | "  \(.status | ascii_upcase | .[0:4])\(if .blocking then "" else " (info)" end)  \(.name): \(.detail)")' "$1" >&2
}

result_code() {
  case "$(jq -r '.result' "$1")" in pass) return 0 ;; pending) return 2 ;; *) return 1 ;; esac
}

cmd_verify() {
  local target="" version="" track rc=0 one
  while [ $# -gt 0 ]; do
    case "$1" in
      --version) version="${2:?}"; shift 2 ;;
      -*) die "unknown option: $1" ;;
      *) target="$1"; shift ;;
    esac
  done
  [ -n "$target" ] || die "usage: release.sh verify <track|group> [--version X]"
  local tracks
  tracks="$(expand_tracks "$target")"
  if [ -n "$version" ] && [ "$(printf '%s\n' "$tracks" | wc -l | tr -d ' ')" -gt 1 ]; then
    die "--version applies to one track; $target has several"
  fi
  for track in $tracks; do
    verify_track "$track" "$version" 0 >"$WORK/v-$track.json"
    print_verify_table "$WORK/v-$track.json"
    cat "$WORK/v-$track.json"
    one=0
    result_code "$WORK/v-$track.json" || one=$?
    if [ "$one" -eq 1 ]; then rc=1; elif [ "$one" -eq 2 ] && [ "$rc" -eq 0 ]; then rc=2; fi
  done
  return "$rc"
}

# ---------------------------------------------------------------- status

# unique_commits <repo path> <upstream> <branch>: how many commits of <branch>
# have no patch-equivalent in <upstream>. Fails when git cherry fails (missing
# ref, bad branch), so callers never mistake an error for "fully merged".
# No `| grep -q` here: under pipefail an early grep exit can SIGPIPE git and
# flip the result.
unique_commits() {
  local out
  out="$(git -C "$1" cherry "$2" "$3" 2>/dev/null)" || return 1
  printf '%s\n' "$out" | awk '/^\+/ { n++ } END { print n + 0 }'
}

# idle_minutes <worktree>: minutes since its HEAD, index or reflog last changed.
idle_minutes() {
  local gitdir
  gitdir="$(git -C "$1" rev-parse --absolute-git-dir 2>/dev/null)" || return 1
  python3 - "$1" "$gitdir" <<'PY'
import os, sys, time
wt, gitdir = sys.argv[1], sys.argv[2]
paths = [wt] + [os.path.join(gitdir, name) for name in ('HEAD', 'index', os.path.join('logs', 'HEAD'))]
times = [os.path.getmtime(path) for path in paths if os.path.exists(path)]
if not times:
    sys.exit(1)
print(max(0, int((time.time() - max(times)) // 60)))
PY
}

# worktree_rows <repo path>: "path|head|branch|locked" per worktree, main checkout first.
worktree_rows() {
  git -C "$1" worktree list --porcelain 2>/dev/null | awk '
    /^worktree / { if (w != "") print w "|" h "|" b "|" l; w = substr($0, 10); h = ""; b = ""; l = "" }
    /^HEAD / { h = $2 } /^branch / { b = substr($2, 12) } /^locked/ { l = "locked" }
    END { if (w != "") print w "|" h "|" b "|" l }'
}

status_repo() {
  local name="$1" out="$2" slug def path prefix vfile pkg
  slug="$(repo_field "$name" slug)"
  def="$(repo_field "$name" default_branch)"
  path="$(repo_abs_path "$name")"
  prefix="$(repo_field "$name" tag_prefix)"
  vfile="$(repo_field "$name" version_file)"
  pkg="$(repo_field "$name" npm_package)"
  local branch="" dirty=0 ahead=0 behind=0 local_def="" wt_total=0 wt_merged=0 present=false
  if [ -e "$path/.git" ]; then
    present=true
    if [ "$FETCH" -eq 1 ]; then
      if ! git -C "$path" fetch -q origin "$def" 2>/dev/null; then log "warning: fetch failed in $path"; fi
    fi
    branch="$(git -C "$path" symbolic-ref --short -q HEAD 2>/dev/null)" || branch="(detached)"
    dirty="$(GIT_OPTIONAL_LOCKS=0 git -C "$path" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
    local_def="$(git -C "$path" rev-parse -q --verify "refs/remotes/origin/$def" 2>/dev/null)" || local_def=""
    if [ -n "$local_def" ]; then
      local counts
      counts="$(git -C "$path" rev-list --left-right --count "origin/$def...HEAD" 2>/dev/null)" || counts="0 0"
      behind="$(printf '%s\n' "$counts" | awk '{print $1}')"
      ahead="$(printf '%s\n' "$counts" | awk '{print $2}')"
      local wt_path wt_head wt_branch wt_locked wt_n=0 wt_unique
      while IFS='|' read -r wt_path wt_head wt_branch wt_locked <&3; do
        wt_n=$((wt_n + 1))
        [ "$wt_n" -gt 1 ] || continue
        wt_total=$((wt_total + 1))
        if [ -n "$wt_branch" ] && wt_unique="$(unique_commits "$path" "origin/$def" "$wt_branch")" && [ "$wt_unique" -eq 0 ]; then
          wt_merged=$((wt_merged + 1))
        fi
      done 3< <(worktree_rows "$path")
    fi
  fi
  local remote_def prs ci latest="" unreleased="" pkg_version="" published=""
  remote_def="$(gh api "repos/$slug/branches/$def" --jq '.commit.sha' 2>/dev/null)" || remote_def=""
  prs="$(gh pr list -R "$slug" --state open -L 50 --json number,title,isDraft,headRefName,statusCheckRollup 2>/dev/null)" || prs="[]"
  ci="$(gh run list -R "$slug" -b "$def" -L 40 --json workflowName,status,conclusion,databaseId,createdAt 2>/dev/null)" || ci="[]"
  if [ -n "$prefix" ]; then
    latest="$(latest_release_version "$slug" "$prefix")"
    if [ -n "$latest" ]; then
      unreleased="$(gh api "repos/$slug/compare/$prefix$latest...$def" --jq '.ahead_by' 2>/dev/null)" || unreleased=""
    fi
  fi
  [ -z "$vfile" ] || pkg_version="$(default_branch_version "$slug" "$def" "$vfile")"
  [ -z "$pkg" ] || published="$(npm view "$pkg" dist-tags.latest 2>/dev/null)" || published=""
  local actions
  actions="$(mf '.repos[] | select(.name == $n) | if .actions_enabled == false then "false" else "true" end' --arg n "$name")"
  jq -n --arg name "$name" --argjson actions "$actions" --arg slug "$slug" --arg defbranch "$def" --arg path "$path" --argjson present "$present" \
    --arg branch "$branch" --argjson dirty "${dirty:-0}" --argjson ahead "${ahead:-0}" --argjson behind "${behind:-0}" \
    --arg local_def "$local_def" --arg remote_def "$remote_def" --argjson wt_total "$wt_total" --argjson wt_merged "$wt_merged" \
    --argjson prs "$prs" --argjson ci "$ci" --argjson noise "$NOISE" --arg latest "$latest" --arg prefix "$prefix" \
    --arg unreleased "$unreleased" --arg pkg_version "$pkg_version" --arg published "$published" '
    def noisy: ascii_downcase as $n | ($noise | index($n)) != null;
    def red: [.statusCheckRollup[]? | select(((.name // .context // "") | noisy) | not)
              | select((.conclusion // .state // "") | IN("FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "STARTUP_FAILURE"))] | length > 0;
    def pending: [.statusCheckRollup[]? | select((.status // "COMPLETED") != "COMPLETED" or (.state // "") == "PENDING")] | length > 0;
    ($ci | group_by(.workflowName) | map(max_by(.createdAt))) as $latest_runs
    | {name: $name, slug: $slug, default_branch: $defbranch, path: $path, local_checkout: $present, actions_enabled: $actions,
       local: {branch: $branch, dirty_files: $dirty, ahead: $ahead, behind: $behind,
               origin_ref_stale: ($local_def != "" and $remote_def != "" and $local_def != $remote_def),
               worktrees: $wt_total, worktrees_merged_by_patch: $wt_merged},
       open_prs: [$prs[] | {number, title, draft: .isDraft, branch: .headRefName,
                            checks: (if red then "red" elif pending then "pending" else "green" end)}],
       default_branch_ci: [$latest_runs[] | {workflow: .workflowName, status, conclusion, run_id: .databaseId,
                                             noise: (.workflowName | noisy)}],
       latest_tag: (if $latest == "" then null else $prefix + $latest end),
       unreleased_commits: (if $unreleased == "" then null else ($unreleased | tonumber) end),
       version_on_default_branch: (if $pkg_version == "" then null else $pkg_version end),
       npm_latest: (if $published == "" then null else $published end)}' >"$out"
}

print_status_table() {
  local file="$1"
  {
    printf '%-17s %-30s %-9s %-5s %-12s %-26s %-14s %-6s %-9s %-8s %s\n' REPO LOCAL-BRANCH BEHIND/AH DIRTY "PRS open/red" "DEFAULT-BRANCH CI" TAG UNREL VERSION NPM "WORKTREES merged/all"
    jq -r '.repos[] |
      [ .name,
        (if .local_checkout then (.local.branch | .[0:30]) else "(no checkout)" end),
        "\(.local.behind)/\(.local.ahead)\(if .local.origin_ref_stale then "*" else "" end)",
        (.local.dirty_files | tostring),
        "\(.open_prs | length)/\([.open_prs[] | select(.checks == "red")] | length)",
        ([.default_branch_ci[] | select(.status == "completed" and .conclusion != "success" and .conclusion != "skipped" and (.noise | not))] as $bad
          | [.default_branch_ci[] | select(.status != "completed")] as $run
          | if (.actions_enabled | not) then "Actions disabled"
            elif ($bad | length) > 0 then "red: " + ($bad | map(.workflow) | join(",")) | .[0:26]
            elif ($run | length) > 0 then "running: \($run | length)"
            else "ok (\(.default_branch_ci | length) workflows)" end),
        (.latest_tag // "-"), ((.unreleased_commits // "-") | tostring), (.version_on_default_branch // "-"),
        (.npm_latest // "-"), "\(.local.worktrees_merged_by_patch)/\(.local.worktrees)"
      ] | @tsv' "$file" | awk -F'\t' '{ printf "%-17s %-30s %-9s %-5s %-12s %-26s %-14s %-6s %-9s %-8s %s\n", $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11 }'
    printf '\n%-16s %-9s %-8s %s\n' TRACK EXPECTED LIVE DETAIL
    jq -r '.tracks[] | [.track, (if .version == "" then "-" else .version end), .result,
      ([.checks[] | select(.status != "pass")] | if length == 0 then "all live checks pass"
       else map("\(.name): \(.detail)") | join("; ") end)] | @tsv' "$file" |
      awk -F'\t' '{ printf "%-16s %-9s %-8s %s\n", $1, $2, $3, substr($4, 1, 160) }'
    printf '(* local origin ref is behind GitHub; run status --fetch for exact counts)\n'
  } >&2
}

render_run_state() {
  if [ ! -s "$RELEASE_STATE" ]; then
    log "no release run recorded in $RELEASE_STATE"
    return 0
  fi
  jq -r '"release run started \(.started_at), updated \(.updated_at)",
         (.tracks | to_entries[] | "  \(.key): \(.value.phase) since \(.value.phase_started_at)\(if (.value.waiting_on // "") != "" then ", waiting on \(.value.waiting_on)" else "" end)\(if .value.result then ", result \(.value.result)" else "" end)\(if .value.log then " (log \(.value.log))" else "" end)")' "$RELEASE_STATE" >&2
  cat "$RELEASE_STATE"
}

cmd_status() {
  FETCH=0
  local run=0 name track pids=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --fetch) FETCH=1; shift ;;
      --run) run=1; shift ;;
      *) die "unknown option: $1" ;;
    esac
  done
  if [ "$run" -eq 1 ]; then
    render_run_state
    return 0
  fi
  require_tools gh jq git npm curl
  NOISE="$(noise_checks | jq -R 'ascii_downcase' | jq -s .)"
  mkdir -p "$WORK/status"
  for name in $(mf '.repos[].name'); do
    status_repo "$name" "$WORK/status/repo-$name.json" &
    pids="$pids $!"
  done
  for track in $(mf '.groups.all[]'); do
    verify_track "$track" "" 1 >"$WORK/status/track-$track.json" &
    pids="$pids $!"
  done
  local pid failed=0
  for pid in $pids; do
    wait "$pid" || failed=1
  done
  [ "$failed" -eq 0 ] || log "warning: some status probes failed; their entries may be missing"
  jq -n --arg at "$(now_iso)" \
    --slurpfile repos <(for n in $(mf '.repos[].name'); do cat "$WORK/status/repo-$n.json" 2>/dev/null; done) \
    --slurpfile tracks <(for t in $(mf '.groups.all[]'); do cat "$WORK/status/track-$t.json" 2>/dev/null; done) \
    '{generated_at: $at, repos: $repos, tracks: $tracks}' >"$WORK/status.json"
  print_status_table "$WORK/status.json"
  cat "$WORK/status.json"
}

# ---------------------------------------------------------------- cleanup

cmd_cleanup() {
  local track="" apply=0
  while [ $# -gt 0 ]; do
    case "$1" in
      --apply) apply=1; shift ;;
      -*) die "unknown option: $1" ;;
      *) track="$1"; shift ;;
    esac
  done
  [ -n "$track" ] && track_exists "$track" || die "usage: release.sh cleanup <track> [--apply] (a single track)"
  local gate_file="$WORK/gate-$track.json"
  verify_track "$track" "" 0 >"$gate_file"
  print_verify_table "$gate_file"
  local gate=0
  result_code "$gate_file" || gate=$?
  if [ "$gate" -ne 0 ]; then
    log "cleanup $track: refused, verify is $(jq -r .result "$gate_file"); nothing was touched"
    return "$gate"
  fi
  local repo path slug def
  repo="$(track_field "$track" repo)"
  path="$(repo_abs_path "$repo")"
  slug="$(repo_field "$repo" slug)"
  def="$(repo_field "$repo" default_branch)"
  [ -e "$path/.git" ] || die "no checkout at $path"
  git -C "$path" rev-parse -q --verify "refs/remotes/origin/$def" >/dev/null ||
    die "no origin/$def ref in $path; fetch it first (cleanup compares every branch against it)"
  local globs idle_min
  globs="$(mf '.cleanup.protected_globs[]')"
  [ -n "$globs" ] || die "manifest has no cleanup.protected_globs"
  idle_min="$(mf '.cleanup.min_idle_minutes // 30')"
  case "$idle_min" in ''|*[!0-9]*) die "cleanup.min_idle_minutes must be whole minutes" ;; esac
  local out="$WORK/cleanup-$track.jsonl" err="$WORK/wt-$track.err"
  : >"$out"
  local wt head branch locked n=0 rc=0
  while IFS='|' read -r wt head branch locked <&3; do
    n=$((n + 1))
    [ "$n" -gt 1 ] || continue
    local action=keep reason="" base glob protected=0 wt_status="" idle="" unique=""
    base="$(basename "$wt")"
    while IFS= read -r glob; do
      # shellcheck disable=SC2254
      case "$base" in $glob) protected=1 ;; esac
    done <<<"$globs"
    if [ "$protected" -eq 1 ]; then reason="protected (in-flight release pattern)"
    elif [ -n "$locked" ]; then reason="locked"
    elif [ -z "$branch" ]; then reason="detached HEAD"
    elif [ ! -d "$wt" ]; then reason="missing directory (git worktree prune handles it)"
    elif ! wt_status="$(GIT_OPTIONAL_LOCKS=0 git -C "$wt" status --porcelain 2>/dev/null)"; then reason="git status failed"
    elif [ -n "$wt_status" ]; then reason="uncommitted changes"
    elif ! idle="$(idle_minutes "$wt")"; then reason="cannot read worktree activity"
    elif [ "$idle" -lt "$idle_min" ]; then reason="active ${idle} min ago (kept under ${idle_min} min idle)"
    elif ! unique="$(unique_commits "$path" "origin/$def" "$branch")"; then reason="git cherry failed"
    elif [ "$unique" -eq 0 ]; then
      action=remove; reason="no commits outside origin/$def"
    else
      local merged_tip
      merged_tip="$(gh pr list -R "$slug" --head "$branch" --state merged -L 5 --json headRefOid --jq '.[].headRefOid' 2>/dev/null | grep -x "$head" | head -1)" || merged_tip=""
      if [ -n "$merged_tip" ]; then action=remove; reason="PR merged at this exact tip"
      else reason="unmerged commits"
      fi
    fi
    if [ "$action" = remove ] && [ "$apply" -eq 1 ]; then
      if git -C "$path" worktree remove "$wt" 2>"$err"; then
        if git -C "$path" branch -d "$branch" >/dev/null 2>&1 || git -C "$path" branch -D "$branch" >/dev/null 2>&1; then
          action=removed
        else
          action=removed-worktree; reason="$reason; branch $branch kept"
        fi
      else
        action=keep; reason="git worktree remove refused: $(tail -1 "$err")"; rc=1
      fi
    fi
    jq -cn --arg path "$wt" --arg branch "$branch" --arg action "$action" --arg reason "$reason" \
      '{path: $path, branch: $branch, action: $action, reason: $reason}' >>"$out"
  done 3< <(worktree_rows "$path")
  jq -r '"\(.action)\t\(.branch)\t\(.path)\t\(.reason)"' "$out" |
    awk -F'\t' '{ printf "%-16s %-40s %s (%s)\n", $1, substr($2, 1, 40), $3, $4 }' >&2
  log "cleanup $track: $(jq -s '[.[] | select(.action | startswith("remov"))] | length' "$out") to remove of $((n - 1)) worktrees$([ "$apply" -eq 1 ] || printf ' (dry run; pass --apply)')"
  jq -s --arg track "$track" --argjson applied "$([ "$apply" -eq 1 ] && echo true || echo false)" \
    '{track: $track, applied: $applied, worktrees: .}' "$out"
  return "$rc"
}

# ---------------------------------------------------------------- ship

# script_tree <repo> <checkout>: where a track whose manifest says "run_script_from": "origin" runs
# its release script. The local checkout can sit hundreds of commits off origin (studio's did on
# 2026-10-19), and a stale release.sh published 1.0.52 in the old stage order: the fleet waited on a
# release only the private feed had, so no host updated. This keeps one detached tree per repo at
# origin/<default>, synced before every run; the checkout itself is never touched.
script_tree() {
  local repo="$1" checkout="$2" def tree
  def="$(repo_field "$repo" default_branch)"
  def="${def:-main}"
  tree="${RELEASE_SCRIPT_TREES:-$HOME/Projects/github/release-scripts.noindex}/release-script-$repo"
  git -C "$checkout" fetch --quiet origin "$def" >&2 || die "$repo: cannot fetch origin/$def for its release script"
  if [ -e "$tree/.git" ]; then
    git -C "$tree" checkout --quiet --detach --force "origin/$def" >&2 ||
      die "$repo: cannot move $tree to origin/$def"
  else
    mkdir -p "$(dirname "$tree")"
    git -C "$checkout" worktree add --quiet --detach --force "$tree" "origin/$def" >&2 ||
      die "$repo: cannot create the release script tree $tree"
  fi
  log "[$repo] release script from origin/$def at $(git -C "$tree" rev-parse --short HEAD) ($tree)"
  printf '%s\n' "$tree"
}

ship_track() {
  local track="$1" dry="$2" plan="$3"
  shift 3
  local repo path script_rel log_dir log_file start rc=0 arg
  repo="$(track_field "$track" repo)"
  path="$(repo_abs_path "$repo")"
  if [ "$(track_field "$track" run_script_from)" = origin ] && [ "$plan" -eq 0 ]; then
    path="$(script_tree "$repo" "$path")" || exit 1
  fi
  local cmd=()
  while IFS= read -r arg; do cmd+=("$arg"); done < <(mf '.tracks[$t].release[]' --arg t "$track")
  [ ${#cmd[@]} -ge 2 ] || die "track $track has no release command"
  script_rel="${cmd[1]}"
  local args=()
  if [ $# -gt 0 ]; then
    args=("$@")
  else
    while IFS= read -r arg; do
      if [ "$arg" = "{next_patch}" ]; then
        local prefix latest
        prefix="$(repo_field "$repo" tag_prefix)"
        latest="$(latest_release_version "$(repo_field "$repo" slug)" "$prefix")"
        [ -n "$latest" ] || die "$track: cannot find the latest $prefix tag to compute the next version; pass it after --"
        arg="$(next_patch "$latest")"
      fi
      args+=("$arg")
    done < <(mf '.tracks[$t].default_args // [] | .[]' --arg t "$track")
  fi
  local dry_flag="" no_dry=0
  if [ "$dry" -eq 1 ]; then
    dry_flag="$(track_field "$track" dry_run_flag)"
    [ -n "$dry_flag" ] || die "$track: the manifest names no dry_run_flag, so it cannot be dry-run"
    args+=("$dry_flag")
    # An older script that does not parse the flag would take it as a positional
    # argument and run for real, so refuse unless the script mentions it.
    if [ -f "$path/$script_rel" ] && ! grep -qF -- "$dry_flag" "$path/$script_rel"; then no_dry=1; fi
  fi
  local shown="${cmd[*]}${args[*]+ ${args[*]}}"
  if [ "$plan" -eq 1 ]; then
    if [ ! -f "$path/$script_rel" ]; then
      printf '[%s] would run: (cd %s && %s), but %s is missing there: merge its 0925 branch first\n' "$track" "$path" "$shown" "$script_rel"
    elif [ "$no_dry" -eq 1 ]; then
      printf '[%s] would refuse: %s in %s has no %s option, so a dry run would run for real\n' "$track" "$script_rel" "$path" "$dry_flag"
    elif [ "$dry" -eq 1 ]; then
      printf '[%s] would run: (cd %s && %s); a dry run skips verify and cleanup\n' "$track" "$path" "$shown"
    else
      printf '[%s] would run: (cd %s && %s), then verify %s and cleanup %s --apply\n' "$track" "$path" "$shown" "$track" "$track"
    fi
    return 0
  fi
  [ -f "$path/$script_rel" ] || die "$track: $path/$script_rel does not exist; merge the branch that adds it first"
  [ "$no_dry" -eq 0 ] || die "$track: $script_rel has no $dry_flag option; refusing a dry run that would run for real (merge its 0925 branch first)"
  log_dir="$(dirname "$RELEASE_STATE")/release-logs"
  mkdir -p "$log_dir"
  log_file="$log_dir/$track-$(date -u +%Y%m%dT%H%M%SZ).log"
  state_set "$track" ship "" "$log_file"
  log "[$track] $shown (log $log_file)"
  start="$(now_epoch)"
  (cd "$path" && RELEASE_TRACK="$track" "${cmd[@]}" ${args[@]+"${args[@]}"}) 2>&1 | tee -a "$log_file" | sed "s/^/[$track] /" || rc=$?
  local seconds=$(( $(now_epoch) - start ))
  if [ "$dry" -eq 0 ]; then
    if ! python3 "$TIMING_PY" record --repo "$(repo_field "$repo" slug)" --workflow "release.sh" --step "ship $track" \
      --seconds "$seconds" --kind phase --conclusion "$([ "$rc" -eq 0 ] && echo success || echo failure)" >/dev/null; then
      log "warning: timing record for ship $track failed"
    fi
  fi
  if [ "$rc" -ne 0 ]; then
    state_set "$track" failed "" "" "release script exited $rc after ${seconds}s"
    log "[$track] FAILED after ${seconds}s; see $log_file"
    local gate
    while IFS= read -r gate; do [ -z "$gate" ] || log "[$track] manual gate: $gate"; done < <(mf '.tracks[$t].manual_gates // [] | .[]' --arg t "$track")
    return 1
  fi
  if [ "$dry" -eq 1 ]; then
    state_set "$track" done "" "" "dry run ok in ${seconds}s"
    return 0
  fi
  state_set "$track" verify
  verify_track "$track" "" 0 >"$WORK/ship-verify-$track.json"
  print_verify_table "$WORK/ship-verify-$track.json"
  local vr=0
  result_code "$WORK/ship-verify-$track.json" || vr=$?
  if [ "$vr" -eq 2 ]; then
    state_set "$track" verify-pending "" "" "shipped; verify pending"
    log "[$track] shipped; verify still pending. Re-run: release.sh verify $track, then release.sh cleanup $track --apply"
    return 2
  elif [ "$vr" -ne 0 ]; then
    state_set "$track" failed "" "" "shipped but verify failed"
    return 1
  fi
  state_set "$track" cleanup
  # A subshell, so a cleanup that dies cannot turn a shipped, verified track
  # into a failed one.
  local cleaned="cleaned up"
  if ! (cmd_cleanup "$track" --apply) >"$WORK/ship-cleanup-$track.json"; then
    cleaned="cleanup reported a problem (release.sh cleanup $track)"
    log "[$track] cleanup reported a problem; see release.sh cleanup $track"
  fi
  state_set "$track" done "" "" "shipped and verified, $cleaned, in $(( $(now_epoch) - start ))s"
  return 0
}

cmd_ship() {
  local target="" dry=0 plan=0 extra=()
  while [ $# -gt 0 ]; do
    case "$1" in
      --dry-run) dry=1; shift ;;
      --plan) plan=1; shift ;;
      --) shift; extra=("$@"); break ;;
      -*) die "unknown option: $1" ;;
      *) [ -z "$target" ] || die "one track or group at a time"; target="$1"; shift ;;
    esac
  done
  [ -n "$target" ] || die "usage: release.sh ship <track|group> [--dry-run] [--plan] [-- args]"
  [ "$(mf '.policy.release')" = "true" ] || die "manifest policy.release is not true"
  local tracks
  tracks="$(expand_tracks "$target")"
  if [ ${#extra[@]} -gt 0 ] && [ "$(printf '%s\n' "$tracks" | wc -l | tr -d ' ')" -gt 1 ]; then
    die "track script args after -- need a single track"
  fi
  if [ "$target" = "all" ] && [ "$plan" -eq 0 ]; then
    cmd_status >"$WORK/pre-status.json"
  fi
  # One pipeline per repo, run in parallel; tracks sharing a repo run in order.
  # A track whose verify is still pending (exit 2) does not stop the next one.
  local repos repo pids="" names="" track
  repos="$(for track in $tracks; do track_field "$track" repo; done | awk '!seen[$0]++')"
  for repo in $repos; do
    (
      local_rc=0
      for track in $tracks; do
        [ "$(track_field "$track" repo)" = "$repo" ] || continue
        one=0
        ship_track "$track" "$dry" "$plan" ${extra[@]+"${extra[@]}"} || one=$?
        if [ "$one" -eq 2 ]; then
          local_rc=2
        elif [ "$one" -ne 0 ]; then
          local_rc=1
          break
        fi
      done
      exit "$local_rc"
    ) &
    pids="$pids $!"
    names="$names $repo"
  done
  local pid rc=0 i=1 failed="" pending="" w
  for pid in $pids; do
    w=0
    wait "$pid" || w=$?
    if [ "$w" -eq 2 ]; then
      pending="$pending $(printf '%s\n' $names | sed -n "${i}p")"
    elif [ "$w" -ne 0 ]; then
      rc=1
      failed="$failed $(printf '%s\n' $names | sed -n "${i}p")"
    fi
    i=$((i + 1))
  done
  if [ "$rc" -eq 0 ] && [ -n "$pending" ]; then rc=2; fi
  if [ "$plan" -eq 0 ] && [ "$dry" -eq 0 ]; then
    local tc=0
    python3 "$TIMING_PY" check >&2 || tc=$?
    [ "$tc" -ne 2 ] || log "timing: regressions flagged above (report only)"
  fi
  [ -z "$pending" ] || log "ship: verify still pending for:$pending (call release.sh verify, then cleanup --apply)"
  if [ "$rc" -eq 1 ]; then
    log "ship: failed for:$failed (state: release.sh status --run)"
  else
    log "ship: $target finished"
  fi
  return "$rc"
}

cmd_tracks() {
  mf '.tracks | to_entries[] | "\(.key)\t\(.value.repo)\t\(.value.release | join(" ")) \(.value.args_help // "")"' |
    awk -F'\t' '{ printf "%-16s %-18s %s\n", $1, $2, $3 }'
  mf '.groups | to_entries[] | "group \(.key): \(.value | join(", "))"'
}

[ $# -ge 1 ] || { usage >&2; exit 64; }
SUB="$1"
shift
case "$SUB" in
  status) cmd_status "$@" ;;
  ship) require_tools gh jq git; cmd_ship "$@" ;;
  verify) require_tools gh jq curl npm; cmd_verify "$@" ;;
  cleanup) require_tools gh jq git; cmd_cleanup "$@" ;;
  timing) if [ $# -eq 0 ]; then python3 "$TIMING_PY" check; else python3 "$TIMING_PY" "$@"; fi ;;
  tracks) cmd_tracks ;;
  -h|--help|help) usage ;;
  *) usage >&2; exit 64 ;;
esac
