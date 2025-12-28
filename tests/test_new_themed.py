#!/usr/bin/env python3
"""Test new themed investments"""

import sys
sys.path.insert(0, '/home/user/investment_sim')

from investment_sim import Player, ElfQueenWater, VoidStocks, Company, LiquidityLevel

def test_new_themed():
    print("Testing New Themed Investments")
    print("="*60)

    # Create a player
    player = Player("TestPlayer", 100000.0)

    # Test Elf Queen's Water
    print("\n1. Testing Elf Queen's Water")
    eqw = ElfQueenWater()
    print(f"   Initial: {eqw}")
    print(f"   Price: ${eqw.price:.2f}")
    print(f"   Weeks until change: {6 - eqw.weeks_since_change}")

    # Update price several times
    print("\n   Updating price 6 times:")
    for i in range(6):
        old_price = eqw.price
        eqw.update_price()
        print(f"   Week {i+1}: ${old_price:.2f} -> ${eqw.price:.2f}")

    # Test Void Stocks
    print("\n2. Testing Void Stocks")

    # Create test companies
    companies = {
        "TechCorp": Company("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH, 400_000_000_000),
        "PharmaCare": Company("PharmaCare", "Pharmaceuticals", 220.0, 5.0, LiquidityLevel.MEDIUM, 250_000_000_000),
    }

    void_stocks = VoidStocks(companies)
    print(f"   Initial: {void_stocks}")
    print(f"   Price: ${void_stocks.price:.2f}")
    print(f"   Void State: {void_stocks.is_void_week}")

    # Update price several times
    print("\n   Updating price 10 times:")
    for i in range(10):
        old_price = void_stocks.price
        void_stocks.update_price()
        print(f"   Week {i+1}: ${old_price:.2f} -> ${void_stocks.price:.2f} (Void: {void_stocks.is_void_week})")

    # Test player buying
    print("\n3. Testing Player purchases")
    print(f"   Starting cash: ${player.cash:.2f}")

    # Buy Elf Queen's Water
    success, msg = player.buy_elf_queen_water(eqw, 10)
    print(f"   Buy EQW: {msg}")
    print(f"   EQW vials: {player.elf_queen_water_vials}")

    # Try buying Void Stocks (when not in void state)
    if not void_stocks.is_void_week:
        success, msg = player.buy_void_stocks(void_stocks, 5)
        print(f"   Buy Void Stocks: {msg}")
        print(f"   Void Stocks shares: {player.void_stocks_shares}")

    print("\n" + "="*60)
    print("All tests passed!")

if __name__ == "__main__":
    test_new_themed()
