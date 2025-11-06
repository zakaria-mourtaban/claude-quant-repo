# Staged Testing Guide - Multi-Stage Bot Validation

## 🎯 Overview

This guide covers the **Staged Testing System** - a robust, progressive validation approach that ensures your trading bot is ready for live trading through 3 distinct stages.

### Why Staged Testing?

Instead of a simple 2-week test, the staged approach:

✅ **Progressive Validation** - Each stage builds confidence gradually
✅ **Clear Criteria** - Know exactly what you need to pass each stage
✅ **Early Problem Detection** - Catch issues in Stage 1, not after 2 weeks
✅ **Network Resilience** - Auto-restart on crashes/disconnects
✅ **Flexibility** - Advance when ready, not on a fixed schedule

---

## 📋 The 3 Stages

### Stage 1: Initial Testing (3-5 days)
**Goal**: Verify bot stability and basic functionality

**Criteria to Advance**:
- ✅ Minimum 3 days running
- ✅ At least 10 trades executed
- ✅ Win rate > 30% (lenient)
- ✅ Max drawdown < 30% (lenient)
- ✅ Uptime > 80%

**What We're Testing**: Bot doesn't crash, trades execute, basic profitability

---

### Stage 2: Performance Validation (7-10 days)
**Goal**: Validate strategy performance with more data

**Criteria to Advance**:
- ✅ Minimum 7 days running
- ✅ At least 25 trades executed
- ✅ Win rate > 40%
- ✅ Positive return (any profit)
- ✅ Max drawdown < 20%
- ✅ Profit factor > 1.2
- ✅ Uptime > 85%

**What We're Testing**: Consistent profitability, risk management, reliability

---

### Stage 3: Final Validation (14 days)
**Goal**: Confirm consistency over 2 weeks

**Criteria to Advance**:
- ✅ Minimum 14 days running
- ✅ At least 40 trades executed
- ✅ Win rate > 40%
- ✅ Total return > 2%
- ✅ Max drawdown < 20%
- ✅ Profit factor > 1.5
- ✅ Sharpe ratio > 1.0
- ✅ Uptime > 90%

**What We're Testing**: Long-term viability, ready for live trading

---

## 🚀 Quick Start

### Step 1: Start the Staged Test

```bash
./scripts/start_staged_test.sh
```

This will:
- Initialize Stage 1
- Start bot with auto-restart
- Enable network reconnection
- Begin tracking all metrics

### Step 2: Monitor Progress

**Live Dashboard** (updates every 30 seconds):
```bash
python monitoring/live_dashboard.py
```

Shows:
- Current stage and progress
- Days elapsed in current stage
- Ready to advance indicator
- All performance metrics
- Reliability metrics (crashes, disconnects)

**Check Stage Criteria**:
```bash
python monitoring/evaluate_stage.py
```

Shows:
- Detailed breakdown of each criterion
- What you've achieved
- What's still needed
- Pass/fail status for each

### Step 3: Advance Stages

When all criteria are met:

```bash
python monitoring/advance_stage.py
```

This will:
- Verify all criteria
- Ask for confirmation
- Advance to next stage
- Show new stage requirements

### Step 4: Complete All Stages

After Stage 3 completion:

```bash
python monitoring/generate_final_report.py
```

---

## 🛡️ Network Resilience Features

### Auto-Restart on Crash

If the bot crashes:
1. ✅ Crash is automatically recorded
2. ✅ Bot restarts after 5 seconds
3. ✅ Continues from last known state
4. ✅ Downtime is tracked

### Network Reconnection

If network drops:
1. ✅ Disconnect is recorded
2. ✅ Bot attempts reconnection
3. ✅ Uses exponential backoff (5s, 10s, 20s, 40s...)
4. ✅ Caps at 5-minute retry interval

### Safety Limits

- **Max Consecutive Failures**: 5
- **Quick Failure**: < 60 seconds runtime
- **Auto-Stop**: After 5 quick failures (prevents boot loops)

