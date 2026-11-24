#!/bin/bash
# ci-wait.sh: bounded waits on CI runs, PR checks, tag workflows, npm, URLs and logs.
#
#   ci-wait.sh pr  <repo> <number>|<pr url>          checks on the PR head commit
#   ci-wait.sh run [<repo>] <run id>|<run url>        one workflow run
#   ci-wait.sh tag <repo> <tag> <workflow file>       the run a tag push started
#   ci-wait.sh npm <package> <version>                registry has the version
#   ci-wait.sh url <url> [<substring>] [--status N] [--header 'name: value'] [--fail REGEX]
#   ci-wait.sh log <file> --ok REGEX [--ok-count N] --fail REGEX [--fail-count N]
#
# Options: --budget SECONDS (default 540, under the 600s tool cap), --ignore NAME
# (extra noise check, repeatable), --fail-fast (run mode: stop on the first failed
# job), --no-record (skip timing records), --repo SLUG.
#
# Exit codes: 0 success, 1 failure (prints failing jobs and a log tail),
# 2 still pending when the budget ran out: call it again.
# <repo> is owner/name, a GitHub URL, or a repo name from .specweave/release/manifest.json.
# GitHub polls send If-None-Match, so unchanged answers (304) do not use rate limit.
set -euo pipefail
. "$(dirname "$0")/lib.sh"

usage() { sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; }

[ $# -ge 1 ] || { usage >&2; exit 64; }
MODE="$1"
shift
case "$MODE" in -h|--help|help) usage; exit 0 ;; esac

BUDGET=""
FAIL_FAST=0
RECORD=1
REPO_OPT=""
OK_RE=""
FAIL_RE=""
OK_COUNT=1
FAIL_COUNT=1
WANT_STATUS=""
WANT_HEADER=""
IGNORE=()
POS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --budget) BUDGET="${2:?--budget needs seconds}"; shift 2 ;;
    --ignore) IGNORE+=("${2:?--ignore needs a name}"); shift 2 ;;
    --fail-fast) FAIL_FAST=1; shift ;;
    --no-record) RECORD=0; shift ;;
    --repo) REPO_OPT="${2:?--repo needs a slug}"; shift 2 ;;
    --ok) OK_RE="${2:?}"; shift 2 ;;
    --fail) FAIL_RE="${2:?}"; shift 2 ;;
    --ok-count) OK_COUNT="${2:?}"; shift 2 ;;
    --fail-count) FAIL_COUNT="${2:?}"; shift 2 ;;
    --status) WANT_STATUS="${2:?}"; shift 2 ;;
    --header) WANT_HEADER="${2:?}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; while [ $# -gt 0 ]; do POS+=("$1"); shift; done ;;
    -*) die "unknown option: $1" ;;
    *) POS+=("$1"); shift ;;
  esac
done
NPOS=${#POS[@]}

if [ -z "$BUDGET" ]; then
  BUDGET="$(jq -r '.ci_wait.default_budget_seconds // 540' "$MANIFEST" 2>/dev/null || printf '540')"
fi
case "$BUDGET" in ''|*[!0-9]*) die "--budget must be whole seconds" ;; esac
START="$(now_epoch)"
DEADLINE=$((START + BUDGET))
TICK=0
LAST_HB=0
CACHE="${TMPDIR:-/tmp}/ci-wait-$(id -u)"
mkdir -p "$CACHE"
chmod 700 "$CACHE"
find "$CACHE" -type f -mmin +1440 -exec rm -f {} + 2>/dev/null || :

