#!/usr/bin/env python3
"""Test script for void stock counter functionality"""

import sys
sys.path.insert(0, '/home/user/investment_sim')

from investment_sim import Player, Company, VoidStocks

def test_void_counter():
    print("Testing Void Stock Counter Functionality")
    print("="*60)

    # Create test companies for VoidStocks
    companies = {
        "TechCorp": Company("TechCorp", "Technology", 150.0, 8.0),
        "PharmaCare": Company("PharmaCare", "Pharmaceuticals", 220.0, 5.0),
        "EnergyPlus": Company("EnergyPlus", "Energy", 110.0, 9.0),
    }

    void_stocks = VoidStocks(companies)
    player = Player("Alice", 500000.0)

    print("\n1. Initial state (void week)")
    print(f"   Week: {void_stocks.weeks_elapsed}, Is void: {void_stocks.is_void_week}")
    print(f"   {void_stocks}")

    # Week 1 - transition to active week
    print("\n2. Week 1 - transition to active (can buy)")
    void_stocks.update_price()
    print(f"   Week: {void_stocks.weeks_elapsed}, Is void: {void_stocks.is_void_week}")
    print(f"   {void_stocks}")

    # Buy some shares
    success, msg = player.buy_void_stocks(void_stocks, 100)
    print(f"   Buy 100 shares: {msg}")
    print(f"   Purchases tracked: {len(player.void_stocks_purchases)}")
    print(f"   Purchase details: {player.void_stocks_purchases[0]}")

    # Week 2 - transition to void (first void state for our purchase)
    print("\n3. Week 2 - transition to void (1st void state)")
    void_stocks.update_price()
    print(f"   Week: {void_stocks.weeks_elapsed}, Is void: {void_stocks.is_void_week}")
    messages = player.process_void_state_transition(void_stocks)
    print(f"   Void state counter incremented")
    print(f"   Purchase details: {player.void_stocks_purchases[0]}")
    print(f"   Messages: {messages if messages else 'None'}")

    # Week 3 - active week
    print("\n4. Week 3 - active week (buy more shares)")
    void_stocks.update_price()
    print(f"   Week: {void_stocks.weeks_elapsed}, Is void: {void_stocks.is_void_week}")
    success, msg = player.buy_void_stocks(void_stocks, 50)
    print(f"   Buy 50 shares: {msg}")
    print(f"   Total purchases tracked: {len(player.void_stocks_purchases)}")
    print(f"   First purchase: {player.void_stocks_purchases[0]}")
    print(f"   Second purchase: {player.void_stocks_purchases[1]}")

    # Simulate void states
    print("\n5. Simulating void states...")
    for i in range(4, 12):  # Weeks 4-11 (4 more void states)
        void_stocks.update_price()
        messages = player.process_void_state_transition(void_stocks)

        if void_stocks.is_void_week:
            print(f"   Week {i}: VOID STATE")
            if player.void_stocks_purchases:
                for idx, p in enumerate(player.void_stocks_purchases):
                    print(f"      Purchase {idx+1}: {p['shares']} shares, void count: {p['void_state_count']}")
            if messages:
                for msg in messages:
                    print(f"      {msg}")
        else:
            print(f"   Week {i}: Active")

        print(f"      Total shares remaining: {player.void_stocks_shares}")

        # Check for warnings
        if not void_stocks.is_void_week:
            has_warning, at_risk = player.check_void_stock_warning(void_stocks)
            if has_warning:
                print(f"      ⚠️  WARNING: {sum(p['shares'] for p in at_risk)} shares at risk next week!")

    print("\n" + "="*60)
    print("Test complete!")
    print(f"Final shares: {player.void_stocks_shares}")
    print(f"Remaining purchases: {player.void_stocks_purchases}")

if __name__ == "__main__":
    test_void_counter()
