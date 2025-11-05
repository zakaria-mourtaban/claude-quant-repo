# Freqtrade Installation & Setup Guide

This guide walks through setting up Freqtrade for crypto trading bot development.

## Prerequisites

- Python 3.11 or higher
- Git
- 4GB+ RAM
- Linux/macOS (recommended) or Windows with WSL

## Installation Methods

### Method 1: Using Docker (Recommended for Beginners)

Docker provides an isolated environment with all dependencies pre-installed.

#### 1. Install Docker
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# macOS (install Docker Desktop from docker.com)

# Verify installation
docker --version
docker-compose --version
```

#### 2. Clone Freqtrade
```bash
cd ~/claude-quant-repo
git clone https://github.com/freqtrade/freqtrade.git freqtrade_source
cd freqtrade_source
```

#### 3. Create Docker Compose Configuration
```bash
# Create docker-compose.yml
curl https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docker-compose.yml -o docker-compose.yml
```

#### 4. Build and Start
```bash
docker-compose build
docker-compose up -d
```

#### 5. Access Freqtrade
```bash
# Run commands via docker-compose
docker-compose run --rm freqtrade --help
```

---

### Method 2: Native Installation (Recommended for Development)

Native installation gives you more control and better performance.

#### 1. Install System Dependencies

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y build-essential git libssl-dev libffi-dev python3-dev python3-pip python3-venv
```

**macOS**:
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install python@3.11 ta-lib
```

#### 2. Install TA-Lib (Technical Analysis Library)

**Ubuntu/Debian**:
```bash
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

**macOS**:
```bash
brew install ta-lib
```

#### 3. Create Python Virtual Environment
```bash
cd ~/claude-quant-repo
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 4. Install Freqtrade
```bash
# Upgrade pip
pip install --upgrade pip

# Install Freqtrade
pip install freqtrade

# Verify installation
freqtrade --version
```

#### 5. Install Additional Dependencies
```bash
# Install project dependencies
pip install -r requirements.txt
```

---

## Post-Installation Setup

### 1. Create User Data Directory
```bash
cd ~/claude-quant-repo
freqtrade create-userdir --userdir user_data
```

This creates:
- `user_data/strategies/` - Your trading strategies
- `user_data/data/` - Downloaded market data
- `user_data/notebooks/` - Jupyter notebooks for analysis

### 2. Create Initial Configuration
```bash
freqtrade new-config --config config/config.json
```

**Interactive prompts**:
- Exchange: `binance` (for data download, we'll use Bybit for demo trading)
- Telegram: `No` (we'll set up later)
- Dry-run: `Yes` (start with paper trading)
- Other settings: Use defaults for now

### 3. Edit Configuration for Bybit Testnet

Create `config/config_bybit_testnet.json`:
```json
{
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": "unlimited",
  "tradable_balance_ratio": 0.99,
  "fiat_display_currency": "USD",
  "dry_run": false,
  "dry_run_wallet": 50000,

  "exchange": {
    "name": "bybit",
    "key": "YOUR_API_KEY",
    "secret": "YOUR_API_SECRET",
    "ccxt_config": {
      "enableRateLimit": true,
      "options": {
        "defaultType": "spot"
      }
    },
    "ccxt_async_config": {
      "enableRateLimit": true
    },
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "SOL/USDT",
      "ADA/USDT",
      "AVAX/USDT"
    ],
    "pair_blacklist": []
  },

  "entry_pricing": {
    "price_side": "same",
    "use_order_book": true,
    "order_book_top": 1,
    "price_last_balance": 0.0,
    "check_depth_of_market": {
      "enabled": false,
      "bids_to_ask_delta": 1
    }
  },

  "exit_pricing": {
    "price_side": "same",
    "use_order_book": true,
    "order_book_top": 1
  },

  "order_types": {
    "entry": "limit",
    "exit": "limit",
    "stoploss": "market",
    "stoploss_on_exchange": false
  },

  "pairlists": [
    {
      "method": "StaticPairList"
    }
  ],

  "edge": {
    "enabled": false
  },

  "telegram": {
    "enabled": false
  },

  "api_server": {
    "enabled": true,
    "listen_ip_address": "127.0.0.1",
    "listen_port": 8080,
    "verbosity": "error",
    "jwt_secret_key": "REPLACE_WITH_RANDOM_SECRET",
    "CORS_origins": [],
    "username": "freqtrader",
    "password": "REPLACE_WITH_PASSWORD"
  },

  "bot_name": "crypto-trading-bot",
  "initial_state": "running",
  "force_entry_enable": false,

  "internals": {
    "process_throttle_secs": 5
  }
}
```

**Important**: Replace placeholders:
- `YOUR_API_KEY` - From Bybit Testnet account
- `YOUR_API_SECRET` - From Bybit Testnet account
- `REPLACE_WITH_RANDOM_SECRET` - Generate: `python -c "import secrets; print(secrets.token_hex(32))"`
- `REPLACE_WITH_PASSWORD` - Choose a secure password

### 4. Download Historical Data

```bash
# Download 1 year of data for backtesting
freqtrade download-data \
  --exchange binance \
  --pairs BTC/USDT ETH/USDT SOL/USDT ADA/USDT AVAX/USDT \
  --timeframes 5m 15m 1h 4h 1d \
  --days 365 \
  --datadir user_data/data