NOISE_JSON="$(
  {
    if [ -s "$MANIFEST" ]; then noise_checks; fi
    if [ ${#IGNORE[@]} -gt 0 ]; then printf '%s\n' "${IGNORE[@]}"; fi
  } | jq -R . | jq -s 'map(ascii_downcase)'
)"

elapsed() { echo $(( $(now_epoch) - START )); }

tick() {
  printf 'ci-wait %s %s (elapsed %ss)\n' "$(date +%H:%M:%S)" "$*" "$(elapsed)"
  if [ -n "${RELEASE_TRACK:-}" ] && [ $(( $(now_epoch) - LAST_HB )) -ge 60 ]; then
    LAST_HB="$(now_epoch)"
    if ! state_set "$RELEASE_TRACK" waiting "$MODE ${POS[*]-}" 2>/dev/null; then
      log "warning: could not update $RELEASE_STATE"
    fi
  fi
}

# Sleep before the next poll, growing 10 -> 30s (2 -> 5s for local logs).
# Returns 1 when the budget is spent.
next_poll() {
  local schedule="$1" remaining interval
  remaining=$((DEADLINE - $(now_epoch)))
  [ "$remaining" -gt 1 ] || return 1
  interval="$(printf '%s\n' "$schedule" | tr ' ' '\n' | sed -n "$((TICK + 1))p")"
  [ -n "$interval" ] || interval="$(printf '%s\n' "$schedule" | tr ' ' '\n' | tail -1)"
  TICK=$((TICK + 1))
  [ "$interval" -lt "$remaining" ] || interval=$((remaining - 1))
  sleep "$interval"
  return 0
}

pending_exit() {
  printf 'ci-wait: still pending after %ss: %s. Call again to keep waiting.\n' "$(elapsed)" "$*"
  exit 2
}

# api_get <path>: GET with If-None-Match. Sets API_CODE and API_BODY (a file).
# Each body is stored under a name derived from its own ETag, so a 304 always
# reuses the body that ETag belongs to, even when several ci-wait processes
# poll the same path at once.
API_CODE=""
API_BODY=""
api_get() {
  local path="$1" key raw etag="" body_f new_etag new_body tmp
  key="$(printf '%s' "$path" | cksum | awk '{print $1}')"
  if [ -s "$CACHE/$key.etag" ]; then etag="$(cat "$CACHE/$key.etag")"; fi
  body_f="$CACHE/$key.$(printf '%s' "$etag" | cksum | awk '{print $1}').body"
  raw="$(mktemp "$CACHE/raw.XXXXXX")"
  if [ -n "$etag" ] && [ -s "$body_f" ]; then
    if gh api -i -H "If-None-Match: $etag" "$path" >"$raw" 2>"$raw.err"; then :; fi
  else
    if gh api -i "$path" >"$raw" 2>"$raw.err"; then :; fi
  fi
  API_CODE="$(head -1 "$raw" | awk '{print $2}')"
  case "$API_CODE" in
    304)
      API_BODY="$body_f"
      touch "$body_f" "$CACHE/$key.etag"  # in use: keep it out of the daily prune
      rm -f "$raw" "$raw.err"
      return 0 ;;
    200)
      new_etag="$(grep -i '^etag:' "$raw" | sed -n '1s/^[^:]*:[[:space:]]*//p' | tr -d '\r\n')"
      new_body="$CACHE/$key.$(printf '%s' "$new_etag" | cksum | awk '{print $1}').body"
      tmp="$(mktemp "$CACHE/body.XXXXXX")"
      awk 'BEGIN { h = 1 } h && /^\r?$/ { h = 0; next } !h' "$raw" >"$tmp"
      mv "$tmp" "$new_body"
      tmp="$(mktemp "$CACHE/etag.XXXXXX")"
      printf '%s' "$new_etag" >"$tmp"
      mv "$tmp" "$CACHE/$key.etag"
      API_BODY="$new_body"
      rm -f "$raw" "$raw.err"
      return 0
      ;;
    *)
      API_CODE="${API_CODE:-000}"
      rm -f "$raw" "$raw.err"
      return 1 ;;
  esac
}

