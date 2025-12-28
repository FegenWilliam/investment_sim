#!/usr/bin/env python3
"""Quick test script for themed investments"""

import sys
sys.path.insert(0, '/home/user/investment_sim')

from investment_sim import QuantumSingularity, ElfQueenWater, Player

def test_themed_investments():
    print("Testing Themed Investments")
    print("="*60)

    # Test Quantum Singularity
    print("\n1. Testing Quantum Singularity")
    qs = QuantumSingularity()
    print(f"   {qs}")
    print(f"   Monthly return for 5 units: ${qs.calculate_monthly_return(5):.2f}")

    # Test Elf Queen's Water
    print("\n2. Testing Elf Queen's Water")
    eqw = ElfQueenWater()
    print(f"   {eqw}")
    for i in range(10):
        eqw.update_price()
    print(f"   After 10 updates: {eqw}")

    # Test Player buying
    print("\n3. Testing Player purchases")
    player = Player("TestPlayer", 50000.0)
    print(f"   Starting cash: ${player.cash:.2f}")

    # Buy Quantum Singularity
    success, msg = player.buy_quantum_singularity(qs, 3)
    print(f"   Buy QS: {msg}")
    print(f"   Cash after: ${player.cash:.2f}")
    print(f"   QS units: {player.quantum_singularity_units}")

    # Buy Elf Queen's Water
    success, msg = player.buy_elf_queen_water(eqw, 5)
    print(f"   Buy Elf Queen's Water: {msg}")
    print(f"   EQW vials: {player.elf_queen_water_vials}")

    # Apply monthly income
    income = player.apply_quantum_singularity_income(qs)
    print(f"\n4. Monthly QS income: ${income:.2f}")
    print(f"   Cash after income: ${player.cash:.2f}")

    # Sell Elf Queen's Water
    success, msg = player.sell_elf_queen_water(eqw, 2)
    print(f"\n5. Sell Elf Queen's Water: {msg}")
    print(f"   EQW vials remaining: {player.elf_queen_water_vials}")
    print(f"   Cash: ${player.cash:.2f}")

    print("\n" + "="*60)
    print("All tests passed!")

if __name__ == "__main__":
    test_themed_investments()
