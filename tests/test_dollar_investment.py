#!/usr/bin/env python3
"""Test the new dollar-based investment system with fractional shares and leverage"""

from investment_sim import Company, Player, Treasury, LiquidityLevel

def test_fractional_shares():
    """Test that fractional shares work correctly"""
    print("Testing fractional shares...")

    # Create a company and player
    company = Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.HIGH)
    player = Player("TestPlayer", starting_cash=10000.0)
    treasury = Treasury()
    companies = {"TestCorp": company}

    # Buy $250 worth (should get 2.5 shares at $100/share)
    success, msg = player.buy_stock(company, 250.0, leverage=1.0, companies=companies, treasury=treasury)
    print(f"Buy result: {success}, {msg}")

    # Check portfolio
    shares = player.portfolio.get("TestCorp", 0)
    print(f"Shares owned: {shares:.4f}")
    assert shares > 2.4 and shares < 2.6, f"Expected ~2.5 shares, got {shares}"

    # Check cash
    expected_cash = 10000 - 250
    print(f"Cash remaining: ${player.cash:.2f} (expected ~${expected_cash:.2f})")
    assert abs(player.cash - expected_cash) < 1, f"Cash mismatch"

    print("✓ Fractional shares test passed!\n")

def test_leverage():
    """Test that leverage multiplies investment correctly"""
    print("Testing leverage...")

    # Create a company and player
    company = Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.HIGH)
    player = Player("TestPlayer", starting_cash=10000.0)
    treasury = Treasury()
    companies = {"TestCorp": company}

    # Buy $500 with 4x leverage (total $2000 investment)
    success, msg = player.buy_stock(company, 500.0, leverage=4.0, companies=companies, treasury=treasury)
    print(f"Buy result: {success}, {msg}")

    # Should have ~20 shares (2000 / 100)
    shares = player.portfolio.get("TestCorp", 0)
    print(f"Shares owned: {shares:.4f}")
    assert shares > 19.5 and shares < 20.5, f"Expected ~20 shares, got {shares}"

    # Check cash (should have spent $500)
    expected_cash = 10000 - 500
    print(f"Cash remaining: ${player.cash:.2f} (expected ${expected_cash:.2f})")
    assert abs(player.cash - expected_cash) < 1, f"Cash mismatch"

    # Check borrowed amount (should be $1500)
    expected_borrowed = 1500
    print(f"Borrowed: ${player.borrowed_amount:.2f} (expected ${expected_borrowed:.2f})")
    assert abs(player.borrowed_amount - expected_borrowed) < 1, f"Borrowed amount mismatch"

    print("✓ Leverage test passed!\n")

def test_sell_fractional():
    """Test selling fractional shares"""
    print("Testing selling fractional shares...")

    # Create a company and player
    company = Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.HIGH)
    player = Player("TestPlayer", starting_cash=10000.0)
    treasury = Treasury()
    companies = {"TestCorp": company}

    # Buy $300 worth (should get ~3 shares)
    player.buy_stock(company, 300.0, leverage=1.0, companies=companies, treasury=treasury)
    initial_shares = player.portfolio.get("TestCorp", 0)
    print(f"Initial shares: {initial_shares:.4f}")

    # Sell half the shares
    success, msg = player.sell_stock(company, shares=initial_shares/2)
    print(f"Sell result: {success}, {msg}")

    # Check remaining shares
    remaining_shares = player.portfolio.get("TestCorp", 0)
    print(f"Remaining shares: {remaining_shares:.4f}")
    assert abs(remaining_shares - initial_shares/2) < 0.01, f"Expected ~{initial_shares/2} shares remaining"

    print("✓ Sell fractional shares test passed!\n")

def test_sell_by_dollar_amount():
    """Test selling by dollar amount"""
    print("Testing selling by dollar amount...")

    # Create a company and player
    company = Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.HIGH)
    player = Player("TestPlayer", starting_cash=10000.0)
    treasury = Treasury()
    companies = {"TestCorp": company}

    # Buy $500 worth
    player.buy_stock(company, 500.0, leverage=1.0, companies=companies, treasury=treasury)
    initial_shares = player.portfolio.get("TestCorp", 0)
    print(f"Initial shares: {initial_shares:.4f}")

    # Sell $200 worth
    success, msg = player.sell_stock(company, dollar_amount=200.0)
    print(f"Sell result: {success}, {msg}")

    # Check that some shares remain
    remaining_shares = player.portfolio.get("TestCorp", 0)
    print(f"Remaining shares: {remaining_shares:.4f}")
    assert remaining_shares > 0 and remaining_shares < initial_shares, "Should have sold some but not all shares"

    print("✓ Sell by dollar amount test passed!\n")

if __name__ == "__main__":
    print("="*60)
    print("Running Dollar Investment System Tests")
    print("="*60 + "\n")

    test_fractional_shares()
    test_leverage()
    test_sell_fractional()
    test_sell_by_dollar_amount()

    print("="*60)
    print("All tests passed! ✓")
    print("="*60)
