#!/usr/bin/env python3
"""Quick test script for themed investments"""

import sys
sys.path.insert(0, '/home/user/investment_sim')

from investment_sim import QuantumSingularity, Gold, HolyWater, Player

def test_themed_investments():
    print("Testing Themed Investments")
    print("="*60)

    # Test Quantum Singularity
    print("\n1. Testing Quantum Singularity")
    qs = QuantumSingularity()
    print(f"   {qs}")
    print(f"   Monthly return for 5 units: ${qs.calculate_monthly_return(5):.2f}")

    # Test Gold
    print("\n2. Testing Gold")
    gold = Gold()
    print(f"   {gold}")
    gold.update_price()
    print(f"   After update: {gold}")

    # Test Holy Water
    print("\n3. Testing Holy Water")
    hw = HolyWater()
    print(f"   {hw}")
    for i in range(10):
        hw.update_price()
    print(f"   After 10 updates: {hw}")

    # Test Player buying
    print("\n4. Testing Player purchases")
    player = Player("TestPlayer", 50000.0)
    print(f"   Starting cash: ${player.cash:.2f}")

    # Buy Quantum Singularity
    success, msg = player.buy_quantum_singularity(qs, 3)
    print(f"   Buy QS: {msg}")
    print(f"   Cash after: ${player.cash:.2f}")
    print(f"   QS units: {player.quantum_singularity_units}")

    # Buy Gold
    success, msg = player.buy_gold(gold, 5)
    print(f"   Buy Gold: {msg}")
    print(f"   Gold ounces: {player.gold_ounces}")

    # Buy Holy Water
    success, msg = player.buy_holy_water(hw, 10)
    print(f"   Buy HW: {msg}")
    print(f"   HW vials: {player.holy_water_vials}")

    # Apply monthly income
    income = player.apply_quantum_singularity_income(qs)
    print(f"\n5. Monthly QS income: ${income:.2f}")
    print(f"   Cash after income: ${player.cash:.2f}")

    # Sell Gold
    success, msg = player.sell_gold(gold, 2)
    print(f"\n6. Sell Gold: {msg}")
    print(f"   Gold ounces remaining: {player.gold_ounces}")
    print(f"   Cash: ${player.cash:.2f}")

    # Sell Holy Water
    success, msg = player.sell_holy_water(hw, 5)
    print(f"\n7. Sell HW: {msg}")
    print(f"   HW vials remaining: {player.holy_water_vials}")
    print(f"   Cash: ${player.cash:.2f}")

    print("\n" + "="*60)
    print("All tests passed!")

if __name__ == "__main__":
    test_themed_investments()
