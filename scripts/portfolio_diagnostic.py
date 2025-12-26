#!/usr/bin/env python3
"""
Portfolio Diagnostic Tool
Analyzes your portfolio and breaks down the borrowed amount
"""

def analyze_portfolio():
    """Analyze the portfolio shown in the issue"""
    print("="*60)
    print("PORTFOLIO DIAGNOSTIC ANALYSIS")
    print("="*60)
    print()

    # Current state
    cash = 8000.00
    borrowed = 16011.50

    # Investments
    techcorp = 79.9680 * 150.00  # $11,995.20
    rock_friends = 25.6082 * 78.00  # $1,997.44
    blue_energy = 23.9885 * 125.00  # $2,998.56
    quantum = 1 * 1000.00  # $1,000.00

    total_investments = techcorp + rock_friends + blue_energy + quantum
    equity = cash + total_investments - borrowed
    total_net_worth = equity

    print(f"Current State:")
    print(f"  Cash: ${cash:,.2f}")
    print(f"  Borrowed: ${borrowed:,.2f}")
    print(f"  Equity (Net - Debt): ${equity:,.2f}")
    print()

    print(f"Investments:")
    print(f"  TechCorp: ${techcorp:,.2f}")
    print(f"  Rock Friends Inc.: ${rock_friends:,.2f}")
    print(f"  Blue Energy Industries: ${blue_energy:,.2f}")
    print(f"  Quantum Singularity: ${quantum:,.2f}")
    print(f"  ───────────────────────────")
    print(f"  Total Investments: ${total_investments:,.2f}")
    print()

    print(f"Total Net Worth: ${total_net_worth:,.2f}")
    print()
    print("="*60)
    print("ANALYSIS OF BORROWED AMOUNT")
    print("="*60)
    print()

    # Expected borrowing if only TechCorp had 2x leverage
    expected_techcorp_borrowed = 6000.00  # $6k cash * 2x = $12k position, $6k borrowed

    print(f"If you invested in TechCorp with 2x leverage:")
    print(f"  Cash invested: $6,000")
    print(f"  Borrowed: $6,000")
    print(f"  Total position: $12,000 ✓ (matches your ${techcorp:,.2f})")
    print()

    remaining_borrowed = borrowed - expected_techcorp_borrowed
    print(f"Remaining borrowed to explain: ${remaining_borrowed:,.2f}")
    print()

    # Hypothesis: Other investments also used leverage
    print("Possible explanations for the extra borrowed amount:")
    print()

    # Scenario 1: All investments used 2x leverage
    total_non_techcorp = rock_friends + blue_energy + quantum
    potential_borrowed_others = total_non_techcorp / 2  # If they used 2x leverage
    print(f"1. If other investments (${ total_non_techcorp:,.2f}) used 2x leverage:")
    print(f"   Expected borrowed: ${potential_borrowed_others:,.2f}")
    total_scenario1 = expected_techcorp_borrowed + potential_borrowed_others
    print(f"   Total borrowed: ${total_scenario1:,.2f}")
    print(f"   Difference from actual: ${abs(borrowed - total_scenario1):,.2f}")
    print()

    # Scenario 2: Used "Borrow Money" function
    extra_borrowed = remaining_borrowed - potential_borrowed_others
    print(f"2. If you used the 'Borrow Money' function:")
    print(f"   Additional borrowed beyond investments: ${extra_borrowed:,.2f}")
    print()

    # Scenario 3: Interest accumulation
    print(f"3. Interest accumulation:")
    print(f"   Interest rate: 0.115% per week")
    # Calculate how many weeks of interest on $9k would reach $16k
    principal = 9000  # Rough estimate of base borrowed
    target = borrowed
    weeks_needed = 0
    current = principal
    while current < target and weeks_needed < 200:
        current *= 1.00115
        weeks_needed += 1

    if weeks_needed < 200:
        print(f"   If you borrowed ~${principal:,.2f} initially,")
        print(f"   it would take ~{weeks_needed} weeks to reach ${borrowed:,.2f}")
    else:
        print(f"   Interest alone cannot explain this amount")
    print()

    # Scenario 4: Very high leverage on one position
    print(f"4. If TechCorp was purchased with higher leverage:")
    actual_leverage = techcorp / (techcorp - expected_techcorp_borrowed) if (techcorp - expected_techcorp_borrowed) > 0 else 0
    print(f"   If ~${techcorp:,.2f} position with ${expected_techcorp_borrowed + (remaining_borrowed - potential_borrowed_others):,.2f} borrowed")
    possible_techcorp_leverage = techcorp / (techcorp - (expected_techcorp_borrowed + (remaining_borrowed - potential_borrowed_others)))
    if possible_techcorp_leverage > 0 and possible_techcorp_leverage < 10:
        print(f"   That would be ~{possible_techcorp_leverage:.1f}x leverage")
    print()

    print("="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    print()
    print("To understand what happened:")
    print("1. Check your game's transaction history (if available)")
    print("2. Check if you used the 'Borrow Money' menu option")
    print("3. Check how many weeks/turns have passed (interest adds up)")
    print("4. Verify the leverage used for each investment")
    print()
    print("The good news:")
    print(f"- Your leverage ratio is 1.60x (well below max of 5.00x)")
    print(f"- Your equity is ${equity:,.2f} (healthy)")
    print(f"- No immediate margin call risk")

if __name__ == "__main__":
    analyze_portfolio()
