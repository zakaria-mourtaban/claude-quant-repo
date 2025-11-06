"""
Multi-pair backtest to validate strategy across different cryptocurrencies
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from run_simple_backtest import load_data, simulate_backtest, calculate_metrics, MomentumMeanReversion


def main():
    print("\n" + "=" * 80)
    print(" " * 20 + "MULTI-PAIR BACKTEST ANALYSIS")
    print("=" * 80)
    print()

    pairs = ['BTC_USDT', 'ETH_USDT', 'SOL_USDT']
    timeframe = '15m'
    initial_balance = 10000

    # Initialize strategy
    config = {
        'stake_currency': 'USDT',
        'dry_run': True,
        'exchange': {'name': 'binance'}
    }
    strategy = MomentumMeanReversion(config)

    all_results = {}

    for pair in pairs:
        print(f"\n📊 Testing {pair.replace('_', '/')}...")
        print("-" * 80)

        # Load data
        data_file = Path(f'user_data/data/binance/{pair}-{timeframe}.json')

        if not data_file.exists():
            print(f"❌ Data file not found: {data_file}")
            continue

        df = load_data(data_file)
        print(f"✅ Loaded {len(df)} candles")
        print(f"Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")

        # Run backtest
        trades, equity_curve, _ = simulate_backtest(
            strategy, df, initial_balance=initial_balance, stake_amount_pct=0.33
        )

        # Calculate metrics
        metrics = calculate_metrics(trades, equity_curve, initial_balance)

        all_results[pair] = {
            'metrics': metrics,
            'trades_count': len(trades)
        }

        # Print summary for this pair
        print(f"Total Trades:    {metrics['total_trades']}")
        print(f"Win Rate:        {metrics['win_rate']:.1f}%")
        print(f"Total Return:    {metrics['total_profit_pct']:+.2f}%")
        print(f"Profit Factor:   {metrics['profit_factor']:.2f}")
        print(f"Max Drawdown:    {metrics['max_drawdown_pct']:.2f}%")
        print(f"Sharpe Ratio:    {metrics['sharpe_ratio']:.2f}")

    # Summary comparison
    print("\n" + "=" * 80)
    print(" " * 25 + "COMPARISON SUMMARY")
    print("=" * 80)
    print()

    print(f"{'Pair':12} {'Trades':>8} {'Win Rate':>10} {'Return':>10} {'P.Factor':>10} {'Max DD':>10} {'Sharpe':>10}")
    print("-" * 80)

    for pair, results in all_results.items():
        m = results['metrics']
        print(
            f"{pair.replace('_', '/'):12} "
            f"{m['total_trades']:>8} "
            f"{m['win_rate']:>9.1f}% "
            f"{m['total_profit_pct']:>9.2f}% "
            f"{m['profit_factor']:>10.2f} "
            f"{m['max_drawdown_pct']:>9.2f}% "
            f"{m['sharpe_ratio']:>10.2f}"
        )

    # Calculate averages
    avg_win_rate = sum(r['metrics']['win_rate'] for r in all_results.values()) / len(all_results)
    avg_return = sum(r['metrics']['total_profit_pct'] for r in all_results.values()) / len(all_results)
    avg_profit_factor = sum(r['metrics']['profit_factor'] for r in all_results.values()) / len(all_results)
    avg_max_dd = sum(r['metrics']['max_drawdown_pct'] for r in all_results.values()) / len(all_results)
    avg_sharpe = sum(r['metrics']['sharpe_ratio'] for r in all_results.values()) / len(all_results)

    print("-" * 80)
    print(
        f"{'AVERAGE':12} "
        f"{'':>8} "
        f"{avg_win_rate:>9.1f}% "
        f"{avg_return:>9.2f}% "
        f"{avg_profit_factor:>10.2f} "
        f"{avg_max_dd:>9.2f}% "
        f"{avg_sharpe:>10.2f}"
    )

    print("\n" + "=" * 80)
    print("\n✅ Multi-pair backtest complete!")
    print(f"\nAverage Performance Across {len(all_results)} Pairs:")
    print(f"  • Win Rate: {avg_win_rate:.1f}%")
    print(f"  • Return: {avg_return:+.2f}%")
    print(f"  • Profit Factor: {avg_profit_factor:.2f}")
    print(f"  • Max Drawdown: {avg_max_dd:.2f}%")
    print(f"  • Sharpe Ratio: {avg_sharpe:.2f}")

    # Overall assessment
    print("\n🎯 OVERALL ASSESSMENT:")
    print("-" * 80)

    criteria_pass = 0
    total_criteria = 5

    if avg_win_rate > 40:
        print("✅ Average Win Rate > 40%")
        criteria_pass += 1
    else:
        print("❌ Average Win Rate < 40%")

    if avg_return > 0:
        print("✅ Positive Average Return")
        criteria_pass += 1
    else:
        print("❌ Negative Average Return")

    if avg_profit_factor > 1.5:
        print("✅ Average Profit Factor > 1.5")
        criteria_pass += 1
    else:
        print("❌ Average Profit Factor < 1.5")

    if avg_max_dd < 20:
        print("✅ Average Max Drawdown < 20%")
        criteria_pass += 1
    else:
        print("❌ Average Max Drawdown > 20%")

    if avg_sharpe > 1.0:
        print("✅ Average Sharpe Ratio > 1.0")
        criteria_pass += 1
    else:
        print("❌ Average Sharpe Ratio < 1.0")

    print(f"\nScore: {criteria_pass}/{total_criteria} criteria passed")

    if criteria_pass >= 4:
        print("\n✅ Strategy performs consistently well across multiple pairs!")
        print("Recommendation: Proceed to parameter optimization (hyperopt)")
    elif criteria_pass >= 3:
        print("\n⚠️  Strategy shows promise but may need adjustment")
        print("Recommendation: Review and optimize parameters")
    else:
        print("\n❌ Strategy needs significant improvement")
        print("Recommendation: Review entry/exit logic and indicators")

    print("=" * 80)


if __name__ == "__main__":
    main()
