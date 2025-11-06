"""
Simple backtesting script that works offline
Tests the MomentumMeanReversion strategy without requiring exchange API access
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from user_data.strategies.MomentumMeanReversion import MomentumMeanReversion


def load_data(file_path):
    """Load OHLCV data from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)

    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index('date')

    return df


def simulate_backtest(strategy, dataframe, initial_balance=10000, stake_amount_pct=0.33):
    """Simple backtesting simulation"""

    balance = initial_balance
    position = None
    trades = []
    equity_curve = [initial_balance]

    # Populate indicators and signals
    df = strategy.populate_indicators(dataframe.copy(), {})
    df = strategy.populate_entry_trend(df, {})
    df = strategy.populate_exit_trend(df, {})

    for i in range(strategy.startup_candle_count, len(df)):
        current_candle = df.iloc[i]
        current_price = current_candle['close']

        # Check exit signal if we have a position
        if position is not None:
            should_exit = current_candle.get('exit_long', 0) == 1

            # Also check stop loss (simple 5% hard stop)
            if current_price <= position['entry_price'] * 0.95:
                should_exit = True

            if should_exit:
                # Exit position
                profit = (current_price - position['entry_price']) * position['amount']
                balance += position['value'] + profit

                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': current_candle.name,
                    'entry_price': position['entry_price'],
                    'exit_price': current_price,
                    'amount': position['amount'],
                    'profit': profit,
                    'profit_pct': (profit / position['value']) * 100,
                    'duration': (current_candle.name - position['entry_date']).total_seconds() / 3600
                })

                position = None

        # Check entry signal if we don't have a position
        if position is None and current_candle.get('enter_long', 0) == 1:
            # Enter position
            stake_amount = balance * stake_amount_pct
            amount = stake_amount / current_price

            position = {
                'entry_date': current_candle.name,
                'entry_price': current_price,
                'amount': amount,
                'value': stake_amount
            }

            balance -= stake_amount

        # Update equity curve
        current_equity = balance
        if position is not None:
            current_equity += position['amount'] * current_price

        equity_curve.append(current_equity)

    return trades, equity_curve, df


def calculate_metrics(trades, equity_curve, initial_balance):
    """Calculate performance metrics"""

    if not trades:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_profit': 0,
            'total_profit_pct': 0,
            'avg_profit': 0,
            'avg_profit_pct': 0,
            'max_drawdown': 0,
            'max_drawdown_pct': 0,
            'sharpe_ratio': 0,
            'profit_factor': 0
        }

    df_trades = pd.DataFrame(trades)

    # Basic metrics
    total_trades = len(trades)
    winning_trades = len(df_trades[df_trades['profit'] > 0])
    losing_trades = len(df_trades[df_trades['profit'] < 0])
    win_rate = winning_trades / total_trades if total_trades > 0 else 0

    total_profit = df_trades['profit'].sum()
    total_profit_pct = (total_profit / initial_balance) * 100

    avg_profit = df_trades['profit'].mean()
    avg_profit_pct = df_trades['profit_pct'].mean()

    # Profit factor
    gross_profit = df_trades[df_trades['profit'] > 0]['profit'].sum() if winning_trades > 0 else 0
    gross_loss = abs(df_trades[df_trades['profit'] < 0]['profit'].sum()) if losing_trades > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf

    # Maximum drawdown
    equity_series = pd.Series(equity_curve)
    running_max = equity_series.expanding().max()
    drawdown = equity_series - running_max
    max_drawdown = abs(drawdown.min())
    max_drawdown_pct = (max_drawdown / initial_balance) * 100

    # Sharpe ratio (simplified)
    returns = df_trades['profit_pct'].values / 100
    sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 1 and np.std(returns) > 0 else 0

    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate * 100,
        'total_profit': total_profit,
        'total_profit_pct': total_profit_pct,
        'avg_profit': avg_profit,
        'avg_profit_pct': avg_profit_pct,
        'max_drawdown': max_drawdown,
        'max_drawdown_pct': max_drawdown_pct,
        'sharpe_ratio': sharpe_ratio,
        'profit_factor': profit_factor
    }


