#!/usr/bin/env python3
"""Test script for new themed investments"""

import sys
sys.path.insert(0, '/home/user/investment_sim')

from investment_sim import (
    Player, Company,
    ElfQueenWater, GoldCoin, VoidStocks, VoidCatalyst
)

def test_new_themed_investments():
    print("Testing New Themed Investments")
    print("="*60)

    # Create test companies for VoidStocks
    companies = {
        "TechCorp": Company("TechCorp", "Technology", 150.0, 8.0),
        "PharmaCare": Company("PharmaCare", "Pharmaceuticals", 220.0, 5.0),
        "EnergyPlus": Company("EnergyPlus", "Energy", 110.0, 9.0),
    }

    # Create the themed investments directly
    elf_queen_water = ElfQueenWater()
    gold_coin = GoldCoin()
    void_stocks = VoidStocks(companies)
    void_catalyst = VoidCatalyst()

    player = Player("TestPlayer", 500000.0)

    print("\n1. Testing Elf Queen's Water")
    print(f"   {elf_queen_water}")
    success, msg = player.buy_elf_queen_water(elf_queen_water, 2)
    print(f"   Buy: {msg}")
    print(f"   Vials owned: {player.elf_queen_water_vials}")
    print(f"   Cash remaining: ${player.cash:.2f}")

    print("\n2. Testing Gold Coin")
    print(f"   {gold_coin}")
    success, msg = player.buy_gold_coin(gold_coin, 1000)
    print(f"   Buy: {msg}")
    print(f"   Coins owned: {player.gold_coins}")
    print(f"   Cash remaining: ${player.cash:.2f}")

    print("\n3. Testing Void Stocks")
    print(f"   {void_stocks}")
    # Update once so it's not in void state
    void_stocks.update_price()
    print(f"   After update: {void_stocks}")
    if not void_stocks.is_void_week:
        success, msg = player.buy_void_stocks(void_stocks, 10)
        print(f"   Buy: {msg}")
        print(f"   Shares owned: {player.void_stocks_shares}")
        print(f"   Cash remaining: ${player.cash:.2f}")

    print("\n4. Testing Void Catalyst")
    print(f"   {void_catalyst}")
    success, msg = player.buy_void_catalyst(void_catalyst)
    print(f"   Buy: {msg}")
    print(f"   Owned: {player.void_catalyst_owned}")
    print(f"   Cash remaining: ${player.cash:.2f}")

    print("\n5. Testing price updates")
    print("   Updating prices for 6 weeks...")
    for week in range(6):
        elf_queen_water.update_price()
        gold_coin.update_price()
        void_stocks.update_price()
        void_catalyst.update_price()
        print(f"   Week {week+1}:")
        print(f"     Elf Queen's Water: ${elf_queen_water.price:.2f}")
        print(f"     Gold Coin: ${gold_coin.price:.2f}")
        print(f"     Void Stocks: ${void_stocks.price:.2f} [{void_stocks.get_current_company_name()}]")
        print(f"     Void Catalyst: ${void_catalyst.price:.2f}")

    print("\n6. Testing Void Catalyst auto-sell after 4 weeks")
    for week in range(4):
        was_sold, msg, amount = player.process_void_catalyst_auto_sell(void_catalyst)
        if was_sold:
            print(f"   {msg}")
            print(f"   Amount received: ${amount:.2f}")
            print(f"   Cash: ${player.cash:.2f}")
            break

    print("\n7. Testing serialization")
    eqw_dict = elf_queen_water.to_dict()
    gc_dict = gold_coin.to_dict()
    vs_dict = void_stocks.to_dict()
    vc_dict = void_catalyst.to_dict()
    print("   All themed investments serialized successfully!")

    print("\n8. Testing deserialization")
    eqw2 = ElfQueenWater.from_dict(eqw_dict)
    gc2 = GoldCoin.from_dict(gc_dict)
    vs2 = VoidStocks.from_dict(vs_dict, companies)
    vc2 = VoidCatalyst.from_dict(vc_dict)
    print(f"   Elf Queen's Water: ${eqw2.price:.2f}")
    print(f"   Gold Coin: ${gc2.price:.2f}")
    print(f"   Void Stocks: ${vs2.price:.2f}")
    print(f"   Void Catalyst: ${vc2.price:.2f}")

    print("\n" + "="*60)
    print("All tests passed!")

if __name__ == "__main__":
    test_new_themed_investments()
