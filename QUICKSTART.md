# Quick Start Guide - Crypto Trading Bot

Get up and running with the crypto trading bot in minutes.

## Current Status: Ready for Setup

✅ **Phases 1 & 2 Complete** (Research & Strategy Selection)
🔄 **Phase 3 Starting** (Implementation)

## Prerequisites

Before you begin, ensure you have:
- Linux or macOS (Windows users: use WSL)
- Python 3.11 or higher
- 4GB+ RAM
- Stable internet connection
- 30 minutes for initial setup

## Step-by-Step Setup (5 Steps)

### Step 1: Install Freqtrade (10 minutes)

```bash
# Navigate to project directory
cd ~/claude-quant-repo

# Run automated installation
./scripts/install_freqtrade.sh

# Activate virtual environment
source venv/bin/activate
```

**What this does**: Installs Freqtrade trading bot framework, TA-Lib, and all Python dependencies.

**Troubleshooting**: If installation fails, see `docs/FREQTRADE_SETUP.md` for manual installation.

---

### Step 2: Download Historical Data (5 minutes)

```bash
# Download 1 year of data for backtesting
freqtrade download-data \
  --exchange binance \
  --pairs BTC/USDT ETH/USDT SOL/USDT ADA/USDT AVAX/USDT \
  --timeframes 5m 15m 1h 4h 1d \
  --days 365 \
  --datadir user_data/data
```

**What this does**: Downloads historical price data from Binance for backtesting strategies.

**Note**: This may take 5-10 minutes depending on your internet speed.

---

### Step 3: Set Up Bybit Testnet Account (10 minutes)

Follow the detailed guide: `docs/BYBIT_TESTNET_SETUP.md`

**Quick Steps**:
1. Go to https://testnet.bybit.com
2. Sign up with email
3. Create API keys (Read + Trade permissions, NO Withdraw)
4. Copy API key and secret

**Create `.env` file**:
```bash
nano .env
```

Add:
```bash
BYBIT_TESTNET_API_KEY=your_api_key_here
BYBIT_TESTNET_API_SECRET=your_api_secret_here
```

Save (Ctrl+O, Enter, Ctrl+X)

**Secure it**:
```bash
chmod 600 .env
```

**Result**: You now have $50,000 in virtual funds for demo trading!

---

### Step 4: Test Installation (2 minutes)

```bash
# Test Freqtrade installation
freqtrade --version

# Test data download
ls user_data/data/binance/

# Test Bybit connection (create this script first)
python3 << 'EOF'
import ccxt
import os
from dotenv import load_dotenv
load_dotenv()

bybit = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
    'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
    'enableRateLimit': True,
    'urls': {
        'api': {
            'public': 'https://api-testnet.bybit.com',
            'private': 'https://api-testnet.bybit.com',
        }
    }
})

balance = bybit.fetch_balance()
print("✅ Bybit Testnet Connected!")
print(f"Balance: {balance['USDT']['total']} USDT")
EOF
```

**Expected Output**:
```
Freqtrade 2024.x
✅ Bybit Testnet Connected!
Balance: 10000.0 USDT
```

---

### Step 5: Run Your First Backtest (3 minutes)

```bash
# Test with a simple strategy (we'll implement our custom strategies next)
freqtrade backtesting \
  --config config/config.json \
  --strategy SampleStrategy \
  --timeframe 1h \
  --timerange 20240101-20241101 \
  --datadir user_data/data
```

**What this does**: Tests a sample strategy on historical data to verify everything works.

**Expected Output**: You'll see performance metrics (profit/loss, win rate, drawdown).

---

## ✅ Setup Complete!

You're now ready to implement custom trading strategies.

## What's Next?

### Immediate Next Steps (This Week):

1. **Implement Strategy 1**: Momentum + Mean Reversion Hybrid
   - See `docs/PHASE2_STRATEGY_SELECTION.md` for detailed strategy specs
   - Create `user_data/strategies/MomentumMeanReversion.py`

