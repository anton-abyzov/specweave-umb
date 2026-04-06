#!/bin/bash
set -e

# ============================================================
# Cloudflare Cost Monitor - Setup Script
# ============================================================
#
# This script:
# 1. Validates your Cloudflare API token
# 2. Creates a macOS LaunchAgent to run the monitor every 6 hours
# 3. Optionally configures Slack webhook for alerts
#
# PREREQUISITE: Create a Cloudflare API Token
#   1. Go to: https://dash.cloudflare.com/profile/api-tokens
#   2. Click "Create Token"
#   3. Use template "Read All Resources" OR create custom with:
#      - Account > Account Analytics > Read
#      - Account > Workers Scripts > Read
#      - Account > Account Settings > Read
#   4. Copy the token
#
# Usage:
#   ./cf-cost-monitor-setup.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/cf-cost-monitor.mjs"
PLIST_NAME="com.specweave.cf-cost-monitor"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"
ENV_FILE="$SCRIPT_DIR/.cf-monitor.env"
LOG_DIR="$HOME/Library/Logs/cf-cost-monitor"
NODE_PATH=$(which node)

echo "============================================"
echo "  Cloudflare Cost Monitor Setup"
echo "============================================"
echo ""

# Check Node.js
if [ -z "$NODE_PATH" ]; then
  echo "ERROR: Node.js not found. Install it first."
  exit 1
fi
echo "Node.js: $NODE_PATH ($(node --version))"

# Check if env file exists
if [ -f "$ENV_FILE" ]; then
  echo "Found existing config at $ENV_FILE"
  source "$ENV_FILE"
fi

# Prompt for config
if [ -z "$CF_ACCOUNT_ID" ]; then
  echo ""
  echo "Your Cloudflare Account ID (from the dashboard URL):"
  read -r CF_ACCOUNT_ID
fi

if [ -z "$CF_API_TOKEN" ]; then
  echo ""
  echo "Your Cloudflare API Token (create at https://dash.cloudflare.com/profile/api-tokens):"
  echo "  Required scopes: Account Analytics (Read), Workers Scripts (Read), Account Settings (Read)"
  read -rs CF_API_TOKEN
  echo ""
fi

# Validate token
echo ""
echo "Validating API token..."
VERIFY=$(curl -s -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/user/tokens/verify")

if echo "$VERIFY" | grep -q '"success":true'; then
  echo "Token is valid!"
else
  echo "ERROR: Token validation failed."
  echo "$VERIFY" | python3 -m json.tool 2>/dev/null || echo "$VERIFY"
  exit 1
fi

# Slack webhook (optional)
if [ -z "$SLACK_WEBHOOK_URL" ]; then
  echo ""
  echo "Slack webhook URL for alerts (press Enter to skip):"
  echo "  Create one at: https://api.slack.com/messaging/webhooks"
  read -r SLACK_WEBHOOK_URL
fi

# Budget thresholds
if [ -z "$CF_BUDGET_WARN" ]; then
  CF_BUDGET_WARN=50
fi
if [ -z "$CF_BUDGET_CRIT" ]; then
  CF_BUDGET_CRIT=100
fi

echo ""
echo "Alert thresholds: warn=\$$CF_BUDGET_WARN, critical=\$$CF_BUDGET_CRIT"
echo "Change? Enter new warn,crit (e.g., 75,150) or press Enter to keep:"
read -r THRESHOLDS
if [ -n "$THRESHOLDS" ]; then
  CF_BUDGET_WARN=$(echo "$THRESHOLDS" | cut -d, -f1)
  CF_BUDGET_CRIT=$(echo "$THRESHOLDS" | cut -d, -f2)
fi

# Save env file
cat > "$ENV_FILE" << ENVEOF
CF_ACCOUNT_ID=$CF_ACCOUNT_ID
CF_API_TOKEN=$CF_API_TOKEN
SLACK_WEBHOOK_URL=$SLACK_WEBHOOK_URL
CF_BUDGET_WARN=$CF_BUDGET_WARN
CF_BUDGET_CRIT=$CF_BUDGET_CRIT
CF_QUIET=0
ENVEOF
chmod 600 "$ENV_FILE"
echo ""
echo "Config saved to $ENV_FILE (chmod 600)"

# Create log directory
mkdir -p "$LOG_DIR"

# Test run
echo ""
echo "Running a test..."
set +e
source "$ENV_FILE"
export CF_ACCOUNT_ID CF_API_TOKEN SLACK_WEBHOOK_URL CF_BUDGET_WARN CF_BUDGET_CRIT CF_QUIET
"$NODE_PATH" "$MONITOR_SCRIPT" 2>&1
TEST_EXIT=$?
set -e

if [ $TEST_EXIT -eq 3 ]; then
  echo ""
  echo "ERROR: Test run failed. Check the error above."
  echo "Common issues:"
  echo "  - Token doesn't have Analytics scope"
  echo "  - Account ID is wrong"
  exit 1
fi

echo ""
echo "Test successful!"

# Create LaunchAgent plist
cat > "$PLIST_PATH" << PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>$NODE_PATH</string>
        <string>$MONITOR_SCRIPT</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>CF_ACCOUNT_ID</key>
        <string>$CF_ACCOUNT_ID</string>
        <key>CF_API_TOKEN</key>
        <string>$CF_API_TOKEN</string>
        <key>SLACK_WEBHOOK_URL</key>
        <string>$SLACK_WEBHOOK_URL</string>
        <key>CF_BUDGET_WARN</key>
        <string>$CF_BUDGET_WARN</string>
        <key>CF_BUDGET_CRIT</key>
        <string>$CF_BUDGET_CRIT</string>
        <key>CF_QUIET</key>
        <string>1</string>
    </dict>
    <key>StartInterval</key>
    <integer>21600</integer>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/stderr.log</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
PLISTEOF

echo "LaunchAgent created at $PLIST_PATH"

# Load the agent
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"
echo "LaunchAgent loaded (runs every 6 hours + on boot)"

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "  Monitor runs every 6 hours automatically."
echo "  Logs: $LOG_DIR/"
echo "  Config: $ENV_FILE"
echo "  Plist: $PLIST_PATH"
echo ""
echo "  Manual run:  source $ENV_FILE && node $MONITOR_SCRIPT"
echo "  View logs:   tail -f $LOG_DIR/stdout.log"
echo "  Stop:        launchctl unload $PLIST_PATH"
echo "  Uninstall:   launchctl unload $PLIST_PATH && rm $PLIST_PATH"
echo ""
