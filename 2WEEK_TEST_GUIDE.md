# 2-Week Live Test Guide

## 📋 Overview

This guide will help you run a **2-week live test** of the Sharia-compliant trading bot on your laptop. The bot will:

- Trade with **real market data** from Binance
- Use **paper trading** (dry-run mode - no real money)
- Run **continuously** for 2 weeks
- **Auto-restart** if it crashes
- Generate **daily reports** automatically
- Provide a **real-time dashboard** to monitor performance

### Key Features

✅ **Zero Risk** - Dry-run mode (fake money, real prices)
✅ **Real Market Data** - Live data from Binance exchange
✅ **Sharia Compliant** - Spot trading only, no leverage, long positions only
✅ **Auto-Restart** - Bot automatically restarts if it crashes
✅ **Daily Reports** - Automated performance tracking
✅ **Live Dashboard** - Real-time monitoring
✅ **Final Report** - Comprehensive analysis after 2 weeks

---

## 🚀 Quick Start

### 1. Start the 2-Week Test

```bash
./scripts/start_2week_test.sh
```

This will:
- Start the bot in dry-run mode
- Initialize performance tracking
- Set up auto-restart
- Begin the 2-week test

### 2. Monitor the Bot

**Real-Time Dashboard** (updates every 30 seconds):
```bash
python monitoring/live_dashboard.py
```

**Check Status** (quick snapshot):
```bash
./scripts/check_status.sh
```

**View Logs** (detailed activity):
```bash
tail -f user_data/logs/freqtrade.log
```

### 3. After 2 Weeks - Generate Final Report

```bash
python monitoring/generate_final_report.py
```

---

## 📊 What You'll See

### Live Dashboard Example

```
================================================================================
                    🤖 LIVE TRADING DASHBOARD - 2 WEEK TEST
================================================================================

⏱️  TEST PROGRESS
--------------------------------------------------------------------------------
   [████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 35.7%
   Started:     2025-11-06 18:00:00
   Current:     2025-11-11 18:00:00
   Elapsed:     5d 0h 0m (Day 5 of 14)
   Remaining:   9d 0h 0m
   ETA:         2025-11-20 18:00:00

💰 PERFORMANCE
--------------------------------------------------------------------------------
   Initial Balance:      $10,000.00
   Current Balance:      $10,412.00 📈
   Profit/Loss:          +$412.00 (+4.12%)
   Daily Average:        +$82.40/day

📊 TRADING STATISTICS
--------------------------------------------------------------------------------
   Total Trades:         25
   Winning Trades:       15 (60.0%)
   Losing Trades:        10
   Trades per Day:       5.0 trades/day

⚠️  RISK METRICS
--------------------------------------------------------------------------------
   Max Drawdown:         3.11%
   Risk Level:           🟢 LOW RISK

📝 RECENT TRADES (Last 10)
--------------------------------------------------------------------------------
   ✅ BTC/USDT    2025-11-11 17:00  2025-11-11 17:30  $+52.85    +1.55%   0.5h
   ❌ ETH/USDT    2025-11-11 14:00  2025-11-11 14:45  $-23.06    -0.67%   0.8h
   ...
```

### Daily Report Example

Every day, a report is automatically generated showing:
- Daily performance summary
- Cumulative returns
- Trade statistics
- Progress toward 2-week goal

---

## 📁 File Structure

After starting the test, you'll see:

```
claude-quant-repo/
├── user_data/
│   ├── live_test_results/
│   │   ├── current_session.json       # Current test session data
│   │   ├── daily_reports/             # Daily performance reports
│   │   │   ├── report_20251106.txt
│   │   │   ├── report_20251107.txt
│   │   │   └── ...
│   │   └── FINAL_REPORT.txt           # Generated after 2 weeks
│   │
│   ├── logs/
│   │   ├── freqtrade.log              # Bot activity log
│   │   └── wrapper.log                # Auto-restart wrapper log
│   │
│   ├── trades.json                     # All executed trades
│   └── bot.pid                         # Bot process ID
│
└── monitoring/
    ├── live_dashboard.py               # Real-time dashboard
    ├── live_tracker.py                 # Daily report generator
    └── generate_final_report.py        # Final analysis
```

---

## 🎮 Commands Reference

### Start/Stop

| Command | Description |
|---------|-------------|
| `./scripts/start_2week_test.sh` | Start the 2-week test |
| `./scripts/stop_2week_test.sh` | Stop the bot (preserves data) |
| `./scripts/check_status.sh` | Check bot status |

### Monitoring

