"""
Position Sizing Module

Implements various position sizing strategies:
- Fixed percentage risk
- Kelly Criterion (fractional)
- ATR-based position sizing
- Portfolio heat calculation

Author: Claude Code
Version: 1.0.0
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PositionSizer:
    """Calculate position sizes based on various risk management strategies"""

    def __init__(self, portfolio_value: float, risk_per_trade: float = 0.02):
        """
        Initialize PositionSizer

        Args:
            portfolio_value: Total portfolio value in base currency (USDT)
            risk_per_trade: Fraction of portfolio to risk per trade (default: 0.02 = 2%)
        """
        self.portfolio_value = portfolio_value
        self.risk_per_trade = risk_per_trade

    def fixed_risk_position_size(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_amount: Optional[float] = None
    ) -> float:
        """
        Calculate position size using fixed risk method

        Args:
            entry_price: Entry price for the trade
            stop_loss_price: Stop loss price
            risk_amount: Amount to risk (if None, uses self.risk_per_trade * portfolio_value)

        Returns:
            Position size in base asset units

        Example:
            Portfolio: $10,000
            Risk per trade: 2% = $200
            Entry: $100
            Stop loss: $95 (5% away)
            Position size: $200 / ($100 - $95) = $200 / $5 = 40 units
        """
        if risk_amount is None:
            risk_amount = self.portfolio_value * self.risk_per_trade

        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss_price)

        if risk_per_unit == 0:
            logger.error("Stop loss price equals entry price. Cannot calculate position size.")
            return 0

        # Calculate position size
        position_size = risk_amount / risk_per_unit

        # Convert to quote currency (USDT) amount
        position_value = position_size * entry_price

        logger.info(
            f"Fixed Risk Position Sizing: "
            f"Risk=${risk_amount:.2f}, Entry=${entry_price:.2f}, "
            f"Stop=${stop_loss_price:.2f}, Position={position_size:.4f} units "
            f"(${position_value:.2f})"
        )

        return position_size

    def kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        kelly_fraction: float = 0.1
    ) -> float:
        """
        Calculate position size using Kelly Criterion

        Formula: f* = (bp - q) / b
        - f* = fraction of capital to bet
        - b = odds received (reward/risk ratio)
        - p = probability of winning
        - q = probability of losing (1 - p)

        Args:
            win_rate: Historical win rate (0.0 to 1.0)
            avg_win: Average profit per winning trade (percentage)
            avg_loss: Average loss per losing trade (percentage, positive number)
            kelly_fraction: Fraction of Kelly to use (default: 0.1 for 1/10th Kelly)

        Returns:
            Fraction of portfolio to risk (0.0 to 1.0)

        Example:
            Win rate: 55%
            Avg win: 3%
            Avg loss: 2%
            b = 3/2 = 1.5 (reward/risk ratio)
            f* = (1.5 * 0.55 - 0.45) / 1.5 = 0.25 (25% Kelly)
            With 1/10th Kelly: 2.5% position size
        """
        if avg_loss == 0:
            logger.error("Average loss cannot be zero.")
            return 0

        # Odds (reward/risk ratio)
        b = avg_win / avg_loss

        # Probability of losing
        q = 1 - win_rate

        # Kelly formula
        kelly_pct = (b * win_rate - q) / b

        # Apply Kelly fraction (reduce Kelly to fractional)
        fractional_kelly = kelly_pct * kelly_fraction

        # Ensure non-negative and capped at 20% (safety limit)
        fractional_kelly = max(0, min(fractional_kelly, 0.20))

        logger.info(
            f"Kelly Criterion: Win Rate={win_rate*100:.1f}%, "
            f"Avg Win={avg_win*100:.1f}%, Avg Loss={avg_loss*100:.1f}%, "
            f"Full Kelly={kelly_pct*100:.1f}%, "
            f"Fractional Kelly ({kelly_fraction*100:.0f}%)={fractional_kelly*100:.1f}%"
        )

        return fractional_kelly

    def atr_based_position_size(
        self,
        entry_price: float,
        atr: float,
        atr_multiplier: float = 2.0,
        risk_amount: Optional[float] = None
    ) -> float:
        """
        Calculate position size using ATR (Average True Range)

        Stop loss is set at ATR_multiplier * ATR below entry price

        Args:
            entry_price: Entry price for the trade
            atr: Current ATR value
            atr_multiplier: Number of ATRs for stop loss distance (default: 2.0)
            risk_amount: Amount to risk (if None, uses self.risk_per_trade * portfolio_value)

        Returns:
            Position size in base asset units

        Example:
            Entry: $100
            ATR: $3
            Multiplier: 2
            Stop loss: $100 - (2 * $3) = $94
            Risk: $200
            Position size: $200 / $6 = 33.33 units
        """
        if risk_amount is None:
            risk_amount = self.portfolio_value * self.risk_per_trade

        # Calculate stop loss distance
        stop_distance = atr * atr_multiplier

        # Calculate position size
        position_size = risk_amount / stop_distance

        # Convert to quote currency amount
        position_value = position_size * entry_price

        logger.info(
            f"ATR-Based Position Sizing: "
            f"Risk=${risk_amount:.2f}, Entry=${entry_price:.2f}, "
            f"ATR=${atr:.2f}, Multiplier={atr_multiplier}x, "
            f"Position={position_size:.4f} units (${position_value:.2f})"
        )

        return position_size

    def calculate_portfolio_heat(
        self,
        open_positions: list[dict]
    ) -> float:
        """
        Calculate total portfolio heat (total % at risk across all positions)

        Args:
            open_positions: List of dicts with 'risk_amount' key

        Returns:
            Portfolio heat as fraction (0.0 to 1.0)

        Example:
            3 positions, each risking $200
            Total risk: $600
            Portfolio: $10,000
            Portfolio heat: $600 / $10,000 = 6%
        """
        total_risk = sum(pos.get('risk_amount', 0) for pos in open_positions)
        portfolio_heat = total_risk / self.portfolio_value

        logger.info(
            f"Portfolio Heat: {len(open_positions)} positions, "
            f"Total Risk=${total_risk:.2f}, "
            f"Heat={portfolio_heat*100:.2f}%"
        )

        return portfolio_heat

    def is_portfolio_heat_acceptable(
        self,
        open_positions: list[dict],
        max_heat: float = 0.10
    ) -> bool:
        """
        Check if portfolio heat is within acceptable limits

        Args:
            open_positions: List of open positions
            max_heat: Maximum acceptable portfolio heat (default: 0.10 = 10%)

        Returns:
            True if heat is acceptable, False otherwise
        """
        current_heat = self.calculate_portfolio_heat(open_positions)

        if current_heat > max_heat:
            logger.warning(
                f"⚠️  Portfolio heat too high! "
                f"Current: {current_heat*100:.2f}%, Max: {max_heat*100:.2f}%"
            )
            return False

        return True


def calculate_stake_amount(
    portfolio_value: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss_price: float
) -> float:
    """
    Convenience function to calculate stake amount (position value in quote currency)

    Args:
        portfolio_value: Total portfolio value
        risk_per_trade: Risk per trade as fraction (e.g., 0.02 = 2%)
        entry_price: Entry price
        stop_loss_price: Stop loss price

    Returns:
        Stake amount in quote currency (e.g., USDT)
    """
    sizer = PositionSizer(portfolio_value, risk_per_trade)
    position_size = sizer.fixed_risk_position_size(entry_price, stop_loss_price)
    stake_amount = position_size * entry_price
    return stake_amount


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize position sizer
    portfolio = 10000  # $10,000 USDT
    risk_pct = 0.02    # 2% per trade
    sizer = PositionSizer(portfolio, risk_pct)

    print("=" * 60)
    print("Position Sizing Examples")
    print("=" * 60)
    print(f"Portfolio: ${portfolio:,.2f}")
    print(f"Risk per trade: {risk_pct*100:.1f}%")
    print()

    # Example 1: Fixed risk position sizing
    print("Example 1: Fixed Risk Position Sizing")
    print("-" * 60)
    entry = 100
    stop = 95
    size = sizer.fixed_risk_position_size(entry, stop)
    print(f"Position size: {size:.4f} units (${size*entry:.2f})")
    print()

    # Example 2: Kelly Criterion
    print("Example 2: Kelly Criterion")
    print("-" * 60)
    kelly_fraction = sizer.kelly_criterion(
        win_rate=0.55,
        avg_win=0.03,
        avg_loss=0.02,
        kelly_fraction=0.1
    )
    print(f"Recommended position size: {kelly_fraction*100:.2f}% of portfolio")
    print()

    # Example 3: ATR-based position sizing
    print("Example 3: ATR-Based Position Sizing")
    print("-" * 60)
    entry = 100
    atr = 3
    size = sizer.atr_based_position_size(entry, atr, atr_multiplier=2.0)
    print(f"Position size: {size:.4f} units (${size*entry:.2f})")
    print()

    # Example 4: Portfolio heat
    print("Example 4: Portfolio Heat")
    print("-" * 60)
    open_positions = [
        {'risk_amount': 200},
        {'risk_amount': 200},
        {'risk_amount': 200},
    ]
    heat = sizer.calculate_portfolio_heat(open_positions)
    is_acceptable = sizer.is_portfolio_heat_acceptable(open_positions, max_heat=0.10)
    print(f"Is heat acceptable (< 10%)? {is_acceptable}")
    print()
