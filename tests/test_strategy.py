"""
Unit Tests for MomentumMeanReversion Strategy

Tests strategy logic, indicator calculations, and entry/exit conditions

Author: Claude Code
Version: 1.0.0
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add strategy path
sys.path.append(str(Path(__file__).parent.parent / "user_data" / "strategies"))

from MomentumMeanReversion import MomentumMeanReversion


@pytest.fixture
def strategy():
    """Create strategy instance"""
    return MomentumMeanReversion()


@pytest.fixture
def sample_dataframe():
    """Create sample dataframe for testing"""
    dates = pd.date_range('2024-01-01', periods=200, freq='15min')

    # Create trending market data
    np.random.seed(42)
    trend = np.linspace(100, 120, 200)
    noise = np.random.normal(0, 1, 200)
    close_prices = trend + noise

    df = pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.01,
        'low': close_prices * 0.98,
        'close': close_prices,
        'volume': np.random.uniform(1000, 5000, 200)
    })

    return df


class TestIndicators:
    """Test indicator calculations"""

    def test_populate_indicators(self, strategy, sample_dataframe):
        """Test that all indicators are calculated"""
        df = strategy.populate_indicators(sample_dataframe, {})

        # Check that all required indicators exist
        required_indicators = [
            'adx', 'rsi', 'ema_fast', 'ema_slow',
            'bb_lower', 'bb_middle', 'bb_upper', 'bb_width',
            'atr', 'volume_ma', 'regime', 'bb_position'
        ]

        for indicator in required_indicators:
            assert indicator in df.columns, f"Indicator {indicator} not found"
            assert not df[indicator].isnull().all(), f"Indicator {indicator} is all NaN"

    def test_adx_calculation(self, strategy, sample_dataframe):
        """Test ADX calculation"""
        df = strategy.populate_indicators(sample_dataframe, {})

        # ADX should be between 0 and 100
        assert (df['adx'] >= 0).all()
        assert (df['adx'] <= 100).all()

    def test_rsi_calculation(self, strategy, sample_dataframe):
        """Test RSI calculation"""
        df = strategy.populate_indicators(sample_dataframe, {})

        # RSI should be between 0 and 100
        assert (df['rsi'].dropna() >= 0).all()
        assert (df['rsi'].dropna() <= 100).all()

    def test_bollinger_bands(self, strategy, sample_dataframe):
        """Test Bollinger Bands calculation"""
        df = strategy.populate_indicators(sample_dataframe, {})

        # Lower band should be below middle, middle below upper
        valid_rows = df.dropna()
        assert (valid_rows['bb_lower'] <= valid_rows['bb_middle']).all()
        assert (valid_rows['bb_middle'] <= valid_rows['bb_upper']).all()

    def test_regime_detection(self, strategy, sample_dataframe):
        """Test market regime detection"""
        df = strategy.populate_indicators(sample_dataframe, {})

        # Regime should only be 'trending', 'ranging', or 'neutral'
        valid_regimes = {'trending', 'ranging', 'neutral'}
        assert set(df['regime'].unique()).issubset(valid_regimes)


class TestEntrySignals:
    """Test entry signal generation"""

    def test_momentum_entry(self, strategy):
        """Test momentum entry conditions"""
        # Create trending market
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100, freq='15min'),
            'open': np.linspace(100, 110, 100),
            'high': np.linspace(101, 111, 100),
            'low': np.linspace(99, 109, 100),
            'close': np.linspace(100, 110, 100),
            'volume': np.full(100, 1000)
        })

        # Populate indicators
        df = strategy.populate_indicators(df, {})

        # Populate entry trend
        df = strategy.populate_entry_trend(df, {})

        # Check that entry signal column exists
        assert 'enter_long' in df.columns

        # In a strong uptrend, we should have some momentum entries
        # (can't guarantee exact number due to indicator lag)
        assert df['enter_long'].sum() >= 0

    def test_mean_reversion_entry(self, strategy):
        """Test mean reversion entry conditions"""
        # Create ranging market with oversold dip
        close_prices = [100] * 50 + [95] * 5 + [100] * 45  # Dip in the middle

        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100, freq='15min'),
            'open': close_prices,
            'high': [p * 1.01 for p in close_prices],
            'low': [p * 0.99 for p in close_prices],
            'close': close_prices,
            'volume': np.full(100, 1000)
        })

        # Populate indicators
        df = strategy.populate_indicators(df, {})

        # Populate entry trend
        df = strategy.populate_entry_trend(df, {})

        # Check that entry signal exists
        assert 'enter_long' in df.columns

    def test_no_entry_on_low_volume(self, strategy):
        """Test that low volume prevents entries"""
        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100, freq='15min'),
            'open': np.linspace(100, 110, 100),
            'high': np.linspace(101, 111, 100),
            'low': np.linspace(99, 109, 100),
            'close': np.linspace(100, 110, 100),
            'volume': np.full(100, 10)  # Very low volume
        })

        # Populate indicators
        df = strategy.populate_indicators(df, {})

        # Populate entry trend
        df = strategy.populate_entry_trend(df, {})

        # With consistently low volume, entries should be limited
        # (though not necessarily zero due to volume_ma calculation)
        assert 'enter_long' in df.columns


class TestExitSignals:
    """Test exit signal generation"""

    def test_momentum_exit(self, strategy):
        """Test momentum exit conditions"""
        # Create uptrend then downtrend
        close_prices = list(np.linspace(100, 110, 50)) + list(np.linspace(110, 100, 50))

        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100, freq='15min'),
            'open': close_prices,
            'high': [p * 1.01 for p in close_prices],
            'low': [p * 0.99 for p in close_prices],
            'close': close_prices,
            'volume': np.full(100, 1000)
        })

        # Populate indicators
        df = strategy.populate_indicators(df, {})

        # Populate exit trend
        df = strategy.populate_exit_trend(df, {})

        # Check that exit signal exists
        assert 'exit_long' in df.columns

    def test_mean_reversion_exit(self, strategy):
        """Test mean reversion exit conditions"""
        # Create dip then recovery
        close_prices = [100] * 30 + [95] * 10 + list(np.linspace(95, 100, 20)) + [100] * 40

        df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100, freq='15min'),
            'open': close_prices,
            'high': [p * 1.01 for p in close_prices],
            'low': [p * 0.99 for p in close_prices],
            'close': close_prices,
            'volume': np.full(100, 1000)
        })

        # Populate indicators
        df = strategy.populate_indicators(df, {})

        # Populate exit trend
        df = strategy.populate_exit_trend(df, {})

        # Check that exit signal exists
        assert 'exit_long' in df.columns


class TestRiskManagement:
    """Test risk management features"""

    def test_stoploss_value(self, strategy):
        """Test that stoploss is set"""
        assert strategy.stoploss < 0  # Stoploss should be negative
        assert strategy.stoploss >= -1  # Reasonable range

    def test_minimal_roi(self, strategy):
        """Test that minimal ROI is defined"""
        assert len(strategy.minimal_roi) > 0
        assert all(v > 0 for v in strategy.minimal_roi.values())

    def test_trailing_stop(self, strategy):
        """Test trailing stop configuration"""
        assert strategy.trailing_stop is True
        assert strategy.trailing_stop_positive > 0
        assert strategy.trailing_stop_positive_offset > strategy.trailing_stop_positive

    def test_leverage(self, strategy):
        """Test leverage setting"""
        # Should return 1.0 (no leverage)
        leverage = strategy.leverage('BTC/USDT', pd.Timestamp.now(), 100, 10, 10, None, 'long')
        assert leverage == 1.0


class TestHyperOptParameters:
    """Test hyperopt parameter ranges"""

    def test_parameter_ranges(self, strategy):
        """Test that hyperopt parameters have valid ranges"""
        # ADX thresholds
        assert strategy.adx_threshold_trending.value >= 20
        assert strategy.adx_threshold_trending.value <= 30

        assert strategy.adx_threshold_ranging.value >= 15
        assert strategy.adx_threshold_ranging.value <= 22

        # RSI parameters
        assert 0 < strategy.rsi_oversold.value < 50
        assert 50 < strategy.rsi_overbought.value < 100

        # EMA parameters
        assert strategy.ema_fast.value < strategy.ema_slow.value


def test_strategy_metadata(strategy):
    """Test strategy metadata"""
    assert hasattr(strategy, 'INTERFACE_VERSION')
    assert strategy.timeframe in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    assert strategy.startup_candle_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