```

**Note**: We use Binance for historical data (free and high-quality), but will trade on Bybit Testnet.

### 5. Create Sample Strategy

Freqtrade includes a sample strategy:
```bash
freqtrade new-strategy --strategy SampleStrategy --userdir user_data
```

This creates `user_data/strategies/SampleStrategy.py`.

### 6. Test Installation with Backtest

```bash
freqtrade backtesting \
  --config config/config.json \
  --strategy SampleStrategy \
  --timeframe 1h \
  --timerange 20240101-20241101 \
  --datadir user_data/data
```

If this runs without errors, installation is successful!

---

## Freqtrade Basics

### Key Commands

**Backtesting**:
```bash
freqtrade backtesting --config config/config.json --strategy YourStrategy
```

**Hyperopt (Parameter Optimization)**:
```bash
freqtrade hyperopt --config config/config.json --strategy YourStrategy --hyperopt-loss SharpeHyperOptLoss --epochs 500
```

**Dry-Run (Paper Trading)**:
```bash
freqtrade trade --config config/config.json --strategy YourStrategy --dry-run
```

**Live Trading (Demo)**:
```bash
freqtrade trade --config config/config_bybit_testnet.json --strategy YourStrategy
```

**Plot Results**:
```bash
freqtrade plot-dataframe --config config/config.json --strategy YourStrategy --pairs BTC/USDT
```

**Show Trades**:
```bash
freqtrade show-trades --config config/config.json
```

---

## Directory Structure After Setup

```
claude-quant-repo/
├── config/
│   ├── config.json                      # Main config (dry-run)
│   └── config_bybit_testnet.json        # Bybit Testnet config
├── user_data/
│   ├── strategies/
│   │   └── SampleStrategy.py            # Example strategy
│   ├── data/
│   │   └── binance/                     # Downloaded data
│   │       ├── BTC_USDT-5m.json
│   │       ├── BTC_USDT-1h.json
│   │       └── ...
│   ├── backtest_results/                # Backtest outputs (auto-created)
│   ├── hyperopt_results/                # Hyperopt outputs (auto-created)
│   ├── notebooks/                       # Jupyter notebooks
│   └── logs/                            # Bot logs (auto-created)
├── venv/                                # Python virtual environment
├── requirements.txt
└── README.md
```

---

## Troubleshooting

### Issue: "TA-Lib not found"

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install -y libta-lib0-dev
pip install TA-Lib

# macOS
brew install ta-lib
pip install TA-Lib
```

### Issue: "Exchange binance not found"

**Solution**:
```bash
pip install ccxt --upgrade
```

### Issue: "No module named freqtrade"

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall freqtrade
pip install freqtrade
```

### Issue: Docker permission denied

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

---

## Next Steps

1. ✅ Freqtrade installed and tested
2. [ ] Set up Bybit Testnet account (see `BYBIT_TESTNET_SETUP.md`)
3. [ ] Implement first strategy (Momentum + Mean Reversion)
4. [ ] Run backtests and optimize parameters
5. [ ] Deploy to Bybit Testnet for demo trading

---

## Resources

- [Freqtrade Documentation](https://www.freqtrade.io/en/stable/)
- [Freqtrade Strategies Repository](https://github.com/freqtrade/freqtrade-strategies)
- [Freqtrade Discord Community](https://discord.gg/p7nuUNVfP7)
- [CCXT Documentation](https://docs.ccxt.com/)

---

**Status**: Setup guide complete. Follow this guide to install Freqtrade before proceeding to strategy implementation.
