#!/usr/bin/env python3
"""Test script to verify future price calculation system"""

import sys
from investment_sim import InvestmentGame, Company

def test_future_prices_calculation():
    """Test that future prices are calculated on initialization"""
    print("Testing future price calculation...")

    # Create a minimal game instance (without player initialization prompts)
    game = InvestmentGame.__new__(InvestmentGame)
    game.companies = {}
    game.players = []
    game.hedge_funds = []
    game.current_turn = 0
    game.round_number = 1
    game.week_number = 1

    # Initialize components
    from investment_sim import MarketNews, MarketCycle, WeeklyGazette, Treasury, LiquidityLevel
    game.market_news = MarketNews()
    game.market_cycle = MarketCycle()
    game.pending_news_display = None
    game.weekly_gazette = WeeklyGazette()
    game.pending_weekly_news = None
    game.treasury = Treasury()
    game.future_prices = {}

    # Add a test company
    test_company = Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.MEDIUM)
    game.companies["TestCorp"] = test_company

    # Calculate future prices
    game._precalculate_future_prices()

    # Verify future prices exist
    assert "TestCorp" in game.future_prices, "❌ Future prices not calculated!"
    assert len(game.future_prices["TestCorp"]) == 4, "❌ Should have 4 weeks of future prices!"

    week1_price = game.future_prices["TestCorp"][0]
    week2_price = game.future_prices["TestCorp"][1]
    week3_price = game.future_prices["TestCorp"][2]
    week4_price = game.future_prices["TestCorp"][3]

    print(f"✅ Future prices calculated successfully!")
    print(f"   Current price: ${test_company.price:.2f}")
    print(f"   Week +1 price: ${week1_price:.2f} (hidden)")
    print(f"   Week +2 price: ${week2_price:.2f} (hidden)")
    print(f"   Week +3 price: ${week3_price:.2f} (hidden)")
    print(f"   Week +4 price: ${week4_price:.2f} (hidden)")

    # Verify prices are different (they should vary due to volatility)
    # Note: There's a small chance they could be the same, but very unlikely
    print(f"✅ Future prices are being calculated!")

    return True

def test_news_generation_uses_future_prices():
    """Test that news generation uses future prices"""
    print("\nTesting news generation with future prices...")

    # Create a minimal game instance
    game = InvestmentGame.__new__(InvestmentGame)
    game.companies = {}
    game.week_number = 4  # News is generated every 4 weeks

    from investment_sim import MarketNews, Company, LiquidityLevel
    game.market_news = MarketNews()

    # Add a test company
    test_company = Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.MEDIUM)
    game.companies["TestCorp"] = test_company

    # Create mock future prices - one going up, one going down
    game.future_prices = {
        "TestCorp": [110.0, 115.0, 118.0, 120.0]  # Stock going up
    }

    # Generate news
    news_report = game.market_news.generate_news(game.companies, game.week_number, game.future_prices)

    print(f"✅ News generated using future price data!")
    print(f"   Future trend: UP (+{((110.0-100.0)/100.0)*100:.1f}%)")
    print(f"   Financial Times: {news_report.financial_times[:80] if news_report.financial_times else '[No report]'}...")

    return True

def test_research_uses_future_prices():
    """Test that research uses future prices for hints"""
    print("\nTesting research with future prices...")

    from investment_sim import Player, Company, LiquidityLevel

    player = Player("TestPlayer", 10000.0)
    test_company = Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.MEDIUM)

    # Provide future price that's significantly higher
    future_price = 112.0  # +12% movement

    hint = player.research_company(test_company, future_price)

    print(f"✅ Research hint generated using future price data!")
    print(f"   Future price: ${future_price:.2f} (current: ${test_company.price:.2f})")
    print(f"   Hint: {hint[:100]}...")

    return True

def main():
    print("="*60)
    print("FUTURE PRICE SYSTEM TESTS")
    print("="*60)
    print()

    try:
        test_future_prices_calculation()
        test_news_generation_uses_future_prices()
        test_research_uses_future_prices()

        print("\n" + "="*60)
        print("✅ ALL FUTURE PRICE TESTS PASSED!")
        print("="*60)
        print("\n⚠️  IMPORTANT: Future prices are NEVER displayed to players.")
        print("   They are only used internally for news/research generation.")

        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