| Command | Description |
|---------|-------------|
| `python monitoring/live_dashboard.py` | Real-time dashboard (updates every 30s) |
| `python monitoring/live_tracker.py` | Generate current daily report |
| `tail -f user_data/logs/freqtrade.log` | View live logs |
| `cat user_data/live_test_results/daily_reports/report_YYYYMMDD.txt` | View specific day's report |

### After 2 Weeks

| Command | Description |
|---------|-------------|
| `python monitoring/generate_final_report.py` | Generate comprehensive final report |
| `cat user_data/live_test_results/FINAL_REPORT.txt` | View final report |

---

## ⚙️ Test Configuration

The 2-week test uses these settings:

| Setting | Value |
|---------|-------|
| **Trading Mode** | Dry-Run (Paper Trading) |
| **Initial Balance** | $10,000 USDT (virtual) |
| **Trading Pairs** | BTC/USDT, ETH/USDT, SOL/USDT |
| **Max Open Trades** | 3 positions |
| **Timeframe** | 15 minutes |
| **Strategy** | MomentumMeanReversion (Sharia-Compliant) |
| **Leverage** | 1x (Spot only - Halal ✅) |
| **Risk per Trade** | ~2% (via stop loss) |
| **Data Source** | Real-time from Binance |

---

## 🎯 Success Criteria

After 2 weeks, the final report will evaluate these criteria:

| Criterion | Target | Good Performance Example |
|-----------|--------|--------------------------|
| **Win Rate** | > 40% | 60% |
| **Total Return** | Positive | +4.12% |
| **Profit Factor** | > 1.5 | 1.63 |
| **Max Drawdown** | < 20% | 3.11% |
| **Total Trades** | ≥ 20 | 25+ |
| **Sharpe Ratio** | > 1.0 | 3.25 |

---

## 🔧 Troubleshooting

### Bot Not Starting

```bash
# Check if Freqtrade is installed
freqtrade --version

# If not installed
source venv/bin/activate
pip install freqtrade

# Try starting again
./scripts/start_2week_test.sh
```

### Bot Stopped Unexpectedly

The bot has auto-restart enabled, but if it keeps crashing:

```bash
# Check logs for errors
tail -50 user_data/logs/freqtrade.log

# Common issues:
# 1. Network issues - check internet connection
# 2. API rate limits - wait a few minutes and restart
# 3. Configuration errors - verify config/config.json

# Restart manually
./scripts/stop_2week_test.sh
./scripts/start_2week_test.sh
```

### Dashboard Not Updating

```bash
# Ensure bot is running
./scripts/check_status.sh

# If bot is running but dashboard shows old data:
# 1. Trades may not be happening (normal in low volatility)
# 2. Check logs to see if bot is active:
tail -f user_data/logs/freqtrade.log
```

### No Trades After Several Days

This can be normal! The strategy only trades when conditions are right:

- **ADX > 25**: Trending market (momentum entry)
- **ADX < 20**: Ranging market (mean reversion entry)
- **Volume confirmation**: Needs sufficient volume
- **Not overbought/oversold**: Won't enter at extremes

If you want more trades:
1. Add more trading pairs to `config/config.json`
2. Increase `max_open_trades` from 3 to 5
3. Consider running hyperopt to find more aggressive parameters

---

## 💡 Tips for Success

### 1. **Keep Your Laptop Running**

The bot needs to run continuously for 2 weeks:

- **Option A**: Keep laptop on 24/7 (disable sleep mode)
- **Option B**: Run on a cloud server (AWS, DigitalOcean, etc.)
- **Option C**: Use a Raspberry Pi or dedicated machine

