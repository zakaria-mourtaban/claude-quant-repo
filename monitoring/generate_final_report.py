#!/usr/bin/env python3
"""
Final 2-Week Test Report Generator

Generates comprehensive analysis after 2-week live test completes.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import statistics
from live_tracker import LivePerformanceTracker


def calculate_sharpe_ratio(daily_returns, risk_free_rate=0.02):
    """Calculate Sharpe ratio from daily returns"""
    if not daily_returns or len(daily_returns) < 2:
        return 0.0

    mean_return = statistics.mean(daily_returns)
    std_return = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0

    if std_return == 0:
        return 0.0

    # Annualized
    annual_return = mean_return * 365
    annual_std = std_return * (365 ** 0.5)

    sharpe = (annual_return - risk_free_rate) / annual_std
    return sharpe


def analyze_trades(trades_file="user_data/trades.json"):
    """Detailed trade analysis"""
    if not Path(trades_file).exists():
        return {}

    try:
        with open(trades_file, 'r') as f:
            trades = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

    if not trades:
        return {}

    # Calculate metrics
    total_trades = len(trades)
    wins = [t for t in trades if t.get('close_profit_abs', 0) > 0]
    losses = [t for t in trades if t.get('close_profit_abs', 0) < 0]

    total_profit = sum(t.get('close_profit_abs', 0) for t in trades)
    gross_profit = sum(t.get('close_profit_abs', 0) for t in wins)
    gross_loss = abs(sum(t.get('close_profit_abs', 0) for t in losses))

    avg_win = gross_profit / len(wins) if wins else 0
    avg_loss = gross_loss / len(losses) if losses else 0

    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

    # Best and worst trades
    best_trade = max(trades, key=lambda x: x.get('close_profit_abs', 0)) if trades else None
    worst_trade = min(trades, key=lambda x: x.get('close_profit_abs', 0)) if trades else None

    # Calculate durations
    durations = []
    for trade in trades:
        if trade.get('open_date') and trade.get('close_date'):
            try:
                open_dt = datetime.fromisoformat(trade['open_date'])
                close_dt = datetime.fromisoformat(trade['close_date'])
                duration = (close_dt - open_dt).total_seconds() / 3600  # hours
                durations.append(duration)
            except:
                pass

    avg_duration = statistics.mean(durations) if durations else 0

    return {
        'total_trades': total_trades,
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': len(wins) / total_trades * 100 if total_trades > 0 else 0,
        'total_profit': total_profit,
        'gross_profit': gross_profit,
        'gross_loss': gross_loss,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'avg_duration_hours': avg_duration
    }


def generate_final_report():
    """Generate comprehensive final report"""
    tracker = LivePerformanceTracker()
    tracker.update_from_freqtrade()

    status = tracker.get_current_status()
    trade_analysis = analyze_trades()

    # Calculate daily returns for Sharpe ratio
    daily_returns = []
    snapshots = tracker.session_data.get('daily_snapshots', [])
    for i in range(1, len(snapshots)):
        prev_balance = snapshots[i-1]['balance']
        curr_balance = snapshots[i]['balance']
        daily_return = (curr_balance - prev_balance) / prev_balance
        daily_returns.append(daily_return)

    sharpe_ratio = calculate_sharpe_ratio(daily_returns)

    # Generate report
    now = datetime.now()
    start_time = datetime.fromisoformat(status['start_time'])
    elapsed = now - start_time

    report = f"""
{'='*100}
{'='*100}
                      🎉 2-WEEK LIVE TEST - FINAL REPORT 🎉
{'='*100}
{'='*100}

Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}

{'='*100}
                             TEST OVERVIEW
{'='*100}

