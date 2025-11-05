"""
Unit Tests for Risk Management Modules

Tests position sizing, drawdown protection, and portfolio heat calculations

Author: Claude Code
Version: 1.0.0
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from risk_management.position_sizing import PositionSizer
from risk_management.drawdown_protection import DrawdownProtector


class TestPositionSizer:
    """Test position sizing calculations"""

    @pytest.fixture
    def sizer(self):
        """Create PositionSizer instance"""
        return PositionSizer(portfolio_value=10000, risk_per_trade=0.02)

    def test_initialization(self, sizer):
        """Test PositionSizer initialization"""
        assert sizer.portfolio_value == 10000
        assert sizer.risk_per_trade == 0.02

    def test_fixed_risk_position_size(self, sizer):
        """Test fixed risk position sizing"""
        entry = 100
        stop = 95  # 5% stop loss

        position_size = sizer.fixed_risk_position_size(entry, stop)

        # Risk: $10,000 * 0.02 = $200
        # Risk per unit: $100 - $95 = $5
        # Position size: $200 / $5 = 40 units
        assert position_size == 40

    def test_fixed_risk_with_small_stop(self, sizer):
        """Test position sizing with tight stop"""
        entry = 100
        stop = 99  # 1% stop loss

        position_size = sizer.fixed_risk_position_size(entry, stop)

        # Risk: $200
        # Risk per unit: $1
        # Position size: 200 units
        assert position_size == 200

    def test_kelly_criterion_basic(self, sizer):
        """Test Kelly Criterion calculation"""
        # 55% win rate, 3% avg win, 2% avg loss
        kelly_pct = sizer.kelly_criterion(
            win_rate=0.55,
            avg_win=0.03,
            avg_loss=0.02,
            kelly_fraction=0.1
        )

        # b = 3/2 = 1.5
        # f* = (1.5 * 0.55 - 0.45) / 1.5 = 0.25
        # 1/10th Kelly = 0.025
        assert 0.02 < kelly_pct < 0.03  # Approximately 2.5%

    def test_kelly_criterion_negative_expectancy(self, sizer):
        """Test Kelly with negative expectancy"""
        # Losing strategy
        kelly_pct = sizer.kelly_criterion(
            win_rate=0.40,
            avg_win=0.02,
            avg_loss=0.03,
            kelly_fraction=0.1
        )

        # Should return 0 (no position)
        assert kelly_pct == 0

    def test_kelly_criterion_capped_at_20pct(self, sizer):
        """Test that Kelly is capped at 20%"""
        # Unrealistically good strategy
        kelly_pct = sizer.kelly_criterion(
            win_rate=0.90,
            avg_win=0.10,
            avg_loss=0.01,
            kelly_fraction=1.0  # Full Kelly
        )

        # Should be capped at 20%
        assert kelly_pct <= 0.20

    def test_atr_based_position_size(self, sizer):
        """Test ATR-based position sizing"""
        entry = 100
        atr = 3
        multiplier = 2.0

        position_size = sizer.atr_based_position_size(entry, atr, multiplier)

        # Risk: $200
        # Stop distance: 2 * $3 = $6
        # Position size: $200 / $6 = 33.33 units
        assert 33 < position_size < 34

    def test_portfolio_heat_calculation(self, sizer):
        """Test portfolio heat calculation"""
        open_positions = [
            {'risk_amount': 200},
            {'risk_amount': 200},
            {'risk_amount': 200},
        ]

        heat = sizer.calculate_portfolio_heat(open_positions)

        # Total risk: $600
        # Portfolio: $10,000
        # Heat: 6%
        assert heat == 0.06

    def test_portfolio_heat_acceptable(self, sizer):
        """Test portfolio heat limit checking"""
        # Within limits
        low_risk_positions = [
            {'risk_amount': 100},
            {'risk_amount': 100},
        ]
        assert sizer.is_portfolio_heat_acceptable(low_risk_positions, max_heat=0.10)

        # Exceeds limits
        high_risk_positions = [
            {'risk_amount': 500},
            {'risk_amount': 500},
            {'risk_amount': 500},
        ]
        assert not sizer.is_portfolio_heat_acceptable(high_risk_positions, max_heat=0.10)


class TestDrawdownProtector:
    """Test drawdown protection mechanisms"""

    @pytest.fixture
    def protector(self):
        """Create DrawdownProtector instance"""
        return DrawdownProtector(
            max_drawdown=0.20,
            daily_loss_limit=0.06,
            consecutive_loss_limit=5
        )

    def test_initialization(self, protector):
        """Test DrawdownProtector initialization"""
        assert protector.max_drawdown == 0.20
        assert protector.daily_loss_limit == 0.06
        assert protector.consecutive_loss_limit == 5

    def test_update_equity(self, protector):
        """Test equity updates"""
        protector.update_equity(10000)
        assert protector.current_equity == 10000
        assert protector.peak_equity == 10000

        # New high
        protector.update_equity(11000)
        assert protector.peak_equity == 11000

        # Drawdown (peak should not change)
        protector.update_equity(10500)
        assert protector.peak_equity == 11000
        assert protector.current_equity == 10500

    def test_calculate_drawdown(self, protector):
        """Test drawdown calculation"""
        protector.update_equity(10000)
        assert protector.calculate_current_drawdown() == 0

        # 10% drawdown
        protector.update_equity(9000)
        dd = protector.calculate_current_drawdown()
        assert dd == 0.10

        # 20% drawdown
        protector.update_equity(8000)
        dd = protector.calculate_current_drawdown()
        assert dd == 0.20

    def test_max_drawdown_trigger(self, protector):
        """Test maximum drawdown kill switch"""
        protector.update_equity(10000)

        # Within limits
        protector.update_equity(8500)  # 15% drawdown
        should_stop, _ = protector.check_max_drawdown()
        assert not should_stop

        # Breach limit
        protector.update_equity(7900)  # 21% drawdown
        should_stop, reason = protector.check_max_drawdown()
        assert should_stop
        assert reason is not None

    def test_daily_loss_limit(self, protector):
        """Test daily loss limit"""
        protector.update_equity(10000)

        # Add losing trades
        protector.add_trade(-200)  # 2% loss
        protector.add_trade(-200)  # 2% loss
        protector.add_trade(-200)  # 2% loss (total 6%)

        # Should trigger daily loss limit
        should_stop, reason = protector.check_daily_loss_limit()
        assert should_stop
        assert reason is not None

    def test_consecutive_loss_limit(self, protector):
        """Test consecutive loss limit"""
        # Add 4 losses (should not trigger)
        for _ in range(4):
            protector.add_trade(-100)

        should_stop, _ = protector.check_consecutive_losses()
        assert not should_stop

        # Add 5th consecutive loss (should trigger)
        protector.add_trade(-100)
        should_stop, reason = protector.check_consecutive_losses()
        assert should_stop
        assert reason is not None

    def test_consecutive_losses_reset_on_win(self, protector):
        """Test that consecutive losses reset on a win"""
        # Add 4 losses
        for _ in range(4):
            protector.add_trade(-100)

        # Add a win
        protector.add_trade(150)

        # Add 4 more losses (should not trigger, counter reset)
        for _ in range(4):
            protector.add_trade(-100)

        should_stop, _ = protector.check_consecutive_losses()
        assert not should_stop

    def test_check_all_limits(self, protector):
        """Test checking all limits at once"""
        protector.update_equity(10000)

        # No breaches
        should_stop, reasons = protector.check_all_limits()
        assert not should_stop
        assert len(reasons) == 0

        # Multiple breaches
        protector.update_equity(7000)  # 30% drawdown (breach)
        for _ in range(5):
            protector.add_trade(-100)  # 5 consecutive losses (breach)

        should_stop, reasons = protector.check_all_limits()
        assert should_stop
        assert len(reasons) >= 1  # At least one limit breached

    def test_get_stats(self, protector):
        """Test statistics retrieval"""
        protector.update_equity(10000)
        protector.add_trade(-100)
        protector.add_trade(-100)
        protector.add_trade(150)

        stats = protector.get_stats()

        assert 'current_drawdown' in stats
        assert 'peak_equity' in stats
        assert 'current_equity' in stats
        assert 'today_pnl' in stats
        assert 'consecutive_losses' in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
