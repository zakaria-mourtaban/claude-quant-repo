#!/usr/bin/env python3
"""
Stage Advancement Script

Attempts to advance to the next stage if criteria are met.
"""

import sys
sys.path.insert(0, '.')

from live_tracker import LivePerformanceTracker
from stage_manager import StageManager


def main():
    """Attempt to advance stage"""
    tracker = LivePerformanceTracker()
    manager = StageManager()

    # Update tracker from Freqtrade
    tracker.update_from_freqtrade()

    # Get current status
    status = tracker.get_current_status()

    # Get stage info
    stage_info = manager.get_current_stage_info()
    current_stage = stage_info['stage_number']

    print("="*80)
    print("                      STAGE ADVANCEMENT")
    print("="*80)
    print()
    print(f"Current Stage: {stage_info['stage_name']}")
    print()

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

    # Evaluate criteria first
    ready, evaluation = manager.evaluate_stage_criteria(performance_metrics)

    print("📊 Current Performance:")
    print(f"   Days Elapsed:   {status['days_elapsed']}")
    print(f"   Total Trades:   {status['total_trades']}")
    print(f"   Win Rate:       {status['win_rate']:.1f}%")
    print(f"   Return:         {status['total_return_pct']:+.2f}%")
    print(f"   Max Drawdown:   {status['max_drawdown_pct']:.2f}%")
    print(f"   Profit Factor:  {status['profit_factor']:.2f}")
    print(f"   Sharpe Ratio:   {status['sharpe_ratio']:.2f}")
    print(f"   Uptime:         {status['uptime_pct']:.1f}%")
    print()

    if not ready:
        print("❌ ADVANCEMENT FAILED")
        print()
        print("Not all criteria are met. Failed criteria:")
        print()
        for check in evaluation['checks']:
            if not check['passed']:
                print(f"   ❌ {check['criterion']}")
                print(f"      Current: {check['current']:.2f} | Target: {check['target']:.2f}")
        print()
        print("💡 Run evaluation to see details:")
        print("   python monitoring/evaluate_stage.py")
        print()
        sys.exit(1)

    # Ask for confirmation
    print("✅ ALL CRITERIA MET!")
    print()
    print(f"You are about to advance from Stage {current_stage} to Stage {current_stage + 1}")
    print()

    if current_stage >= 3:
        print("🎉 This is the FINAL STAGE!")
        print("   Completing this will mark your bot as ready for live trading.")
        print()

    response = input("Do you want to advance? (yes/no): ")
    print()

    if response.lower() != 'yes':
        print("Advancement cancelled.")
        sys.exit(0)

    # Attempt to advance
    success, message = manager.advance_stage(performance_metrics)

    if success:
        print("="*80)
        print("                     🎉 ADVANCEMENT SUCCESSFUL! 🎉")
        print("="*80)
        print()
        print(message)
        print()

        if current_stage >= 3:
            print("🎊 CONGRATULATIONS! 🎊")
            print()
            print("You have completed all 3 stages successfully!")
            print("Your bot has demonstrated:")
            print("   ✅ Stability and reliability")
            print("   ✅ Consistent positive performance")
            print("   ✅ Strong risk management")
            print()
            print("🚀 NEXT STEPS:")
            print()
            print("1. Generate final report:")
            print("   python monitoring/generate_final_report.py")
            print()
            print("2. Consider deploying to Bybit Testnet (virtual funds):")
            print("   - Get API keys: https://testnet.bybit.com")
            print("   - Update .env with keys")
            print("   - Run: ./scripts/start_testnet.sh")
            print()
            print("3. If testnet successful, consider live trading:")
            print("   - Start with 1-5% of total capital")
            print("   - Monitor closely for first 2 weeks")
            print("   - Scale up gradually")
            print()
        else:
            new_stage_info = manager.get_current_stage_info()
            print(f"📊 New Stage: {new_stage_info['stage_name']}")
            print(f"   {new_stage_info['stage_description']}")
            print()
            print(f"⏱️  Target Duration: {new_stage_info['target_days']} days")
            print()
            print("🎯 New Criteria:")
            for criterion, value in new_stage_info['criteria'].items():
                criterion_name = criterion.replace('_', ' ').title()
                print(f"   • {criterion_name}: {value}")
            print()
            print("💡 The bot continues running. Monitor your progress:")
            print("   python monitoring/evaluate_stage.py")
            print()

        print("="*80)
        print()

    else:
        print("="*80)
        print("                     ❌ ADVANCEMENT FAILED")
        print("="*80)
        print()
        print(message)
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