Example scenario:
```
[11:00:00] Bot starts
[11:00:05] Crash (quick failure 1/5)
[11:00:10] Bot restarts (5s delay)
[11:00:15] Crash (quick failure 2/5)
[11:00:25] Bot restarts (10s delay)
[11:00:30] Crash (quick failure 3/5)
[11:00:50] Bot restarts (20s delay)
[11:01:10] Runs successfully for 10 minutes
[11:11:10] Network disconnect
[11:11:15] Bot restarts (5s delay)
[11:11:20] Connects successfully
```

All events are recorded and tracked in reliability metrics.

---

## 📊 Commands Reference

### Start/Stop

| Command | Description |
|---------|-------------|
| `./scripts/start_staged_test.sh` | Start staged test (current stage) |
| `./scripts/stop_2week_test.sh` | Stop bot (preserves all data) |
| `./scripts/check_status.sh` | Quick status check |

### Monitoring

| Command | Description |
|---------|-------------|
| `python monitoring/live_dashboard.py` | Real-time dashboard with stage info |
| `python monitoring/evaluate_stage.py` | Check criteria for current stage |
| `python monitoring/stage_manager.py` | View stage system details |
| `tail -f user_data/logs/freqtrade.log` | View live logs |

### Stage Management

| Command | Description |
|---------|-------------|
| `python monitoring/advance_stage.py` | Advance to next stage (when ready) |
| `python monitoring/live_tracker.py` | Generate daily report |

### After Completion

| Command | Description |
|---------|-------------|
| `python monitoring/generate_final_report.py` | Generate final 3-stage report |

---

## 📁 File Structure

```
user_data/
├── live_test_results/
│   ├── current_session.json       # Session data
│   ├── stage_data.json             # Stage information
│   ├── daily_reports/              # Daily reports
│   └── FINAL_REPORT.txt            # After Stage 3
│
├── logs/
│   ├── freqtrade.log               # Bot activity
│   └── wrapper.log                 # Auto-restart log
│
├── trades.json                     # All trades
└── bot.pid                         # Bot process ID
```

---

## 🎯 Detailed Stage Criteria

### Understanding Each Criterion

**1. Minimum Days Running**
- Ensures sufficient time has passed
- Can't rush through stages
- Real-world market exposure

**2. Minimum Trades**
- Ensures enough sample size
- Statistical significance
- Pattern validation

**3. Win Rate**
- Percentage of profitable trades
- Stage 1: >30% (lenient)
- Stages 2-3: >40% (standard)

**4. Return Percentage**
- Total profit/loss as %
- Stage 2: Any profit (>0%)
- Stage 3: >2% (meaningful profit)

**5. Max Drawdown**
- Largest peak-to-trough decline
- Stage 1: <30% (very lenient)
- Stages 2-3: <20% (good risk management)

**6. Profit Factor**
- Gross profit / Gross loss
- Stage 2: >1.2 (basic profitability)
- Stage 3: >1.5 (solid profitability)

**7. Sharpe Ratio**
- Risk-adjusted return
- Stage 3: >1.0 (good risk-adjusted performance)

**8. Uptime**
- % of time bot was running
- Stage 1: >80%
- Stage 2: >85%
- Stage 3: >90%

---

## 💡 Tips for Success

### Stage 1 Tips

**Goal**: Just get through it without major issues

1. **Monitor closely** - Check dashboard 2-3 times per day
2. **Watch for crashes** - If >3 crashes in first day, investigate
3. **Check logs** - Look for error patterns
4. **Network stability** - Ensure internet is stable

**Common Issues**:
- Network disconnects → Check internet connection
- Crashes on startup → Check configuration
- No trades → Normal, wait for conditions

### Stage 2 Tips

**Goal**: Prove the strategy works

1. **Daily evaluation** - Run `evaluate_stage.py` daily
2. **Track win rate** - Should stay above 40%
3. **Monitor drawdown** - Should stay under 20%
4. **Check profit factor** - Needs to be >1.2

**Common Issues**:
- Win rate below 40% → May need more time or better conditions
- High drawdown → Check stop losses are working
- Too few trades → Normal in low volatility

