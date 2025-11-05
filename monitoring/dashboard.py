"""
Simple Performance Dashboard for Crypto Trading Bot

Displays real-time performance metrics using a simple text-based interface
For a full web-based dashboard, install Streamlit and run the Streamlit version

Author: Claude Code
Version: 1.0.0
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from monitoring.metrics import PerformanceMetrics


class TradingDashboard:
    """Simple text-based trading dashboard"""

    def __init__(self, db_path: str = "user_data/tradesv3.sqlite"):
        """
        Initialize dashboard

        Args:
            db_path: Path to Freqtrade database
        """
        self.db_path = db_path
        self.metrics_calc = PerformanceMetrics()

    def load_trades(self, days: int = 30) -> pd.DataFrame:
        """
        Load trades from Freqtrade database

        Args:
            days: Number of days of history to load

        Returns:
            DataFrame of trades
        """
        if not os.path.exists(self.db_path):
            print(f"⚠️  Database not found: {self.db_path}")
            return pd.DataFrame()

        conn = sqlite3.connect(self.db_path)

        # Calculate date threshold
        date_threshold = datetime.now() - timedelta(days=days)
        date_str = date_threshold.strftime('%Y-%m-%d %H:%M:%S')

        query = f"""
        SELECT
            id,
            pair,
            open_date,
            close_date,
            open_rate,
            close_rate,
            amount,
            stake_amount,
            close_profit,
            close_profit_abs,
            trade_duration,
            exit_reason
        FROM trades
        WHERE close_date >= '{date_str}'
        AND is_open = 0
        ORDER BY close_date DESC
        """

        try:
            df = pd.read_sql_query(query, conn)
            conn.close()

            if len(df) > 0:
                df['close_date'] = pd.to_datetime(df['close_date'])
                df['open_date'] = pd.to_datetime(df['open_date'])

            return df

        except Exception as e:
            print(f"Error loading trades: {e}")
            conn.close()
            return pd.DataFrame()

    def calculate_equity_curve(self, trades_df: pd.DataFrame, initial_balance: float = 10000) -> pd.Series:
        """
        Calculate equity curve from trades

        Args:
            trades_df: DataFrame of trades
            initial_balance: Starting balance

        Returns:
            Series of equity over time
        """
        if len(trades_df) == 0:
            return pd.Series([initial_balance], index=[datetime.now()])

        # Sort by close date
        trades_df = trades_df.sort_values('close_date')

        # Calculate cumulative profit
        equity = [initial_balance]
        for profit in trades_df['close_profit_abs']:
            equity.append(equity[-1] + profit)

        # Create series
        dates = [trades_df['close_date'].iloc[0]] + list(trades_df['close_date'])
        equity_series = pd.Series(equity, index=dates)

        return equity_series

    def display_dashboard(self, days: int = 30):
        """
        Display trading dashboard

        Args:
            days: Number of days of history to show
        """
        print()
        print("=" * 80)
        print(" " * 25 + "CRYPTO TRADING BOT DASHBOARD")
        print("=" * 80)
        print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Period: Last {days} days")
        print("=" * 80)
        print()

        # Load trades
        trades_df = self.load_trades(days)

        if len(trades_df) == 0:
            print("⚠️  No trades found in the specified period.")
            print()
            print("Possible reasons:")
            print("  1. Bot hasn't completed any trades yet")
            print("  2. Database path is incorrect")
            print("  3. Trades are older than the specified period")
            print()
            return

        # Convert to list of dicts for metrics calculation
        trades_list = []
        for _, row in trades_df.iterrows():
            trades_list.append({'profit_loss': row['close_profit_abs']})

        # Calculate equity curve
        equity_curve = self.calculate_equity_curve(trades_df)

        # Calculate all metrics
        metrics = self.metrics_calc.calculate_all_metrics(trades_list, equity_curve)

        # Display Overview
        print("📊 OVERVIEW")
        print("-" * 80)
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Winning Trades: {metrics['winning_trades']}")
        print(f"Losing Trades: {metrics['losing_trades']}")
        print(f"Win Rate: {metrics['win_rate_pct']}")
        print()

        # Display Profitability
        print("💰 PROFITABILITY")
        print("-" * 80)
        total_profit = equity_curve.iloc[-1] - equity_curve.iloc[0]
        profit_pct = (total_profit / equity_curve.iloc[0]) * 100
        print(f"Total Profit/Loss: ${total_profit:,.2f} ({profit_pct:+.2f}%)")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"Avg Winning Trade: ${metrics['avg_win']:.2f}")
        print(f"Avg Losing Trade: ${metrics['avg_loss']:.2f}")
        print(f"Avg Trade: ${metrics['avg_trade']:.2f}")
        print(f"Risk:Reward Ratio: {metrics['risk_reward_ratio']:.2f}")
        print()

        # Display Risk Metrics
        print("⚠️  RISK METRICS")
        print("-" * 80)
        print(f"Maximum Drawdown: ${metrics['max_drawdown']:,.2f} ({metrics['max_dd_pct_str']})")
        print(f"Max DD Duration: {metrics['max_dd_duration']} periods")
        print()

        # Display Risk-Adjusted Returns
        print("📈 RISK-ADJUSTED RETURNS")
        print("-" * 80)
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}", end="")
        self._print_rating(metrics['sharpe_ratio'], [0, 1, 2, 3])
        print(f"Sortino Ratio: {metrics['sortino_ratio']:.2f}", end="")
        self._print_rating(metrics['sortino_ratio'], [0, 1, 2, 3])
        print(f"Calmar Ratio: {metrics['calmar_ratio']:.2f}", end="")
        self._print_rating(metrics['calmar_ratio'], [0, 0.5, 1, 3])
        print()

        # Display Recent Trades
        print("📋 RECENT TRADES (Last 10)")
        print("-" * 80)
        recent_trades = trades_df.head(10)
        for _, trade in recent_trades.iterrows():
            profit_str = f"${trade['close_profit_abs']:+.2f}"
            profit_pct = f"{trade['close_profit']*100:+.2f}%"
            duration = trade['trade_duration']

            status = "✅" if trade['close_profit_abs'] > 0 else "❌"

            print(
                f"{status} {trade['pair']:12} | "
                f"{trade['close_date'].strftime('%Y-%m-%d %H:%M')} | "
                f"P/L: {profit_str:>10} ({profit_pct:>7}) | "
                f"Duration: {duration:>3} min | "
                f"Exit: {trade['exit_reason']}"
            )

        print()
        print("=" * 80)

        # Display Performance Summary
        self._display_performance_summary(metrics)

    def _print_rating(self, value: float, thresholds: list):
        """Print rating based on value and thresholds"""
        if value >= thresholds[3]:
            print("  ⭐⭐⭐ (Excellent)")
        elif value >= thresholds[2]:
            print("  ⭐⭐ (Good)")
        elif value >= thresholds[1]:
            print("  ⭐ (Fair)")
        else:
            print("  ❌ (Poor)")

    def _display_performance_summary(self, metrics: dict):
        """Display go/no-go decision based on success criteria"""
        print()
        print("🎯 SUCCESS CRITERIA EVALUATION")
        print("=" * 80)

        criteria = [
            ("Sharpe Ratio > 1.5", metrics['sharpe_ratio'] > 1.5, metrics['sharpe_ratio']),
            ("Max Drawdown < 20%", metrics['max_drawdown_pct'] < 0.20, metrics['max_drawdown_pct'] * 100),
            ("Profit Factor > 1.5", metrics['profit_factor'] > 1.5, metrics['profit_factor']),
            ("Win Rate > 40%", metrics['win_rate'] > 0.40, metrics['win_rate'] * 100),
        ]

        passed = 0
        for criterion, result, value in criteria:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status:9} | {criterion:25} | Current: {value:.2f}")
            if result:
                passed += 1

        print("-" * 80)
        print(f"Score: {passed}/4 criteria passed")
        print()

        if passed >= 3:
            print("✅ Strategy performing well! Consider continuing demo trading.")
        elif passed >= 2:
            print("⚠️  Strategy shows potential. Monitor closely and consider adjustments.")
        else:
            print("❌ Strategy needs significant improvement before real money deployment.")

        print("=" * 80)


def main():
    """Run dashboard"""
    import argparse

    parser = argparse.ArgumentParser(description='Crypto Trading Bot Dashboard')
    parser.add_argument('--days', type=int, default=30, help='Number of days of history to show')
    parser.add_argument('--db', type=str, default='user_data/tradesv3.sqlite', help='Path to database')

    args = parser.parse_args()

    dashboard = TradingDashboard(db_path=args.db)
    dashboard.display_dashboard(days=args.days)


if __name__ == "__main__":
    main()
