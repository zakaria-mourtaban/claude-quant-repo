#!/bin/bash
#
# Start Staged Live Test with Network Resilience
#
# This script starts the bot in stages with auto-restart and network reconnection
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "================================================================================
"
echo "           🚀 STARTING STAGED LIVE TEST"
echo "================================================================================
"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Freqtrade is installed
if ! command -v freqtrade &> /dev/null; then
    echo "❌ Freqtrade not installed!"
    echo "Please install: pip install freqtrade"
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p user_data/live_test_results
mkdir -p user_data/live_test_results/daily_reports
mkdir -p user_data/logs

# Check configuration
if [ ! -f "config/config.json" ]; then
    echo "❌ Configuration file not found: config/config.json"
    exit 1
fi

# Initialize stage manager
echo "🎯 Initializing stage system..."
python3 monitoring/stage_manager.py > /dev/null 2>&1

# Get current stage
CURRENT_STAGE=$(python3 << 'EOF'
import sys
sys.path.insert(0, 'monitoring')
from stage_manager import StageManager
manager = StageManager()
stage_info = manager.get_current_stage_info()
print(f"{stage_info['stage_number']}:{stage_info['stage_name']}")
EOF
)

STAGE_NUM=$(echo $CURRENT_STAGE | cut -d':' -f1)
STAGE_NAME=$(echo $CURRENT_STAGE | cut -d':' -f2-)

# Display configuration
echo ""
echo "================================================================================
"
echo "           ⚙️  TEST CONFIGURATION"
echo "================================================================================
"
echo ""
echo "🎯 CURRENT STAGE:      $STAGE_NAME"
echo ""
echo "Strategy:              MomentumMeanReversion (Sharia-Compliant)"
echo "Trading Mode:          DRY-RUN (Paper Trading)"
echo "Initial Balance:       \$10,000 USDT (virtual)"
echo "Trading Pairs:         BTC/USDT, ETH/USDT, SOL/USDT"
echo "Max Open Trades:       3"
echo "Timeframe:             15 minutes"
echo ""
echo "Data Source:           Real-time from Binance"
echo "Risk per Trade:        ~2% (via stop loss)"
echo "Leverage:              1x (Spot only - Halal ✅)"
echo ""
echo "🛡️  RESILIENCE FEATURES:"
echo "   ✅ Auto-restart on crash"
echo "   ✅ Network reconnection with exponential backoff"
echo "   ✅ Stage-based progression"
echo "   ✅ Downtime tracking"
echo ""
echo "================================================================================
"
echo ""

# Ask for confirmation
read -p "Do you want to start the staged test? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Test cancelled."
    exit 0
fi

echo ""
echo "================================================================================
"
echo "           🎬 STARTING BOT WITH NETWORK RESILIENCE"
echo "================================================================================
"
echo ""

# Initialize session
echo "📊 Initializing session tracker..."
python3 monitoring/live_tracker.py > /dev/null 2>&1

# Create resilient wrapper script
cat > /tmp/freqtrade_resilient_wrapper.sh << 'WRAPPER_EOF'
#!/bin/bash

PROJECT_ROOT="$1"
cd "$PROJECT_ROOT"
source venv/bin/activate

# Import stage manager functions
record_crash() {
    python3 << 'EOF'
import sys
sys.path.insert(0, 'monitoring')
from stage_manager import StageManager
manager = StageManager()
manager.record_crash()
print(f"Recorded crash #{manager.stage_data['crash_count']}")
EOF
}

record_disconnect() {
    python3 << 'EOF'
import sys
sys.path.insert(0, 'monitoring')
from stage_manager import StageManager
manager = StageManager()
manager.record_disconnect()
print(f"Recorded disconnect #{manager.stage_data['disconnect_count']}")
EOF
}

record_downtime() {
    local seconds=$1
    python3 << EOF
import sys
sys.path.insert(0, 'monitoring')
from stage_manager import StageManager
manager = StageManager()
manager.record_downtime($seconds)
print(f"Recorded {$seconds}s downtime")
EOF
}

CONSECUTIVE_FAILURES=0
MAX_CONSECUTIVE_FAILURES=5
RESTART_DELAY=5

