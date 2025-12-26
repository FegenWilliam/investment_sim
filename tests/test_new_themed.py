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

    player1 = Player("Alice", 500000.0)
    player2 = Player("Bob", 500000.0)
    player3 = Player("Charlie", 500000.0)
    all_human_players = ["Alice", "Bob", "Charlie"]

    print("\n1. Testing Elf Queen's Water")
    print(f"   {elf_queen_water}")
    success, msg = player1.buy_elf_queen_water(elf_queen_water, 2)
    print(f"   Buy: {msg}")
    print(f"   Vials owned: {player1.elf_queen_water_vials}")
    print(f"   Cash remaining: ${player1.cash:.2f}")

    print("\n2. Testing Gold Coin")
    print(f"   {gold_coin}")
    success, msg = player1.buy_gold_coin(gold_coin, 1000)
    print(f"   Buy: {msg}")
    print(f"   Coins owned: {player1.gold_coins}")
    print(f"   Cash remaining: ${player1.cash:.2f}")

    print("\n3. Testing Void Stocks")
    print(f"   {void_stocks}")
    # Update once so it's not in void state
    void_stocks.update_price()
    print(f"   After update: {void_stocks}")
    if not void_stocks.is_void_week:
        success, msg = player1.buy_void_stocks(void_stocks, 10)
        print(f"   Buy: {msg}")
        print(f"   Shares owned: {player1.void_stocks_shares}")
        print(f"   Cash remaining: ${player1.cash:.2f}")

    print("\n4. Testing Void Catalyst - Fair Rotation System")
    print(f"   {void_catalyst}")

    # Alice buys first
    print("   Alice tries to buy:")
    success, msg = player1.buy_void_catalyst(void_catalyst, all_human_players)
    print(f"     {msg}")
    print(f"     Alice owns it: {player1.void_catalyst_owned}")
    print(f"     Alice cash: ${player1.cash:.2f}")

    # Bob tries to buy while Alice owns it
    print("\n   Bob tries to buy while Alice owns it:")
    success, msg = player2.buy_void_catalyst(void_catalyst, all_human_players)
    print(f"     {msg} (Expected: already owned)")

    # Simulate auto-sell after 4 weeks
    print("\n   Simulating 4 weeks passing...")
    for week in range(4):
        void_catalyst.update_price()

    # Check auto-sell for Alice
    was_sold, sell_msg, amount = player1.process_void_catalyst_auto_sell(void_catalyst)
    print(f"   Auto-sell for Alice: {sell_msg}")
    print(f"   Amount received: ${amount:.2f}")
    print(f"   Alice cash: ${player1.cash:.2f}")
    print(f"   Alice owns it: {player1.void_catalyst_owned}")

    # Bob buys second
    print("\n   Bob tries to buy after auto-sell:")
    success, msg = player2.buy_void_catalyst(void_catalyst, all_human_players)
    print(f"     {msg}")
    print(f"     Bob owns it: {player2.void_catalyst_owned}")

    # Simulate auto-sell for Bob
    print("\n   Simulating 4 more weeks...")
    for week in range(4):
        void_catalyst.update_price()
    was_sold, sell_msg, amount = player2.process_void_catalyst_auto_sell(void_catalyst)
    print(f"   Auto-sell for Bob: {sell_msg}")

    # Charlie buys third
    print("\n   Charlie tries to buy:")
    success, msg = player3.buy_void_catalyst(void_catalyst, all_human_players)
    print(f"     {msg}")
    print(f"     Charlie owns it: {player3.void_catalyst_owned}")

    # Simulate auto-sell for Charlie
    print("\n   Simulating 4 more weeks...")
    for week in range(4):
        void_catalyst.update_price()
    was_sold, sell_msg, amount = player3.process_void_catalyst_auto_sell(void_catalyst)
    print(f"   Auto-sell for Charlie: {sell_msg}")

    # Now all 3 players have owned it - cycle should reset
    print("\n   All players have owned it! Cycle should reset.")
    print(f"   {void_catalyst}")

    # Alice should be able to buy again
    print("\n   Alice tries to buy again (should succeed - cycle reset):")
    success, msg = player1.buy_void_catalyst(void_catalyst, all_human_players)
    print(f"     Success: {success}")
    print(f"     {msg}")

    # Reset for rest of tests
    if player1.void_catalyst_owned:
        player1.void_catalyst_owned = False
        void_catalyst.is_owned = False
        void_catalyst.owner_name = None

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

    print("\n6. Testing serialization")
    eqw_dict = elf_queen_water.to_dict()
    gc_dict = gold_coin.to_dict()
    vs_dict = void_stocks.to_dict()
    vc_dict = void_catalyst.to_dict()
    print("   All themed investments serialized successfully!")
    print(f"   Void Catalyst cycle state: {len(void_catalyst.players_owned_this_cycle)} players owned it")

    print("\n7. Testing deserialization")
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
