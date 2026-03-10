#!/bin/bash
# GitHub-only sync for increments that need it
# Waits for rate limit reset, then syncs one at a time

set +e

# Extract GH_TOKEN properly (handles = in base64 tokens)
GH_TOKEN=$(node -e "const fs=require('fs'); const env=fs.readFileSync('.env','utf-8'); for(const l of env.split('\n')){if(l.startsWith('GITHUB_TOKEN='))console.log(l.slice('GITHUB_TOKEN='.length).trim().replace(/^[\"']|[\"']\$/g,''))}")

if [ -z "$GH_TOKEN" ]; then
  echo "ERROR: GITHUB_TOKEN not found in .env"
  exit 1
fi

export GH_TOKEN

echo "Checking GitHub API rate limit..."
remaining=$(GH_TOKEN="$GH_TOKEN" gh api rate_limit --jq '.rate.remaining' 2>/dev/null || echo "0")
reset_epoch=$(GH_TOKEN="$GH_TOKEN" gh api rate_limit --jq '.rate.reset' 2>/dev/null || echo "0")

if [ "$remaining" = "0" ] || [ "$remaining" -lt 500 ]; then
  wait_secs=$((reset_epoch - $(date +%s)))
  if [ "$wait_secs" -gt 0 ]; then
    echo "Rate limit: $remaining remaining. Resets in ${wait_secs}s. Waiting..."
    sleep $((wait_secs + 10))
  fi
fi

# Verify rate limit is available
remaining=$(GH_TOKEN="$GH_TOKEN" gh api rate_limit --jq '.rate.remaining' 2>/dev/null || echo "0")
echo "Rate limit after wait: $remaining remaining"

if [ "$remaining" -lt 200 ]; then
  echo "ERROR: Not enough API calls remaining ($remaining). Need at least 200."
  exit 1
fi

IDS="0450 0453 0455 0456 0457 0458 0459 0460 0461 0462 0465 0466 0467 0470 0471 0472"

echo ""
echo "Starting GitHub sync for 16 increments..."
echo ""

success=0
failed=0
for id in $IDS; do
  echo "=== Syncing $id ==="

  # Check rate limit before each sync
  remaining=$(GH_TOKEN="$GH_TOKEN" gh api rate_limit --jq '.rate.remaining' 2>/dev/null || echo "0")
  if [ "$remaining" -lt 50 ]; then
    echo "WARNING: Only $remaining API calls remaining. Stopping to avoid exhaustion."
    echo "Run this script again after rate limit resets."
    break
  fi

  output=$(npx specweave sync-living-docs "$id" 2>&1)

  # Check for GitHub success
  if echo "$output" | grep -q "Synced to GitHub"; then
    echo "  OK - GitHub synced"
    success=$((success + 1))
  elif echo "$output" | grep -q "Using existing Milestone"; then
    echo "  OK - Milestone already exists"
    success=$((success + 1))
  elif echo "$output" | grep -q "rate limit"; then
    echo "  FAILED - rate limit hit"
    failed=$((failed + 1))
  else
    echo "  RESULT: $(echo "$output" | grep -E "GitHub|Milestone|milestone|⚠️.*github" | head -3)"
    # Check if it at least didn't error
    if echo "$output" | grep -q "Synced.*→.*FS-"; then
      success=$((success + 1))
    else
      failed=$((failed + 1))
    fi
  fi

  echo ""
  sleep 3
done

echo ""
echo "Done! Succeeded: $success, Failed: $failed"

# Final rate limit check
remaining=$(GH_TOKEN="$GH_TOKEN" gh api rate_limit --jq '.rate.remaining' 2>/dev/null || echo "?")
echo "Rate limit remaining: $remaining"
