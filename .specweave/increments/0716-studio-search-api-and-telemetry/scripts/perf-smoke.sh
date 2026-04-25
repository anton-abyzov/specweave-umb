#!/usr/bin/env bash
# Studio search proxy perf smoke (T-010 / AC-US2-07).
#
# Hits /api/v1/studio/search with N sequential requests against a running
# Worker (default localhost:3000) and prints p50 / p95 latency in ms.
# A first call primes the LRU; the next N are cache hits.
#
# Usage:
#   bash scripts/perf-smoke.sh                           # 20 hits against localhost
#   BASE=https://verified-skill.com bash scripts/perf-smoke.sh 50
#
set -euo pipefail

BASE="${BASE:-http://localhost:3000}"
N="${1:-20}"
QUERY="react"
URL="${BASE}/api/v1/studio/search?q=${QUERY}&limit=20&offset=0"

echo "Priming LRU at ${URL} ..."
curl -s -o /dev/null -w "prime: %{time_total}s status=%{http_code} x-cache=%header{x-cache}\n" "$URL"

echo "Running ${N} cache-hit measurements ..."
TIMES=()
for i in $(seq 1 "$N"); do
  T=$(curl -s -o /dev/null -w "%{time_total}" "$URL")
  TIMES+=("$T")
done

# Sort ascending and pick p50 / p95.
SORTED=$(printf '%s\n' "${TIMES[@]}" | sort -n)
COUNT=$(printf '%s\n' "${TIMES[@]}" | wc -l | tr -d ' ')
P50_IDX=$(( COUNT / 2 ))
P95_IDX=$(( (COUNT * 95 + 99) / 100 - 1 ))
[ "$P95_IDX" -lt 0 ] && P95_IDX=0
P50=$(echo "$SORTED" | sed -n "$((P50_IDX + 1))p")
P95=$(echo "$SORTED" | sed -n "$((P95_IDX + 1))p")

# curl reports seconds — convert to ms (multiply by 1000).
P50_MS=$(awk -v t="$P50" 'BEGIN { printf "%.2f", t * 1000 }')
P95_MS=$(awk -v t="$P95" 'BEGIN { printf "%.2f", t * 1000 }')

echo "p50 = ${P50_MS} ms"
echo "p95 = ${P95_MS} ms"
echo "Budget (AC-US2-07): cache-hit p50 < 5ms, p95 < 15ms"
