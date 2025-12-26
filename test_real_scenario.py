#!/usr/bin/env python3
"""Test that simulates real game scenario with multiple impacts"""

from investment_sim import InvestmentGame, Company, LiquidityLevel, BreakingNewsSystem, PendingNewsImpact, NewsSentiment

def test_real_game_scenario():
    """Test the actual scenario from the user's game"""
    print("="*70)
    print("Testing Real Game Scenario - Multiple Impacts Same Week")
    print("="*70)

    # Create a minimal game setup
    from investment_sim import MarketCycle
    game = InvestmentGame.__new__(InvestmentGame)
    game.week_number = 10
    game.breaking_news = BreakingNewsSystem()
    game.market_cycle = MarketCycle()
    game.market_cycle.active_cycle = None  # No active cycle

    # Initialize companies with realistic prices
    game.companies = {
        "Blue Energy Industries": Company("Blue Energy Industries", "Mana Extraction", 124.42, 5.0, LiquidityLevel.MEDIUM, 3_000_000_000),
        "Out of This World Enterprises": Company("Out of This World Enterprises", "Rare Fantasy Goods", 702.26, 8.0, LiquidityLevel.LOW, 1_500_000_000),
        "ElectroMax": Company("ElectroMax", "Electronics", 89.64, 5.0, LiquidityLevel.MEDIUM, 10_000_000_000),
    }

    # Simulate the impacts from the user's game
    # Blue Energy: 3 impacts all triggering next week
    impact1 = PendingNewsImpact(
        company_name="Blue Energy Industries",
        sentiment=NewsSentiment.NEGATIVE,
        impact_magnitude=-13.3,
        weeks_until_impact=1,
        is_real=True,
        news_text="Supply chain disruption",
        news_report=None
    )
    impact2 = PendingNewsImpact(
        company_name="Blue Energy Industries",
        sentiment=NewsSentiment.POSITIVE,
        impact_magnitude=14.3,
        weeks_until_impact=1,
        is_real=True,
        news_text="Breakthrough technology",
        news_report=None
    )
    impact3 = PendingNewsImpact(
        company_name="Blue Energy Industries",
        sentiment=NewsSentiment.NEGATIVE,
        impact_magnitude=-13.7,
        weeks_until_impact=1,
        is_real=True,
        news_text="Regulatory issues",
        news_report=None
    )

    # Out of This World: 2 impacts
    impact4 = PendingNewsImpact(
        company_name="Out of This World Enterprises",
        sentiment=NewsSentiment.NEGATIVE,
        impact_magnitude=-8.2,
        weeks_until_impact=1,
        is_real=True,
        news_text="Market downturn",
        news_report=None
    )
    impact5 = PendingNewsImpact(
        company_name="Out of This World Enterprises",
        sentiment=NewsSentiment.NEGATIVE,
        impact_magnitude=-13.4,
        weeks_until_impact=1,
        is_real=True,
        news_text="Product recall",
        news_report=None
    )

    # ElectroMax: 1 impact
    impact6 = PendingNewsImpact(
        company_name="ElectroMax",
        sentiment=NewsSentiment.POSITIVE,
        impact_magnitude=10.5,
        weeks_until_impact=1,
        is_real=True,
        news_text="Strong earnings",
        news_report=None
    )

    game.breaking_news.pending_impacts.extend([impact1, impact2, impact3, impact4, impact5, impact6])

    print(f"\nWeek {game.week_number}: Current Prices")
    print(f"  Blue Energy Industries: ${game.companies['Blue Energy Industries'].price:.2f}")
    print(f"  Out of This World Enterprises: ${game.companies['Out of This World Enterprises'].price:.2f}")
    print(f"  ElectroMax: ${game.companies['ElectroMax'].price:.2f}")

    # Calculate expected prices after impacts
    blue_expected = 124.42 * (1 - 0.133) * (1 + 0.143) * (1 - 0.137)
    ootw_expected = 702.26 * (1 - 0.082) * (1 - 0.134)
    electro_expected = 89.64 * (1 + 0.105)

    print(f"\nExpected prices after all impacts (Week {game.week_number + 1}):")
    print(f"  Blue Energy: ${blue_expected:.2f} (from $124.42)")
    print(f"  Out of This World: ${ootw_expected:.2f} (from $702.26)")
    print(f"  ElectroMax: ${electro_expected:.2f} (from $89.64)")

    # Now precalculate future prices
    game.future_prices = {}
    game.future_eps = {}
    game.future_fundamental_prices = {}

    # Call the actual method to precalculate
    print(f"\nCalling _precalculate_future_prices()...")
    game._precalculate_future_prices()

    # Check what price was calculated for week+1
    print(f"\nActual precalculated prices for Week {game.week_number + 1}:")
    print(f"  Blue Energy: ${game.future_prices['Blue Energy Industries'][0]:.2f}")
    print(f"  Out of This World: ${game.future_prices['Out of This World Enterprises'][0]:.2f}")
    print(f"  ElectroMax: ${game.future_prices['ElectroMax'][0]:.2f}")

    # Verify
    print(f"\nVerification:")
    blue_match = abs(game.future_prices['Blue Energy Industries'][0] - blue_expected) < 0.01
    ootw_match = abs(game.future_prices['Out of This World Enterprises'][0] - ootw_expected) < 0.01
    electro_match = abs(game.future_prices['ElectroMax'][0] - electro_expected) < 0.01

    if blue_match and ootw_match and electro_match:
        print("  ✅ All prices match expected values!")
        print("  ✅ Multiple impacts are being properly accumulated!")
        return True
    else:
        print("  ❌ Price mismatch detected!")
        if not blue_match:
            print(f"     Blue Energy: Expected ${blue_expected:.2f}, Got ${game.future_prices['Blue Energy Industries'][0]:.2f}")
        if not ootw_match:
            print(f"     Out of This World: Expected ${ootw_expected:.2f}, Got ${game.future_prices['Out of This World Enterprises'][0]:.2f}")
        if not electro_match:
            print(f"     ElectroMax: Expected ${electro_expected:.2f}, Got ${game.future_prices['ElectroMax'][0]:.2f}")
        return False

if __name__ == "__main__":
    import random
    random.seed(42)  # Fixed seed for reproducibility
    test_real_game_scenario()
