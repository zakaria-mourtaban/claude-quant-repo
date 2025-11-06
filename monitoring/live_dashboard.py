#!/usr/bin/env python3
"""
Real-Time Live Trading Dashboard

Shows current bot status, recent trades, and performance metrics
Updates every 30 seconds
"""

import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from live_tracker import LivePerformanceTracker


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def format_duration(seconds):
    """Format duration in human-readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{days}d {hours}h {minutes}m"


def get_recent_trades(trades_file="user_data/trades.json", limit=10):
    """Get recent trades from Freqtrade"""
    if not Path(trades_file).exists():
        return []

    try:
        with open(trades_file, 'r') as f:
            trades = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

    # Sort by close date (most recent first)
    trades.sort(key=lambda x: x.get('close_date', ''), reverse=True)
    return trades[:limit]


def render_dashboard(tracker, trades):
    """Render the dashboard"""
    clear_screen()

    now = datetime.now()
    status = tracker.get_current_status()

    # Calculate time metrics
    start_time = datetime.fromisoformat(status['start_time'])
    elapsed = now - start_time
    elapsed_seconds = elapsed.total_seconds()
    target_seconds = 14 * 24 * 3600  # 14 days
    progress_pct = min((elapsed_seconds / target_seconds) * 100, 100)

    # Calculate daily stats
    trades_per_day = status['total_trades'] / max(status['days_elapsed'], 1)
    profit_per_day = (status['current_balance'] - status['initial_balance']) / max(status['days_elapsed'], 1)

    # Header
    print("="*100)
    print(" " * 30 + "🤖 LIVE TRADING DASHBOARD - 2 WEEK TEST")
    print("="*100)
    print()

    # Test Progress
    print("⏱️  TEST PROGRESS")
    print("-" * 100)
    bar_length = 60
    filled = int(bar_length * progress_pct / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"   [{bar}] {progress_pct:.1f}%")
    print(f"   Started:     {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Current:     {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Elapsed:     {format_duration(elapsed_seconds)} (Day {status['days_elapsed']} of 14)")
    if progress_pct < 100:
        remaining_seconds = target_seconds - elapsed_seconds
        print(f"   Remaining:   {format_duration(remaining_seconds)}")
        eta = now + timedelta(seconds=remaining_seconds)
        print(f"   ETA:         {eta.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"   Status:      ✅ TEST COMPLETE!")
    print()

    # Performance Metrics
    print("💰 PERFORMANCE")
    print("-" * 100)
    balance_change = status['current_balance'] - status['initial_balance']
    balance_symbol = "📈" if balance_change >= 0 else "📉"

    print(f"   Initial Balance:      ${status['initial_balance']:,.2f}")
    print(f"   Current Balance:      ${status['current_balance']:,.2f} {balance_symbol}")
    print(f"   Profit/Loss:          ${balance_change:+,.2f} ({status['total_return_pct']:+.2f}%)")
    print(f"   Daily Average:        ${profit_per_day:+,.2f}/day")
    print()

    # Trading Statistics
    print("📊 TRADING STATISTICS")
    print("-" * 100)
    print(f"   Total Trades:         {status['total_trades']}")
    print(f"   Winning Trades:       {status['winning_trades']} ({status['win_rate']:.1f}%)")
    print(f"   Losing Trades:        {status['losing_trades']}")
    print(f"   Trades per Day:       {trades_per_day:.1f} trades/day")
    print()

    # Risk Metrics
    print("⚠️  RISK METRICS")
    print("-" * 100)
    print(f"   Max Drawdown:         {status['max_drawdown_pct']:.2f}%")

    # Status indicator
    if status['max_drawdown_pct'] < 5:
        risk_level = "🟢 LOW RISK"
    elif status['max_drawdown_pct'] < 10:
        risk_level = "🟡 MODERATE RISK"
    else:
        risk_level = "🔴 HIGH RISK"
    print(f"   Risk Level:           {risk_level}")
    print()

    # Recent Trades
    print("📝 RECENT TRADES (Last 10)")
    print("-" * 100)
    if trades:
        print(f"   {'Pair':<12} {'Entry':<20} {'Exit':<20} {'Profit':<12} {'%':<8} {'Duration':<10}")
        print("   " + "-" * 96)
        for trade in trades[:10]:
            pair = trade.get('pair', 'N/A')
            open_date = trade.get('open_date', 'N/A')[:16]  # Remove seconds
            close_date = trade.get('close_date', 'N/A')[:16] if trade.get('close_date') else 'OPEN'
            profit_abs = trade.get('close_profit_abs', 0)
            profit_pct = trade.get('close_profit', 0) * 100
            duration = trade.get('close_date', '')

            # Calculate duration
            if trade.get('close_date'):
                try:
                    open_dt = datetime.fromisoformat(trade['open_date'])
                    close_dt = datetime.fromisoformat(trade['close_date'])
                    dur_seconds = (close_dt - open_dt).total_seconds()
                    dur_str = format_duration(dur_seconds)
                except:
                    dur_str = "N/A"
            else:
                dur_str = "OPEN"

            # Emoji for profit/loss
            emoji = "✅" if profit_abs > 0 else "❌" if profit_abs < 0 else "➖"

            print(f"   {emoji} {pair:<10} {open_date:<20} {close_date:<20} ${profit_abs:>9.2f}  {profit_pct:>6.2f}%  {dur_str}")
    else:
        print("   No trades yet...")
    print()

    # Success Criteria
    print("🎯 SUCCESS CRITERIA (2-Week Targets)")
    print("-" * 100)
    criteria = [
        ("Win Rate > 40%", status['win_rate'], 40, status['win_rate'] > 40),
        ("Positive Return", status['total_return_pct'], 0, status['total_return_pct'] > 0),
        ("Max Drawdown < 20%", status['max_drawdown_pct'], 20, status['max_drawdown_pct'] < 20),
        ("Min 10 Trades", status['total_trades'], 10, status['total_trades'] >= 10),
    ]

    passed = 0
    for criterion, value, target, is_pass in criteria:
        status_icon = "✅" if is_pass else "⏳" if status['days_elapsed'] < 14 else "❌"
        passed += 1 if is_pass else 0
        print(f"   {status_icon} {criterion:<30} (Current: {value:.1f})")

    print()
    print(f"   Score: {passed}/{len(criteria)} criteria met")
    print()

    # Footer
    print("="*100)
    print(f"   Last Update: {now.strftime('%H:%M:%S')} | Updates every 30 seconds | Press Ctrl+C to exit")
    print("="*100)


def main():
    """Main dashboard loop"""
    print("Starting Live Trading Dashboard...")
    print("Press Ctrl+C to exit")
    time.sleep(2)

    tracker = LivePerformanceTracker()

    try:
        while True:
            # Update tracker from Freqtrade data
            tracker.update_from_freqtrade()

            # Get recent trades
            trades = get_recent_trades()

            # Render dashboard
            render_dashboard(tracker, trades)

            # Wait 30 seconds before next update
            time.sleep(30)

    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user.")
        print("Bot continues running in background.")
        print("\nTo view status again, run: python monitoring/live_dashboard.py")


if __name__ == "__main__":
    main()
