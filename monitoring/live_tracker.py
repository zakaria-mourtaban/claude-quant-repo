#!/usr/bin/env python3
"""
Live Trading Performance Tracker

Tracks bot performance in real-time during 2-week live test.
Generates daily reports and maintains detailed logs.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import time
import statistics
from stage_manager import StageManager


class LivePerformanceTracker:
    """Tracks live trading performance and generates reports"""

    def __init__(self, results_dir="user_data/live_test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.session_file = self.results_dir / "current_session.json"
        self.trades_file = self.results_dir / "trades_log.json"
        self.daily_reports_dir = self.results_dir / "daily_reports"
        self.daily_reports_dir.mkdir(exist_ok=True)

        self.start_time = datetime.now()
        self.session_data = self._load_or_create_session()

        # Initialize stage manager
        self.stage_manager = StageManager()

    def _load_or_create_session(self):
        """Load existing session or create new one"""
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                # Convert string back to datetime
                data['start_time'] = datetime.fromisoformat(data['start_time'])
                return data
        else:
            return {
                'start_time': self.start_time,
                'initial_balance': 10000.0,
                'current_balance': 10000.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_profit': 0.0,
                'max_balance': 10000.0,
                'min_balance': 10000.0,
                'peak_balance': 10000.0,
                'max_drawdown_pct': 0.0,
                'daily_snapshots': []
            }

    def save_session(self):
        """Save current session data"""
        # Convert datetime to string for JSON
        data_to_save = self.session_data.copy()
        data_to_save['start_time'] = self.session_data['start_time'].isoformat()

        with open(self.session_file, 'w') as f:
            json.dump(data_to_save, f, indent=2)

    def update_from_freqtrade(self, trades_file="user_data/trades.json"):
        """
        Update tracker from Freqtrade's trades.json file

        This reads the trades from Freqtrade and updates our metrics
        """
        if not Path(trades_file).exists():
            return

        with open(trades_file, 'r') as f:
            try:
                trades = json.load(f)
            except json.JSONDecodeError:
                return

        if not trades:
            return

        # Calculate metrics from trades
        total_profit = 0.0
        winning = 0
        losing = 0

        for trade in trades:
            profit = trade.get('close_profit_abs', 0)
            total_profit += profit

            if profit > 0:
                winning += 1
            elif profit < 0:
                losing += 1

        # Update session data
        self.session_data['total_trades'] = len(trades)
        self.session_data['winning_trades'] = winning
        self.session_data['losing_trades'] = losing
        self.session_data['total_profit'] = total_profit
        self.session_data['current_balance'] = self.session_data['initial_balance'] + total_profit

        # Track peak and drawdown
        current_balance = self.session_data['current_balance']
        if current_balance > self.session_data['peak_balance']:
            self.session_data['peak_balance'] = current_balance

        # Calculate drawdown
        drawdown = (self.session_data['peak_balance'] - current_balance) / self.session_data['peak_balance']
        if drawdown > self.session_data['max_drawdown_pct']:
            self.session_data['max_drawdown_pct'] = drawdown

        self.save_session()

    def generate_daily_snapshot(self):
        """Generate a daily snapshot of performance"""
        snapshot = {
            'date': datetime.now().isoformat(),
            'balance': self.session_data['current_balance'],
            'total_trades': self.session_data['total_trades'],
            'winning_trades': self.session_data['winning_trades'],
            'losing_trades': self.session_data['losing_trades'],
            'total_profit': self.session_data['total_profit'],
            'win_rate': (self.session_data['winning_trades'] / self.session_data['total_trades'] * 100)
                       if self.session_data['total_trades'] > 0 else 0,
            'max_drawdown': self.session_data['max_drawdown_pct'] * 100
        }

        self.session_data['daily_snapshots'].append(snapshot)
        self.save_session()

        return snapshot

    def generate_daily_report(self):
        """Generate a daily performance report"""
        now = datetime.now()
        elapsed = now - self.session_data['start_time']
        days_elapsed = elapsed.days

        # Generate snapshot
        snapshot = self.generate_daily_snapshot()

        # Calculate metrics
        initial = self.session_data['initial_balance']
        current = self.session_data['current_balance']
        total_return = ((current - initial) / initial) * 100
        total_trades = self.session_data['total_trades']
        win_rate = snapshot['win_rate']

        # Trades today (rough estimate - last snapshot)
        trades_today = 0
        if len(self.session_data['daily_snapshots']) > 1:
            trades_today = (self.session_data['daily_snapshots'][-1]['total_trades'] -
                          self.session_data['daily_snapshots'][-2]['total_trades'])

        report = f"""
{'='*80}
                    DAILY PERFORMANCE REPORT
{'='*80}

📅 Date: {now.strftime('%Y-%m-%d %H:%M:%S')}
⏱️  Days Running: {days_elapsed} of 14 (Target: 2 weeks)
📊 Progress: [{('█' * int(days_elapsed * 50 / 14)).ljust(50, '░')}] {days_elapsed * 100 / 14:.0f}%

{'='*80}
                         PERFORMANCE SUMMARY
{'='*80}

💰 Balance:          ${current:,.2f} (Initial: ${initial:,.2f})
📈 Total Return:     {total_return:+.2f}%
💵 Total Profit:     ${self.session_data['total_profit']:+,.2f}

📊 Trades:           {total_trades} total
   ├─ Today:         {trades_today} trades
   ├─ Winning:       {self.session_data['winning_trades']} ({win_rate:.1f}%)
   └─ Losing:        {self.session_data['losing_trades']}

