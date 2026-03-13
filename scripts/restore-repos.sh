#!/usr/bin/env bash
# Restore child repositories from umbrella config.json
# Run after cloning the umbrella repo: ./scripts/restore-repos.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG="$ROOT_DIR/.specweave/config.json"

if [ ! -f "$CONFIG" ]; then
  echo "Error: $CONFIG not found"
  exit 1
fi

# Check for jq
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required. Install with: brew install jq"
  exit 1
fi

# Parse child repos from config
COUNT=$(jq '.umbrella.childRepos | length' "$CONFIG")

for ((i = 0; i < COUNT; i++)); do
  DISABLED=$(jq -r ".umbrella.childRepos[$i].disabled // false" "$CONFIG")
  if [ "$DISABLED" = "true" ]; then
    NAME=$(jq -r ".umbrella.childRepos[$i].name" "$CONFIG")
    echo "Skipping $NAME (disabled)"
    continue
  fi

  PATH_REL=$(jq -r ".umbrella.childRepos[$i].path" "$CONFIG")
  URL=$(jq -r ".umbrella.childRepos[$i].githubUrl // empty" "$CONFIG")
  NAME=$(jq -r ".umbrella.childRepos[$i].name" "$CONFIG")
  FULL_PATH="$ROOT_DIR/$PATH_REL"

  if [ -z "$URL" ]; then
    # Derive URL from sync.github if githubUrl not set
    OWNER=$(jq -r ".umbrella.childRepos[$i].sync.github.owner // empty" "$CONFIG")
    REPO=$(jq -r ".umbrella.childRepos[$i].sync.github.repo // empty" "$CONFIG")
    if [ -n "$OWNER" ] && [ -n "$REPO" ]; then
      URL="https://github.com/$OWNER/$REPO.git"
    else
      echo "Skipping $NAME — no URL or github sync config"
      continue
    fi
  fi

  if [ -d "$FULL_PATH/.git" ]; then
    echo "Already cloned: $NAME ($PATH_REL)"
  else
    echo "Cloning $NAME → $PATH_REL"
    mkdir -p "$(dirname "$FULL_PATH")"
    git clone "$URL" "$FULL_PATH"
  fi
done

echo "Done. All child repositories restored."
