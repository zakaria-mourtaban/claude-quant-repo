# Sharia Compliance Documentation

## ✅ Halal Trading Bot - Islamic Finance Compliant

This cryptocurrency trading bot has been designed to be **fully compliant with Islamic finance principles (Sharia law)**. This document explains how the bot operates within Halal guidelines.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Islamic Finance Principles](#key-islamic-finance-principles)
3. [How This Bot Complies](#how-this-bot-complies)
4. [What This Bot Does NOT Do](#what-this-bot-does-not-do)
5. [Technical Implementation](#technical-implementation)
6. [Verification](#verification)
7. [Scholarly Considerations](#scholarly-considerations)
8. [FAQ](#faq)

---

## Overview

This trading bot is designed to trade cryptocurrencies in a **Sharia-compliant manner**:

- ✅ **Spot trading only** - Buys and holds actual cryptocurrency assets
- ✅ **No leverage** - Uses only your own money (1x leverage)
- ✅ **No short selling** - Only buys and sells (long positions)
- ✅ **No interest (Riba)** - No borrowing or lending with interest
- ✅ **Immediate settlement** - Transactions settle immediately on the blockchain
- ✅ **Ownership-based** - You own the actual cryptocurrency you purchase

---

## Key Islamic Finance Principles

### 1. **No Riba (Interest/Usury)**
Islam prohibits earning or paying interest on borrowed money.

**How we comply**: The bot never borrows money or uses margin. It only trades with funds you already own.

### 2. **No Gharar (Excessive Uncertainty)**
Islam prohibits transactions with excessive uncertainty or speculation.

**How we comply**:
- All trades are immediate spot purchases of real assets
- No futures contracts or derivatives
- Prices are transparent and determined by market supply/demand
- You always know exactly what you're buying and selling

### 3. **No Maisir (Gambling)**
Islam prohibits gambling and games of chance.

**How we comply**:
- The strategy is based on technical analysis, not chance
- Uses proven statistical indicators (RSI, EMA, ADX, Bollinger Bands)
- Risk management with stop losses
- Not a "get rich quick" scheme - systematic approach

### 4. **Asset-Backed Trading**
Transactions must involve the exchange of real assets.

**How we comply**:
- Every trade involves buying or selling actual cryptocurrency
- The cryptocurrency is held in your wallet/account
- No paper claims or IOUs - you own the real asset

### 5. **No Short Selling**
Selling an asset you don't own is considered haram by most scholars.

**How we comply**:
- The bot NEVER short sells
- Only opens long positions (buy first, sell later)
- You must own the asset before selling it

---

## How This Bot Complies

### ✅ Spot Trading Only

```
HALAL EXAMPLE:
1. You have $1,000 USDT in your account
2. Bot sees a buy signal for Bitcoin
3. Bot uses $330 USDT (33% position size) to buy Bitcoin
4. You now own 0.008 BTC (real Bitcoin in your wallet)
5. When price goes up, bot sells the 0.008 BTC you own
6. You receive USDT back (profit or loss)
```

This is **buying and selling real assets** - Halal ✅

### ✅ No Leverage (1x Only)

The strategy explicitly sets leverage to **1.0** (no leverage):

```python
def leverage(self, pair: str, ...) -> float:
    """
    ✅ SHARIA COMPLIANT: Always returns 1.0 (no leverage/margin)

    1x leverage = buying actual cryptocurrency with your own money
    """
    return 1.0
```

**What this means**: If you have $1,000, you can only trade with $1,000. You never borrow additional funds.

### ✅ Long Positions Only

The strategy only implements `enter_long` and `exit_long` signals:

- **enter_long**: Buy cryptocurrency with your money
- **exit_long**: Sell cryptocurrency you already own

There are **NO** `enter_short` or `exit_short` signals. Short selling is impossible with this bot.

### ✅ No Interest-Bearing Activities

- No margin trading (which involves paying interest on borrowed funds)
- No lending your crypto for interest
- No staking with interest-bearing returns
- Pure buying and selling only

### ✅ Transparent Ownership

All trades are executed on **spot markets** where:
- Transactions settle immediately (or within minutes on the blockchain)
- You have real ownership of the cryptocurrency
- Assets are held in your exchange account/wallet
- No counterparty risk (you own the asset directly)

---

## What This Bot Does NOT Do

### ❌ No Margin Trading

**Margin trading is HARAM** because it involves:
- Borrowing money from the exchange
- Paying interest on the borrowed amount
- Trading with money you don't own

**This bot**: Uses only your own funds ✅

### ❌ No Leverage

**Leverage is HARAM** because it's a form of margin trading:
- 10x leverage = borrowing 9x your capital
- Requires paying interest fees
- Can lead to debt

**This bot**: 1x leverage only (no borrowing) ✅

### ❌ No Short Selling

**Short selling is HARAM** because:
- You sell an asset you don't own
- You borrow the asset to sell it
- Involves riba (interest) and gharar (uncertainty)

**This bot**: Long positions only (buy then sell) ✅

### ❌ No Futures/Derivatives

**Futures contracts are HARAM** (according to most scholars) because:
- Settlement is delayed (not immediate)
- Often cash-settled (no actual asset exchange)
- High uncertainty and speculation

**This bot**: Spot market only (immediate settlement) ✅

### ❌ No Interest Staking

Some exchanges offer staking with interest returns:
- Locking up your crypto
- Earning interest (riba)

**This bot**: Only buys and sells, never stakes ✅

---

## Technical Implementation

### Configuration Files

Both configuration files explicitly enforce spot trading:

**`config/config.json`** (Dry-run):
```json
{
  "_comment": "✅ SHARIA COMPLIANT CONFIG - Spot trading only, no leverage, long positions only",
  "trading_mode": "spot",
  "margin_mode": "",
  ...
}
```

**`config/config_bybit_testnet.json`** (Testnet):
```json
{
  "_comment": "✅ SHARIA COMPLIANT CONFIG - Spot trading only, no leverage, long positions only",
  "trading_mode": "spot",
  "margin_mode": "",
  "exchange": {
    "ccxt_config": {
      "options": {
        "defaultType": "spot"
      }
    }
  }
}
```

### Strategy Code

**File**: `user_data/strategies/MomentumMeanReversion.py`

The strategy explicitly documents Sharia compliance:

```python
"""
SHARIA COMPLIANCE:
✅ SPOT TRADING ONLY - No margin, no leverage, no futures
✅ LONG POSITIONS ONLY - No short selling (only buy and sell)
✅ OWN CAPITAL ONLY - Trades only with your own funds (1x leverage)
✅ HALAL - Compliant with Islamic finance principles
"""
```

Key methods:

1. **`populate_entry_trend()`**: Only sets `enter_long = 1` (buy signals)
2. **`populate_exit_trend()`**: Only sets `exit_long = 1` (sell signals)
3. **`leverage()`**: Always returns `1.0` (no leverage)

---

## Verification

### How to Verify Sharia Compliance

1. **Check Configuration Files**:
   ```bash
   cat config/config.json | grep trading_mode
   # Should show: "trading_mode": "spot"
   ```

2. **Check Strategy Code**:
   ```bash
   cat user_data/strategies/MomentumMeanReversion.py | grep "def leverage"
   # Should show: return 1.0
   ```

3. **Check for Short Selling**:
   ```bash
   grep -r "enter_short\|exit_short" user_data/strategies/
   # Should return: No results (no short selling code)
   ```

4. **Check Exchange Settings**:
   - Log into your exchange account
   - Verify "Spot Trading" is selected (not Margin or Futures)
   - Check your balance - should only show owned assets

### Backtest Verification

Run the backtest and verify:

```bash
python scripts/run_simple_backtest.py
```

In the results:
- All trades should be "LONG" positions
- Balance never goes negative
- No interest/funding fees charged
- Position sizes always ≤ your balance

---

## Scholarly Considerations

### Cryptocurrency in Islam

The permissibility of cryptocurrency trading is still debated among scholars:

**Arguments for Permissibility (Halal)**:
- Cryptocurrencies are considered commodities/assets
- Spot trading is similar to trading gold, silver, or currencies
- No riba (interest) if trading on spot markets
- Blockchain provides transparency and ownership

**Arguments Against (Haram)**:
- Some scholars say cryptocurrencies lack intrinsic value
- High volatility leads to excessive speculation (maisir)
- Used in illegal activities

**This Bot's Position**:
- We implement **only the Halal aspects** of crypto trading
- Spot trading with owned funds only
- Risk management to reduce gambling-like behavior
- You should **consult your own scholar** for guidance

### Recommended Approach

1. **Consult a Scholar**: Ask a qualified Islamic finance scholar about:
   - Cryptocurrency trading in general
   - Spot trading specifically
   - Technical analysis (is it halal?)

2. **Choose Halal Cryptocurrencies**: Some scholars suggest:
   - ✅ Bitcoin (BTC) - generally considered permissible
   - ✅ Ethereum (ETH) - utility token, no interest
   - ❌ Interest-bearing tokens (lending protocols)
   - ❌ Gambling/casino tokens

3. **Avoid Excessive Risk**: Even if trading is halal:
   - Don't risk more than you can afford to lose
   - Use proper risk management (2% per trade)
   - Avoid greed and excessive speculation

4. **Pay Zakat**: If profitable:
   - Calculate 2.5% of your crypto holdings annually
   - Pay zakat on your profits

---

## FAQ

### Q1: Is this bot 100% Halal?

**A**: The bot implements **only Halal trading methods** (spot trading, no leverage, no short selling). However, the permissibility of cryptocurrency trading itself is debated. **Consult a qualified Islamic scholar** for your specific situation.

### Q2: Does spot trading involve any interest?

**A**: No. Spot trading is buying and selling real assets with your own money. There is no borrowing, lending, or interest involved.

### Q3: Is using technical analysis allowed in Islam?

**A**: Most scholars permit technical analysis as it's based on:
- Market patterns and trends (not gambling)
- Statistical analysis (not guessing)
- Risk management (not recklessness)

However, **intentions matter**. Trading should be for legitimate profit, not gambling or greed.

### Q4: What about the high volatility of crypto?

**A**: Volatility alone doesn't make trading haram. The bot uses:
- Stop losses to limit losses
- Position sizing to manage risk
- Technical indicators to reduce speculation

This is **systematic trading**, not gambling.

### Q5: Can I use this bot on any exchange?

**A**: Use exchanges that support **spot trading** with **no mandatory leverage**:

✅ Recommended:
- Binance (spot market)
- Bybit (spot market)
- OKX (spot market)
- Kraken (spot market)

❌ Avoid:
- Exchanges that force leverage
- Margin-only platforms
- Derivatives-only platforms

### Q6: What if I accidentally enable margin?

**A**: The bot's code **prevents margin trading**:
- `trading_mode: "spot"` in config
- `leverage()` returns `1.0` always
- No short selling code

Even if you enable margin on the exchange, the bot won't use it.

### Q7: Is the 5% stop loss allowed?

**A**: Yes. Stop losses are a **risk management tool**, not gambling. They:
- Protect your capital from large losses
- Are part of prudent trading
- Don't involve interest or prohibited activities

### Q8: What about transaction fees?

**A**: Exchange fees are **permissible** in Islam:
- They're payment for a service (executing trades)
- Not interest (riba)
- Transparent and known in advance

Typical fees: 0.1% per trade (e.g., $1 fee on $1,000 trade).

### Q9: Can I add more strategies later?

**A**: Yes, but ensure any new strategy:
- Uses spot trading only
- No leverage (1x)
- No short selling
- No interest-bearing activities

### Q10: What if I make a loss?

**A**: Losses are a normal part of trading:
- Not your fault if you traded responsibly
- Part of business risk (which is permissible)
- Islam allows risk-taking in business

**What's NOT allowed**:
- Reckless gambling with life savings
- Revenge trading after losses
- Excessive leverage leading to debt

---

## Summary

This crypto trading bot is designed to be **Sharia-compliant** by:

✅ **Spot trading only** - Real asset ownership
✅ **No leverage** - Uses only your own money (1x)
✅ **Long positions only** - No short selling
✅ **No interest** - No riba (interest) or margin
✅ **Transparent** - All code and settings are open
✅ **Risk managed** - Stop losses and position sizing

**IMPORTANT**: The permissibility of cryptocurrency trading is debated among scholars. This bot implements **only the Halal methods** of trading. You should:

1. **Consult a qualified Islamic finance scholar**
2. **Trade responsibly** (don't risk more than you can afford)
3. **Pay Zakat** on profits (2.5% annually)
4. **Have good intentions** (legitimate profit, not gambling)

---

## Questions or Concerns?

If you have questions about Sharia compliance:

1. Review this document thoroughly
2. Check the configuration files (`config/config*.json`)
3. Review the strategy code (`user_data/strategies/MomentumMeanReversion.py`)
4. **Consult a qualified Islamic scholar** for your specific situation

May Allah (SWT) grant you success in your trading and bless your wealth.

**Disclaimer**: This document is for informational purposes only and does not constitute religious advice. Always consult qualified Islamic scholars for religious rulings (fatawa).

---

**Last Updated**: 2025-11-06
**Version**: 1.0.0
**Status**: ✅ Fully Sharia-Compliant Configuration
