#!/usr/bin/env python3
"""
Stage Criteria Evaluation

Evaluates whether current stage criteria are met.
Shows detailed breakdown of each criterion.
"""

import sys
sys.path.insert(0, '.')

from live_tracker import LivePerformanceTracker
from stage_manager import StageManager


def main():
    """Evaluate current stage criteria"""
    tracker = LivePerformanceTracker()
    manager = StageManager()

    # Update tracker from Freqtrade
    tracker.update_from_freqtrade()

    # Get current status
    status = tracker.get_current_status()

    # Get stage info
    stage_info = manager.get_current_stage_info()

    # Prepare metrics for evaluation
    performance_metrics = {
        'days_elapsed': status['days_elapsed'],
        'total_trades': status['total_trades'],
        'win_rate': status['win_rate'],
        'total_return_pct': status['total_return_pct'],
        'max_drawdown_pct': status['max_drawdown_pct'],
        'profit_factor': status['profit_factor'],
        'sharpe_ratio': status['sharpe_ratio'],
        'uptime_pct': status['uptime_pct']
    }

    # Evaluate criteria
    ready, evaluation = manager.evaluate_stage_criteria(performance_metrics)

    # Print report
    print("="*80)
    print("                     STAGE CRITERIA EVALUATION")
    print("="*80)
    print()
    print(f"📊 {stage_info['stage_name']}")
    print(f"   {stage_info['stage_description']}")
    print()
    print(f"⏱️  Stage Progress:")
    print(f"   Days Elapsed: {stage_info['days_elapsed']} of {stage_info['target_days']}")
    progress_pct = min((stage_info['days_elapsed'] / stage_info['target_days']) * 100, 100)
    bar_length = 50
    filled = int(bar_length * progress_pct / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"   [{bar}] {progress_pct:.0f}%")
    print()
    print("="*80)
    print("                        CRITERIA CHECKLIST")
    print("="*80)
    print()

    # Print each criterion
    for i, check in enumerate(evaluation['checks'], 1):
        status_icon = "✅ PASS" if check['passed'] else "❌ FAIL"
        required = "⚠️  REQUIRED" if check.get('required', True) else "Optional"

        print(f"{i}. {check['criterion']}")
        print(f"   Status: {status_icon} ({required})")
        print(f"   Current: {check['current']:.2f}")
        print(f"   Target:  {check['target']:.2f}")
        print()

    print("="*80)
    print("                           SUMMARY")
    print("="*80)
    print()
    print(f"Checks Passed:  {evaluation['passed']}/{evaluation['total']}")
    print(f"Checks Failed:  {evaluation['failed']}/{evaluation['total']}")
    print(f"Success Rate:   {evaluation['passed']/evaluation['total']*100:.0f}%")
    print()

    if ready:
        print("✅ ✅ ✅ ALL CRITERIA MET! ✅ ✅ ✅")
        print()
        print("You are ready to advance to the next stage!")
        print()
        print("Run this command to advance:")
        print("   python monitoring/advance_stage.py")
        print()
    else:
        print("⏳ NOT READY TO ADVANCE YET")
        print()
        print("Failed Criteria:")
        for check in evaluation['checks']:
            if not check['passed']:
                shortfall = check['target'] - check['current']
                print(f"   • {check['criterion']}")
                if 'min_' in check['criterion'].lower() or '>' in check['criterion']:
                    print(f"     Need {abs(shortfall):.2f} more")
                else:
                    print(f"     Need to reduce by {abs(shortfall):.2f}")
        print()
        print("💡 Keep trading and check back later!")
        print("   Run: python monitoring/evaluate_stage.py")
        print()

    print("="*80)
    print()

    # Return exit code based on readiness
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
