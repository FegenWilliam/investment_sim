#!/usr/bin/env python3
"""
Test script for short selling functionality
"""

import sys
sys.path.insert(0, '/home/user/investment_sim')

from investment_sim import Player, Company, Treasury, LiquidityLevel

def test_short_selling():
    print("Testing Short Selling Functionality")
    print("=" * 60)

    # Create test entities
    player = Player("Test Player", starting_cash=10000.0)
    company = Company("TestCorp", "Technology", initial_price=100.0, volatility=5.0, liquidity=LiquidityLevel.HIGH)
    treasury = Treasury()
    companies = {"TestCorp": company}

    print(f"\nInitial State:")
    print(f"  Cash: ${player.cash:.2f}")
    print(f"  Net Worth: ${player.calculate_net_worth(companies, treasury):.2f}")
    print(f"  Equity: ${player.calculate_equity(companies, treasury):.2f}")

    # Test 1: Short sell some shares
    print(f"\n--- Test 1: Short Sell 50 shares at ${company.price:.2f} ---")
    success, message = player.short_sell(company, 50, companies, treasury)
    print(f"Success: {success}")
    print(f"Message: {message}")
    print(f"Cash after short: ${player.cash:.2f}")
    print(f"Short positions: {player.short_positions}")
    print(f"Net Worth: ${player.calculate_net_worth(companies, treasury):.2f}")
    print(f"Equity: ${player.calculate_equity(companies, treasury):.2f}")

    # Test 2: Price movement (simulate stock going up - bad for short)
    print(f"\n--- Test 2: Stock price increases to $120 ---")
    company.price = 120.0
    print(f"New Net Worth: ${player.calculate_net_worth(companies, treasury):.2f}")
    print(f"New Equity: ${player.calculate_equity(companies, treasury):.2f}")
    print(f"Unrealized loss: ${(120.0 - 100.0) * 50:.2f}")

    # Test 3: Apply short borrow fees
    print(f"\n--- Test 3: Apply weekly short borrow fees ---")
    fees = player.apply_short_borrow_fees(companies)
    print(f"Short borrow fees: ${fees:.2f}")
    print(f"Cash after fees: ${player.cash:.2f}")

    # Test 4: Cover short position
    print(f"\n--- Test 4: Cover 30 shares at ${company.price:.2f} ---")
    success, message = player.cover_short(company, 30)
    print(f"Success: {success}")
    print(f"Message: {message}")
    print(f"Cash after cover: ${player.cash:.2f}")
    print(f"Remaining short positions: {player.short_positions}")

    # Test 5: Check margin call with short positions
    print(f"\n--- Test 5: Test margin call logic ---")
    margin_call = player.check_margin_call(companies, treasury)
    print(f"Margin call triggered: {margin_call}")
    print(f"Current Equity: ${player.calculate_equity(companies, treasury):.2f}")

    # Test 6: Portfolio display
    print(f"\n--- Test 6: Display Portfolio ---")
    player.display_portfolio(companies, treasury)

    # Test 7: Serialization
    print(f"\n--- Test 7: Serialization Test ---")
    player_dict = player.to_dict()
    print(f"Serialized short_positions: {player_dict['short_positions']}")

    restored_player = Player.from_dict(player_dict)
    print(f"Restored short_positions: {restored_player.short_positions}")
    print(f"Serialization successful: {restored_player.short_positions == player.short_positions}")

    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    test_short_selling()
