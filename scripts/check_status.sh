#!/bin/bash
#
# Check 2-Week Test Status
#
# Quick status check of the running bot
#

echo "================================================================================
"
echo "           📊 2-WEEK TEST STATUS"
echo "================================================================================
"
echo ""

# Check if bot is running
if [ -f "user_data/bot.pid" ]; then
    BOT_PID=$(cat user_data/bot.pid)
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo "✅ Bot Status: RUNNING (PID: $BOT_PID)"

        # Get process start time
        START_TIME=$(ps -p $BOT_PID -o lstart= 2>/dev/null)
        echo "   Started: $START_TIME"

        # Get CPU and memory usage
        CPU_MEM=$(ps -p $BOT_PID -o %cpu,%mem 2>/dev/null | tail -1)
        echo "   CPU/Memory: $CPU_MEM"
    else
        echo "❌ Bot Status: NOT RUNNING (stale PID file)"
        echo "   PID $BOT_PID not found"
    fi
else
    echo "❌ Bot Status: NOT RUNNING (no PID file)"
fi

echo ""

# Check for Freqtrade processes
FREQTRADE_COUNT=$(pgrep -f "freqtrade trade" | wc -l)
if [ $FREQTRADE_COUNT -gt 0 ]; then
    echo "🤖 Freqtrade Processes: $FREQTRADE_COUNT running"
    ps aux | grep "freqtrade trade" | grep -v grep | awk '{print "   PID:", $2, "CPU:", $3"%", "MEM:", $4"%"}'
else
    echo "🤖 Freqtrade Processes: None running"
fi

echo ""
echo "================================================================================
"
echo "           📈 PERFORMANCE SUMMARY"
echo "================================================================================
"
echo ""

# Quick performance check
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python3 << 'EOF'
import sys
sys.path.insert(0, 'monitoring')
from live_tracker import LivePerformanceTracker
from datetime import datetime

try:
    tracker = LivePerformanceTracker()
    tracker.update_from_freqtrade()
    status = tracker.get_current_status()

    print(f"💰 Balance:        ${status['current_balance']:,.2f} (started with ${status['initial_balance']:,.2f})")
    print(f"📊 Return:         {status['total_return_pct']:+.2f}%")
    print(f"📈 Trades:         {status['total_trades']} ({status['win_rate']:.1f}% win rate)")
    print(f"⚠️  Max Drawdown:   {status['max_drawdown_pct']:.2f}%")
    print(f"")
    print(f"⏱️  Test Progress:")
    print(f"   Days Elapsed:   {status['days_elapsed']} of 14")
    progress = min(status['days_elapsed'] / 14 * 100, 100)
    print(f"   Completion:     {progress:.0f}%")

    if status['days_elapsed'] < 14:
        days_left = 14 - status['days_elapsed']
        print(f"   Days Remaining: {days_left}")
    else:
        print(f"   Status:         ✅ TEST COMPLETE!")
        print(f"   Run: python monitoring/generate_final_report.py")

except Exception as e:
    print(f"⚠️  Could not load performance data: {e}")
    print("   This is normal if no trades have been executed yet.")
EOF
else
    echo "⚠️  Virtual environment not found"
fi

echo ""
echo "================================================================================
"
echo "           📁 FILES & LOGS"
echo "================================================================================
"
echo ""

# Check log file
if [ -f "user_data/logs/freqtrade.log" ]; then
    LOG_SIZE=$(du -h user_data/logs/freqtrade.log | cut -f1)
    LOG_LINES=$(wc -l < user_data/logs/freqtrade.log)
    LOG_MODIFIED=$(stat -c %y user_data/logs/freqtrade.log 2>/dev/null || stat -f "%Sm" user_data/logs/freqtrade.log)
    echo "📄 Log File:       user_data/logs/freqtrade.log"
    echo "   Size:           $LOG_SIZE ($LOG_LINES lines)"
    echo "   Last Modified:  $LOG_MODIFIED"
    echo ""
    echo "   Last 5 lines:"
    tail -5 user_data/logs/freqtrade.log | sed 's/^/   │ /'
else
    echo "📄 Log File:       Not found"
fi

echo ""

# Check trades file
if [ -f "user_data/trades.json" ]; then
    TRADES_SIZE=$(du -h user_data/trades.json | cut -f1)
    TRADES_COUNT=$(python3 -c "import json; print(len(json.load(open('user_data/trades.json'))))" 2>/dev/null || echo "?")
    echo "📊 Trades File:    user_data/trades.json"
    echo "   Size:           $TRADES_SIZE"
    echo "   Trades:         $TRADES_COUNT"
else
    echo "📊 Trades File:    Not found (no trades yet)"
fi

echo ""

# Check session file
if [ -f "user_data/live_test_results/current_session.json" ]; then
    SESSION_SIZE=$(du -h user_data/live_test_results/current_session.json | cut -f1)
    echo "💾 Session File:   user_data/live_test_results/current_session.json"
    echo "   Size:           $SESSION_SIZE"
else
    echo "💾 Session File:   Not found (not started yet)"
fi

echo ""
echo "================================================================================
"
echo "           🎮 COMMANDS"
echo "================================================================================
"
echo ""
echo "📊 View live dashboard:     python monitoring/live_dashboard.py"
echo "📝 View daily report:       python monitoring/live_tracker.py"
echo "📋 View logs:               tail -f user_data/logs/freqtrade.log"
echo "🛑 Stop bot:                ./scripts/stop_2week_test.sh"
echo "🔄 Restart bot:             ./scripts/stop_2week_test.sh && ./scripts/start_2week_test.sh"
echo "📊 Final report (after 2w): python monitoring/generate_final_report.py"
echo ""
echo "================================================================================
"
