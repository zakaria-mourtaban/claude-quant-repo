# Crypto Trading Bot - Research & Implementation

A systematic approach to building a profitable cryptocurrency trading bot with demo account testing before real money deployment.

## Project Status: Phase 3 - Implementation

- ✅ Phase 1: Research & Analysis (Complete)
- ✅ Phase 2: Strategy Selection & Design (Complete)
- 🔄 Phase 3: Implementation (In Progress)
- ⏳ Phase 4: Demo Account Live Testing (Planned: 8-12 weeks)
- ⏳ Phase 5: Iteration & Optimization (Ongoing)

## Overview

This project follows a disciplined, research-driven approach to algorithmic cryptocurrency trading:

1. **Extensive Research**: Analyzed academic papers, successful open-source bots, and quantitative trading methodologies
2. **Strategy Selection**: Identified top-performing strategies backed by research
3. **Demo Testing First**: NO REAL MONEY until 3-6 months of profitable demo trading
4. **Risk Management**: Conservative position sizing, kill switches, and strict limits
5. **Systematic Iteration**: Continuous improvement based on data

## Key Findings (Phase 1 Research)

### Best Strategy: Momentum + Mean Reversion Hybrid
- **Annualized Return**: 56%
- **Sharpe Ratio**: 1.71
- **Key Advantage**: Adapts to different market regimes (trending vs. ranging)

### Technology Stack
- **Framework**: Freqtrade (44.3k ⭐ on GitHub)
- **Exchange**: Bybit Testnet ($50K virtual funds), future production on OKX
- **Backtesting**: Freqtrade built-in + VectorBT for optimization
- **Language**: Python 3.11+

### Demo Trading Platforms
1. **Bybit Testnet** (Primary): $50K balance, 355 assets, spot + derivatives
2. **Binance Futures Testnet** (Secondary): 3K USDT, futures only

## Project Structure

