#!/bin/bash
set -euo pipefail

###############################################################################
# Cloudflare Billing/Usage Alert Setup
# Account: 1364b528762500de4f870e064229d443 (anton.abyzov@gmail.com)
#
# Prerequisites:
#   1. Create an API token at https://dash.cloudflare.com/profile/api-tokens
#   2. Use template "Create Custom Token" with:
#        - Permissions: Account > Notifications > Edit
#        - Account Resources: Include > Anton.abyzov@gmail.com's Account
#   3. Run: CF_API_TOKEN=<your-token> ./setup-cf-billing-alerts.sh
###############################################################################

ACCOUNT_ID="1364b528762500de4f870e064229d443"
EMAIL="anton.abyzov@gmail.com"

if [ -z "${CF_API_TOKEN:-}" ]; then
  echo "==========================================================="
  echo " CF_API_TOKEN not set. Create one first:"
  echo ""
  echo " 1. Go to: https://dash.cloudflare.com/profile/api-tokens"
  echo " 2. Click 'Create Token'"
  echo " 3. Scroll to 'Create Custom Token' -> 'Get started'"
  echo " 4. Set:"
  echo "      Token name: billing-alerts-setup"
  echo "      Permissions: Account | Notifications | Edit"
  echo "      Account Resources: Include | Anton.abyzov@gmail.com's Account"
  echo " 5. Continue to summary -> Create Token"
  echo " 6. Copy the token and run:"
  echo ""
  echo "    CF_API_TOKEN=<token> $0"
  echo "==========================================================="
  exit 1
fi

TOKEN="$CF_API_TOKEN"

# -- Verify token --
echo "[1/5] Verifying API token..."
VERIFY=$(curl -sf "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null || true)
if ! echo "$VERIFY" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] else 1)" 2>/dev/null; then
  echo "  FAILED: Token is invalid or expired."
  echo "  Response: $VERIFY"
  exit 1
fi
echo "  Token is valid."

# -- Get available alert types --
echo ""
echo "[2/5] Fetching available alert types..."
AVAILABLE=$(curl -sf "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/alerting/v3/available_alerts" \
  -H "Authorization: Bearer $TOKEN")

if ! echo "$AVAILABLE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] else 1)" 2>/dev/null; then
  echo "  FAILED to fetch alert types. Token may lack Notifications permission."
  echo "  Response: $(echo "$AVAILABLE" | head -c 500)"
  exit 1
fi

# Find billing/usage alert types
BILLING_TYPE=$(echo "$AVAILABLE" | python3 -c "
import sys, json
data = json.load(sys.stdin)['result']
found = []
for category, alerts in data.items():
    for alert in alerts:
        atype = alert.get('type', '')
        name = alert.get('display_name', '')
        desc = alert.get('description', '')
        lower_all = (name + desc + atype + category).lower()
        if any(kw in lower_all for kw in ['billing', 'usage_based', 'spend', 'budget']):
            found.append(alert)
            print(f'  Found: {name} (type={atype})')
            if alert.get('filter_options'):
                print(f'    Filters: {json.dumps(alert[\"filter_options\"], indent=6)}')
if not found:
    print('  No billing-specific alert type found.')
    print('  Checking for Workers-related alerts...')
    for category, alerts in data.items():
        for alert in alerts:
            atype = alert.get('type', '')
            name = alert.get('display_name', '')
            lower_all = (name + atype + category).lower()
            if 'worker' in lower_all:
                print(f'  Workers alert: {name} (type={atype})')
                found.append(alert)
    if not found:
        print('  Dumping ALL alert types for manual review:')
        for category, alerts in data.items():
            for alert in alerts:
                print(f'    [{category}] {alert.get(\"display_name\",\"?\")} -> type={alert.get(\"type\",\"?\")}')
")

echo "$BILLING_TYPE"

# -- Get eligible notification destinations --
echo ""
echo "[3/5] Checking notification destinations..."
DESTINATIONS=$(curl -sf "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/alerting/v3/destinations/eligible" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo '{"success":false}')
echo "$DESTINATIONS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    result = data.get('result', {})
    for dtype, dests in result.items():
        print(f'  {dtype}: {json.dumps(dests)}')
else:
    print('  Could not fetch destinations (non-blocking)')
" 2>/dev/null || echo "  (parse error, continuing)"

# -- Create billing alerts --
echo ""
echo "[4/5] Creating usage/billing alerts..."

# Try the most likely alert type names
# We'll attempt billing_usage_alert first, then fall back to what we discovered
for ALERT_TYPE in "billing_usage_alert" "usage_based_billing"; do
  echo "  Trying alert_type='${ALERT_TYPE}'..."
  
  for CENTS in 5000 10000 15000 20000; do
    DOLLARS=$((CENTS / 100))

    RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/alerting/v3/policies" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"name\": \"Workers usage alert - \$${DOLLARS}\",
        \"description\": \"Alert when Workers monthly usage exceeds \$${DOLLARS}\",
        \"enabled\": true,
        \"alert_type\": \"${ALERT_TYPE}\",
        \"mechanisms\": {
          \"email\": [{\"id\": \"${EMAIL}\"}]
        },
        \"filters\": {
          \"product\": [\"workers\"],
          \"limit\": [\"${CENTS}\"]
        }
      }")

    SUCCESS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "error")

    if [ "$SUCCESS" = "True" ]; then
      POLICY_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['id'])" 2>/dev/null || echo "?")
      echo "    \$${DOLLARS} alert created (policy: ${POLICY_ID})"
    else
      ERROR_MSG=$(echo "$RESULT" | python3 -c "import sys,json; errs=json.load(sys.stdin).get('errors',[]); print(errs[0].get('message','unknown') if errs else 'unknown')" 2>/dev/null || echo "unknown")
      echo "    \$${DOLLARS} FAILED: ${ERROR_MSG}"
      
      if echo "$ERROR_MSG" | grep -qi "alert_type\|not valid\|not found\|not supported"; then
        echo "  Alert type '${ALERT_TYPE}' not supported. Trying next..."
        break
      fi
    fi
  done

  # Check if the first threshold succeeded - if so, we found the right type
  FIRST_CHECK=$(curl -sf "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/alerting/v3/policies" \
    -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
count = sum(1 for p in data.get('result',[]) if 'Workers usage alert' in p.get('name',''))
print(count)
" 2>/dev/null || echo "0")

  if [ "$FIRST_CHECK" -ge 1 ] 2>/dev/null; then
    echo "  Success with alert_type='${ALERT_TYPE}'!"
    break
  fi
done

# -- List final state --
echo ""
echo "[5/5] Current notification policies:"
curl -sf "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/alerting/v3/policies" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('success'):
    policies = data.get('result', [])
    if not policies:
        print('  No policies configured.')
    for p in policies:
        status = 'ON' if p.get('enabled') else 'OFF'
        mechs = ', '.join(p.get('mechanisms', {}).keys())
        print(f'  [{status}] {p[\"name\"]} (type: {p[\"alert_type\"]}, notify: {mechs})')
else:
    print('  Error fetching policies')
" 2>/dev/null || echo "  (Could not list policies)"

echo ""
echo "Done. If alerts could not be created via API, set them up manually in the dashboard:"
echo "  https://dash.cloudflare.com/${ACCOUNT_ID}/notifications/create"