2. **Run Backtests**: Test strategy on historical data
3. **Optimize Parameters**: Use Hyperopt to find best settings
4. **Deploy to Dry-Run**: Test with real-time data (no money)

### Next Month:

5. **Build Monitoring Dashboard**: Real-time performance tracking
6. **Deploy to Bybit Testnet**: Start demo trading with $50K virtual funds
7. **Monitor for 8-12 Weeks**: Daily reviews and weekly reports

### Long-Term (3-6 Months):

8. **Evaluate Performance**: Compare to success metrics
9. **Iterate and Improve**: Refine strategies based on data
10. **Go/No-Go Decision**: Only proceed to real money if consistently profitable

---

## Key Files to Know

### Documentation
- `README.md` - Project overview
- `docs/RESEARCH_PHASE1.md` - Complete research findings
- `docs/PHASE2_STRATEGY_SELECTION.md` - Strategy details and architecture
- `docs/FREQTRADE_SETUP.md` - Detailed Freqtrade installation
- `docs/BYBIT_TESTNET_SETUP.md` - Bybit demo account setup

### Configuration
- `config/config.json` - Main Freqtrade config (to be created)
- `config/config_bybit_testnet.json` - Bybit Testnet config (to be created)
- `.env` - API keys and secrets (create this, never commit)

### Strategy Development
- `user_data/strategies/` - Your trading strategies go here
- `user_data/notebooks/` - Jupyter notebooks for analysis

### Scripts
- `scripts/install_freqtrade.sh` - Installation script
- `scripts/download_data.sh` - Data download (to be created)
- `scripts/run_backtest.sh` - Backtesting helper (to be created)

---

## Common Commands

### Activate Environment
```bash
source venv/bin/activate
```

### Backtesting
```bash
freqtrade backtesting --strategy YourStrategy --timeframe 15m
```

### Hyperopt (Optimization)
```bash
freqtrade hyperopt --strategy YourStrategy --hyperopt-loss SharpeHyperOptLoss --epochs 500
```

### Dry-Run (Paper Trading)
```bash
freqtrade trade --config config/config.json --strategy YourStrategy --dry-run
```

### Demo Trading (Bybit Testnet)
```bash
freqtrade trade --config config/config_bybit_testnet.json --strategy YourStrategy
```

### Plot Results
```bash
freqtrade plot-dataframe --strategy YourStrategy --pairs BTC/USDT
```

---

## Support & Resources

### Internal Documentation
- All docs are in the `docs/` folder
- Start with README.md for overview

### External Resources
- [Freqtrade Docs](https://www.freqtrade.io/en/stable/)
- [Freqtrade Strategies Repo](https://github.com/freqtrade/freqtrade-strategies)
- [Freqtrade Discord](https://discord.gg/p7nuUNVfP7)
- [CCXT Docs](https://docs.ccxt.com/)
- [Bybit API Docs](https://bybit-exchange.github.io/docs/v5/intro)

### Troubleshooting
- Check `.gitignore` to ensure secrets not committed
- Verify virtual environment is activated (`which python` should show `venv/bin/python`)
- Check Bybit Testnet balance: https://testnet.bybit.com/user/assets
- View Freqtrade logs: `tail -f user_data/logs/freqtrade.log`

---

## Important Reminders

⚠️ **DEMO TRADING ONLY** for first 3-6 months
⚠️ **NO REAL MONEY** until consistently profitable on demo
⚠️ **Risk Management** is 90% of success
⚠️ **Most bots lose money** - realistic expectations
⚠️ **Market conditions change** - adapt strategies

✅ **You're ready!** Proceed with confidence, test thoroughly, and iterate based on data.

---

**Next Action**: Implement your first strategy (Momentum + Mean Reversion Hybrid).
See `docs/PHASE2_STRATEGY_SELECTION.md` for detailed specifications.
