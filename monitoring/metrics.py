"""
Performance Metrics Module

Calculates key trading performance metrics:
- Sharpe Ratio
- Maximum Drawdown
- Profit Factor
- Win Rate
- Calmar Ratio
- Sortino Ratio

Author: Claude Code
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Calculate trading performance metrics"""

    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize PerformanceMetrics

        Args:
            risk_free_rate: Annual risk-free rate (default: 0.02 = 2%)
        """
        self.risk_free_rate = risk_free_rate

    @staticmethod
    def calculate_sharpe_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 365
    ) -> float:
        """
        Calculate Sharpe Ratio

        Formula: (Mean Return - Risk Free Rate) / Std Dev of Returns

        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of periods in a year (365 for daily, 252 for trading days)

        Returns:
            Sharpe Ratio (annualized)

        Interpretation:
            < 0: Strategy loses money
            0-1: Subpar
            1-2: Good
            2-3: Very good
            > 3: Excellent (rare)
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0

        # Annualize return and volatility
        mean_return = returns.mean() * periods_per_year
        std_return = returns.std() * np.sqrt(periods_per_year)

        sharpe = (mean_return - risk_free_rate) / std_return

        logger.info(
            f"Sharpe Ratio: {sharpe:.2f} "
            f"(Return: {mean_return*100:.2f}%, Volatility: {std_return*100:.2f}%)"
        )

        return sharpe

    @staticmethod
    def calculate_sortino_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 365
    ) -> float:
        """
        Calculate Sortino Ratio (similar to Sharpe but only penalizes downside volatility)

        Formula: (Mean Return - Risk Free Rate) / Downside Deviation

        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of periods in a year

        Returns:
            Sortino Ratio (annualized)
        """
        if len(returns) == 0:
            return 0

        # Calculate downside deviation (only negative returns)
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0:
            return np.inf  # No downside risk

        # Annualize
        mean_return = returns.mean() * periods_per_year
        downside_std = downside_returns.std() * np.sqrt(periods_per_year)

        if downside_std == 0:
            return np.inf

        sortino = (mean_return - risk_free_rate) / downside_std

        logger.info(
            f"Sortino Ratio: {sortino:.2f} "
            f"(Downside Vol: {downside_std*100:.2f}%)"
        )

        return sortino

    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> Dict[str, float]:
        """
        Calculate maximum drawdown

        Args:
            equity_curve: Series of equity values over time

        Returns:
            Dictionary with max_drawdown, max_drawdown_pct, duration
        """
        if len(equity_curve) == 0:
            return {'max_drawdown': 0, 'max_drawdown_pct': 0, 'duration': 0}

        # Calculate running maximum
        running_max = equity_curve.expanding().max()

        # Calculate drawdown
        drawdown = equity_curve - running_max
        drawdown_pct = drawdown / running_max

        # Find maximum drawdown
        max_dd = drawdown.min()
        max_dd_pct = drawdown_pct.min()

        # Find drawdown duration
        is_drawdown = drawdown < 0
        drawdown_periods = is_drawdown.astype(int).groupby(
            (is_drawdown != is_drawdown.shift()).cumsum()
        ).sum()
        max_duration = drawdown_periods.max() if len(drawdown_periods) > 0 else 0

        result = {
            'max_drawdown': abs(max_dd),
            'max_drawdown_pct': abs(max_dd_pct),
            'duration': int(max_duration)
        }

        logger.info(
            f"Max Drawdown: ${result['max_drawdown']:,.2f} "
            f"({result['max_drawdown_pct']*100:.2f}%), "
            f"Duration: {result['duration']} periods"
        )

        return result

    @staticmethod
    def calculate_win_rate(trades: List[Dict]) -> Dict[str, float]:
        """
        Calculate win rate and related statistics

        Args:
            trades: List of trade dictionaries with 'profit_loss' key

        Returns:
            Dictionary with win_rate, total_trades, winning_trades, losing_trades
        """
        if not trades:
            return {
                'win_rate': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0
            }

        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.get('profit_loss', 0) > 0)
        losing_trades = total_trades - winning_trades

        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        result = {
            'win_rate': win_rate,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades
        }

        logger.info(
            f"Win Rate: {win_rate*100:.2f}% "
            f"({winning_trades}W / {losing_trades}L / {total_trades}T)"
        )

        return result

    @staticmethod
    def calculate_profit_factor(trades: List[Dict]) -> float:
        """
        Calculate profit factor

        Formula: Gross Profit / Gross Loss

        Args:
            trades: List of trade dictionaries with 'profit_loss' key

        Returns:
            Profit factor

        Interpretation:
            < 1.0: Losing strategy
            1.0-1.5: Marginal
            1.5-2.0: Good
            > 2.0: Excellent
        """
        if not trades:
            return 0

        gross_profit = sum(t.get('profit_loss', 0) for t in trades if t.get('profit_loss', 0) > 0)
        gross_loss = abs(sum(t.get('profit_loss', 0) for t in trades if t.get('profit_loss', 0) < 0))

        if gross_loss == 0:
            return np.inf if gross_profit > 0 else 0

        profit_factor = gross_profit / gross_loss

        logger.info(
            f"Profit Factor: {profit_factor:.2f} "
            f"(Gross Profit: ${gross_profit:,.2f}, Gross Loss: ${gross_loss:,.2f})"
        )

        return profit_factor

    @staticmethod
    def calculate_calmar_ratio(
        annual_return: float,
        max_drawdown_pct: float
    ) -> float:
        """
        Calculate Calmar Ratio

        Formula: Annual Return / Maximum Drawdown

        Args:
            annual_return: Annual return (as decimal, e.g., 0.56 for 56%)
            max_drawdown_pct: Maximum drawdown (as decimal, e.g., 0.20 for 20%)

        Returns:
            Calmar Ratio

        Interpretation:
            < 0.5: Poor
            0.5-1.0: Average
            1.0-3.0: Good
            > 3.0: Excellent
        """
        if max_drawdown_pct == 0:
            return np.inf if annual_return > 0 else 0

        calmar = annual_return / max_drawdown_pct

        logger.info(
            f"Calmar Ratio: {calmar:.2f} "
            f"(Return: {annual_return*100:.2f}%, Max DD: {max_drawdown_pct*100:.2f}%)"
        )

        return calmar

    @staticmethod
    def calculate_avg_trade_metrics(trades: List[Dict]) -> Dict[str, float]:
        """
        Calculate average trade metrics

        Args:
            trades: List of trade dictionaries with 'profit_loss' key

        Returns:
            Dictionary with avg_win, avg_loss, avg_trade, risk_reward_ratio
        """
        if not trades:
            return {
                'avg_win': 0,
                'avg_loss': 0,
                'avg_trade': 0,
                'risk_reward_ratio': 0
            }

        wins = [t['profit_loss'] for t in trades if t.get('profit_loss', 0) > 0]
        losses = [abs(t['profit_loss']) for t in trades if t.get('profit_loss', 0) < 0]

        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        avg_trade = np.mean([t.get('profit_loss', 0) for t in trades])

        risk_reward_ratio = avg_win / avg_loss if avg_loss > 0 else 0

        result = {
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_trade': avg_trade,
            'risk_reward_ratio': risk_reward_ratio
        }

        logger.info(
            f"Avg Trade Metrics: "
            f"Avg Win=${avg_win:.2f}, Avg Loss=${avg_loss:.2f}, "
            f"Avg Trade=${avg_trade:.2f}, R:R={risk_reward_ratio:.2f}"
        )

        return result

    def calculate_all_metrics(
        self,
        trades: List[Dict],
        equity_curve: pd.Series,
        returns: Optional[pd.Series] = None
    ) -> Dict:
        """
        Calculate all performance metrics

        Args:
            trades: List of completed trades
            equity_curve: Equity curve over time
            returns: Series of returns (if None, calculated from equity_curve)

        Returns:
            Dictionary with all metrics
        """
        if returns is None and len(equity_curve) > 1:
            returns = equity_curve.pct_change().dropna()

        # Calculate all metrics
        win_rate_metrics = self.calculate_win_rate(trades)
        profit_factor = self.calculate_profit_factor(trades)
        avg_metrics = self.calculate_avg_trade_metrics(trades)
        max_dd_metrics = self.calculate_max_drawdown(equity_curve)

        sharpe = 0
        sortino = 0
        calmar = 0

        if len(returns) > 0:
            sharpe = self.calculate_sharpe_ratio(returns, self.risk_free_rate)
            sortino = self.calculate_sortino_ratio(returns, self.risk_free_rate)

        # Calculate annual return
        if len(equity_curve) > 1:
            total_return = (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0]
            days = (equity_curve.index[-1] - equity_curve.index[0]).days
            annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0

            calmar = self.calculate_calmar_ratio(
                annual_return,
                max_dd_metrics['max_drawdown_pct']
            )
        else:
            annual_return = 0

        # Combine all metrics
        all_metrics = {
            # Win/Loss metrics
            'total_trades': win_rate_metrics['total_trades'],
            'winning_trades': win_rate_metrics['winning_trades'],
            'losing_trades': win_rate_metrics['losing_trades'],
            'win_rate': win_rate_metrics['win_rate'],
            'win_rate_pct': f"{win_rate_metrics['win_rate']*100:.2f}%",

            # Profit metrics
            'profit_factor': profit_factor,
            'avg_win': avg_metrics['avg_win'],
            'avg_loss': avg_metrics['avg_loss'],
            'avg_trade': avg_metrics['avg_trade'],
            'risk_reward_ratio': avg_metrics['risk_reward_ratio'],

            # Risk metrics
            'max_drawdown': max_dd_metrics['max_drawdown'],
            'max_drawdown_pct': max_dd_metrics['max_drawdown_pct'],
            'max_dd_pct_str': f"{max_dd_metrics['max_drawdown_pct']*100:.2f}%",
            'max_dd_duration': max_dd_metrics['duration'],

            # Risk-adjusted returns
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,

            # Return metrics
            'annual_return': annual_return,
            'annual_return_pct': f"{annual_return*100:.2f}%",
            'total_return': equity_curve.iloc[-1] - equity_curve.iloc[0] if len(equity_curve) > 0 else 0,
        }

        return all_metrics


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Performance Metrics Examples")
    print("=" * 60)
    print()

    # Create sample data
    np.random.seed(42)

    # Sample trades
    trades = []
    for i in range(100):
        # 60% win rate
        is_win = np.random.random() < 0.60
        if is_win:
            profit = np.random.uniform(50, 150)
        else:
            profit = -np.random.uniform(30, 100)

        trades.append({'profit_loss': profit})

    # Sample equity curve
    equity = [10000]
    for trade in trades:
        equity.append(equity[-1] + trade['profit_loss'])

    equity_series = pd.Series(
        equity,
        index=pd.date_range('2024-01-01', periods=len(equity), freq='D')
    )

    # Calculate metrics
    metrics_calc = PerformanceMetrics(risk_free_rate=0.02)
    all_metrics = metrics_calc.calculate_all_metrics(trades, equity_series)

    print()
    print("Summary Metrics:")
    print("=" * 60)
    print(f"Total Trades: {all_metrics['total_trades']}")
    print(f"Win Rate: {all_metrics['win_rate_pct']}")
    print(f"Profit Factor: {all_metrics['profit_factor']:.2f}")
    print(f"Avg Win: ${all_metrics['avg_win']:.2f}")
    print(f"Avg Loss: ${all_metrics['avg_loss']:.2f}")
    print(f"Risk:Reward: {all_metrics['risk_reward_ratio']:.2f}")
    print()
    print(f"Max Drawdown: ${all_metrics['max_drawdown']:,.2f} ({all_metrics['max_dd_pct_str']})")
    print(f"Sharpe Ratio: {all_metrics['sharpe_ratio']:.2f}")
    print(f"Sortino Ratio: {all_metrics['sortino_ratio']:.2f}")
    print(f"Calmar Ratio: {all_metrics['calmar_ratio']:.2f}")
    print()
    print(f"Annual Return: {all_metrics['annual_return_pct']}")
    print(f"Total Return: ${all_metrics['total_return']:,.2f}")
