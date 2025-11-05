#!/bin/bash
# Download historical data for backtesting
# This script downloads OHLCV data from Binance for multiple pairs and timeframes

set -e

echo "========================================="
echo "Downloading Historical Data for Backtesting"
echo "========================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Configuration
EXCHANGE="binance"
DAYS=365
DATA_DIR="user_data/data"

# Pairs to download
PAIRS=(
    "BTC/USDT"
    "ETH/USDT"
    "SOL/USDT"
    "ADA/USDT"
    "AVAX/USDT"
    "MATIC/USDT"
    "DOT/USDT"
    "LINK/USDT"
)

# Timeframes to download
TIMEFRAMES=(
    "5m"
    "15m"
    "1h"
    "4h"
    "1d"
)

echo "Exchange: $EXCHANGE"
echo "Days: $DAYS"
echo "Pairs: ${PAIRS[@]}"
echo "Timeframes: ${TIMEFRAMES[@]}"
echo ""

# Convert pairs array to comma-separated string
PAIRS_STRING=$(IFS=, ; echo "${PAIRS[*]}")
TIMEFRAMES_STRING=$(IFS=, ; echo "${TIMEFRAMES[*]}")

echo "Starting download..."
echo ""

freqtrade download-data \
    --exchange "$EXCHANGE" \
    --pairs $PAIRS_STRING \
    --timeframes $TIMEFRAMES_STRING \
    --days $DAYS \
    --datadir "$DATA_DIR"

echo ""
echo "========================================="
echo "✅ Data download complete!"
echo "========================================="
echo ""
echo "Data saved to: $DATA_DIR/$EXCHANGE/"
echo ""
echo "Next steps:"
echo "1. Run a backtest: ./scripts/run_backtest.sh"
echo "2. Or optimize strategy: ./scripts/run_hyperopt.sh"
