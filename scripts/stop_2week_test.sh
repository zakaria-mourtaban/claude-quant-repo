#!/bin/bash
#
# Stop 2-Week Live Test
#
# Gracefully stops the trading bot
#

echo "================================================================================
"
echo "           🛑 STOPPING 2-WEEK TEST"
echo "================================================================================
"
echo ""

# Check if PID file exists
if [ ! -f "user_data/bot.pid" ]; then
    echo "⚠️  No PID file found. Bot may not be running."
    echo ""
    echo "Checking for Freqtrade processes..."
    if pgrep -f "freqtrade trade" > /dev/null; then
        echo "Found running Freqtrade process(es):"
        ps aux | grep "freqtrade trade" | grep -v grep
        echo ""
        read -p "Kill all Freqtrade processes? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            pkill -f "freqtrade trade"
            echo "✅ Killed all Freqtrade processes"
        fi
    else
        echo "No Freqtrade processes found."
    fi
    exit 0
fi

# Read PID
BOT_PID=$(cat user_data/bot.pid)
echo "Found bot PID: $BOT_PID"
echo ""

# Check if process is running
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "Stopping bot (PID: $BOT_PID)..."

    # Send SIGTERM (graceful shutdown)
    kill $BOT_PID 2>/dev/null

    # Wait for up to 30 seconds for graceful shutdown
    for i in {1..30}; do
        if ! ps -p $BOT_PID > /dev/null 2>&1; then
            echo "✅ Bot stopped gracefully"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""

    # Force kill if still running
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo "⚠️  Bot didn't stop gracefully, force killing..."
        kill -9 $BOT_PID 2>/dev/null
        sleep 2

        if ps -p $BOT_PID > /dev/null 2>&1; then
            echo "❌ Failed to stop bot"
            exit 1
        else
            echo "✅ Bot force-killed"
        fi
    fi
else
    echo "⚠️  Process not running (PID $BOT_PID not found)"
fi

# Also kill wrapper script if running
pkill -f "freqtrade_wrapper" 2>/dev/null && echo "✅ Stopped wrapper script"

# Remove PID file
rm -f user_data/bot.pid
echo "✅ Cleaned up PID file"

echo ""
echo "================================================================================
"
echo "           ✅ BOT STOPPED"
echo "================================================================================
"
echo ""
echo "Your trading session has been saved."
echo ""
echo "📊 View results:"
echo "   - Live tracker: python monitoring/live_tracker.py"
echo "   - Final report: python monitoring/generate_final_report.py"
echo "   - Trade log: user_data/trades.json"
echo "   - Daily reports: user_data/live_test_results/daily_reports/"
echo ""
echo "🔄 Restart test:"
echo "   ./scripts/start_2week_test.sh"
echo ""
echo "================================================================================
"