while true; do
    echo "[$(date)] Starting Freqtrade..." | tee -a user_data/logs/freqtrade.log

    START_TIME=$(date +%s)

    # Start Freqtrade
    freqtrade trade \
        --config config/config.json \
        --strategy MomentumMeanReversion \
        --logfile user_data/logs/freqtrade.log \
        2>&1 | tee -a user_data/logs/freqtrade.log

    EXIT_CODE=$?
    END_TIME=$(date +%s)
    RUN_DURATION=$((END_TIME - START_TIME))

    echo "[$(date)] Freqtrade exited with code $EXIT_CODE after ${RUN_DURATION}s" | tee -a user_data/logs/freqtrade.log

    # If ran for less than 60 seconds, it's likely a startup failure
    if [ $RUN_DURATION -lt 60 ]; then
        CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
        echo "[$(date)] Quick failure detected ($CONSECUTIVE_FAILURES/$MAX_CONSECUTIVE_FAILURES)" | tee -a user_data/logs/freqtrade.log

        if [ $CONSECUTIVE_FAILURES -ge $MAX_CONSECUTIVE_FAILURES ]; then
            echo "[$(date)] ❌ TOO MANY CONSECUTIVE FAILURES - STOPPING" | tee -a user_data/logs/freqtrade.log
            echo "" | tee -a user_data/logs/freqtrade.log
            echo "The bot has failed $MAX_CONSECUTIVE_FAILURES times in a row." | tee -a user_data/logs/freqtrade.log
            echo "This may indicate a configuration or network issue." | tee -a user_data/logs/freqtrade.log
            echo "Please check the logs and fix the issue before restarting." | tee -a user_data/logs/freqtrade.log
            exit 1
        fi
    else
        # Reset consecutive failures if ran for more than 60 seconds
        CONSECUTIVE_FAILURES=0
    fi

    # If exit code is 0, user stopped it intentionally
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Clean exit, stopping wrapper." | tee -a user_data/logs/freqtrade.log
        break
    fi

    # Check if it's a network error (common error messages)
    if grep -q -i "network\|connection\|timeout\|dns\|resolve" user_data/logs/freqtrade.log | tail -100; then
        echo "[$(date)] Network error detected, recording disconnect" | tee -a user_data/logs/freqtrade.log
        record_disconnect
    else
        echo "[$(date)] Crash detected, recording crash" | tee -a user_data/logs/freqtrade.log
        record_crash
    fi

    # Exponential backoff for restart delay
    if [ $CONSECUTIVE_FAILURES -gt 0 ]; then
        RESTART_DELAY=$((5 * (2 ** (CONSECUTIVE_FAILURES - 1))))
        # Cap at 5 minutes
        if [ $RESTART_DELAY -gt 300 ]; then
            RESTART_DELAY=300
        fi
    else
        RESTART_DELAY=5
    fi

    echo "[$(date)] Restarting in ${RESTART_DELAY} seconds (attempt $((CONSECUTIVE_FAILURES + 1)))..." | tee -a user_data/logs/freqtrade.log

    # Record downtime
    record_downtime $RESTART_DELAY

    sleep $RESTART_DELAY
done
WRAPPER_EOF

chmod +x /tmp/freqtrade_resilient_wrapper.sh

# Start wrapper in background
echo "🤖 Starting bot with resilient wrapper..."
echo ""
nohup bash /tmp/freqtrade_resilient_wrapper.sh "$PROJECT_ROOT" > user_data/logs/wrapper.log 2>&1 &
BOT_PID=$!

# Save PID
echo $BOT_PID > user_data/bot.pid
echo "✅ Bot started with PID: $BOT_PID"
echo ""

# Wait for bot to initialize
echo "⏳ Waiting for bot to initialize..."
sleep 5

# Check if bot is running
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is running!"
else
    echo "❌ Bot failed to start. Check logs: user_data/logs/freqtrade.log"
    exit 1
fi

echo ""
echo "================================================================================
"
echo "           ✅ STAGED TEST STARTED SUCCESSFULLY!"
echo "================================================================================
"
echo ""
echo "🎯 CURRENT STAGE: $STAGE_NAME"
echo ""
echo "📊 Monitor your bot with these commands:"
echo ""
echo "   1. View live dashboard (shows stage progress):"
echo "      python monitoring/live_dashboard.py"
echo ""
echo "   2. Check stage criteria:"
echo "      python monitoring/evaluate_stage.py"
echo ""
echo "   3. Advance to next stage (when ready):"
echo "      python monitoring/advance_stage.py"
echo ""
echo "   4. View logs:"
echo "      tail -f user_data/logs/freqtrade.log"
echo ""
echo "   5. Check bot status:"
echo "      ./scripts/check_status.sh"
echo ""
echo "   6. Stop the bot:"
echo "      ./scripts/stop_2week_test.sh"
echo ""
echo "================================================================================
"
echo "           🎯 STAGE PROGRESSION"
echo "================================================================================
"
echo ""
echo "Stage 1: Initial Testing (3-5 days)"
echo "   Goal: Verify bot stability and basic functionality"
echo "   Criteria: 10+ trades, 30%+ win rate, <30% drawdown"
echo ""
echo "Stage 2: Performance Validation (7-10 days)"
echo "   Goal: Validate strategy performance"
echo "   Criteria: 25+ trades, 40%+ win rate, positive return, <20% drawdown"
echo ""
echo "Stage 3: Final Validation (14 days)"
echo "   Goal: Confirm consistency over 2 weeks"
echo "   Criteria: 40+ trades, 40%+ win rate, 2%+ return, Sharpe > 1.0"
echo ""
echo "💡 The bot will automatically track your progress."
echo "   Check criteria anytime: python monitoring/evaluate_stage.py"
echo "   When all criteria met: python monitoring/advance_stage.py"
echo ""
echo "================================================================================
"
echo "           ⚠️  IMPORTANT REMINDERS"
echo "================================================================================
"
echo ""
echo "1. Keep your laptop running (or set up on a server)"
echo "2. Bot will auto-restart if it crashes or loses network"
echo "3. Check the dashboard daily to monitor progress"
echo "4. Advance stages only when ALL criteria are met"
echo "5. This is DRY-RUN mode - no real money at risk ✅"
echo "6. Bot is Sharia-compliant (spot trading only, no leverage)"
echo ""
echo "================================================================================
"
echo ""
echo "🎉 Good luck with Stage $STAGE_NUM!"
echo "May Allah (SWT) bless your trading."
echo ""

# Optional: Start dashboard immediately
read -p "Do you want to view the live dashboard now? (yes/no): " show_dashboard
if [ "$show_dashboard" = "yes" ]; then
    python monitoring/live_dashboard.py
fi
