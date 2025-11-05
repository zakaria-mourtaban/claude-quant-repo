#!/bin/bash
# Start bot on Bybit Testnet (demo trading with virtual funds)
# Usage: ./scripts/start_testnet.sh [strategy_name]

set -e

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with Bybit Testnet API keys"
    echo "See: docs/BYBIT_TESTNET_SETUP.md"
    exit 1
fi

STRATEGY="${1:-MomentumMeanReversion}"
CONFIG="config/config_bybit_testnet.json"

echo "========================================="
echo "Starting Freqtrade on Bybit TESTNET"
echo "========================================="
echo ""
echo "Strategy: $STRATEGY"
echo "Config: $CONFIG"
echo ""
echo "⚠️  TESTNET MODE: Using virtual funds (no real money)"
echo "This trades on Bybit Testnet with \$50,000 virtual balance"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Start freqtrade on testnet
freqtrade trade \
    --config "$CONFIG" \
    --strategy "$STRATEGY"
