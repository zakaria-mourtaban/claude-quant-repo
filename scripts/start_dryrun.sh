#!/bin/bash
# Start bot in dry-run mode (paper trading with real-time data)
# Usage: ./scripts/start_dryrun.sh [strategy_name]

set -e

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

STRATEGY="${1:-MomentumMeanReversion}"
CONFIG="config/config.json"

echo "========================================="
echo "Starting Freqtrade in DRY-RUN Mode"
echo "========================================="
echo ""
echo "Strategy: $STRATEGY"
echo "Config: $CONFIG"
echo ""
echo "⚠️  DRY-RUN MODE: No real money will be used"
echo "This simulates trading with real-time market data"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""

# Start freqtrade in dry-run mode
freqtrade trade \
    --config "$CONFIG" \
    --strategy "$STRATEGY"