resolve_slug() {
  local arg="$1" name
  case "$arg" in
    https://github.com/*)
      printf '%s\n' "$arg" | sed -E 's#^https://github.com/([^/]+/[^/]+).*#\1#'
      return 0 ;;
    */*) printf '%s\n' "$arg"; return 0 ;;
  esac
  name="$(repo_field "$arg" slug 2>/dev/null)"
  [ -n "$name" ] || die "unknown repo '$arg': use owner/name or a manifest repo name"
  printf '%s\n' "$name"
}

record_run() {
  [ "$RECORD" -eq 1 ] || return 0
  if ! python3 "$TIMING_PY" ingest --gh "$1" "$2" >/dev/null 2>"$CACHE/record.err"; then
    log "warning: timing record for run $2 failed: $(tail -1 "$CACHE/record.err")"
  fi
}

record_wait() {
  [ "$RECORD" -eq 1 ] || return 0
  if ! python3 "$TIMING_PY" record --repo "$1" --workflow "$2" --step "$3" --seconds "$4" --kind wait >/dev/null 2>"$CACHE/record.err"; then
    log "warning: timing record failed: $(tail -1 "$CACHE/record.err")"
  fi
}

# Print failing jobs of a run and the tail of their failed-step logs.
report_run_failure() {
  local slug="$1" id="$2" jobs_body
  if api_get "repos/$slug/actions/runs/$id/jobs?per_page=100"; then
    jobs_body="$API_BODY"
    printf 'Failed jobs:\n'
    jq -r '.jobs[] | select(.conclusion == "failure" or .conclusion == "timed_out" or .conclusion == "cancelled" or .conclusion == "startup_failure") | "  - \(.name) [\(.conclusion)] \(.html_url)"' "$jobs_body"
    local job_id
    job_id="$(jq -r '[.jobs[] | select(.conclusion == "failure" or .conclusion == "timed_out")][0].id // empty' "$jobs_body")"
    if [ -n "$job_id" ]; then
      printf -- '--- last 80 lines of failed steps (job %s) ---\n' "$job_id"
      if ! gh run view "$id" -R "$slug" --job "$job_id" --log-failed 2>/dev/null | tail -80; then
        printf '(log not available yet: gh run view %s -R %s --log-failed)\n' "$id" "$slug"
      fi
    fi
  else
    printf 'Could not list jobs (HTTP %s); see gh run view %s -R %s\n' "$API_CODE" "$id" "$slug"
  fi
}

wait_run() {
  local slug="$1" id="$2" status conclusion name url summary failed
  while :; do
    if api_get "repos/$slug/actions/runs/$id"; then
      status="$(jq -r '.status' "$API_BODY")"
      conclusion="$(jq -r '.conclusion // ""' "$API_BODY")"
      name="$(jq -r '.name' "$API_BODY")"
      url="$(jq -r '.html_url' "$API_BODY")"
      if [ "$status" = "completed" ]; then
        case "$conclusion" in
          success|neutral|skipped)
            printf 'ci-wait: %s run %s %s after %ss: %s\n' "$name" "$id" "$conclusion" "$(elapsed)" "$url"
            record_run "$slug" "$id"
            exit 0 ;;
          *)
            printf 'ci-wait: %s run %s concluded %s: %s\n' "$name" "$id" "$conclusion" "$url"
            report_run_failure "$slug" "$id"
            record_run "$slug" "$id"
            exit 1 ;;
        esac
      fi
      summary="$status"
      if api_get "repos/$slug/actions/runs/$id/jobs?per_page=100"; then
        summary="$status, $(jq -r '"\([.jobs[] | select(.status == "completed")] | length)/\(.jobs | length) jobs done"' "$API_BODY")"
        failed="$(jq -r --argjson noise "$NOISE_JSON" '[.jobs[] | select(.status == "completed" and (.conclusion == "failure" or .conclusion == "timed_out")) | select((.name | ascii_downcase) as $n | ($noise | index($n)) | not) | .name] | join(", ")' "$API_BODY")"
        if [ -n "$failed" ]; then
          summary="$summary, failed so far: $failed"
          if [ "$FAIL_FAST" -eq 1 ]; then
            printf 'ci-wait: %s run %s has failed jobs (fail-fast): %s\n' "$name" "$id" "$url"
            report_run_failure "$slug" "$id"
            exit 1
          fi
        fi
      fi
      tick "run $slug#$id $summary"
    elif [ "$API_CODE" = "404" ]; then
      printf 'ci-wait: run %s not found in %s\n' "$id" "$slug"
      exit 1
    else
      tick "run $slug#$id: GitHub API answered HTTP $API_CODE, retrying"
    fi
    next_poll "10 15 20 30" || pending_exit "run $slug#$id is ${status:-unknown}"
  done
}

mode_run() {
  local slug="" id=""
  if [ "$NPOS" -eq 1 ]; then
    case "${POS[0]}" in
      https://github.com/*/actions/runs/*)
        slug="$(resolve_slug "${POS[0]}")"
        id="$(printf '%s\n' "${POS[0]}" | sed -E 's#.*/actions/runs/([0-9]+).*#\1#')" ;;
      *) id="${POS[0]}" ;;
    esac
  elif [ "$NPOS" -eq 2 ]; then
    slug="$(resolve_slug "${POS[0]}")"
    id="${POS[1]}"
  else
    die "usage: ci-wait.sh run [<repo>] <run id>"
  fi
  [ -z "$REPO_OPT" ] || slug="$(resolve_slug "$REPO_OPT")"
  case "$id" in ''|*[!0-9]*) die "run id must be numeric: $id" ;; esac
  if [ -z "$slug" ]; then
    local candidate
    for candidate in $(mf '.repos[].slug'); do
      if gh api "repos/$candidate/actions/runs/$id" --silent >/dev/null 2>&1; then
        slug="$candidate"
        break
      fi
    done
    [ -n "$slug" ] || die "run $id not found in any manifest repo; pass <repo>"
  fi
  wait_run "$slug" "$id"
}

