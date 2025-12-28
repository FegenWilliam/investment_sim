#!/usr/bin/env python3
"""Test share limit and dynamic market cap functionality"""

from investment_sim import Company, LiquidityLevel

def test_share_calculation():
    """Test that shares are calculated correctly from initial market cap"""
    print("Testing share calculation...")

    # Create TechCorp with $400B market cap at $150 per share
    techcorp = Company("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH, 400_000_000_000)

    expected_shares = 400_000_000_000 // 150  # Integer division
    actual_shares = techcorp.total_shares

    print(f"  Initial price: ${techcorp.price:.2f}")
    print(f"  Total shares: {techcorp.total_shares:,}")
    print(f"  Expected shares: {expected_shares:,}")
    print(f"  Initial market cap: ${techcorp.market_cap:,.0f}")
    print(f"  Expected market cap: $400,000,000,000")

    assert actual_shares == expected_shares, f"Share calculation failed: {actual_shares} != {expected_shares}"
    print("  ✓ Share calculation correct!")
    print()

def test_dynamic_market_cap():
    """Test that market cap scales with price changes"""
    print("Testing dynamic market cap scaling...")

    # Create a company
    company = Company("TestCo", "Test", 100.0, 5.0, LiquidityLevel.MEDIUM, 10_000_000_000)

    initial_shares = company.total_shares
    initial_market_cap = company.market_cap

    print(f"  Initial state:")
    print(f"    Price: ${company.price:.2f}")
    print(f"    Shares: {company.total_shares:,}")
    print(f"    Market cap: ${company.market_cap:,.0f}")

    # Simulate a price increase
    company.price = 150.0
    new_market_cap = company.market_cap

    print(f"\n  After price increase to $150:")
    print(f"    Price: ${company.price:.2f}")
    print(f"    Shares: {company.total_shares:,} (should be unchanged)")
    print(f"    Market cap: ${company.market_cap:,.0f}")
    print(f"    Expected market cap: ${150.0 * initial_shares:,.0f}")

    assert company.total_shares == initial_shares, "Shares should not change!"
    assert new_market_cap == 150.0 * initial_shares, f"Market cap should scale: {new_market_cap} != {150.0 * initial_shares}"
    print("  ✓ Market cap scales correctly with price!")
    print()

def test_serialization():
    """Test that serialization preserves total_shares"""
    print("Testing serialization...")

    # Create a company
    original = Company("SerializeCo", "Test", 200.0, 6.0, LiquidityLevel.LOW, 50_000_000_000)

    print(f"  Original:")
    print(f"    Price: ${original.price:.2f}")
    print(f"    Shares: {original.total_shares:,}")
    print(f"    Market cap: ${original.market_cap:,.0f}")

    # Serialize
    data = original.to_dict()

    # Verify total_shares is in the dict
    assert 'total_shares' in data, "total_shares should be serialized!"
    print(f"  ✓ total_shares serialized: {data['total_shares']:,}")

    # Deserialize
    restored = Company.from_dict(data)

    print(f"\n  Restored:")
    print(f"    Price: ${restored.price:.2f}")
    print(f"    Shares: {restored.total_shares:,}")
    print(f"    Market cap: ${restored.market_cap:,.0f}")

    assert restored.total_shares == original.total_shares, "Shares should be preserved!"
    assert restored.market_cap == original.market_cap, "Market cap should be preserved!"
    print("  ✓ Serialization works correctly!")
    print()

def test_all_companies():
    """Test all initialized companies have correct values"""
    print("Testing all company initializations...")

    company_data = [
        ("TechCorp", "Technology", 150.0, 400_000_000_000),
        ("PharmaCare", "Pharmaceuticals", 220.0, 250_000_000_000),
        ("EnergyPlus", "Energy", 110.0, 200_000_000_000),
        ("AutoDrive", "Automotive", 95.0, 160_000_000_000),
        ("ElectroMax", "Electronics", 85.0, 150_000_000_000),
        ("Blue Energy Industries", "Mana Extraction", 125.0, 120_000_000_000),
        ("AutoDrive", "Automotive", 95.0, 60_000_000_000),
        ("Out of This World Enterprises", "Rare Fantasy Goods", 666.0, 35_000_000_000),
    ]

    for name, industry, price, expected_market_cap in company_data:
        company = Company(name, industry, price, 5.0, LiquidityLevel.MEDIUM, expected_market_cap)
        shares = company.total_shares
        actual_market_cap = company.market_cap

        # Calculate expected shares
        expected_shares = expected_market_cap // price

        print(f"  {name}:")
        print(f"    Price: ${price:.2f}")
        print(f"    Shares: {shares:,}")
        print(f"    Market cap: ${actual_market_cap:,.0f}")
        print(f"    Expected: ${expected_market_cap:,.0f}")

        # Verify market cap is close (within rounding error)
        market_cap_diff = abs(actual_market_cap - expected_market_cap)
        max_error = price  # Allow up to one share's worth of difference due to integer division

        assert market_cap_diff <= max_error, f"{name} market cap off by too much: {market_cap_diff}"
        print(f"    ✓ Market cap correct (diff: ${market_cap_diff:.0f})")
        print()

if __name__ == "__main__":
    print("="*60)
    print("Share Limit and Dynamic Market Cap Tests")
    print("="*60)
    print()

    test_share_calculation()
    test_dynamic_market_cap()
    test_serialization()
    test_all_companies()

    print("="*60)
    print("All tests passed! ✓")
    print("="*60)
