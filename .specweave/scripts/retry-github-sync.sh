#!/bin/bash
# Retry GitHub sync for all increments that were blocked by rate limit
# JIRA and ADO are already synced (idempotent re-sync is safe)

set -e

IDS="0450 0453 0455 0456 0458 0459 0460 0461 0462 0465 0466 0467 0470 0471 0472"

echo "Checking GitHub API rate limit..."
GH_TOKEN=$(grep GITHUB_TOKEN .env | cut -d= -f2 | tr -d '"' | tr -d "'")
remaining=$(curl -s -I -H "Authorization: token $GH_TOKEN" https://api.github.com/rate_limit 2>/dev/null | grep "x-ratelimit-remaining" | awk '{print $2}' | tr -d '\r')

if [ "$remaining" = "0" ]; then
  reset_epoch=$(curl -s -I -H "Authorization: token $GH_TOKEN" https://api.github.com/rate_limit 2>/dev/null | grep "x-ratelimit-reset" | awk '{print $2}' | tr -d '\r')
  wait_secs=$((reset_epoch - $(date +%s)))
  if [ "$wait_secs" -gt 0 ]; then
    echo "Rate limit still active. Resets in ${wait_secs}s. Waiting..."
    sleep $((wait_secs + 5))
  fi
fi

echo ""
echo "Starting GitHub sync for 15 increments..."
echo ""

for id in $IDS; do
  echo "=== Syncing $id ==="
  npx specweave sync-living-docs "$id" 2>&1 | grep -E "✅.*(Created|Synced)|❌|Feature ID|Files created|GitHub"
  echo ""
  # Small delay to avoid hitting secondary rate limits
  sleep 2
done

echo "Done! All increments synced."