mode_tag() {
  [ "$NPOS" -eq 3 ] || die "usage: ci-wait.sh tag <repo> <tag> <workflow file>"
  local slug tag wf run_id
  slug="$(resolve_slug "${POS[0]}")"
  tag="${POS[1]}"
  wf="${POS[2]}"
  while :; do
    if api_get "repos/$slug/actions/workflows/$wf/runs?branch=$tag&per_page=1"; then
      run_id="$(jq -r '.workflow_runs[0].id // empty' "$API_BODY")"
      if [ -n "$run_id" ]; then
        tick "tag $tag started run $run_id"
        wait_run "$slug" "$run_id"
      fi
      tick "tag $tag: no $wf run yet"
    elif [ "$API_CODE" = "404" ]; then
      printf 'ci-wait: workflow %s not found in %s\n' "$wf" "$slug"
      exit 1
    else
      tick "tag $tag: GitHub API answered HTTP $API_CODE, retrying"
    fi
    next_poll "10 15 20 30" || pending_exit "no $wf run for $tag yet"
  done
}

mode_pr() {
  local slug number sha="" new_sha head_age=0 checks statuses wf_runs verdict
  if [ "$NPOS" -eq 1 ]; then
    case "${POS[0]}" in
      https://github.com/*/pull/*)
        slug="$(resolve_slug "${POS[0]}")"
        number="$(printf '%s\n' "${POS[0]}" | sed -E 's#.*/pull/([0-9]+).*#\1#')" ;;
      *) die "usage: ci-wait.sh pr <repo> <number>" ;;
    esac
  elif [ "$NPOS" -eq 2 ]; then
    slug="$(resolve_slug "${POS[0]}")"
    number="${POS[1]}"
  else
    die "usage: ci-wait.sh pr <repo> <number>"
  fi
  while :; do
    if api_get "repos/$slug/pulls/$number"; then
      new_sha="$(jq -r '.head.sha' "$API_BODY")"
      if [ "$new_sha" != "$sha" ]; then
        [ -z "$sha" ] || tick "PR head moved to ${new_sha:0:9}"
        sha="$new_sha"
        if api_get "repos/$slug/commits/$sha"; then
          head_age=$(( $(now_epoch) - $(python3 -c 'import sys,datetime;print(int(datetime.datetime.strptime(sys.argv[1],"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()))' "$(jq -r '.commit.committer.date' "$API_BODY")") ))
        fi
      fi
    elif [ "$API_CODE" = "404" ]; then
      printf 'ci-wait: PR %s not found in %s\n' "$number" "$slug"
      exit 1
    fi
    if [ -n "$sha" ] && api_get "repos/$slug/commits/$sha/check-runs?per_page=100"; then
      checks="$API_BODY"
      statuses="$CACHE/empty-status.json"
      printf '{"statuses":[]}' >"$statuses"
      if api_get "repos/$slug/commits/$sha/status"; then statuses="$API_BODY"; fi
      wf_runs="$CACHE/empty-runs.json"
      printf '{"workflow_runs":[]}' >"$wf_runs"
      if api_get "repos/$slug/actions/runs?head_sha=$sha&per_page=100"; then wf_runs="$API_BODY"; fi
      verdict="$(jq -n -r --argjson noise "$NOISE_JSON" --slurpfile c "$checks" --slurpfile s "$statuses" --slurpfile w "$wf_runs" '
        def noisy: (ascii_downcase) as $n | ($noise | index($n)) != null;
        ($c[0].check_runs) as $all
        | ([$all[] | select((.name | noisy) | not)]) as $runs
        | ([$s[0].statuses[]? | select((.context | noisy) | not)]) as $sts
        # A workflow run still going counts as pending unless every check run it
        # has created so far is known noise.
        | ([$w[0].workflow_runs[]? | select(.status != "completed")
            | .check_suite_id as $suite
            | select(([$all[] | select(.check_suite.id == $suite)] as $mine
                      | ($mine | length) > 0 and all($mine[]; .name | noisy)) | not)]) as $open_runs
        | ([$runs[] | select(.status == "completed" and (.conclusion | IN("failure", "timed_out", "cancelled", "action_required", "startup_failure")))] | map("\(.name) [\(.conclusion)] \(.details_url // "")")
           + [$sts[] | select(.state == "failure" or .state == "error") | "\(.context) [\(.state)] \(.target_url // "")"]) as $failed
        | (([$runs[] | select(.status != "completed")] | length) + ([$sts[] | select(.state == "pending")] | length)) as $pending
        | (($runs | length) + ($sts | length)) as $total
        | if ($failed | length) > 0 then "FAIL\t" + ($failed | join("\n"))
          elif $total == 0 and ($open_runs | length) == 0 then "NONE\t"
          elif $pending == 0 and ($open_runs | length) == 0 then "PASS\t\($total) checks green"
          elif $pending == 0 then "WAIT\t\($total) checks done; workflow still running: \($open_runs | map(.name) | unique | join(", "))"
          else "WAIT\t\($total - $pending)/\($total) checks done" end')"
      case "${verdict%%	*}" in
        FAIL)
          printf 'ci-wait: PR %s#%s has failing checks on %s:\n%s\n' "$slug" "$number" "${sha:0:9}" "${verdict#*	}"
          local fail_url run_id
          fail_url="$(printf '%s\n' "${verdict#*	}" | grep -oE 'https://github.com/[^ ]+/actions/runs/[0-9]+' | head -1)"
          if [ -n "$fail_url" ]; then
            run_id="$(printf '%s\n' "$fail_url" | sed -E 's#.*/runs/([0-9]+)#\1#')"
            report_run_failure "$slug" "$run_id"
          fi
          exit 1 ;;
        PASS)
          printf 'ci-wait: PR %s#%s green on %s after %ss (%s)\n' "$slug" "$number" "${sha:0:9}" "$(elapsed)" "${verdict#*	}"
          exit 0 ;;
        NONE)
          # GitHub needs a few seconds to create runs after a push, and the head
          # commit can be older than the push, so also require 60s of no checks.
          if [ "$head_age" -gt 300 ] && [ "$(elapsed)" -ge 60 ]; then
            printf 'ci-wait: PR %s#%s: no checks reported for %s (head pushed %ss ago); nothing to wait on\n' "$slug" "$number" "${sha:0:9}" "$head_age"
            exit 0
          fi
          tick "PR $slug#$number: no checks yet on ${sha:0:9}" ;;
        *) tick "PR $slug#$number ${verdict#*	} on ${sha:0:9}" ;;
      esac
    else
      tick "PR $slug#$number: GitHub API answered HTTP $API_CODE, retrying"
    fi
    next_poll "10 15 20 30" || pending_exit "PR $slug#$number checks still running"
  done
}