### Stage 3 Tips

**Goal**: Prove long-term consistency

1. **Weekly reviews** - Comprehensive check every week
2. **Watch Sharpe ratio** - Needs to reach >1.0
3. **Track total return** - Needs to be >2%
4. **Monitor all metrics** - Everything must pass

**Common Issues**:
- Sharpe ratio too low → Need more consistent returns
- Total return < 2% → May need more time
- Uptime < 90% → Too many crashes/disconnects

---

## 🔧 Troubleshooting

### Bot Won't Start

```bash
# Check if Freqtrade is installed
freqtrade --version

# If not installed
source venv/bin/activate
pip install freqtrade

# Try starting again
./scripts/start_staged_test.sh
```

### Too Many Crashes

```bash
# Check logs for error pattern
tail -100 user_data/logs/freqtrade.log

# Common fixes:
# 1. Network issues - Check internet
# 2. API rate limits - Wait 5 minutes
# 3. Config errors - Verify config/config.json
```

### Criteria Not Met After Long Time

```bash
# Evaluate what's failing
python monitoring/evaluate_stage.py

# If win rate too low:
# - May be bad market conditions
# - Consider running hyperopt for better parameters
# - Wait for better conditions

# If too few trades:
# - Normal in low volatility
# - Add more pairs to config
# - Be patient

# If drawdown too high:
# - Check if stop losses are working
# - May need tighter risk management
```

### Can't Advance Stage

```bash
# Check exact criteria
python monitoring/evaluate_stage.py

# See what's missing and wait for it
# OR
# If stuck for too long, consider:
# - Running hyperopt to optimize
# - Adjusting parameters
# - Changing market conditions
```

---

## 📈 Stage Advancement Examples

### Example 1: Fast Progression

```
Day 1-3: Stage 1
- 12 trades, 58% win rate, 1.5% return
- ✅ All criteria met on day 3
- Advance to Stage 2

Day 4-10: Stage 2
- 28 trades, 54% win rate, 3.2% return, PF 1.8
- ✅ All criteria met on day 10
- Advance to Stage 3

Day 11-24: Stage 3
- 45 trades, 51% win rate, 4.5% return, Sharpe 1.4
- ✅ All criteria met on day 14
- Complete all stages!

Total time: 14 days
```

### Example 2: Slower Progression

```
Day 1-5: Stage 1
- 8 trades on day 3 (need 10)
- Wait 2 more days
- 13 trades on day 5, 45% win rate
- ✅ Advance to Stage 2

Day 6-12: Stage 2
- Low volatility, only 18 trades by day 12
- Win rate 42%, but need 25 trades
- Wait for more trades

Day 13-15: Stage 2 continued
- 27 trades on day 15, 41% win rate, +1.2% return
- ✅ Advance to Stage 3

Day 16-30: Stage 3
- Need to reach 40 trades and 2% return
- 42 trades on day 29, 43% win rate, 2.3% return
- ✅ Complete on day 29!

Total time: 29 days
```

### Example 3: Failed Attempt

```
Day 1-4: Stage 1
- 15 trades, but only 25% win rate
- Max drawdown 35% (too high)
- ❌ Cannot advance

Action taken:
- Ran hyperopt to optimize parameters
- Restarted from Stage 1
- New parameters: 48% win rate, 8% drawdown
- ✅ Successfully advanced after restart
```

---

## 🎊 After Stage 3 Completion

Congratulations! You've completed all 3 stages. Your bot has demonstrated:

✅ **Stability** - Consistent uptime, minimal crashes
✅ **Profitability** - Positive returns with good win rate
✅ **Risk Management** - Controlled drawdowns
✅ **Consistency** - Performance over 14+ days
✅ **Reliability** - Handles network issues gracefully

### Next Steps

**1. Generate Final Report**
```bash
python monitoring/generate_final_report.py
```

Review:
- Complete trading history
- All 3 stages summarized
- Performance metrics
- Recommendations

**2. Deploy to Bybit Testnet**

