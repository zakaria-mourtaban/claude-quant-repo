#!/usr/bin/env python3
"""
Comprehensive Profit Projection Analysis

Shows realistic profit potential with different capital amounts.
"""

def calculate_projections():
    """Calculate profit projections based on backtest performance"""

    # Backtested performance
    monthly_return_pct = 4.12  # From 90-day backtest
    win_rate = 60.0
    max_drawdown = 3.11
    sharpe_ratio = 3.25

    # Annualized (conservative estimate)
    annual_return_pct = monthly_return_pct * 12 * 0.7  # 70% of theoretical (conservative)

    print("="*80)
    print("                  PROFIT PROJECTION ANALYSIS")
    print("="*80)
    print()
    print(f"Based on Backtest Performance:")
    print(f"  • Monthly Return: {monthly_return_pct:.2f}%")
    print(f"  • Win Rate: {win_rate:.1f}%")
    print(f"  • Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"  • Max Drawdown: {max_drawdown:.2f}%")
    print()
    print(f"Conservative Annual Estimate: {annual_return_pct:.1f}%")
    print()
    print("="*80)
    print("              PROFIT PROJECTIONS BY CAPITAL SIZE")
    print("="*80)
    print()

    capital_amounts = [100, 500, 1000, 5000, 10000, 25000, 50000]

    for capital in capital_amounts:
        monthly_profit = capital * (monthly_return_pct / 100) * 0.7  # Conservative
        annual_profit = capital * (annual_return_pct / 100)

        # Compound over time
        month_3 = capital * ((1 + monthly_return_pct * 0.7 / 100) ** 3)
        month_6 = capital * ((1 + monthly_return_pct * 0.7 / 100) ** 6)
        month_12 = capital * ((1 + monthly_return_pct * 0.7 / 100) ** 12)

        print(f"Starting Capital: ${capital:,}")
        print(f"  Monthly Profit:   ${monthly_profit:,.2f}")
        print(f"  Annual Profit:    ${annual_profit:,.2f}")
        print(f"  After 3 months:   ${month_3:,.2f} (+${month_3 - capital:,.2f})")
        print(f"  After 6 months:   ${month_6:,.2f} (+${month_6 - capital:,.2f})")
        print(f"  After 12 months:  ${month_12:,.2f} (+${month_12 - capital:,.2f})")
        print()

    print("="*80)
    print("                  PATH TO $100,000 PROFIT")
    print("="*80)
    print()

    # Calculate time to reach $100k profit from different starting points
    target_profit = 100000
    monthly_rate = monthly_return_pct * 0.7 / 100

    for start_capital in [10000, 25000, 50000]:
        months = 0
        current = start_capital

        while (current - start_capital) < target_profit and months < 120:  # Max 10 years
            current = current * (1 + monthly_rate)
            months += 1

        years = months / 12
        final_amount = current
        total_profit = final_amount - start_capital

        if total_profit >= target_profit:
            print(f"Starting with ${start_capital:,}:")
            print(f"  Time to $100k profit: {years:.1f} years ({months} months)")
            print(f"  Final Amount: ${final_amount:,.2f}")
            print(f"  Total Profit: ${total_profit:,.2f}")
            print()

    print("="*80)
    print("                     RISK ANALYSIS")
    print("="*80)
    print()
    print(f"Maximum Drawdown: {max_drawdown:.2f}%")
    print()
    print("On $10,000 capital:")
    print(f"  Max expected loss: ${10000 * max_drawdown / 100:,.2f}")
    print()
    print("On $50,000 capital:")
    print(f"  Max expected loss: ${50000 * max_drawdown / 100:,.2f}")
    print()
    print("="*80)
    print("                  RECOMMENDATIONS")
    print("="*80)
    print()
    print("1. START SMALL: Begin with $500-1000 to test real conditions")
    print("2. VALIDATE: Run for 3 months before increasing capital")
    print("3. SCALE GRADUALLY: Add 20% more capital each profitable month")
    print("4. RISK MANAGEMENT: Never risk more than you can afford to lose")
    print()
    print("="*80)
    print()
    print("This analysis is based on backtested data.")
    print("Past performance does not guarantee future results.")
    print("Cryptocurrency trading involves risk of loss.")
    print()

if __name__ == "__main__":
    calculate_projections()