mode_npm() {
  [ "$NPOS" -eq 2 ] || die "usage: ci-wait.sh npm <package> <version>"
  local pkg="${POS[0]}" ver="${POS[1]}" enc code seen
  enc="$(printf '%s' "$pkg" | sed 's#/#%2f#')"
  while :; do
    code="$(curl -s -o /dev/null -m 20 -w '%{http_code}' "https://registry.npmjs.org/$enc/$ver")" || code="000"
    if [ "$code" = "200" ]; then
      seen="$(npm view "$pkg@$ver" version --prefer-online 2>/dev/null)" || seen=""
      if [ "$seen" = "$ver" ]; then
        printf 'ci-wait: %s@%s is on the registry after %ss\n' "$pkg" "$ver" "$(elapsed)"
        record_wait "$pkg" registry "npm propagation" "$(elapsed)"
        exit 0
      fi
      tick "npm $pkg@$ver: version document is up, npm view not yet"
    else
      tick "npm $pkg@$ver: registry HTTP $code"
    fi
    next_poll "5 10 15" || pending_exit "$pkg@$ver not on the registry yet"
  done
}

mode_url() {
  [ "$NPOS" -ge 1 ] && [ "$NPOS" -le 2 ] || die "usage: ci-wait.sh url <url> [<substring>]"
  local url="${POS[0]}" want="" code body hdr ok
  [ "$NPOS" -lt 2 ] || want="${POS[1]}"
  body="$CACHE/url.$$.body"
  hdr="$CACHE/url.$$.hdr"
  while :; do
    code="$(curl -s -m 20 -D "$hdr" -o "$body" -w '%{http_code}' "$url")" || code="000"
    if [ -n "$FAIL_RE" ] && grep -qE -- "$FAIL_RE" "$body"; then
      printf 'ci-wait: %s matched the failure pattern (HTTP %s)\n' "$url" "$code"
      grep -oE -- "$FAIL_RE" "$body" | head -5
      exit 1
    fi
    ok=1
    if [ -n "$WANT_STATUS" ]; then [ "$code" = "$WANT_STATUS" ] || ok=0
    else case "$code" in 2??) ;; *) ok=0 ;; esac
    fi
    if [ "$ok" -eq 1 ] && [ -n "$want" ] && ! grep -qF -- "$want" "$body"; then ok=0; fi
    if [ "$ok" -eq 1 ] && [ -n "$WANT_HEADER" ]; then
      tr -d '\r' <"$hdr" >"$hdr.lf"
      grep -qiF -- "$WANT_HEADER" "$hdr.lf" || ok=0
    fi
    if [ "$ok" -eq 1 ]; then
      printf 'ci-wait: %s ready (HTTP %s) after %ss\n' "$url" "$code" "$(elapsed)"
      rm -f "$body" "$hdr" "$hdr.lf"
      exit 0
    fi
    tick "url $url HTTP $code, not ready"
    next_poll "5 10 15 20" || { rm -f "$body" "$hdr" "$hdr.lf"; pending_exit "$url not ready"; }
  done
}

