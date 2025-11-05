# Deployment Guide - Crypto Trading Bot

This guide covers deploying the trading bot to different environments.

## Table of Contents
1. [Dry-Run Deployment](#dry-run-deployment) (Paper Trading)
2. [Testnet Deployment](#testnet-deployment) (Bybit Virtual Funds)
3. [Production Deployment](#production-deployment) (Real Money - Future)
4. [Monitoring](#monitoring)
5. [Troubleshooting](#troubleshooting)

---

## Dry-Run Deployment

Dry-run mode simulates trading with real-time market data but doesn't execute real trades.

### Setup

1. **Ensure Configuration**:
   ```bash
   # Verify config exists
   cat config/config.json

   # Check that dry_run is true
   grep "dry_run" config/config.json
   ```

2. **Start Dry-Run**:
   ```bash
   ./scripts/start_dryrun.sh MomentumMeanReversion
   ```

3. **Monitor**:
   ```bash
   # In another terminal, tail the logs
   tail -f user_data/logs/freqtrade.log
   ```

### What to Watch

- **Entry Signals**: Verify bot identifies entry opportunities
- **Exit Signals**: Check that exits trigger correctly
- **Risk Management**: Confirm position sizing is appropriate
- **No Errors**: Ensure no API errors or crashes

### Expected Behavior

- Bot runs continuously
- Simulates trades in database (user_data/tradesv3.sqlite)
- No real API connections to exchanges
- Virtual balance starts at configured amount (default: 10,000 USDT)

### Duration

**Minimum**: 2 weeks
**Recommended**: 4 weeks

### Success Criteria

✅ No crashes or errors for 2+ weeks
✅ Entry/exit logic behaves as expected
✅ Performance metrics look promising
✅ Ready for testnet deployment

---

## Testnet Deployment

Testnet deployment uses Bybit Testnet with $50,000 virtual funds and real API execution.

### Prerequisites

1. **Bybit Testnet Account**:
   - Follow `docs/BYBIT_TESTNET_SETUP.md`
   - Create API keys (Read + Trade permissions)
   - Add to `.env` file

2. **Verify API Connection**:
   ```bash
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
   print(f"✅ Connected! Balance: {balance['USDT']['total']} USDT")
   EOF
   ```

### Deployment Steps

1. **Final Pre-Deployment Checks**:
   ```bash
   # Verify configuration
   cat config/config_bybit_testnet.json

   # Check environment variables
   source .env && echo $BYBIT_TESTNET_API_KEY | head -c 10
   ```

2. **Start Testnet Bot**:
   ```bash
   ./scripts/start_testnet.sh MomentumMeanReversion
   ```

3. **Verify First Trade**:
   - Watch logs for first entry signal
   - Check Bybit Testnet web interface for order
   - Confirm order execution

4. **Set Up Monitoring**:
   ```bash
   # In another terminal, run dashboard
   python monitoring/dashboard.py --days 7
   ```

### Monitoring Checklist

**Daily**:
- [ ] Check bot is still running (no crashes)
- [ ] Review open positions
- [ ] Check daily P&L
- [ ] Verify no API errors

**Weekly**:
- [ ] Run performance dashboard
- [ ] Calculate Sharpe ratio, max drawdown
- [ ] Compare to backtest results
- [ ] Review losing trades for patterns

**Monthly**:
- [ ] Comprehensive performance review
- [ ] Strategy adjustment decisions
- [ ] Document lessons learned

### Safety Features Active

✅ Maximum 3 concurrent positions
✅ 2% risk per trade (position sizing)
✅ ATR-based stop losses
✅ Trailing stop enabled
✅ API rate limiting enabled
✅ No leverage (1x)

### Duration

**Minimum**: 8 weeks
**Recommended**: 12-16 weeks (3-4 months)

### Success Criteria

After 8-12 weeks, evaluate:

✅ **Sharpe Ratio > 1.5**
✅ **Max Drawdown < 20%**
✅ **Win Rate > 40%** (with R:R > 2:1)
✅ **Profit Factor > 1.5**
✅ **60%+ winning weeks**
✅ **No critical bugs/failures**
✅ **Demo performance matches backtest** (within 20%)

### Red Flags (Stop Trading)

❌ Sharpe Ratio < 0.5
❌ Max Drawdown > 30%
❌ Profit Factor < 1.0
❌ Frequent unexplained errors
❌ Large gap between backtest and demo results

---

## Production Deployment

⚠️ **NOT RECOMMENDED UNTIL 3-6 MONTHS OF SUCCESSFUL TESTNET TRADING**

### Prerequisites

**Required Before Production**:
1. ✅ 3-6 months of profitable testnet trading
2. ✅ All success criteria met (Sharpe > 1.5, DD < 20%, etc.)
3. ✅ No critical bugs or failures
4. ✅ Thorough understanding of strategy behavior
5. ✅ Risk management verified and tested
6. ✅ Emergency procedures documented and tested

### Production Differences

- **Real Money**: Use only funds you can afford to lose
- **Start Small**: 1-5% of intended capital initially
- **Scale Gradually**: Increase capital over weeks, not days
- **Different Exchange**: Consider OKX for production (best APIs/fees)
- **Tax Implications**: Track all trades for tax reporting
- **Legal Compliance**: Ensure compliance with local regulations

### Production Setup (Future Reference)

1. **Create Production API Keys**:
   - OKX or Binance production account
   - API keys with Read + Trade only (NO withdraw)
   - IP restrictions enabled
   - Store securely in `.env.production`

2. **Production Configuration**:
   ```json
   {
     "dry_run": false,
     "stake_amount": 50,  // Start with small amounts
     "tradable_balance_ratio": 0.05,  // Use only 5% initially
     ...
   }
   ```

3. **Enhanced Monitoring**:
   - Set up alerts (SMS, Email, Telegram)
   - Daily performance reports
   - Weekly review meetings
   - Monthly comprehensive audits

4. **Emergency Procedures**:
   - Manual kill switch procedure
   - Contact information for exchange support
   - Backup API keys (read-only for monitoring)
   - Incident response plan

### Scaling Strategy

**Week 1-4**: $500 - $1,000
**Week 5-8**: $2,000 - $5,000
**Week 9-12**: $5,000 - $10,000
**Week 13+**: Scale based on performance

**Never risk more than you can afford to lose!**

---

## Monitoring

### Real-Time Monitoring

**Dashboard**:
```bash
python monitoring/dashboard.py --days 30
```

**Logs**:
```bash
# Follow logs in real-time
tail -f user_data/logs/freqtrade.log

# Search for errors
grep ERROR user_data/logs/freqtrade.log

# Search for specific trade
grep "BTC/USDT" user_data/logs/freqtrade.log
```

**Freqtrade Web UI**:
1. Ensure API server is enabled in config
2. Visit: http://localhost:8080
3. Login with credentials from config
4. View open trades, performance charts, etc.

### Performance Metrics

```bash
# View recent performance
python monitoring/dashboard.py --days 7

# Full history
python monitoring/dashboard.py --days 365
```

### Alerts Setup (Optional)

**Telegram Bot**:
1. Create bot via [@BotFather](https://t.me/BotFather)
2. Add token to `.env`
3. Update config: `"telegram": {"enabled": true}`
4. Restart bot

**Email Alerts** (Advanced):
- Set up SMTP in custom script
- Send daily performance reports
- Alert on drawdown thresholds

---

## Troubleshooting

### Bot Won't Start

**Issue**: Bot exits immediately

**Solutions**:
```bash
# Check configuration syntax
python -m json.tool config/config.json

# Verify API keys
source .env && echo "Key: ${BYBIT_TESTNET_API_KEY:0:10}..."

# Check logs
tail -50 user_data/logs/freqtrade.log
```

### No Trades Executing

**Issue**: Bot runs but no trades

**Check**:
1. **Market Conditions**: Are entry conditions met?
   ```bash
   # View current market data
   freqtrade test-pairlist --config config/config.json
   ```

2. **Dry-Run Mode**: Is dry_run disabled for testnet?
   ```bash
   grep dry_run config/config_bybit_testnet.json
   ```

3. **Balance**: Do you have sufficient balance?
   ```bash
   # Check via API or web interface
   ```

4. **Strategy Logic**: Are indicators calculating correctly?
   ```bash
   # Run strategy in test mode
   python user_data/strategies/MomentumMeanReversion.py
   ```

### API Errors

**Issue**: Rate limit exceeded

**Solution**:
- Ensure `enableRateLimit: true` in config
- Reduce `process_throttle_secs` if too fast
- Wait 60 seconds and retry

**Issue**: Invalid API signature

**Solution**:
- Verify API keys are correct
- Check for extra spaces in `.env` file
- Ensure using testnet keys for testnet URL

### Database Locked

**Issue**: Database is locked error

**Solution**:
```bash
# Stop all freqtrade instances
pkill freqtrade

# Wait a moment
sleep 5

# Restart
./scripts/start_testnet.sh
```

### Memory Issues

**Issue**: Bot crashes with memory error

**Solution**:
- Reduce number of pairs in whitelist
- Increase system RAM
- Reduce `startup_candle_count` in strategy

---

## Best Practices

### General

✅ **Always** start with dry-run before testnet
✅ **Always** start with testnet before production
✅ **Never** skip risk management steps
✅ **Always** monitor daily during testnet phase
✅ **Document** all issues and resolutions
✅ **Keep** detailed performance logs

### Security

✅ **Never** commit `.env` file to git
✅ **Never** share API keys publicly
✅ **Always** use IP restrictions on API keys
✅ **Never** enable withdrawal permissions on API keys
✅ **Rotate** API keys every 90 days
✅ **Use** 2FA on exchange accounts

### Risk Management

✅ **Start** with minimal position sizes
✅ **Test** kill switches regularly
✅ **Set** realistic drawdown limits
✅ **Monitor** portfolio heat constantly
✅ **Never** override stop losses manually
✅ **Be prepared** to shut down if strategy fails

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (`pytest tests/`)
- [ ] Backtest results reviewed and acceptable
- [ ] Dry-run completed successfully (2+ weeks)
- [ ] .env file configured with API keys
- [ ] Configuration files reviewed
- [ ] Monitoring setup tested

### Testnet Deployment

- [ ] Bybit Testnet account created
- [ ] API keys generated and stored
- [ ] API connection tested
- [ ] Bot started successfully
- [ ] First trade verified
- [ ] Monitoring dashboard running
- [ ] Logs being collected

### Ongoing

- [ ] Daily monitoring routine established
- [ ] Weekly performance reviews scheduled
- [ ] Emergency procedures documented
- [ ] Backup and recovery plan in place

---

## Support

**Documentation**:
- README.md - Project overview
- QUICKSTART.md - Fast setup
- RESEARCH_PHASE1.md - Strategy research
- PHASE2_STRATEGY_SELECTION.md - Strategy details

**External Resources**:
- [Freqtrade Docs](https://www.freqtrade.io/en/stable/)
- [Freqtrade Discord](https://discord.gg/p7nuUNVfP7)
- [Bybit API Docs](https://bybit-exchange.github.io/docs/v5/intro)

**Troubleshooting**:
- Check logs: `user_data/logs/freqtrade.log`
- Review database: `user_data/tradesv3.sqlite`
- Test strategy: `pytest tests/test_strategy.py -v`

---

**Last Updated**: 2025-11-05
**Version**: 1.0.0
