# Phase 2: Strategy Selection & Design
## Date: 2025-11-05

Based on Phase 1 research, this document outlines recommended strategies, architecture design, and implementation roadmap.

---

## 1. RECOMMENDED STRATEGIES (Top 5)

### Strategy 1: Momentum + Mean Reversion Hybrid (⭐ HIGHEST PRIORITY)
**Type**: Combined trend-following and range-trading
**Complexity**: Medium
**Capital Required**: Moderate ($1,000+ for meaningful testing)
**Timeframe**: 15m - 4h

**Research Backing**:
- Academic research shows 56% annualized return with Sharpe Ratio of 1.71
- Performs well across different market regimes
- Momentum excels in trending markets, mean reversion in choppy conditions

**How it Works**:
1. **Momentum Component**:
   - Identify trending markets using ADX (Average Directional Index) > 25
   - Enter long when price > EMA(50) and RSI crosses above 50
   - Enter short when price < EMA(50) and RSI crosses below 50
   - Use ATR-based trailing stops to capture trends

2. **Mean Reversion Component**:
   - Identify ranging markets using ADX < 20
   - Enter long when RSI < 30 (oversold) and Bollinger Band touch
   - Enter short when RSI > 70 (overbought) and Bollinger Band touch
   - Fixed profit targets at mean (middle Bollinger Band)

3. **Regime Detection**:
   - Calculate ADX to determine market state
   - Use momentum strategy when ADX > 25 (trending)
   - Use mean reversion when ADX < 20 (ranging)
   - Stay flat when 20 < ADX < 25 (transitional/unclear)

**Indicators Needed**:
- ADX (14) - Regime detection
- EMA (50, 200) - Trend direction
- RSI (14) - Momentum and overbought/oversold
- Bollinger Bands (20, 2) - Mean reversion levels
- ATR (14) - Stop loss and position sizing

**Risk Management**:
- Stop loss: 2x ATR from entry
- Position size: 2% risk per trade (Kelly 1/10th)
- Maximum 3 concurrent positions
- Daily loss limit: 6% of portfolio

**Pros**:
✅ Proven performance (56% annual return in research)
✅ Adapts to market conditions automatically
✅ Reduces drawdowns by switching strategies
✅ Well-documented approach with academic backing
✅ Easy to backtest and optimize

**Cons**:
❌ Requires accurate regime detection (ADX may lag)
❌ Transition periods can generate false signals
❌ More complex than single-strategy approach
❌ Needs optimization for specific markets

**Implementation Priority**: 🔴 **HIGHEST** - Start here

---

### Strategy 2: BTC-Neutral Mean Reversion (⭐ HIGH PRIORITY)
**Type**: Statistical arbitrage / mean reversion
**Complexity**: Medium-High
**Capital Required**: Moderate-High ($2,000+)
**Timeframe**: 1h - 1d

**Research Backing**:
- Post-2021 research shows this excelled when other strategies failed
- Extracts idiosyncratic signals (coin-specific, not market-wide)
- Market-neutral approach reduces exposure to BTC swings

**How it Works**:
1. **Select Altcoin Universe**:
   - Choose 10-20 liquid altcoins (ETH, SOL, ADA, AVAX, etc.)
   - Focus on established coins with good liquidity

2. **Calculate BTC-Neutral Residuals**:
   - For each altcoin, calculate beta to BTC (regression ALTCOIN ~ BTC)
   - Calculate residual: Residual = ALTCOIN_return - (beta × BTC_return)
   - This isolates the coin-specific movement (removes BTC influence)

3. **Z-Score Mean Reversion**:
   - Calculate rolling Z-score of residual (mean/std over 30 periods)
   - Enter long when Z-score < -2 (extremely underperforming vs BTC)
   - Enter short when Z-score > +2 (extremely overperforming vs BTC)
   - Exit when Z-score returns to 0 (mean)

4. **Market-Neutral Portfolio**:
   - Hedge BTC exposure: If long ALT, short equivalent BTC exposure
   - This isolates profit to the idiosyncratic mean reversion, not market moves