```
crypto-trading-bot/
├── config/                      # Configuration files
├── user_data/
│   ├── strategies/              # Trading strategies
│   ├── data/                    # Historical data
│   ├── backtest_results/        # Backtest outputs
│   └── notebooks/               # Analysis notebooks
├── scripts/                     # Utility scripts
├── monitoring/                  # Dashboard and alerts
├── risk_management/             # Position sizing, stop losses
├── tests/                       # Unit tests
├── docs/                        # Documentation
│   ├── RESEARCH_PHASE1.md       # Comprehensive research
│   └── PHASE2_STRATEGY_SELECTION.md  # Strategy details
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Top 5 Strategies (Priority Order)

1. **Momentum + Mean Reversion Hybrid** (🔴 Highest Priority)
   - Combines trend-following and range-trading
   - 56% annual return, Sharpe 1.71
   - Adapts to market conditions

2. **BTC-Neutral Mean Reversion** (🟡 High Priority)
   - Statistical arbitrage approach
   - Market-neutral (profits in up/down markets)
   - Excelled in post-2021 conditions

3. **Grid Trading with Volatility Filter** (🟢 Medium Priority)
   - Range-bound automated trading
   - Profits from sideways markets
   - Simple and consistent

4. **Breakout with Volume Confirmation** (🟢 Medium Priority)
   - Momentum/breakout strategy
   - Captures explosive crypto moves
   - High win rate with confirmation

5. **DCA with Trend Filter** (🟢 Low-Medium Priority)
   - Conservative accumulation strategy
   - Long-term approach
   - Lower stress, proven method

## Risk Management (Non-Negotiables)

- **Position Size**: 1-2% risk per trade maximum
- **Kelly Criterion**: Use 1/10th Kelly, never > 20% position
- **Max Drawdown**: 10-20% portfolio stop (kill switch)
- **Stop Losses**: Always enabled (2-5% per trade or 2x ATR)
- **Portfolio Heat**: Maximum 6-10% total risk
- **Daily Loss Limit**: Stop trading after threshold
- **Kill Switch**: Auto-stop on connection loss or extreme drawdown

## Success Metrics (Demo Trading)

**Minimum Demo Period**: 8-12 weeks (ideally 3-6 months)

**Target Metrics** (before considering real money):
- ✅ Sharpe Ratio > 1.5
- ✅ Maximum Drawdown < 20%
- ✅ Win Rate > 40% (with R:R > 2:1)
- ✅ Profit Factor > 1.5
- ✅ Consistent weekly profitability (60%+ positive weeks)

**Warning Signs** (do NOT proceed):
- ❌ Sharpe Ratio < 0.5
- ❌ Maximum Drawdown > 30%
- ❌ Irregular performance (huge swings)
- ❌ Strategy works only in specific conditions
- ❌ Large gap between backtest and demo results

## Installation & Setup

### Prerequisites
- Python 3.11+
- Git
- 4GB+ RAM recommended
- Stable internet connection

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd claude-quant-repo
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Freqtrade**:
   ```bash
   # See docs/FREQTRADE_SETUP.md for detailed instructions
   ./scripts/install_freqtrade.sh
   ```

4. **Set up Bybit Testnet**:
   ```bash
   # See docs/BYBIT_TESTNET_SETUP.md for account creation
   # Add API keys to .env file
   ```

5. **Download historical data**:
   ```bash
   ./scripts/download_data.sh
   ```

6. **Run your first backtest**:
   ```bash
   ./scripts/run_backtest.sh MomentumMeanReversion
   ```

## Usage

### Backtesting
```bash
freqtrade backtesting --strategy MomentumMeanReversion --timeframe 15m --timerange 20240101-20251101
```

### Hyperopt (Parameter Optimization)
```bash
freqtrade hyperopt --strategy MomentumMeanReversion --hyperopt-loss SharpeHyperOptLoss --epochs 500
```

### Dry-Run (Paper Trading)
```bash
freqtrade trade --config config/config.json --strategy MomentumMeanReversion --dry-run
```

### Demo Trading (Bybit Testnet)
```bash
freqtrade trade --config config/config_bybit_testnet.json --strategy MomentumMeanReversion
```

### Performance Dashboard
```bash
streamlit run monitoring/dashboard.py
```

## Implementation Roadmap (24 Weeks)

### Week 1-2: Setup & Infrastructure ✅
- [x] Research and documentation
- [ ] Install Freqtrade
- [ ] Configure Bybit Testnet
- [ ] Download historical data

### Week 3-4: Strategy 1 Implementation
- [ ] Implement Momentum + Mean Reversion Hybrid
- [ ] Add indicators (ADX, RSI, EMA, BB, ATR)
- [ ] Code entry/exit logic
- [ ] Implement risk management

### Week 5-6: Backtesting & Optimization
- [ ] Run backtests (train/test split)
- [ ] Hyperopt optimization
- [ ] Walk-forward analysis
- [ ] Document results

### Week 7-8: Dry-Run Testing
- [ ] 2-week dry-run with real-time data
- [ ] Bug fixes and validation
- [ ] Build monitoring dashboard

### Week 9-10: Monitoring & Dashboard
- [ ] Streamlit dashboard
- [ ] Telegram alerts
- [ ] Performance metrics
- [ ] Kill switches

### Week 11-12: Bybit Testnet Deployment
- [ ] Deploy with virtual funds
- [ ] Start 8-12 week demo trading period
- [ ] Daily monitoring and weekly reviews

### Week 13-24: Demo Trading & Iteration
- [ ] Continuous performance monitoring
- [ ] Weekly performance reports
- [ ] Strategy refinements
- [ ] Go/No-Go decision at week 24

## Key Learnings from Research

### Critical Success Factors
1. **Risk Management > Strategy**: 90% of success is managing risk
2. **Realistic Expectations**: Most bots lose money; takes months/years to profit
3. **Avoid Overfitting**: Perfect backtests often fail in live trading
4. **Transaction Costs Matter**: Fees and slippage destroy profits
5. **Market Regimes Change**: Adapt strategies to current conditions

### Common Pitfalls to Avoid
- ❌ Using future data in backtests (shift(-1))
- ❌ Over-optimizing parameters
- ❌ Ignoring transaction costs and slippage
- ❌ Testing only in bull markets
- ❌ Skipping dry-run/demo testing
- ❌ Risking too much per trade (>2%)
- ❌ No kill switches or safety limits

## Resources

### Documentation
- [Phase 1: Research & Analysis](docs/RESEARCH_PHASE1.md)
- [Phase 2: Strategy Selection & Design](docs/PHASE2_STRATEGY_SELECTION.md)
- [Freqtrade Official Docs](https://www.freqtrade.io/en/stable/)
- [CCXT Documentation](https://docs.ccxt.com/)

### Academic Papers
- "Quantitative Alpha in Crypto Markets" (Mann, 2025) - SSRN Abstract ID 5225612
- "Neural Network-Based Algorithmic Trading" (ArXiv, August 2025)
- "Comprehensive ML Analysis for Bitcoin Trading" (ArXiv, July 2025)

### Open-Source Bots Analyzed
- [Freqtrade](https://github.com/freqtrade/freqtrade) - 44.3k ⭐
- [Hummingbot](https://github.com/hummingbot/hummingbot) - Market making
- [OctoBot](https://github.com/Drakkar-Software/OctoBot) - User-friendly

## Warnings & Disclaimers

⚠️ **CRITICAL REMINDERS**:
- This is an **EXPERIMENTAL** project for learning
- **NO GUARANTEE OF PROFIT** - Most trading bots lose money
- Crypto markets are **EXTREMELY VOLATILE**
- Start with **DEMO TRADING ONLY** (no real money for 3-6 months)
- Risk only what you can **AFFORD TO LOSE**
- Past performance ≠ future results

⚠️ **Key Risks**:
- Market Risk (volatility, flash crashes)
- Technical Risk (bugs, API failures, exchange issues)
- Regulatory Risk (evolving crypto regulations)
- Time Investment (months of testing and iteration)

**Mitigation**:
- Demo trading first (minimum 8-12 weeks)
- Strict position sizing and stop losses
- Kill switches and safety limits
- Daily performance monitoring
- Be prepared to abandon strategies that don't work

## Contributing

This is a personal research project. If you're interested in algorithmic trading:
1. Review the research documents in `docs/`
2. Study the strategy implementations in `user_data/strategies/`
3. Run backtests on your own data
4. Test on demo accounts before real money
5. Share learnings and improvements

## License

This project is for educational and research purposes. Use at your own risk.

## Contact

For questions or discussions about the research and methodologies used in this project, please open an issue.

---

**Remember**: Algorithmic trading is difficult. Most bots are not profitable. Success requires months of testing, iteration, and disciplined risk management. Start with demo trading and never risk money you can't afford to lose.

**Current Status**: Phase 3 Implementation - Building first strategy and backtesting framework.