def print_results(metrics, trades):
    """Print backtest results"""

    print("\n" + "=" * 80)
    print(" " * 25 + "BACKTEST RESULTS")
    print("=" * 80)
    print()

    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Total Trades:        {metrics['total_trades']}")
    print(f"Winning Trades:      {metrics['winning_trades']}")
    print(f"Losing Trades:       {metrics['losing_trades']}")
    print(f"Win Rate:            {metrics['win_rate']:.2f}%")
    print()

    print("💰 PROFITABILITY")
    print("-" * 80)
    print(f"Total Profit:        ${metrics['total_profit']:.2f} ({metrics['total_profit_pct']:+.2f}%)")
    print(f"Average Profit:      ${metrics['avg_profit']:.2f} ({metrics['avg_profit_pct']:+.2f}%)")
    print(f"Profit Factor:       {metrics['profit_factor']:.2f}")
    print()

    print("⚠️  RISK METRICS")
    print("-" * 80)
    print(f"Max Drawdown:        ${metrics['max_drawdown']:.2f} ({metrics['max_drawdown_pct']:.2f}%)")
    print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:.2f}")
    print()

    if trades:
        print("📋 RECENT TRADES (Last 10)")
        print("-" * 80)
        recent_trades = pd.DataFrame(trades).tail(10)
        for _, trade in recent_trades.iterrows():
            status = "✅" if trade['profit'] > 0 else "❌"
            print(
                f"{status} Entry: {trade['entry_date'].strftime('%Y-%m-%d %H:%M')} | "
                f"Exit: {trade['exit_date'].strftime('%Y-%m-%d %H:%M')} | "
                f"P/L: ${trade['profit']:+.2f} ({trade['profit_pct']:+.2f}%) | "
                f"Duration: {trade['duration']:.1f}h"
            )

    print()
    print("=" * 80)

    # Success criteria evaluation
    print()
    print("🎯 SUCCESS CRITERIA EVALUATION")
    print("=" * 80)

    criteria = [
        ("Total Trades > 10", metrics['total_trades'] > 10, metrics['total_trades']),
        ("Win Rate > 40%", metrics['win_rate'] > 40, f"{metrics['win_rate']:.1f}%"),
        ("Profit Factor > 1.5", metrics['profit_factor'] > 1.5, f"{metrics['profit_factor']:.2f}"),
        ("Max Drawdown < 20%", metrics['max_drawdown_pct'] < 20, f"{metrics['max_drawdown_pct']:.1f}%"),
        ("Positive Return", metrics['total_profit_pct'] > 0, f"{metrics['total_profit_pct']:+.2f}%"),
    ]

    passed = 0
    for criterion, result, value in criteria:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:9} | {criterion:25} | Current: {value}")
        if result:
            passed += 1

    print("-" * 80)
    print(f"Score: {passed}/{len(criteria)} criteria passed")
    print()

    if passed >= 4:
        print("✅ Strategy showing good performance! Continue with optimization.")
    elif passed >= 3:
        print("⚠️  Strategy shows potential. Consider parameter optimization.")
    else:
        print("❌ Strategy needs improvement. Review entry/exit logic.")

    print("=" * 80)


def main():
    print("\n🚀 Running Simple Backtest on MomentumMeanReversion Strategy...")
    print("=" * 80)

    # Load data
    data_file = Path('user_data/data/binance/BTC_USDT-15m.json')

    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        print("Run: python scripts/generate_synthetic_data.py")
        return

    print(f"Loading data from: {data_file}")
    df = load_data(data_file)
    print(f"✅ Loaded {len(df)} candles")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print()

    # Initialize strategy with minimal config
    config = {
        'stake_currency': 'USDT',
        'dry_run': True,
        'exchange': {'name': 'binance'}
    }
    strategy = MomentumMeanReversion(config)
    print(f"✅ Strategy initialized: {strategy.__class__.__name__}")
    print(f"Timeframe: {strategy.timeframe}")
    print(f"Startup candles: {strategy.startup_candle_count}")
    print()

    # Run backtest
    print("Running backtest simulation...")
    initial_balance = 10000
    trades, equity_curve, df_with_signals = simulate_backtest(
        strategy, df, initial_balance=initial_balance, stake_amount_pct=0.33
    )

    # Calculate metrics
    metrics = calculate_metrics(trades, equity_curve, initial_balance)

    # Print results
    print_results(metrics, trades)

    # Save results
    results_file = Path('user_data/backtest_results/simple_backtest_results.json')
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w') as f:
        json.dump({
            'metrics': metrics,
            'trades': [
                {
                    'entry_date': str(t['entry_date']),
                    'exit_date': str(t['exit_date']),
                    'entry_price': float(t['entry_price']),
                    'exit_price': float(t['exit_price']),
                    'profit': float(t['profit']),
                    'profit_pct': float(t['profit_pct']),
                    'duration': float(t['duration'])
                }
                for t in trades
            ]
        }, f, indent=2)

    print(f"\n💾 Results saved to: {results_file}")


if __name__ == "__main__":
    main()