**Indicators Needed**:
- BTC price (correlation calculation)
- Rolling regression (beta calculation)
- Z-score (standardized residual)
- Volume filter (ensure liquidity)

**Risk Management**:
- Stop loss: 3 standard deviations (rare but protects against regime change)
- Position size: 1.5% risk per pair
- Maximum 4 pairs simultaneously
- Correlation check: Avoid highly correlated pairs

**Pros**:
✅ Market-neutral (profits in up/down markets)
✅ Excelled in post-2021 market conditions
✅ Exploits coin-specific inefficiencies
✅ Lower correlation to overall market
✅ Diversification across multiple pairs

**Cons**:
❌ Complex to implement (requires regression, hedging)
❌ Requires short selling capability (futures/margin)
❌ Can fail if market structure changes (correlations break)
❌ Needs careful pair selection and monitoring
❌ Higher transaction costs (2x trades per signal)

**Implementation Priority**: 🟡 **HIGH** - Implement after Strategy 1

---

### Strategy 3: Grid Trading with Volatility Filter
**Type**: Range-bound automated trading
**Complexity**: Low-Medium
**Capital Required**: Moderate ($1,000+)
**Timeframe**: 1m - 1h (works continuously)

**How it Works**:
1. **Define Grid**:
   - Set price range based on recent volatility (e.g., ±10% from current price)
   - Divide range into 10-20 grid levels
   - Place buy orders at lower levels, sell orders at upper levels

2. **Volatility Filter**:
   - Calculate ATR or Bollinger Band width
   - Only activate grid when volatility is "normal" (not extreme)
   - Pause during high volatility (flash crashes, pumps)

3. **Execution**:
   - When price hits buy level, purchase fixed amount
   - When price hits sell level, sell fixed amount
   - Profit from each grid hop (buy low, sell high repeatedly)

4. **Dynamic Grid Adjustment**:
   - Shift grid up/down if price trends out of range
   - Widen/narrow grid based on changing volatility

**Indicators Needed**:
- ATR (14) - Volatility measurement
- Bollinger Bands (20, 2) - Range definition
- Recent high/low - Grid boundaries

**Risk Management**:
- Grid size: 0.5-1% between levels
- Maximum capital: 50% of portfolio (rest for rebalancing)
- Stop trading if price moves >20% outside grid (manual intervention)

**Pros**:
✅ Simple to understand and implement
✅ Works well in sideways/ranging markets (most common condition)
✅ Automated and hands-off once configured
✅ Profits from volatility, not direction
✅ Can generate consistent small gains

**Cons**:
❌ Suffers badly in strong trends (one-directional moves)
❌ Can get caught holding depreciating assets in downtrends
❌ Requires capital tied up across many price levels
❌ Transaction costs can eat profits if grid too tight
❌ Manual intervention needed if price breaks out of range

**Implementation Priority**: 🟢 **MEDIUM** - Good for diversification

---

### Strategy 4: Breakout with Volume Confirmation
**Type**: Momentum/breakout trading
**Complexity**: Medium
**Capital Required**: Low-Moderate ($500+)
**Timeframe**: 15m - 4h

**How it Works**:
1. **Identify Consolidation**:
   - Find periods where price trades in narrow range (low ATR)
   - Look for "squeeze" patterns (Bollinger Bands contract)

2. **Detect Breakout**:
   - Breakout occurs when price closes outside consolidation range
   - Must be accompanied by volume spike (>2x average volume)
   - Direction: Long if break above, short if break below

3. **Confirmation**:
   - Wait for retest of breakout level (optional, reduces false signals)
   - Enter on first candle close after retest holds

4. **Exit**:
   - Trailing stop: 1.5x ATR
   - Take profit: 2x risk (R:R = 1:2)
   - Time-based exit: Close after 12-24 hours if target not reached

**Indicators Needed**:
- Bollinger Bands (20, 2) - Consolidation and breakout
- Volume (20-period MA) - Confirmation
- ATR (14) - Stop loss placement

