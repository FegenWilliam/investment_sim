#!/usr/bin/env python3
"""Test script for Mystical Lender functionality"""

from investment_sim import Player, Company, MysticalLender, LiquidityLevel

# Create test objects
player = Player("TestPlayer", starting_cash=50000.0)
company = Company("TestCompany", industry="Technology", initial_price=100.0,
                  volatility=5.0, liquidity=LiquidityLevel.MEDIUM,
                  market_cap=10_000_000.0)
mystical_lender = MysticalLender()

print("="*60)
print("MYSTICAL LENDER TEST")
print("="*60)

# Test 1: Check initial state
print("\n1. Initial State:")
print(f"   Player cash: ${player.cash:.2f}")
print(f"   Mystical Lender debt: ${player.mystical_lender_debt:.2f}")

# Test 2: Accept the loan
print("\n2. Accepting Mystical Lender loan:")
success, msg = player.accept_mystical_lender(mystical_lender)
print(f"   Success: {success}")
print(f"   Message: {msg}")
print(f"   Player cash: ${player.cash:.2f}")
print(f"   Mystical Lender debt: ${player.mystical_lender_debt:.2f}")

# Test 3: Try to accept again (should fail)
print("\n3. Trying to accept loan again:")
success, msg = player.accept_mystical_lender(mystical_lender)
print(f"   Success: {success}")
print(f"   Message: {msg}")

# Test 4: Test slippage without debt (for comparison)
player2 = Player("TestPlayer2", starting_cash=50000.0)
shares = 100
slippage_normal = company.calculate_slippage(shares, is_buy=True, slippage_multiplier=1.0)
slippage_with_debt = company.calculate_slippage(shares, is_buy=True, slippage_multiplier=5.0)

print("\n4. Slippage Comparison (buying 100 shares):")
print(f"   Normal slippage factor: {slippage_normal:.6f}")
print(f"   With 5x multiplier: {slippage_with_debt:.6f}")
print(f"   Multiplier effect: {slippage_with_debt / slippage_normal:.2f}x")

# Test 5: Repay part of the debt
print("\n5. Repaying $100,000 of debt:")
player.cash = 150000  # Give player enough cash to repay
success, msg = player.repay_mystical_lender(100000)
print(f"   Success: {success}")
print(f"   Message: {msg}")
print(f"   Player cash: ${player.cash:.2f}")
print(f"   Remaining debt: ${player.mystical_lender_debt:.2f}")

# Test 6: Repay remaining debt
print("\n6. Repaying remaining debt:")
success, msg = player.repay_mystical_lender()  # Repay all
print(f"   Success: {success}")
print(f"   Message: {msg}")
print(f"   Player cash: ${player.cash:.2f}")
print(f"   Remaining debt: ${player.mystical_lender_debt:.2f}")

# Test 7: Verify serialization
print("\n7. Serialization test:")
player3 = Player("TestPlayer3", starting_cash=100000.0)
player3.mystical_lender_debt = 250000.0
player_dict = player3.to_dict()
print(f"   Original debt: ${player3.mystical_lender_debt:.2f}")
print(f"   Serialized: {player_dict.get('mystical_lender_debt')}")

restored_player = Player.from_dict(player_dict)
print(f"   Restored debt: ${restored_player.mystical_lender_debt:.2f}")
print(f"   Match: {player3.mystical_lender_debt == restored_player.mystical_lender_debt}")

print("\n" + "="*60)
print("ALL TESTS COMPLETED!")
print("="*60)
