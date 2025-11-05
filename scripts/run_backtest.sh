#!/bin/bash
# Run backtest for a strategy
# Usage: ./scripts/run_backtest.sh [strategy_name] [timeframe] [timerange]

set -e

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Default parameters
STRATEGY="${1:-MomentumMeanReversion}"
TIMEFRAME="${2:-15m}"
TIMERANGE="${3:-20240101-20251101}"
CONFIG="config/config.json"

echo "========================================="
echo "Running Backtest"
echo "========================================="
echo ""
echo "Strategy: $STRATEGY"
echo "Timeframe: $TIMEFRAME"
echo "Timerange: $TIMERANGE"
echo "Config: $CONFIG"
echo ""

# Run backtest
freqtrade backtesting \
    --config "$CONFIG" \
    --strategy "$STRATEGY" \
    --timeframe "$TIMEFRAME" \
    --timerange "$TIMERANGE" \
    --export trades \
    --export-filename user_data/backtest_results/backtest-result-${STRATEGY}-${TIMEFRAME}-$(date +%Y%m%d-%H%M%S).json

echo ""
echo "========================================="
echo "✅ Backtest complete!"
echo "========================================="
echo ""
echo "Results saved to: user_data/backtest_results/"
echo ""
echo "Next steps:"
echo "1. Review results above"
echo "2. Plot results: freqtrade plot-dataframe --strategy $STRATEGY --pairs BTC/USDT"
echo "3. Optimize parameters: ./scripts/run_hyperopt.sh"