Test with virtual funds on a real exchange:

```bash
# Get API keys from https://testnet.bybit.com
# Add to .env file:
BYBIT_TESTNET_API_KEY=your_key_here
BYBIT_TESTNET_API_SECRET=your_secret_here

# Start on testnet
./scripts/start_testnet.sh
```

Run for 4-8 weeks on testnet before live trading.

**3. Consider Live Trading (After Testnet Success)**

Start small:
- Use 1-5% of total capital
- Monitor closely for 2 weeks
- Scale up gradually if successful

**4. Continue Optimization**

```bash
# Run hyperopt for better parameters
freqtrade hyperopt \
  --config config/config.json \
  --strategy MomentumMeanReversion \
  --hyperopt-loss SharpeHyperOptLoss \
  --epochs 100
```

---

## ❓ FAQ

### Q: Can I skip stages?
**A**: No. Each stage must be completed with all criteria met. This ensures proper validation.

### Q: Can I go back to a previous stage?
**A**: No, but you can restart from Stage 1 if needed. This resets all data.

### Q: What if I fail Stage 1 multiple times?
**A**: Consider:
- Running hyperopt to optimize parameters
- Testing in different market conditions
- Reviewing strategy logic
- Checking for configuration issues

### Q: How long does it typically take?
**A**:
- Fast: 14-21 days (ideal conditions)
- Average: 21-30 days (normal conditions)
- Slow: 30-45 days (low volatility or issues)

### Q: Can stages overlap?
**A**: No. You must complete Stage 1 before Stage 2 starts. Stage timer resets when you advance.

### Q: What if criteria are met but I don't advance?
**A**: The stage progress is saved. You can advance anytime, even days later. But the clock keeps running.

### Q: Can I pause between stages?
**A**: Yes. Stop the bot, and when you restart, it will resume the current stage.

### Q: What if I have network issues?
**A**: The bot auto-restarts and tracks downtime. As long as uptime criteria are met, you're fine.

### Q: Can I modify configs between stages?
**A**: Not recommended. Changing strategy mid-test invalidates results. Finish all stages, then modify.

### Q: What if I don't meet Stage 3 criteria after 30 days?
**A**: Either:
- Continue waiting (if close)
- Restart from Stage 1 with optimized parameters
- Consider if strategy needs fundamental changes

---

## 🌙 Sharia Compliance

All stages maintain full Sharia compliance:

✅ **Spot Trading Only** - No margin/futures at any stage
✅ **1x Leverage** - No borrowing ever
✅ **Long Positions Only** - No short selling
✅ **No Interest** - No Riba throughout all stages
✅ **Real Assets** - Buys actual cryptocurrency

The staged system doesn't change the Halal nature of the bot - it just validates it more thoroughly.

---

## 📞 Support

### Resources

- **Stage Manager Details**: `python monitoring/stage_manager.py`
- **Daily Reports**: `user_data/live_test_results/daily_reports/`
- **Bot Logs**: `user_data/logs/freqtrade.log`
- **Trade History**: `user_data/trades.json`

### Common Commands

```bash
# Check where you are
python monitoring/evaluate_stage.py

# View dashboard
python monitoring/live_dashboard.py

# Check bot status
./scripts/check_status.sh

# View logs
tail -f user_data/logs/freqtrade.log

# Stop bot
./scripts/stop_2week_test.sh
```

---

## 🎉 Summary

The Staged Testing System ensures your bot is truly ready for live trading through:

1. **Stage 1** (3-5 days): Prove it works
2. **Stage 2** (7-10 days): Prove it's profitable
3. **Stage 3** (14 days): Prove it's consistent

With:
- **Auto-restart** on crashes
- **Network reconnection** on disconnects
- **Progressive criteria** for advancement
- **Comprehensive tracking** of all metrics

**Start your staged test now:**
```bash
./scripts/start_staged_test.sh
```

**May Allah (SWT) bless your trading!** 🌙

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-06
**Strategy**: MomentumMeanReversion v1.0.1 (Sharia-Compliant)
