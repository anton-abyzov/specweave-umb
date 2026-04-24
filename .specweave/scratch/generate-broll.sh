#!/bin/bash
# Generates 4 Veo 3.1 Fast B-roll clips in parallel and polls until done.
# Usage: GEMINI_API_KEY=xxx ./generate-broll.sh
set -u

SCRATCH="/Users/antonabyzov/Projects/github/specweave-umb/.specweave/scratch"
MODEL="veo-3.1-fast-generate-preview"
PROMPTS_FILE="$SCRATCH/veo-prompts.txt"
LOG="$SCRATCH/generate-broll.log"

: > "$LOG"

if [ -z "${GEMINI_API_KEY:-}" ]; then
  echo "GEMINI_API_KEY not set" | tee -a "$LOG"
  exit 1
fi

read_prompt() {
  local NAME="$1"
  awk -v name="=== $NAME ===" '
    $0 == name { found=1; next }
    found && /^=== / { exit }
    found { print }
  ' "$PROMPTS_FILE"
}

generate_one() {
  local NAME="$1"
  local PROMPT
  PROMPT="$(read_prompt "$NAME")"

  local OUTFILE="$SCRATCH/broll-${NAME}.mp4"
  local SUBMIT_TMP
  SUBMIT_TMP="$(mktemp -t "gemini-vid-${NAME}-XXXX.json")"
  local STATUS_TMP
  STATUS_TMP="$(mktemp -t "gemini-vid-${NAME}-status-XXXX.json")"

  # Build JSON body with python (safe quoting)
  local BODY
  BODY=$(python3 -c "import json,sys; print(json.dumps({'instances':[{'prompt': sys.argv[1]}]}))" "$PROMPT")

  echo "[$NAME] submitting..." | tee -a "$LOG"
  curl -sS -X POST \
    "https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:predictLongRunning" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H "Content-Type: application/json" \
    -o "$SUBMIT_TMP" \
    -d "$BODY"

  local OP
  OP=$(python3 -c "
import json, sys
try:
  d = json.load(open(sys.argv[1]))
except Exception as e:
  print('', end='')
  sys.exit(0)
if 'error' in d:
  print('ERROR::' + d['error'].get('message','unknown'))
  sys.exit(0)
print(d.get('name',''))
" "$SUBMIT_TMP")

  if [ -z "$OP" ] || [[ "$OP" == ERROR::* ]]; then
    echo "[$NAME] SUBMIT FAILED: ${OP#ERROR::}" | tee -a "$LOG"
    echo "[$NAME] raw response:" | tee -a "$LOG"
    cat "$SUBMIT_TMP" >> "$LOG"
    rm -f "$SUBMIT_TMP" "$STATUS_TMP"
    return 1
  fi

  echo "[$NAME] operation: $OP" | tee -a "$LOG"

  local MAX_POLLS=36   # 6 min max
  local i=0
  while [ $i -lt $MAX_POLLS ]; do
    sleep 10
    i=$((i+1))
    curl -sS "https://generativelanguage.googleapis.com/v1beta/${OP}" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -o "$STATUS_TMP"

    local DONE
    DONE=$(python3 -c "
import json,sys
try:
  d=json.load(open(sys.argv[1]))
  print(d.get('done', False))
except: print(False)
" "$STATUS_TMP")

    if [ "$DONE" = "True" ]; then
      local URI
      URI=$(python3 -c "
import json,sys
try:
  d=json.load(open(sys.argv[1]))
  if 'error' in d.get('response',{}) or 'error' in d:
    err=d.get('response',{}).get('error') or d.get('error')
    print('ERROR::'+str(err))
  else:
    print(d['response']['generateVideoResponse']['generatedSamples'][0]['video']['uri'])
except Exception as e:
  print('ERROR::'+str(e))
" "$STATUS_TMP")

      if [[ "$URI" == ERROR::* ]] || [ -z "$URI" ]; then
        echo "[$NAME] DONE but URI extract failed: ${URI#ERROR::}" | tee -a "$LOG"
        cat "$STATUS_TMP" >> "$LOG"
        rm -f "$SUBMIT_TMP" "$STATUS_TMP"
        return 1
      fi

      curl -sS -L -o "$OUTFILE" "$URI" -H "x-goog-api-key: $GEMINI_API_KEY"
      if [ -s "$OUTFILE" ]; then
        echo "[$NAME] DONE: $OUTFILE ($(du -h "$OUTFILE" | cut -f1))" | tee -a "$LOG"
        rm -f "$SUBMIT_TMP" "$STATUS_TMP"
        return 0
      else
        echo "[$NAME] download empty" | tee -a "$LOG"
        rm -f "$SUBMIT_TMP" "$STATUS_TMP"
        return 1
      fi
    fi
    echo "[$NAME] poll $i/$MAX_POLLS..." | tee -a "$LOG"
  done

  echo "[$NAME] TIMED OUT after 6 min. Operation still available at: $OP" | tee -a "$LOG"
  rm -f "$SUBMIT_TMP" "$STATUS_TMP"
  return 1
}

echo "=== Starting 4 parallel Veo 3.1 Fast generations at $(date) ===" | tee -a "$LOG"

generate_one "01-cold-open" &
PID1=$!
generate_one "02-hands-montage" &
PID2=$!
generate_one "03-lockin-break" &
PID3=$!
generate_one "04-sse-magic" &
PID4=$!

wait $PID1; R1=$?
wait $PID2; R2=$?
wait $PID3; R3=$?
wait $PID4; R4=$?

echo "=== Finished at $(date) ===" | tee -a "$LOG"
echo "01-cold-open: exit=$R1" | tee -a "$LOG"
echo "02-hands-montage: exit=$R2" | tee -a "$LOG"
echo "03-lockin-break: exit=$R3" | tee -a "$LOG"
echo "04-sse-magic: exit=$R4" | tee -a "$LOG"

ls -lh "$SCRATCH"/broll-*.mp4 2>/dev/null | tee -a "$LOG"