count_matches() {
  local n rc=0
  n="$(grep -cE -- "$1" "$2" 2>/dev/null)" || rc=$?
  if [ "$rc" -le 1 ]; then printf '%s\n' "${n:-0}"; else printf '0\n'; fi
}

mode_log() {
  [ "$NPOS" -eq 1 ] || die "usage: ci-wait.sh log <file> --ok REGEX --fail REGEX"
  [ -n "$OK_RE" ] && [ -n "$FAIL_RE" ] || die "log mode needs both --ok and --fail: a wait that ignores errors is not allowed"
  local file="${POS[0]}" fails oks
  while :; do
    if [ -f "$file" ]; then
      fails="$(count_matches "$FAIL_RE" "$file")"
      if [ "$fails" -ge "$FAIL_COUNT" ]; then
        printf 'ci-wait: %s has %s line(s) matching the failure pattern; last ones:\n' "$file" "$fails"
        grep -E -- "$FAIL_RE" "$file" | tail -5
        exit 1
      fi
      oks="$(count_matches "$OK_RE" "$file")"
      if [ "$oks" -ge "$OK_COUNT" ]; then
        printf 'ci-wait: %s reached %s/%s success line(s) with no failures after %ss\n' "$file" "$oks" "$OK_COUNT" "$(elapsed)"
        exit 0
      fi
      tick "log $file: $oks/$OK_COUNT ok, $fails failures"
    else
      tick "log $file: not created yet"
    fi
    next_poll "2 2 3 5" || pending_exit "log $file has ${oks:-0}/$OK_COUNT success lines"
  done
}

case "$MODE" in
  run) require_tools gh jq; mode_run ;;
  tag) require_tools gh jq; mode_tag ;;
  pr) require_tools gh jq; mode_pr ;;
  npm) require_tools curl npm; mode_npm ;;
  url) require_tools curl; mode_url ;;
  log) mode_log ;;
  *) usage >&2; exit 64 ;;
esac
