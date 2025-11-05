#!/bin/bash
# Run Hyperopt to optimize strategy parameters
# Usage: ./scripts/run_hyperopt.sh [strategy_name] [epochs] [loss_function]

set -e

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Default parameters
STRATEGY="${1:-MomentumMeanReversion}"
EPOCHS="${2:-500}"
LOSS="${3:-SharpeHyperOptLoss}"
TIMEFRAME="15m"
TIMERANGE="20240101-20251101"
CONFIG="config/config.json"

echo "========================================="
echo "Running Hyperopt Optimization"
echo "========================================="
echo ""
echo "Strategy: $STRATEGY"
echo "Epochs: $EPOCHS"
echo "Loss Function: $LOSS"
echo "Timeframe: $TIMEFRAME"
echo "Timerange: $TIMERANGE"
echo ""
echo "⚠️  This may take several hours depending on epochs..."
echo ""

# Run hyperopt
freqtrade hyperopt \
    --config "$CONFIG" \
    --strategy "$STRATEGY" \
    --timeframe "$TIMEFRAME" \
    --timerange "$TIMERANGE" \
    --hyperopt-loss "$LOSS" \
    --epochs "$EPOCHS" \
    --spaces all \
    --export trades

echo ""
echo "========================================="
echo "✅ Hyperopt complete!"
echo "========================================="
echo ""
echo "Results saved to: user_data/hyperopt_results/"
echo ""
echo "Next steps:"
echo "1. Review best parameters above"
echo "2. Update strategy with optimized parameters"
echo "3. Run backtest with new parameters: ./scripts/run_backtest.sh"
