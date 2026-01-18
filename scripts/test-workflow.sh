#!/bin/bash
# =============================================================================
# Test the Multifamily Deep Research Engine Workflow
# =============================================================================
# Usage: ./scripts/test-workflow.sh [address] [deal_name]
# =============================================================================

WEBHOOK_URL="${N8N_WEBHOOK_URL:-https://n8n.flowbaby.net/webhook/analyze-property}"

# Default test property
ADDRESS="${1:-123 Main Street, Austin, TX 78701}"
DEAL_NAME="${2:-Test Property Analysis}"

echo "=============================================="
echo "  Multifamily Deep Research Engine - Test"
echo "=============================================="
echo ""
echo "Webhook URL: $WEBHOOK_URL"
echo "Address:     $ADDRESS"
echo "Deal Name:   $DEAL_NAME"
echo ""
echo "Sending request..."
echo ""

# Send the request
RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"address\": \"$ADDRESS\",
    \"deal_name\": \"$DEAL_NAME\",
    \"context_files\": []
  }")

# Check if curl succeeded
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to connect to webhook"
  exit 1
fi

# Pretty print the response if jq is available
if command -v jq &> /dev/null; then
  echo "Response:"
  echo "$RESPONSE" | jq .
else
  echo "Response (install jq for pretty printing):"
  echo "$RESPONSE"
fi

echo ""
echo "=============================================="