**Risk Management**:
- Stop loss: Below breakout level (1.5x ATR)
- Position size: 2% risk
- Maximum 2 breakout trades simultaneously
- Avoid trading breakouts during low-liquidity hours

**Pros**:
✅ High win rate when volume confirmation used
✅ Clear entry and exit rules
✅ Captures explosive moves in crypto
✅ Easy to implement and backtest
✅ Works well with trend-following

**Cons**:
❌ Many false breakouts (especially without volume)
❌ Can be whipsawed in choppy markets
❌ Requires fast execution (breakouts move quickly)
❌ Needs good risk management (stop losses critical)

**Implementation Priority**: 🟢 **MEDIUM** - Good complement to mean reversion

---

### Strategy 5: DCA with Trend Filter (Conservative)
**Type**: Accumulation with trend protection
**Complexity**: Low
**Capital Required**: Low ($300+)
**Timeframe**: 1d - 1w

**How it Works**:
1. **Regular Purchases**:
   - Buy fixed dollar amount of crypto at regular intervals (daily/weekly)
   - Focus on blue-chip crypto (BTC, ETH)

2. **Trend Filter**:
   - Only buy when price is above 200-day EMA (long-term uptrend)
   - Skip purchases when price < 200 EMA (downtrend)
   - This avoids "catching falling knives"

3. **Enhanced with Dips**:
   - Increase purchase size by 2x when RSI < 30 (oversold)
   - Increase by 1.5x when price drops >10% in 7 days

4. **Profit Taking**:
   - Sell 25% when up 50%
   - Sell 25% when up 100%
   - Keep 50% for long-term hold

**Indicators Needed**:
- EMA (200) - Trend filter
- RSI (14) - Dip detection
- 7-day price change - Drawdown measurement

**Risk Management**:
- Fixed allocation: 2-5% of portfolio per period
- Never use more than 50% total capital
- Stop DCA if loss exceeds 30% (re-evaluate)

**Pros**:
✅ Simple and low-maintenance
✅ Reduces impact of market timing
✅ Trend filter prevents buying falling assets
✅ Low stress, long-term approach
✅ Proven strategy for accumulation

**Cons**:
❌ Lower returns than active strategies
❌ Requires patience (months/years for results)
❌ Opportunity cost (capital tied up)
❌ Still vulnerable to long bear markets
❌ Not suitable for short-term profits

**Implementation Priority**: 🟢 **LOW-MEDIUM** - Good for long-term portfolio

---

## 2. STRATEGY COMPARISON MATRIX

| Strategy | Complexity | Win Rate | Risk/Reward | Market Type | Capital | Priority |
|----------|-----------|----------|-------------|-------------|---------|----------|
| Momentum + Mean Reversion | Medium | 50-60% | 1:2 | All | Moderate | 🔴 Highest |
| BTC-Neutral Mean Reversion | High | 55-65% | 1:1.5 | All (neutral) | High | 🟡 High |
| Grid Trading | Low | 60-70% | 1:1 | Ranging | Moderate | 🟢 Medium |
| Breakout + Volume | Medium | 45-55% | 1:2+ | Trending | Low-Mod | 🟢 Medium |
| DCA + Trend Filter | Low | N/A | Long-term | Uptrend | Low | 🟢 Low-Med |

---

## 3. MODULAR ARCHITECTURE DESIGN

### 3.1 Technology Stack (FINAL DECISION)

**Core Framework**: Freqtrade (Python)
- Most mature open-source bot (44.3k ⭐ on GitHub)
- Built-in backtesting, hyperopt, and dry-run
- Active community and extensive documentation
- Supports 100+ exchanges via CCXT

**Backtesting Library**: Freqtrade built-in (primary) + VectorBT (optional)
- Freqtrade: Integrated, event-driven, realistic execution
- VectorBT: For rapid parameter optimization (vectorized, 1000x faster)

**Exchange**: Bybit (demo) + OKX (future production)
- Bybit Testnet: $50K virtual balance, 355 assets, spot + derivatives
- OKX: Best APIs, liquidity, and fees for algo trading (production target)