⚠️  Risk:
   ├─ Max Drawdown:  {self.session_data['max_drawdown_pct'] * 100:.2f}%
   ├─ Peak Balance:  ${self.session_data['peak_balance']:,.2f}
   └─ Min Balance:   ${self.session_data.get('min_balance', initial):,.2f}

{'='*80}
                        DAILY TREND (Last 7 Days)
{'='*80}

"""
        # Add last 7 days trend
        recent_snapshots = self.session_data['daily_snapshots'][-7:]
        if recent_snapshots:
            report += "Day    | Balance    | Trades | Win Rate | Profit\n"
            report += "-------|------------|--------|----------|----------\n"
            for i, snap in enumerate(recent_snapshots):
                day_num = len(self.session_data['daily_snapshots']) - len(recent_snapshots) + i + 1
                report += f"Day {day_num:2d} | ${snap['balance']:9,.2f} | {snap['total_trades']:6d} | {snap['win_rate']:7.1f}% | ${snap['total_profit']:+8.2f}\n"

        report += "\n" + "="*80 + "\n"
        report += "                      2-WEEK TEST STATUS\n"
        report += "="*80 + "\n\n"

        if days_elapsed < 14:
            days_remaining = 14 - days_elapsed
            report += f"⏰ Days Remaining: {days_remaining} days\n"
            report += f"📅 Estimated Completion: {(now + timedelta(days=days_remaining)).strftime('%Y-%m-%d')}\n"
        else:
            report += "✅ 2-WEEK TEST COMPLETE!\n"
            report += "📊 Run 'python monitoring/generate_final_report.py' for full analysis\n"

        report += "\n" + "="*80 + "\n"

        # Save report to file
        report_file = self.daily_reports_dir / f"report_{now.strftime('%Y%m%d')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)

        return report

    def calculate_profit_factor(self, trades_file="user_data/trades.json"):
        """Calculate profit factor from trades"""
        if not Path(trades_file).exists():
            return 0.0

        try:
            with open(trades_file, 'r') as f:
                trades = json.load(f)
        except:
            return 0.0

        if not trades:
            return 0.0

        gross_profit = sum(t.get('close_profit_abs', 0) for t in trades if t.get('close_profit_abs', 0) > 0)
        gross_loss = abs(sum(t.get('close_profit_abs', 0) for t in trades if t.get('close_profit_abs', 0) < 0))

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    def calculate_sharpe_ratio(self):
        """Calculate Sharpe ratio from daily snapshots"""
        snapshots = self.session_data.get('daily_snapshots', [])
        if len(snapshots) < 2:
            return 0.0

        daily_returns = []
        for i in range(1, len(snapshots)):
            prev_balance = snapshots[i-1]['balance']
            curr_balance = snapshots[i]['balance']
            if prev_balance > 0:
                daily_return = (curr_balance - prev_balance) / prev_balance
                daily_returns.append(daily_return)

        if not daily_returns or len(daily_returns) < 2:
            return 0.0

        mean_return = statistics.mean(daily_returns)
        std_return = statistics.stdev(daily_returns)

        if std_return == 0:
            return 0.0

        # Annualized Sharpe
        annual_return = mean_return * 365
        annual_std = std_return * (365 ** 0.5)
        sharpe = (annual_return - 0.02) / annual_std  # 2% risk-free rate

        return sharpe

    def get_current_status(self):
        """Get current status as dict including stage information"""
        now = datetime.now()
        elapsed = now - self.session_data['start_time']

        # Calculate profit factor and Sharpe
        profit_factor = self.calculate_profit_factor()
        sharpe_ratio = self.calculate_sharpe_ratio()

        # Get reliability metrics
        reliability = self.stage_manager.get_reliability_metrics()

        # Get stage information
        stage_info = self.stage_manager.get_current_stage_info()

        return {
            'start_time': self.session_data['start_time'].isoformat(),
            'current_time': now.isoformat(),
            'days_elapsed': elapsed.days,
            'hours_elapsed': elapsed.total_seconds() / 3600,
            'initial_balance': self.session_data['initial_balance'],
            'current_balance': self.session_data['current_balance'],
            'total_return_pct': ((self.session_data['current_balance'] - self.session_data['initial_balance'])
                                / self.session_data['initial_balance'] * 100),
            'total_trades': self.session_data['total_trades'],
            'winning_trades': self.session_data['winning_trades'],
            'losing_trades': self.session_data['losing_trades'],
            'win_rate': (self.session_data['winning_trades'] / self.session_data['total_trades'] * 100)
                       if self.session_data['total_trades'] > 0 else 0,
            'max_drawdown_pct': self.session_data['max_drawdown_pct'] * 100,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'uptime_pct': reliability['uptime_pct'],
            'crash_count': reliability['crash_count'],
            'disconnect_count': reliability['disconnect_count'],
            'stage_number': stage_info['stage_number'],
            'stage_name': stage_info['stage_name'],
            'stage_days_elapsed': stage_info['days_elapsed'],
            'stage_target_days': stage_info['target_days'],
            'ready_to_advance': stage_info['ready_to_advance']
        }


def main():
    """Main function - update and generate daily report"""
    tracker = LivePerformanceTracker()

    # Update from Freqtrade data
    tracker.update_from_freqtrade()

    # Generate daily report
    report = tracker.generate_daily_report()
    print(report)

    # Also print to console
    status = tracker.get_current_status()
    print("\n💾 Report saved to:", tracker.daily_reports_dir)
    print(f"📊 Current Status: Day {status['days_elapsed']} of 14")
    print(f"💰 Balance: ${status['current_balance']:,.2f} ({status['total_return_pct']:+.2f}%)")
    print(f"📈 Trades: {status['total_trades']} ({status['win_rate']:.1f}% win rate)")


if __name__ == "__main__":
    main()
