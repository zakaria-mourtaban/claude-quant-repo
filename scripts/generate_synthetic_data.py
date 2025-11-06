"""
Generate synthetic OHLCV data for backtesting
This creates realistic cryptocurrency price data with trends and volatility
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta

def generate_crypto_data(
    pair: str,
    start_price: float,
    days: int = 90,
    timeframe: str = '15m',
    trend: float = 0.0002,  # Daily trend
    volatility: float = 0.02  # Daily volatility
):
    """Generate synthetic cryptocurrency OHLCV data"""

    # Calculate number of candles
    minutes_per_candle = {
        '1m': 1, '5m': 5, '15m': 15, '30m': 30,
        '1h': 60, '4h': 240, '1d': 1440
    }

    candles_per_day = 1440 // minutes_per_candle[timeframe]
    total_candles = days * candles_per_day

    # Generate timestamps
    start_date = datetime.now() - timedelta(days=days)
    timestamps = [
        int((start_date + timedelta(minutes=i * minutes_per_candle[timeframe])).timestamp() * 1000)
        for i in range(total_candles)
    ]

    # Generate price data with trend and volatility
    np.random.seed(42)

    # Create base price series with trend
    returns = np.random.normal(trend, volatility, total_candles)
    prices = start_price * np.cumprod(1 + returns)

    # Add some regime changes (trending and ranging periods)
    for i in range(0, total_candles, candles_per_day * 10):
        # Every 10 days, potentially change regime
        if np.random.random() > 0.5:
            # Add strong trend
            trend_strength = np.random.choice([-1, 1]) * 0.001
            for j in range(i, min(i + candles_per_day * 5, total_candles)):
                prices[j] *= (1 + trend_strength)
        else:
            # Add ranging behavior
            mean_price = prices[i]
            for j in range(i, min(i + candles_per_day * 5, total_candles)):
                prices[j] = mean_price + np.random.normal(0, mean_price * 0.01)

    # Generate OHLCV data
    data = []
    for i, (timestamp, close) in enumerate(zip(timestamps, prices)):
        # Generate realistic OHLC from close price
        volatility_factor = np.random.uniform(0.005, 0.015)
        high = close * (1 + volatility_factor * np.random.random())
        low = close * (1 - volatility_factor * np.random.random())
        open_price = np.random.uniform(low, high)

        # Ensure OHLC relationships
        high = max(high, open_price, close)
        low = min(low, open_price, close)

        # Generate volume (inversely related to price for realism)
        base_volume = 1000000
        volume = base_volume * (1 + np.random.normal(0, 0.3))

        data.append([
            timestamp,
            float(open_price),
            float(high),
            float(low),
            float(close),
            float(volume)
        ])

    return data

def save_data(data, pair, timeframe, data_dir):
    """Save data in Freqtrade format"""
    # Create directory structure
    exchange_dir = Path(data_dir) / 'binance'
    exchange_dir.mkdir(parents=True, exist_ok=True)

    # Format pair name for filename
    pair_filename = pair.replace('/', '_')
    filename = exchange_dir / f'{pair_filename}-{timeframe}.json'

    # Save as JSON
    with open(filename, 'w') as f:
        json.dump(data, f)

    print(f"✅ Saved {len(data)} candles to {filename}")

if __name__ == "__main__":
    # Generate data for multiple pairs and timeframes
    pairs = {
        'BTC/USDT': 40000,
        'ETH/USDT': 2500,
        'SOL/USDT': 100,
    }

    timeframes = ['15m', '1h']
    data_dir = 'user_data/data'

    print("Generating synthetic cryptocurrency data...")
    print("=" * 60)

    for pair, start_price in pairs.items():
        for timeframe in timeframes:
            data = generate_crypto_data(
                pair=pair,
                start_price=start_price,
                days=90,
                timeframe=timeframe,
                trend=0.0003,  # Slight uptrend
                volatility=0.025  # 2.5% daily volatility
            )
            save_data(data, pair, timeframe, data_dir)

    print("=" * 60)
    print("✅ Data generation complete!")
    print(f"Generated data for {len(pairs)} pairs and {len(timeframes)} timeframes")
    print(f"Data saved to: {data_dir}/binance/")
