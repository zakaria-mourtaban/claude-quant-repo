#!/usr/bin/env python3
"""
Stage Manager for Multi-Stage Testing

Manages progression through testing stages with criteria-based advancement.

STAGES:
- Stage 1: Initial Testing (3-5 days) - Verify stability
- Stage 2: Performance Validation (7-10 days) - Validate strategy
- Stage 3: Final Validation (14 days) - Confirm consistency
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple


class StageManager:
    """Manages testing stages and advancement criteria"""

    # Stage definitions
    STAGES = {
        1: {
            'name': 'Stage 1: Initial Testing',
            'description': 'Verify bot stability and basic functionality',
            'min_days': 3,
            'target_days': 5,
            'criteria': {
                'min_trades': 10,
                'min_win_rate': 30.0,
                'max_drawdown': 30.0,
                'min_uptime_pct': 80.0
            }
        },
        2: {
            'name': 'Stage 2: Performance Validation',
            'description': 'Validate strategy performance with more data',
            'min_days': 7,
            'target_days': 10,
            'criteria': {
                'min_trades': 25,
                'min_win_rate': 40.0,
                'positive_return': True,
                'max_drawdown': 20.0,
                'min_profit_factor': 1.2,
                'min_uptime_pct': 85.0
            }
        },
        3: {
            'name': 'Stage 3: Final Validation',
            'description': 'Confirm consistency over 2 weeks',
            'min_days': 14,
            'target_days': 14,
            'criteria': {
                'min_trades': 40,
                'min_win_rate': 40.0,
                'min_return': 2.0,
                'max_drawdown': 20.0,
                'min_profit_factor': 1.5,
                'min_sharpe': 1.0,
                'min_uptime_pct': 90.0
            }
        }
    }

    def __init__(self, stage_file="user_data/live_test_results/stage_data.json"):
        self.stage_file = Path(stage_file)
        self.stage_file.parent.mkdir(parents=True, exist_ok=True)
        self.stage_data = self._load_or_create_stage_data()

    def _load_or_create_stage_data(self):
        """Load existing stage data or create new"""
        if self.stage_file.exists():
            with open(self.stage_file, 'r') as f:
                data = json.load(f)
                # Convert timestamps
                data['stage_start_time'] = datetime.fromisoformat(data['stage_start_time'])
                data['test_start_time'] = datetime.fromisoformat(data['test_start_time'])
                if data.get('stage_completion_time'):
                    data['stage_completion_time'] = datetime.fromisoformat(data['stage_completion_time'])
                return data
        else:
            return {
                'current_stage': 1,
                'stage_start_time': datetime.now(),
                'test_start_time': datetime.now(),
                'stage_completion_time': None,
                'stage_history': [],
                'crash_count': 0,
                'disconnect_count': 0,
                'total_downtime_seconds': 0,
                'last_health_check': datetime.now().isoformat(),
                'ready_to_advance': False
            }

    def save_stage_data(self):
        """Save current stage data"""
        data_to_save = self.stage_data.copy()
        data_to_save['stage_start_time'] = self.stage_data['stage_start_time'].isoformat()
        data_to_save['test_start_time'] = self.stage_data['test_start_time'].isoformat()
        if self.stage_data.get('stage_completion_time'):
            data_to_save['stage_completion_time'] = self.stage_data['stage_completion_time'].isoformat()

        with open(self.stage_file, 'w') as f:
            json.dump(data_to_save, f, indent=2)

    def get_current_stage_info(self) -> Dict:
        """Get information about current stage"""
        stage_num = self.stage_data['current_stage']
        stage_info = self.STAGES.get(stage_num, {})

        now = datetime.now()
        stage_start = self.stage_data['stage_start_time']
        stage_elapsed = now - stage_start

        return {
            'stage_number': stage_num,
            'stage_name': stage_info.get('name', f'Stage {stage_num}'),
            'stage_description': stage_info.get('description', ''),
            'min_days': stage_info.get('min_days', 0),
            'target_days': stage_info.get('target_days', 0),
            'days_elapsed': stage_elapsed.days,
            'hours_elapsed': stage_elapsed.total_seconds() / 3600,
            'criteria': stage_info.get('criteria', {}),
            'stage_start_time': stage_start.isoformat(),
            'ready_to_advance': self.stage_data.get('ready_to_advance', False)
        }

    def evaluate_stage_criteria(self, performance_metrics: Dict) -> Tuple[bool, Dict]:
        """
        Evaluate if current stage criteria are met

        Args:
            performance_metrics: Dict with keys like:
                - total_trades
                - win_rate
                - total_return_pct
                - max_drawdown_pct
                - profit_factor
                - sharpe_ratio
                - days_elapsed
                - uptime_pct

        Returns:
            (ready_to_advance, evaluation_details)
        """
        stage_num = self.stage_data['current_stage']
        stage_info = self.STAGES.get(stage_num)

        if not stage_info:
            return False, {'error': f'Invalid stage: {stage_num}'}

        criteria = stage_info['criteria']
        min_days = stage_info['min_days']

        evaluation = {
            'stage': stage_num,
            'stage_name': stage_info['name'],
            'checks': [],
            'passed': 0,
            'failed': 0,
            'total': 0,
            'ready': False
        }

        # Check minimum days
        days_elapsed = performance_metrics.get('days_elapsed', 0)
        day_check = {
            'criterion': f'Minimum {min_days} days',
            'target': min_days,
            'current': days_elapsed,
            'passed': days_elapsed >= min_days,
            'required': True
        }
        evaluation['checks'].append(day_check)
        evaluation['total'] += 1
        if day_check['passed']:
            evaluation['passed'] += 1
        else:
            evaluation['failed'] += 1

        # Check trade count
        if 'min_trades' in criteria:
            min_trades = criteria['min_trades']
            current_trades = performance_metrics.get('total_trades', 0)
            trade_check = {
                'criterion': f'Minimum {min_trades} trades',
                'target': min_trades,
                'current': current_trades,
                'passed': current_trades >= min_trades,
                'required': True
            }
            evaluation['checks'].append(trade_check)
            evaluation['total'] += 1
            if trade_check['passed']:
                evaluation['passed'] += 1
            else:
                evaluation['failed'] += 1

        # Check win rate
        if 'min_win_rate' in criteria:
            min_wr = criteria['min_win_rate']
            current_wr = performance_metrics.get('win_rate', 0)
            wr_check = {
                'criterion': f'Win rate > {min_wr}%',
                'target': min_wr,
                'current': current_wr,
                'passed': current_wr >= min_wr,
                'required': True
            }
            evaluation['checks'].append(wr_check)
            evaluation['total'] += 1
            if wr_check['passed']:
                evaluation['passed'] += 1
            else:
                evaluation['failed'] += 1

        # Check positive return
        if criteria.get('positive_return'):
            current_return = performance_metrics.get('total_return_pct', 0)
            return_check = {
                'criterion': 'Positive return',
                'target': 0,
                'current': current_return,
                'passed': current_return > 0,
                'required': True
            }
            evaluation['checks'].append(return_check)
            evaluation['total'] += 1
            if return_check['passed']:
                evaluation['passed'] += 1
            else:
                evaluation['failed'] += 1

        # Check minimum return
        if 'min_return' in criteria:
            min_return = criteria['min_return']
            current_return = performance_metrics.get('total_return_pct', 0)
            min_return_check = {
                'criterion': f'Return > {min_return}%',
                'target': min_return,
                'current': current_return,
                'passed': current_return >= min_return,
                'required': True
            }
            evaluation['checks'].append(min_return_check)
            evaluation['total'] += 1
            if min_return_check['passed']:
                evaluation['passed'] += 1
            else:
                evaluation['failed'] += 1

        # Check max drawdown
        if 'max_drawdown' in criteria:
            max_dd = criteria['max_drawdown']
            current_dd = performance_metrics.get('max_drawdown_pct', 0)
            dd_check = {
                'criterion': f'Max drawdown < {max_dd}%',
                'target': max_dd,
                'current': current_dd,
                'passed': current_dd < max_dd,
                'required': True
            }
            evaluation['checks'].append(dd_check)
            evaluation['total'] += 1
            if dd_check['passed']:
                evaluation['passed'] += 1
            else:
                evaluation['failed'] += 1

        # Check profit factor
        if 'min_profit_factor' in criteria:
            min_pf = criteria['min_profit_factor']
            current_pf = performance_metrics.get('profit_factor', 0)
            pf_check = {
                'criterion': f'Profit factor > {min_pf}',
                'target': min_pf,
                'current': current_pf,
                'passed': current_pf >= min_pf,
                'required': True
            }
            evaluation['checks'].append(pf_check)
            evaluation['total'] += 1
            if pf_check['passed']:
                evaluation['passed'] += 1
            else:
                evaluation['failed'] += 1

        # Check Sharpe ratio
        if 'min_sharpe' in criteria:
            min_sharpe = criteria['min_sharpe']
            current_sharpe = performance_metrics.get('sharpe_ratio', 0)
            sharpe_check = {
                'criterion': f'Sharpe ratio > {min_sharpe}',
                'target': min_sharpe,
                'current': current_sharpe,
                'passed': current_sharpe >= min_sharpe,
                'required': True
            }
            evaluation['checks'].append(sharpe_check)
            evaluation['total'] += 1
            if sharpe_check['passed']:
                evaluation['passed'] += 1
            else:
                evaluation['failed'] += 1

        # Check uptime
        if 'min_uptime_pct' in criteria:
            min_uptime = criteria['min_uptime_pct']
            current_uptime = performance_metrics.get('uptime_pct', 100)
            uptime_check = {
                'criterion': f'Uptime > {min_uptime}%',
                'target': min_uptime,
                'current': current_uptime,
                'passed': current_uptime >= min_uptime,
                'required': True
            }
            evaluation['checks'].append(uptime_check)
            evaluation['total'] += 1
            if uptime_check['passed']:
                evaluation['passed'] += 1
            else:
                evaluation['failed'] += 1

        # Determine if ready to advance
        evaluation['ready'] = evaluation['failed'] == 0 and evaluation['passed'] == evaluation['total']

        # Update stage data
        self.stage_data['ready_to_advance'] = evaluation['ready']
        self.save_stage_data()

        return evaluation['ready'], evaluation

    def advance_stage(self, performance_metrics: Dict) -> Tuple[bool, str]:
        """
        Attempt to advance to next stage

        Returns:
            (success, message)
        """
        ready, evaluation = self.evaluate_stage_criteria(performance_metrics)

        if not ready:
            failed_checks = [c for c in evaluation['checks'] if not c['passed']]
            failures = ', '.join([c['criterion'] for c in failed_checks])
            return False, f"Cannot advance: Failed criteria - {failures}"

        current_stage = self.stage_data['current_stage']

        # Record stage completion
        stage_record = {
            'stage': current_stage,
            'completed_at': datetime.now().isoformat(),
            'days_elapsed': performance_metrics.get('days_elapsed', 0),
            'total_trades': performance_metrics.get('total_trades', 0),
            'win_rate': performance_metrics.get('win_rate', 0),
            'total_return': performance_metrics.get('total_return_pct', 0),
            'max_drawdown': performance_metrics.get('max_drawdown_pct', 0)
        }
        self.stage_data['stage_history'].append(stage_record)

        # Check if this is the final stage
        if current_stage >= 3:
            self.stage_data['stage_completion_time'] = datetime.now()
            self.save_stage_data()
            return True, "🎉 FINAL STAGE COMPLETED! Bot ready for live trading."

        # Advance to next stage
        self.stage_data['current_stage'] = current_stage + 1
        self.stage_data['stage_start_time'] = datetime.now()
        self.stage_data['ready_to_advance'] = False
        self.save_stage_data()

        next_stage_info = self.STAGES[current_stage + 1]
        return True, f"✅ Advanced to {next_stage_info['name']}"

    def record_crash(self):
        """Record a bot crash"""
        self.stage_data['crash_count'] = self.stage_data.get('crash_count', 0) + 1
        self.save_stage_data()

    def record_disconnect(self):
        """Record a network disconnect"""
        self.stage_data['disconnect_count'] = self.stage_data.get('disconnect_count', 0) + 1
        self.save_stage_data()

    def record_downtime(self, seconds: float):
        """Record downtime in seconds"""
        self.stage_data['total_downtime_seconds'] = self.stage_data.get('total_downtime_seconds', 0) + seconds
        self.save_stage_data()

    def get_reliability_metrics(self) -> Dict:
        """Get reliability metrics (crashes, disconnects, uptime)"""
        now = datetime.now()
        test_start = self.stage_data['test_start_time']
        total_time = (now - test_start).total_seconds()
        downtime = self.stage_data.get('total_downtime_seconds', 0)
        uptime_pct = ((total_time - downtime) / total_time * 100) if total_time > 0 else 100

        return {
            'crash_count': self.stage_data.get('crash_count', 0),
            'disconnect_count': self.stage_data.get('disconnect_count', 0),
            'total_downtime_seconds': downtime,
            'total_downtime_hours': downtime / 3600,
            'uptime_pct': uptime_pct,
            'total_time_hours': total_time / 3600
        }

    def reset_stage(self, stage: int = 1):
        """Reset to a specific stage (for testing or restart)"""
        self.stage_data['current_stage'] = stage
        self.stage_data['stage_start_time'] = datetime.now()
        self.stage_data['ready_to_advance'] = False
        self.save_stage_data()


def main():
    """Test stage manager"""
    manager = StageManager()

    print("=== STAGE MANAGER TEST ===\n")

    # Get current stage info
    stage_info = manager.get_current_stage_info()
    print(f"Current Stage: {stage_info['stage_name']}")
    print(f"Description: {stage_info['stage_description']}")
    print(f"Days Elapsed: {stage_info['days_elapsed']}")
    print(f"Target Days: {stage_info['target_days']}")
    print()

    # Test criteria evaluation
    test_metrics = {
        'days_elapsed': 3,
        'total_trades': 15,
        'win_rate': 55.0,
        'total_return_pct': 3.5,
        'max_drawdown_pct': 8.0,
        'profit_factor': 1.8,
        'sharpe_ratio': 2.5,
        'uptime_pct': 95.0
    }

    ready, evaluation = manager.evaluate_stage_criteria(test_metrics)
    print("=== CRITERIA EVALUATION ===")
    print(f"Ready to Advance: {ready}")
    print(f"Checks Passed: {evaluation['passed']}/{evaluation['total']}")
    print()

    for check in evaluation['checks']:
        status = "✅" if check['passed'] else "❌"
        print(f"{status} {check['criterion']}: {check['current']} (target: {check['target']})")

    # Reliability metrics
    print("\n=== RELIABILITY METRICS ===")
    reliability = manager.get_reliability_metrics()
    print(f"Crashes: {reliability['crash_count']}")
    print(f"Disconnects: {reliability['disconnect_count']}")
    print(f"Uptime: {reliability['uptime_pct']:.1f}%")


if __name__ == "__main__":
    main()