**Disable laptop sleep:**
```bash
# On Linux:
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

# Remember to re-enable after test:
sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

### 2. **Ensure Stable Internet**

- Bot downloads real-time market data
- Needs consistent internet connection
- If connection drops, bot will reconnect automatically

### 3. **Check Daily**

Review the dashboard once per day:
```bash
python monitoring/live_dashboard.py
```

Look for:
- ✅ Positive cumulative return
- ✅ Win rate above 40%
- ✅ Max drawdown below 20%
- ⚠️  If drawdown > 15%, monitor closely

### 4. **Don't Interfere**

- Don't modify config during the test
- Don't manually close trades
- Let the strategy run its course
- This is a hands-off performance test

### 5. **Review Weekly**

At day 7, generate a report:
```bash
python monitoring/live_tracker.py
```

If performance is very poor (e.g., -10% return, 20% win rate):
- Consider stopping the test
- Review strategy parameters
- Possibly run hyperopt for better parameters

---

## 📈 What Happens After 2 Weeks

### 1. Generate Final Report

```bash
python monitoring/generate_final_report.py
```

This creates a comprehensive report with:
- Overall performance metrics
- Trade-by-trade analysis
- Daily performance trend
- Success criteria evaluation
- Recommendations for next steps

### 2. Review Results

Open the report:
```bash
cat user_data/live_test_results/FINAL_REPORT.txt
```

### 3. Next Steps Based on Results

#### ✅ If Results Are Good (5/6 criteria passed):

1. **Proceed to Bybit Testnet** (virtual funds on real exchange):
   ```bash
   # Get API keys from https://testnet.bybit.com
   # Add to .env file
   ./scripts/start_testnet.sh
   ```

2. **Run for another 8-12 weeks** on Bybit Testnet

3. **If still successful, consider live trading**:
   - Start with 1-5% of total capital
   - Monitor closely
   - Scale up gradually

#### ⚠️  If Results Are Moderate (3-4 criteria passed):

1. **Run hyperopt** to optimize parameters:
   ```bash
   freqtrade hyperopt \
     --config config/config.json \
     --strategy MomentumMeanReversion \
     --hyperopt-loss SharpeHyperOptLoss \
     --spaces buy sell \
     --epochs 100
   ```

2. **Run another 2-week test** with optimized parameters

3. **Consider different market conditions**:
   - Test during trending market
   - Test during ranging market
   - Test during high volatility

#### ❌ If Results Are Poor (<3 criteria passed):

1. **Analyze what went wrong**:
   - Check trade log
   - Review market conditions during test
   - Look for pattern in losses

2. **Consider adjustments**:
   - Different timeframe (5m, 1h instead of 15m)
   - Different pairs (add more or change selection)
   - Adjust risk management (tighter stops)

3. **Run hyperopt** to find better parameters

4. **Test different strategies** if needed

---

## 🌙 Sharia Compliance During Test

The bot remains **fully Halal** throughout the test:

✅ **Spot Trading Only**: No margin, no futures
✅ **1x Leverage**: Uses only your capital (even though it's virtual)
✅ **Long Positions Only**: No short selling
✅ **No Interest**: No Riba (usury)
✅ **Real Assets**: Buys and sells actual cryptocurrency

Even though this is paper trading (virtual money), the bot operates exactly as it would with real money - following all Sharia principles.

---

## 📞 Need Help?

### Check Resources

1. **SHARIA_COMPLIANCE.md** - Complete Halal trading guide
2. **BACKTEST_RESULTS.md** - Historical performance analysis
3. **docs/QUICK_START.md** - Setup and installation guide
4. **docs/DEPLOYMENT.md** - Deployment instructions

### Common Questions

**Q: Can I pause the test and resume later?**
A: Yes! Just stop the bot (`./scripts/stop_2week_test.sh`). Your session data is saved. When you restart, it will continue from where you left off.

**Q: Can I run multiple tests simultaneously?**
A: Not recommended. Run one test at a time for clean results. If you want to test multiple strategies, run them sequentially.

**Q: What if my laptop restarts?**
A: The bot won't auto-start on reboot. You'll need to manually restart it:
```bash
./scripts/start_2week_test.sh
```
Your session data is preserved, so you won't lose progress.

**Q: Can I change pairs during the test?**
A: Not recommended. This would invalidate the test. If you must, stop the test, modify `config/config.json`, and start a new test.

**Q: How much disk space do I need?**
A: Very little. Logs and data files typically use less than 100MB over 2 weeks.

**Q: Does this use a lot of internet bandwidth?**
A: No. The bot downloads small amounts of market data (~15MB/day). Total for 2 weeks: ~200MB.

---

## 🎉 Final Thoughts

This 2-week test will give you:

1. **Confidence** in the strategy's performance
2. **Experience** monitoring a live bot
3. **Data** to make informed decisions
4. **Peace of mind** before risking real money

Remember:
- This is paper trading (zero risk)
- Past performance ≠ future results
- Start small when going live
- Keep learning and improving

**Good luck with your 2-week test!**
**May Allah (SWT) bless your trading.**

---

## 📋 Pre-Flight Checklist

Before starting, ensure:

- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Freqtrade installed (`freqtrade --version`)
- [ ] Strategy file exists (`user_data/strategies/MomentumMeanReversion.py`)
- [ ] Config file exists (`config/config.json`)
- [ ] Internet connection stable
- [ ] Laptop can stay on for 2 weeks (or using server/Pi)
- [ ] Sufficient disk space (at least 1GB free)
- [ ] Scripts are executable (`chmod +x scripts/*.sh`)

### Ready to Start?

```bash
./scripts/start_2week_test.sh
```

🚀 **Let's begin your 2-week live test!**

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-06
**Strategy**: MomentumMeanReversion v1.0.1 (Sharia-Compliant)
