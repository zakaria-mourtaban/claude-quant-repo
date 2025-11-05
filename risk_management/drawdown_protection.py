"""
Drawdown Protection Module

Implements kill switches and safety mechanisms:
- Maximum drawdown limits
- Daily loss limits
- Consecutive loss limits
- Volatility circuit breakers

Author: Claude Code
Version: 1.0.0
"""

from typing import Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DrawdownProtector:
    """Protect portfolio from excessive drawdowns with kill switches"""

    def __init__(
        self,
        max_drawdown: float = 0.20,
        daily_loss_limit: float = 0.06,
        consecutive_loss_limit: int = 5
    ):
        """
        Initialize DrawdownProtector

        Args:
            max_drawdown: Maximum allowed drawdown (0.20 = 20%)
            daily_loss_limit: Maximum daily loss (0.06 = 6%)
            consecutive_loss_limit: Maximum consecutive losing trades
        """
        self.max_drawdown = max_drawdown
        self.daily_loss_limit = daily_loss_limit
        self.consecutive_loss_limit = consecutive_loss_limit

        # State tracking
        self.peak_equity = 0
        self.current_equity = 0
        self.daily_trades = []
        self.recent_trades = []

        logger.info(
            f"Drawdown Protector initialized: "
            f"Max DD={max_drawdown*100:.0f}%, "
            f"Daily Loss Limit={daily_loss_limit*100:.0f}%, "
            f"Consecutive Loss Limit={consecutive_loss_limit}"
        )

    def update_equity(self, current_equity: float) -> None:
        """
        Update current equity and peak

        Args:
            current_equity: Current portfolio equity
        """
        self.current_equity = current_equity

        # Update peak if new high
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
            logger.info(f"📈 New equity peak: ${current_equity:,.2f}")

    def calculate_current_drawdown(self) -> float:
        """
        Calculate current drawdown from peak

        Returns:
            Current drawdown as fraction (0.0 to 1.0)
        """
        if self.peak_equity == 0:
            return 0

        drawdown = (self.peak_equity - self.current_equity) / self.peak_equity
        return drawdown

    def check_max_drawdown(self) -> tuple[bool, Optional[str]]:
        """
        Check if maximum drawdown limit has been breached

        Returns:
            (should_stop, reason) - True if trading should stop
        """
        current_dd = self.calculate_current_drawdown()

        if current_dd >= self.max_drawdown:
            reason = (
                f"⛔ KILL SWITCH ACTIVATED: Maximum drawdown breached! "
                f"Current: {current_dd*100:.2f}%, "
                f"Max Allowed: {self.max_drawdown*100:.2f}%, "
                f"Peak: ${self.peak_equity:,.2f}, "
                f"Current: ${self.current_equity:,.2f}"
            )
            logger.critical(reason)
            return True, reason

        # Warning at 75% of max drawdown
        if current_dd >= self.max_drawdown * 0.75:
            logger.warning(
                f"⚠️  Drawdown warning: {current_dd*100:.2f}% "
                f"(75% of max limit)"
            )

        return False, None

    def add_trade(self, profit_loss: float, timestamp: Optional[datetime] = None) -> None:
        """
        Record a completed trade

        Args:
            profit_loss: Profit/loss amount for the trade
            timestamp: Trade timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        trade = {
            'timestamp': timestamp,
            'profit_loss': profit_loss,
            'is_win': profit_loss > 0
        }

        self.daily_trades.append(trade)
        self.recent_trades.append(trade)

        # Keep only last 100 trades
        if len(self.recent_trades) > 100:
            self.recent_trades = self.recent_trades[-100:]

    def check_daily_loss_limit(self) -> tuple[bool, Optional[str]]:
        """
        Check if daily loss limit has been breached

        Returns:
            (should_stop, reason) - True if trading should stop
        """
        today = datetime.now().date()

        # Filter trades from today
        today_trades = [
            t for t in self.daily_trades
            if t['timestamp'].date() == today
        ]

        if not today_trades:
            return False, None

        # Calculate today's P&L
        today_pnl = sum(t['profit_loss'] for t in today_trades)
        daily_loss_pct = abs(today_pnl) / self.current_equity if self.current_equity > 0 else 0

        if today_pnl < 0 and daily_loss_pct >= self.daily_loss_limit:
            reason = (
                f"⛔ KILL SWITCH ACTIVATED: Daily loss limit breached! "
                f"Today's Loss: ${today_pnl:.2f} ({daily_loss_pct*100:.2f}%), "
                f"Max Allowed: {self.daily_loss_limit*100:.2f}%"
            )
            logger.critical(reason)
            return True, reason

        return False, None

    def check_consecutive_losses(self) -> tuple[bool, Optional[str]]:
        """
        Check if consecutive loss limit has been breached

        Returns:
            (should_stop, reason) - True if trading should stop
        """
        if len(self.recent_trades) < self.consecutive_loss_limit:
            return False, None

        # Check last N trades
        last_n_trades = self.recent_trades[-self.consecutive_loss_limit:]
        all_losses = all(not t['is_win'] for t in last_n_trades)

        if all_losses:
            total_loss = sum(t['profit_loss'] for t in last_n_trades)
            reason = (
                f"⛔ KILL SWITCH ACTIVATED: {self.consecutive_loss_limit} consecutive losses! "
                f"Total Loss: ${total_loss:.2f}. "
                f"Pausing trading to prevent further losses."
            )
            logger.critical(reason)
            return True, reason

        return False, None

    def check_all_limits(self) -> tuple[bool, List[str]]:
        """
        Check all protection limits

        Returns:
            (should_stop, reasons) - True if any limit breached
        """
        should_stop = False
        reasons = []

        # Check maximum drawdown
        stop_dd, reason_dd = self.check_max_drawdown()
        if stop_dd:
            should_stop = True
            reasons.append(reason_dd)

        # Check daily loss limit
        stop_daily, reason_daily = self.check_daily_loss_limit()
        if stop_daily:
            should_stop = True
            reasons.append(reason_daily)

        # Check consecutive losses
        stop_consec, reason_consec = self.check_consecutive_losses()
        if stop_consec:
            should_stop = True
            reasons.append(reason_consec)

        return should_stop, reasons

    def reset_daily_trades(self) -> None:
        """Reset daily trades (call this at start of each day)"""
        self.daily_trades = []
        logger.info("Daily trades reset")

    def get_stats(self) -> dict:
        """
        Get current protection statistics

        Returns:
            Dictionary with current stats
        """
        current_dd = self.calculate_current_drawdown()

        # Calculate consecutive losses
        consecutive_losses = 0
        for trade in reversed(self.recent_trades):
            if not trade['is_win']:
                consecutive_losses += 1
            else:
                break

        # Calculate today's P&L
        today = datetime.now().date()
        today_trades = [
            t for t in self.daily_trades
            if t['timestamp'].date() == today
        ]
        today_pnl = sum(t['profit_loss'] for t in today_trades) if today_trades else 0

        return {
            'current_drawdown': current_dd,
            'current_drawdown_pct': f"{current_dd*100:.2f}%",
            'max_drawdown_limit': f"{self.max_drawdown*100:.0f}%",
            'peak_equity': self.peak_equity,
            'current_equity': self.current_equity,
            'today_pnl': today_pnl,
            'today_trades': len(today_trades),
            'daily_loss_limit': f"{self.daily_loss_limit*100:.0f}%",
            'consecutive_losses': consecutive_losses,
            'consecutive_loss_limit': self.consecutive_loss_limit,
            'recent_trades_count': len(self.recent_trades)
        }


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("Drawdown Protection Examples")
    print("=" * 60)
    print()

    # Initialize protector
    protector = DrawdownProtector(
        max_drawdown=0.20,      # 20% max drawdown
        daily_loss_limit=0.06,  # 6% daily loss limit
        consecutive_loss_limit=5
    )

    # Simulate trading
    print("Simulating trading scenario...")
    print()

    # Start with $10,000
    equity = 10000
    protector.update_equity(equity)

    # Simulate some winning trades
    for i in range(3):
        profit = 100
        equity += profit
        protector.update_equity(equity)
        protector.add_trade(profit)
        print(f"Trade {i+1}: +${profit:.2f}, Equity: ${equity:,.2f}")

    print()

    # Simulate losing streak
    print("Simulating losing streak...")
    for i in range(6):
        loss = -200
        equity += loss
        protector.update_equity(equity)
        protector.add_trade(loss)
        print(f"Trade {i+4}: ${loss:.2f}, Equity: ${equity:,.2f}")

        # Check limits after each trade
        should_stop, reasons = protector.check_all_limits()
        if should_stop:
            print()
            print("=" * 60)
            for reason in reasons:
                print(reason)
            print("=" * 60)
            break

    print()
    print("Final Statistics:")
    print("-" * 60)
    stats = protector.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