**Machine Learning** (Phase 3+): FreqAI (Freqtrade's ML module)
- Built-in integration with scikit-learn, TensorFlow
- Supports N-BEATS, LSTM, and other models from research

---

### 3.2 System Architecture

```
crypto-trading-bot/
│
├── config/                          # Configuration files
│   ├── config.json                  # Main Freqtrade config
│   ├── config_bybit_testnet.json    # Bybit demo config
│   ├── config_backtest.json         # Backtesting config
│   └── blacklist.json               # Blacklisted pairs
│
├── user_data/                       # Freqtrade user data
│   ├── strategies/                  # Trading strategies
│   │   ├── MomentumMeanReversion.py     # Strategy 1 (Priority 1)
│   │   ├── BTCNeutralMeanRev.py         # Strategy 2 (Priority 2)
│   │   ├── GridTradingVolFilter.py      # Strategy 3
│   │   ├── VolumeBreakout.py            # Strategy 4
│   │   └── DCA_TrendFilter.py           # Strategy 5
│   │
│   ├── data/                        # Historical data for backtesting
│   │   └── binance/                 # Downloaded OHLCV data
│   │
│   ├── backtest_results/            # Backtest outputs
│   ├── hyperopt_results/            # Hyperopt optimization results
│   └── notebooks/                   # Jupyter notebooks for analysis
│
├── scripts/                         # Utility scripts
│   ├── download_data.sh             # Download historical data
│   ├── run_backtest.sh              # Run backtests
│   ├── run_hyperopt.sh              # Run optimization
│   ├── start_demo_trading.sh        # Start demo trading
│   └── monitor_performance.py       # Performance monitoring
│
├── monitoring/                      # Monitoring and alerting
│   ├── dashboard.py                 # Performance dashboard (Streamlit/Plotly)
│   ├── telegram_bot.py              # Telegram notifications
│   └── metrics.py                   # Calculate performance metrics
│
├── risk_management/                 # Risk management modules
│   ├── position_sizing.py           # Kelly criterion, fixed %
│   ├── stop_loss.py                 # Stop loss logic
│   ├── drawdown_protection.py       # Kill switch, daily limits
│   └── portfolio_heat.py            # Total exposure calculator
│
├── tests/                           # Unit tests
│   ├── test_strategies.py
│   ├── test_risk_management.py
│   └── test_indicators.py
│
├── docs/                            # Documentation
│   ├── RESEARCH_PHASE1.md           # Phase 1 research (DONE)
│   ├── PHASE2_STRATEGY_SELECTION.md # This document
│   ├── STRATEGY_PERFORMANCE.md      # Results tracking
│   └── LESSONS_LEARNED.md           # Observations and improvements
│
├── requirements.txt                 # Python dependencies
├── docker-compose.yml               # Docker setup for deployment
├── README.md                        # Project overview
└── .env                             # Environment variables (API keys)
```

---

### 3.3 Module Design

#### 3.3.1 Strategy Module (Freqtrade Strategy Class)
Each strategy inherits from `IStrategy` and implements:

```python
class MomentumMeanReversion(IStrategy):
    # Hyperparameters (can be optimized)
    adx_threshold_trending = 25
    adx_threshold_ranging = 20
    rsi_oversold = 30
    rsi_overbought = 70

    # Required methods
    def populate_indicators(self, dataframe, metadata):
        """Calculate all indicators"""
        # ADX, RSI, EMA, Bollinger Bands, ATR
        return dataframe

    def populate_entry_trend(self, dataframe, metadata):
        """Define buy conditions"""
        # Momentum entry: ADX > 25, price > EMA50, RSI cross 50
        # Mean reversion entry: ADX < 20, RSI < 30, BB touch
        return dataframe

    def populate_exit_trend(self, dataframe, metadata):
        """Define sell conditions"""
        # Momentum exit: trailing stop, RSI < 50
        # Mean reversion exit: RSI > 50, price at mean
        return dataframe

    def custom_stoploss(self, pair, trade, current_time, current_rate, current_profit):
        """Dynamic stop loss (ATR-based)"""
        return -0.02  # 2% initial stop, then ATR trailing
```

**Key Features**:
- Modular indicator calculation
- Clear entry/exit logic
- Customizable parameters (hyperopt)
- Built-in stop loss and ROI tables

---

#### 3.3.2 Risk Management Module

**Position Sizing** (`position_sizing.py`):
```python
def calculate_position_size(capital, risk_per_trade, stop_loss_pct, kelly_fraction=0.1):
    """
    Calculate position size using Kelly Criterion (fractional)

    Args:
        capital: Total portfolio value
        risk_per_trade: % of capital to risk (e.g., 0.02 for 2%)
        stop_loss_pct: Stop loss % (e.g., 0.05 for 5%)
        kelly_fraction: Fraction of Kelly to use (default 0.1 for 1/10th Kelly)

    Returns:
        Position size in quote currency (USDT)
    """
    risk_amount = capital * risk_per_trade
    position_size = risk_amount / stop_loss_pct
    return position_size
```

**Drawdown Protection** (`drawdown_protection.py`):
```python
def check_kill_switch(current_drawdown, max_drawdown=0.20):
    """
    Kill switch: Stop all trading if drawdown exceeds threshold

    Args:
        current_drawdown: Current portfolio drawdown (0.15 = 15%)
        max_drawdown: Maximum allowed drawdown (0.20 = 20%)

    Returns:
        True if trading should stop, False otherwise
    """
    if current_drawdown >= max_drawdown:
        send_telegram_alert(f"⚠️ KILL SWITCH ACTIVATED! Drawdown {current_drawdown*100:.1f}%")
        return True
    return False
```

**Portfolio Heat** (`portfolio_heat.py`):
```python
def calculate_portfolio_heat(open_trades, capital):
    """
    Calculate total % of capital at risk across all trades

    Args:
        open_trades: List of open trades with stop losses
        capital: Total portfolio value

    Returns:
        Total risk % (e.g., 0.08 = 8% of portfolio at risk)
    """
    total_risk = sum([trade.risk_amount for trade in open_trades])
    return total_risk / capital
```

---

#### 3.3.3 Monitoring Module

**Performance Dashboard** (`dashboard.py` - Streamlit):
- Real-time P&L display
- Open positions table
- Equity curve chart
- Win rate, profit factor, Sharpe ratio
- Drawdown chart
- Recent trades log

**Telegram Alerts** (`telegram_bot.py`):
- Trade entry/exit notifications
- Daily performance summary
- Drawdown warnings
- Error alerts (API issues, connection loss)
- Manual override commands

**Metrics Calculation** (`metrics.py`):
```python
def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Sharpe Ratio = (Return - RiskFree) / StdDev"""
    pass

def calculate_max_drawdown(equity_curve):
    """Maximum peak-to-trough decline"""
    pass

def calculate_profit_factor(trades):
    """Gross Profit / Gross Loss"""
    pass

def calculate_win_rate(trades):
    """% of profitable trades"""
    pass
```

---

### 3.4 Backtesting Infrastructure

**Data Management**:
1. **Download Historical Data**:
   ```bash
   freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT \
       --timeframes 5m 15m 1h 4h --days 365
   ```

2. **Data Quality Checks**:
   - Verify no gaps in data
   - Check for outliers (flash crashes)
   - Ensure sufficient history (12+ months)

**Backtesting Process**:
1. **Train/Test Split**:
   - Train: 70% of data (optimize parameters)
   - Test: 30% of data (out-of-sample validation)
   - Walk-forward: Rolling 3-month train, 1-month test

2. **Hyperopt (Parameter Optimization)**:
   ```bash
   freqtrade hyperopt --strategy MomentumMeanReversion \
       --hyperopt-loss SharpeHyperOptLoss --epochs 500
   ```

3. **Backtest Execution**:
   ```bash
   freqtrade backtesting --strategy MomentumMeanReversion \
       --timeframe 15m --timerange 20240101-20251101
   ```

4. **Transaction Cost Modeling**:
   - Include exchange fees (0.1% for Binance spot)
   - Model slippage (0.05% for market orders)
   - Account for spread (bid-ask)

**Overfitting Prevention**:
- Use cross-validation (multiple train/test periods)
- Test on different market conditions (bull, bear, sideways)
- Avoid over-optimization (limit hyperopt epochs)
- Require consistent performance across timeframes

---

### 3.5 Deployment Strategy (Demo Trading)

**Phase 3A: Dry-Run Testing (Freqtrade built-in)**
- Duration: 2 weeks minimum
- Uses real-time data, simulated execution
- Validates strategy logic without risk
- Identifies bugs and edge cases

**Phase 3B: Bybit Testnet Deployment**
- Duration: 8-12 weeks minimum
- Virtual funds ($50,000 USDT)
- Real API execution, no financial risk
- Full system testing (API limits, latency, errors)

**Monitoring During Demo**:
- Daily performance review
- Weekly detailed analysis
- Compare backtest vs. demo performance
- Log all issues and anomalies

**Go/No-Go Decision Criteria**:
After 8-12 weeks, proceed to real money ONLY if:
✅ Sharpe Ratio > 1.5
✅ Maximum Drawdown < 20%
✅ 60%+ winning weeks
✅ Profit Factor > 1.5
✅ Demo performance matches backtest (within 20%)
✅ No critical bugs or system failures

---

## 4. IMPLEMENTATION ROADMAP

### Phase 3: Implementation (Current Next Step)

#### Week 1-2: Setup & Infrastructure
- [x] Set up Python environment (Python 3.11+)
- [ ] Install Freqtrade and dependencies
- [ ] Configure Bybit Testnet account and API keys
- [ ] Download historical data (12 months, multiple pairs)
- [ ] Set up Git repository and version control
- [ ] Configure Telegram bot for notifications

#### Week 3-4: Strategy 1 Implementation (Momentum + Mean Reversion)
- [ ] Implement indicator calculations (ADX, RSI, EMA, BB, ATR)
- [ ] Code entry logic (momentum and mean reversion conditions)
- [ ] Code exit logic (trailing stops, profit targets)
- [ ] Implement risk management (position sizing, stop losses)
- [ ] Write unit tests for strategy logic
- [ ] Document strategy parameters

#### Week 5-6: Backtesting & Optimization
- [ ] Run initial backtest on train data (70%)
- [ ] Analyze results, identify issues
- [ ] Run Hyperopt to optimize parameters
- [ ] Backtest optimized strategy on test data (30%)
- [ ] Walk-forward analysis (rolling windows)
- [ ] Document backtest results and learnings

#### Week 7-8: Dry-Run Testing
- [ ] Configure Freqtrade for dry-run mode
- [ ] Start dry-run with real-time data
- [ ] Monitor for 2 weeks continuously
- [ ] Fix bugs and edge cases
- [ ] Validate strategy logic matches expectations
- [ ] Compare dry-run to backtest

#### Week 9-10: Monitoring & Dashboard
- [ ] Build Streamlit performance dashboard
- [ ] Implement Telegram alerts (entry, exit, warnings)
- [ ] Set up performance metrics calculation
- [ ] Configure kill switches and safety limits
- [ ] Test monitoring under various scenarios
- [ ] Document dashboard usage

#### Week 11-12: Bybit Testnet Deployment
- [ ] Deploy to Bybit Testnet with virtual funds
- [ ] Start with conservative position sizing (0.5% risk)
- [ ] Monitor performance daily
- [ ] Log all trades and system behavior
- [ ] Begin 8-12 week demo trading period
- [ ] Weekly performance reviews

---

### Phase 4: Demo Account Live Testing (Weeks 13-24)

#### Continuous Activities:
- [ ] Monitor demo trading performance daily
- [ ] Generate weekly performance reports
- [ ] Track all metrics (Sharpe, drawdown, win rate, profit factor)
- [ ] Compare demo results to backtest
- [ ] Log issues, bugs, and unexpected behavior
- [ ] Analyze losing trades for patterns
- [ ] Test strategy adjustments on separate instance

#### Mid-Point Review (Week 18):
- [ ] Comprehensive performance analysis (6 weeks data)
- [ ] Identify strengths and weaknesses
- [ ] Decide: continue, adjust, or abandon strategy
- [ ] Consider implementing Strategy 2 (BTC-Neutral) in parallel

#### End of Demo Period (Week 24):
- [ ] Final performance evaluation
- [ ] Go/No-Go decision for real money
- [ ] Document all lessons learned
- [ ] Prepare for real money deployment (if approved)

---

### Phase 5: Iteration & Optimization (Ongoing)

Based on demo trading results, iterate on:
- Parameter adjustments (ADX thresholds, RSI levels, stop loss)
- Risk management refinements (position sizing, portfolio heat)
- Strategy enhancements (additional filters, ML models)
- Portfolio diversification (add Strategy 2, 3, or 4)
- Exchange optimization (test Binance, OKX for better fills)

---

## 5. KEY LEARNINGS FROM RESEARCH

### 5.1 Critical Success Factors
1. **Risk Management > Strategy**: 90% of success is risk management, 10% is strategy
2. **Realistic Expectations**: Most bots lose money; profitability takes months/years
3. **Avoid Overfitting**: Backtest perfection ≠ live profitability
4. **Transaction Costs Matter**: Fees and slippage destroy theoretical profits
5. **Market Regimes Change**: Strategies that worked in 2021 may not work in 2025

### 5.2 Common Pitfalls to Avoid
❌ Using shift(-1) or future data in backtests
❌ Over-optimizing parameters (hyperopt with too many epochs)
❌ Ignoring transaction costs and slippage
❌ Testing only in bull markets
❌ Skipping dry-run and going straight to real money
❌ Risking too much per trade (>2%)
❌ Not having kill switches or safety limits

### 5.3 Best Practices from Freqtrade Community
✅ Always start with backtesting, then dry-run, then demo
✅ Test strategies in bull, bear, and sideways markets
✅ Use forward testing (dry-run) for reliable performance indication
✅ Look for Sharpe > 1.0, profit factor > 2.0, average trade > 1%
✅ Maximum drawdown < 10% is good, < 20% is acceptable
✅ Update strategy parameters quarterly (markets change)
✅ Keep detailed logs of all trades and decisions

---

## 6. NEXT STEPS (Action Items)

### Immediate (This Week):
1. ✅ Complete Phase 2 document (this document)
2. [ ] Set up Python environment and install Freqtrade
3. [ ] Create Bybit Testnet account and get API keys
4. [ ] Download historical data for backtesting
5. [ ] Set up project repository structure

### Next Week:
6. [ ] Implement Strategy 1: Momentum + Mean Reversion Hybrid
7. [ ] Write unit tests for strategy
8. [ ] Run initial backtests
9. [ ] Begin hyperopt optimization

### Next Month:
10. [ ] Complete backtesting and optimization
11. [ ] Deploy to dry-run mode
12. [ ] Build monitoring dashboard
13. [ ] Start Bybit Testnet deployment

---

## 7. RISK ACKNOWLEDGMENT

**CRITICAL REMINDER**: This is an experimental project for learning and testing. Key risks include:

⚠️ **No Guarantee of Profit**: Most trading bots lose money
⚠️ **Market Risk**: Crypto markets are extremely volatile
⚠️ **Technical Risk**: Bugs, API failures, exchange issues
⚠️ **Regulatory Risk**: Crypto regulations are evolving
⚠️ **Time Investment**: Requires months of testing and iteration

**Mitigation**:
- Start with demo trading only (NO REAL MONEY for 3-6 months)
- Risk only what you can afford to lose
- Maintain strict position sizing and stop losses
- Have kill switches and safety limits
- Monitor performance daily
- Be prepared to abandon strategies that don't work

---

**END OF PHASE 2 DOCUMENT**

**Status**: ✅ Phase 2 Complete
**Next Phase**: Phase 3 - Implementation
**Recommended Action**: Proceed with Week 1-2 setup tasks