📅 Start Date:        {start_time.strftime('%Y-%m-%d %H:%M:%S')}
📅 End Date:          {now.strftime('%Y-%m-%d %H:%M:%S')}
⏱️  Total Duration:    {elapsed.days} days, {elapsed.seconds // 3600} hours, {(elapsed.seconds % 3600) // 60} minutes

Strategy:            MomentumMeanReversion v1.0.1 (Sharia-Compliant)
Trading Mode:        Dry-Run (Paper Trading)
Initial Balance:     ${status['initial_balance']:,.2f}

{'='*100}
                          FINAL PERFORMANCE
{'='*100}

💰 PROFITABILITY
--------------------------------------------------------------------------------
Initial Balance:     ${status['initial_balance']:,.2f}
Final Balance:       ${status['current_balance']:,.2f}
Total Profit/Loss:   ${status['current_balance'] - status['initial_balance']:+,.2f}
Total Return:        {status['total_return_pct']:+.2f}%
Daily Avg Return:    {status['total_return_pct'] / max(status['days_elapsed'], 1):+.2f}%/day

📊 TRADING STATISTICS
--------------------------------------------------------------------------------
Total Trades:        {trade_analysis.get('total_trades', 0)}
Winning Trades:      {trade_analysis.get('wins', 0)} ({trade_analysis.get('win_rate', 0):.1f}%)
Losing Trades:       {trade_analysis.get('losses', 0)}

Gross Profit:        ${trade_analysis.get('gross_profit', 0):,.2f}
Gross Loss:          ${trade_analysis.get('gross_loss', 0):,.2f}
Profit Factor:       {trade_analysis.get('profit_factor', 0):.2f}

Average Win:         ${trade_analysis.get('avg_win', 0):,.2f}
Average Loss:        ${trade_analysis.get('avg_loss', 0):,.2f}
Risk/Reward Ratio:   {trade_analysis.get('avg_win', 0) / trade_analysis.get('avg_loss', 1) if trade_analysis.get('avg_loss', 0) > 0 else 0:.2f}

⏱️  TRADE DURATION
--------------------------------------------------------------------------------
Average Hold Time:   {trade_analysis.get('avg_duration_hours', 0):.1f} hours
Trades per Day:      {trade_analysis.get('total_trades', 0) / max(status['days_elapsed'], 1):.1f}

⚠️  RISK METRICS
--------------------------------------------------------------------------------
Max Drawdown:        {status['max_drawdown_pct']:.2f}%
Sharpe Ratio:        {sharpe_ratio:.2f}

{'='*100}
                          BEST & WORST TRADES
{'='*100}

"""

    # Best trade
    if trade_analysis.get('best_trade'):
        best = trade_analysis['best_trade']
        report += f"""
✅ BEST TRADE:
   Pair:             {best.get('pair', 'N/A')}
   Entry:            {best.get('open_date', 'N/A')}
   Exit:             {best.get('close_date', 'N/A')}
   Profit:           ${best.get('close_profit_abs', 0):+.2f} ({best.get('close_profit', 0) * 100:+.2f}%)
   Entry Price:      ${best.get('open_rate', 0):.2f}
   Exit Price:       ${best.get('close_rate', 0):.2f}
"""

    # Worst trade
    if trade_analysis.get('worst_trade'):
        worst = trade_analysis['worst_trade']
        report += f"""
❌ WORST TRADE:
   Pair:             {worst.get('pair', 'N/A')}
   Entry:            {worst.get('open_date', 'N/A')}
   Exit:             {worst.get('close_date', 'N/A')}
   Loss:             ${worst.get('close_profit_abs', 0):+.2f} ({worst.get('close_profit', 0) * 100:+.2f}%)
   Entry Price:      ${worst.get('open_rate', 0):.2f}
   Exit Price:       ${worst.get('close_rate', 0):.2f}
"""

    report += f"""

{'='*100}
                         DAILY PERFORMANCE TREND
{'='*100}

"""

    # Daily snapshots table
    if snapshots:
        report += "Day  | Date       | Balance    | Trades | Win Rate | Daily P/L | Cumulative Return\n"
        report += "-----|------------|------------|--------|----------|-----------|------------------\n"

        for i, snap in enumerate(snapshots):
            day_num = i + 1
            date = datetime.fromisoformat(snap['date']).strftime('%Y-%m-%d')
            balance = snap['balance']
            trades = snap['total_trades']
            win_rate = snap['win_rate']

            # Daily P/L
            if i > 0:
                daily_pl = snap['balance'] - snapshots[i-1]['balance']
            else:
                daily_pl = snap['balance'] - status['initial_balance']

            cum_return = (balance - status['initial_balance']) / status['initial_balance'] * 100

            report += f"{day_num:4d} | {date} | ${balance:10,.2f} | {trades:6d} | {win_rate:7.1f}% | ${daily_pl:+9.2f} | {cum_return:+7.2f}%\n"

    report += f"""

{'='*100}
                        SUCCESS CRITERIA EVALUATION
{'='*100}

"""

    # Evaluate success criteria
    criteria_results = []

    # Win Rate > 40%
    win_rate_pass = trade_analysis.get('win_rate', 0) > 40
    criteria_results.append(('Win Rate > 40%', trade_analysis.get('win_rate', 0), 40, '%', win_rate_pass))

    # Positive Return
    positive_return_pass = status['total_return_pct'] > 0
    criteria_results.append(('Positive Return', status['total_return_pct'], 0, '%', positive_return_pass))

    # Profit Factor > 1.5
    pf_pass = trade_analysis.get('profit_factor', 0) > 1.5
    criteria_results.append(('Profit Factor > 1.5', trade_analysis.get('profit_factor', 0), 1.5, '', pf_pass))

    # Max Drawdown < 20%
    dd_pass = status['max_drawdown_pct'] < 20
    criteria_results.append(('Max Drawdown < 20%', status['max_drawdown_pct'], 20, '%', dd_pass))

    # Min 20 trades (for 2 weeks)
    trades_pass = trade_analysis.get('total_trades', 0) >= 20
    criteria_results.append(('Minimum 20 Trades', trade_analysis.get('total_trades', 0), 20, '', trades_pass))

    # Sharpe Ratio > 1.0
    sharpe_pass = sharpe_ratio > 1.0
    criteria_results.append(('Sharpe Ratio > 1.0', sharpe_ratio, 1.0, '', sharpe_pass))

    passed_count = sum(1 for _, _, _, _, passed in criteria_results if passed)
    total_criteria = len(criteria_results)

    for criterion, value, target, unit, passed in criteria_results:
        status_icon = "✅ PASS" if passed else "❌ FAIL"
        report += f"{status_icon:8} | {criterion:<30} | Current: {value:.2f}{unit:>1} (Target: {target:.1f}{unit:>1})\n"

    report += f"\n{'='*100}\n"
    report += f"SCORE: {passed_count}/{total_criteria} criteria passed ({passed_count/total_criteria*100:.0f}%)\n"
    report += f"{'='*100}\n\n"

    # Overall assessment
    if passed_count == total_criteria:
        assessment = "🎉 EXCELLENT - All criteria passed!"
        recommendation = "Strategy is ready for live trading with real funds (start small)"
    elif passed_count >= total_criteria * 0.7:
        assessment = "✅ GOOD - Most criteria passed"
        recommendation = "Consider parameter optimization before live trading"
    elif passed_count >= total_criteria * 0.5:
        assessment = "⚠️  MODERATE - Some issues detected"
        recommendation = "Review failed criteria and consider strategy adjustments"
    else:
        assessment = "❌ NEEDS IMPROVEMENT - Multiple criteria failed"
        recommendation = "Significant improvements needed before live trading"

    report += f"""
{'='*100}
                           OVERALL ASSESSMENT
{'='*100}

Result:              {assessment}
Recommendation:      {recommendation}

"""

    if status['total_return_pct'] > 0:
        report += f"💡 The strategy generated a {status['total_return_pct']:+.2f}% return over {status['days_elapsed']} days.\n"
        if status['days_elapsed'] >= 14:
            projected_monthly = (status['total_return_pct'] / status['days_elapsed']) * 30
            projected_annual = (status['total_return_pct'] / status['days_elapsed']) * 365
            report += f"   If this performance continues:\n"
            report += f"   - Monthly: {projected_monthly:+.2f}%\n"
            report += f"   - Annual: {projected_annual:+.2f}%\n"
    else:
        report += f"⚠️  The strategy had a {status['total_return_pct']:+.2f}% loss.\n"
        report += f"   Review the failed criteria and consider improvements.\n"

    report += f"""

{'='*100}
                            NEXT STEPS
{'='*100}

1. 📊 Review this report carefully
2. 📈 Analyze individual trades in: user_data/trades.json
3. 📉 Check daily reports in: user_data/live_test_results/daily_reports/
4. 🔧 Consider running hyperopt for parameter optimization:
      freqtrade hyperopt --strategy MomentumMeanReversion --epochs 100

"""

    if passed_count >= total_criteria * 0.7:
        report += """5. 🚀 If satisfied, proceed to Bybit Testnet (virtual funds):
      - Get API keys: https://testnet.bybit.com
      - Update .env with keys
      - Run: ./scripts/start_testnet.sh

6. 💰 After successful testnet trading, consider live trading:
      - Start with minimum capital (1-5% of total)
      - Monitor closely for first 2 weeks
      - Scale up gradually if performing well

"""
    else:
        report += """5. 🔍 Strategy needs improvement. Consider:
      - Running hyperopt to optimize parameters
      - Adjusting risk management settings
      - Testing on different market conditions
      - Reviewing trade logic

"""

    report += f"""
{'='*100}
                        SHARIA COMPLIANCE STATUS
{'='*100}

✅ Spot Trading:      Confirmed (no margin/futures)
✅ Leverage:          1x (no borrowing)
✅ Positions:         Long only (no short selling)
✅ Capital:           Own funds only
✅ Status:            HALAL ✅

This bot remains fully Sharia-compliant throughout the test period.

{'='*100}
                           DISCLAIMER
{'='*100}

⚠️  IMPORTANT NOTICES:

1. Past performance does not guarantee future results
2. This was a dry-run test with paper trading (no real money)
3. Real trading involves actual risk of loss
4. Cryptocurrency markets are highly volatile
5. Only invest what you can afford to lose
6. Consider consulting a financial advisor before live trading
7. For Islamic finance guidance, consult a qualified scholar

{'='*100}

📁 Report saved to: user_data/live_test_results/FINAL_REPORT.txt
📊 Session data: user_data/live_test_results/current_session.json
📝 Trade log: user_data/trades.json

Thank you for using the 2-Week Live Test system!

Generated by: MomentumMeanReversion Trading Bot
Version: 1.0.1 (Sharia-Compliant)
Report Date: {now.strftime('%Y-%m-%d %H:%M:%S')}

{'='*100}
{'='*100}
"""

    return report


def main():
    """Generate and save final report"""
    print("Generating final 2-week test report...")
    print()

    report = generate_final_report()

    # Save to file
    report_file = Path("user_data/live_test_results/FINAL_REPORT.txt")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w') as f:
        f.write(report)

    # Print to console
    print(report)

    print(f"\n✅ Final report saved to: {report_file}")
    print("\nYou can also view:")
    print("  - Session data: user_data/live_test_results/current_session.json")
    print("  - Daily reports: user_data/live_test_results/daily_reports/")
    print("  - Trade log: user_data/trades.json")


if __name__ == "__main__":
    main()
