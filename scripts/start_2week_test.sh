#!/bin/bash
#
# Start 2-Week Live Test
#
# This script starts the bot in dry-run mode with real market data
# and sets up monitoring for a 2-week test period.
#

set -e

echo "================================================================================
"
echo "           🚀 STARTING 2-WEEK LIVE TEST"
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

# Display configuration
echo ""
echo "================================================================================
"
echo "           ⚙️  TEST CONFIGURATION"
echo "================================================================================
"
echo ""
echo "Strategy:              MomentumMeanReversion (Sharia-Compliant)"
echo "Trading Mode:          DRY-RUN (Paper Trading)"
echo "Initial Balance:       \$10,000 USDT (virtual)"
echo "Trading Pairs:         BTC/USDT, ETH/USDT, SOL/USDT"
echo "Max Open Trades:       3"
echo "Timeframe:             15 minutes"
echo "Test Duration:         14 days (2 weeks)"
echo ""
echo "Data Source:           Real-time from Binance"
echo "Risk per Trade:        ~2% (via stop loss)"
echo "Leverage:              1x (Spot only - Halal ✅)"
echo ""
echo "================================================================================
"
echo ""

# Ask for confirmation
read -p "Do you want to start the 2-week test? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Test cancelled."
    exit 0
fi

echo ""
echo "================================================================================
"
echo "           🎬 STARTING BOT"
echo "================================================================================
"
echo ""

# Initialize session
echo "📊 Initializing session tracker..."
python3 monitoring/live_tracker.py

# Start bot in background with auto-restart
echo "🤖 Starting Freqtrade bot..."
echo ""
echo "The bot will run in the background and auto-restart if it crashes."
echo "Logs are saved to: user_data/logs/freqtrade.log"
echo ""

# Create wrapper script for auto-restart
cat > /tmp/freqtrade_wrapper.sh << 'EOF'
#!/bin/bash
while true; do
    echo "[$(date)] Starting Freqtrade..." >> user_data/logs/freqtrade.log
    freqtrade trade \
        --config config/config.json \
        --strategy MomentumMeanReversion \
        --logfile user_data/logs/freqtrade.log \
        2>&1 | tee -a user_data/logs/freqtrade.log

    EXIT_CODE=$?
    echo "[$(date)] Freqtrade exited with code $EXIT_CODE" >> user_data/logs/freqtrade.log

    # If exit code is 0, user stopped it intentionally
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Clean exit, stopping wrapper." >> user_data/logs/freqtrade.log
        break
    fi

    # Otherwise, restart after 10 seconds
    echo "[$(date)] Restarting in 10 seconds..." >> user_data/logs/freqtrade.log
    sleep 10
done
EOF

chmod +x /tmp/freqtrade_wrapper.sh

# Start wrapper in background
nohup bash /tmp/freqtrade_wrapper.sh > user_data/logs/wrapper.log 2>&1 &
BOT_PID=$!

# Save PID
echo $BOT_PID > user_data/bot.pid
echo "✅ Bot started with PID: $BOT_PID"
echo ""

# Start daily report cron job (runs at midnight)
echo "📅 Setting up daily reports..."
cat > /tmp/daily_report_cron.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate
python3 monitoring/live_tracker.py > user_data/live_test_results/daily_reports/report_$(date +%Y%m%d).txt 2>&1
EOF

chmod +x /tmp/daily_report_cron.sh

# Create a crontab entry (optional - user can set up manually)
echo "⚠️  Optional: Set up daily reports by adding this to crontab:"
echo "   0 0 * * * cd $(pwd) && bash /tmp/daily_report_cron.sh"
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
echo "           ✅ 2-WEEK TEST STARTED SUCCESSFULLY!"
echo "================================================================================
"
echo ""
echo "📊 Monitor your bot with these commands:"
echo ""
echo "   1. View live dashboard:"
echo "      python monitoring/live_dashboard.py"
echo ""
echo "   2. View logs:"
echo "      tail -f user_data/logs/freqtrade.log"
echo ""
echo "   3. Generate daily report:"
echo "      python monitoring/live_tracker.py"
echo ""
echo "   4. Check bot status:"
echo "      ./scripts/check_status.sh"
echo ""
echo "   5. Stop the bot:"
echo "      ./scripts/stop_2week_test.sh"
echo ""
echo "================================================================================
"
echo "           📅 TEST SCHEDULE"
echo "================================================================================
"
echo ""
echo "Start Date:     $(date '+%Y-%m-%d %H:%M:%S')"
echo "Expected End:   $(date -d '+14 days' '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "Daily reports will be generated automatically."
echo "After 2 weeks, run: python monitoring/generate_final_report.py"
echo ""
echo "================================================================================
"
echo "           ⚠️  IMPORTANT REMINDERS"
echo "================================================================================
"
echo ""
echo "1. Keep your laptop running (or set up on a server)"
echo "2. Ensure stable internet connection"
echo "3. The bot will auto-restart if it crashes"
echo "4. Check the dashboard daily to monitor performance"
echo "5. This is DRY-RUN mode - no real money at risk ✅"
echo "6. Bot is Sharia-compliant (spot trading only, no leverage)"
echo ""
echo "================================================================================
"
echo ""
echo "🎉 Good luck with your 2-week test!"
echo "May Allah (SWT) bless your trading."
echo ""
echo "Press Ctrl+C to return to terminal (bot continues in background)"
echo ""

# Optional: Start dashboard immediately
read -p "Do you want to view the live dashboard now? (yes/no): " show_dashboard
if [ "$show_dashboard" = "yes" ]; then
    python monitoring/live_dashboard.py
fi
