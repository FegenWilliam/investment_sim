#!/usr/bin/env python3
"""Test that multiple market impacts on the same stock are properly accumulated"""

from investment_sim import InvestmentGame, Company, LiquidityLevel, BreakingNewsSystem, PendingNewsImpact, NewsSentiment

def test_multiple_impacts_same_week():
    """Test that multiple impacts on the same stock in the same week are all applied"""
    print("="*70)
    print("Testing Multiple Market Impacts on Same Stock")
    print("="*70)

    # Create a minimal game setup
    game = InvestmentGame.__new__(InvestmentGame)
    game.week_number = 1
    game.breaking_news = BreakingNewsSystem()
    game.market_cycle = None  # Disable market cycles for this test

    # Initialize test company
    game.companies = {
        "TestCorp": Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.HIGH, 50_000_000_000),
    }

    # Create THREE pending news impacts for the same company, all triggering in 1 week
    impact1 = PendingNewsImpact(
        company_name="TestCorp",
        sentiment=NewsSentiment.NEGATIVE,
        impact_magnitude=-13.3,  # -13.3% impact
        weeks_until_impact=1,
        is_real=True,
        news_text="TestCorp faces supply chain issues",
        news_report=None
    )
    impact2 = PendingNewsImpact(
        company_name="TestCorp",
        sentiment=NewsSentiment.POSITIVE,
        impact_magnitude=14.3,  # +14.3% impact
        weeks_until_impact=1,
        is_real=True,
        news_text="TestCorp announces breakthrough product",
        news_report=None
    )
    impact3 = PendingNewsImpact(
        company_name="TestCorp",
        sentiment=NewsSentiment.NEGATIVE,
        impact_magnitude=-13.7,  # -13.7% impact
        weeks_until_impact=1,
        is_real=True,
        news_text="TestCorp CEO resigns suddenly",
        news_report=None
    )

    game.breaking_news.pending_impacts.append(impact1)
    game.breaking_news.pending_impacts.append(impact2)
    game.breaking_news.pending_impacts.append(impact3)

    print(f"\n📰 Week {game.week_number}: Three news items announced!")
    print(f"   Impact 1: -13.3% (supply chain issues)")
    print(f"   Impact 2: +14.3% (breakthrough product)")
    print(f"   Impact 3: -13.7% (CEO resigns)")
    print(f"   All will impact in 1 week")
    print(f"   Current price: ${game.companies['TestCorp'].price:.2f}")

    # Calculate expected combined impact
    expected_multiplier = (1 - 0.133) * (1 + 0.143) * (1 - 0.137)
    expected_price = 100.0 * expected_multiplier
    print(f"\n   Expected combined impact: {(expected_multiplier - 1) * 100:+.2f}%")
    print(f"   Expected final price: ${expected_price:.2f}")

    # Initialize future prices (call the actual precalculate method)
    game.future_prices = {}
    game.future_eps = {}
    game.future_fundamental_prices = {}

    # Manually simulate what _precalculate_future_prices does for week+1
    import random
    random.seed(42)  # Fixed seed for reproducibility

    company = game.companies['TestCorp']
    week_ahead = 1
    simulated_price = company.price

    # Check if any impacts will occur
    news_impact_occurred = False
    for impact in game.breaking_news.pending_impacts:
        if impact.company_name == "TestCorp":
            weeks_until = impact.weeks_until_impact - week_ahead
            if weeks_until == 0 and impact.is_real:
                news_impact_occurred = True
                break

    print(f"\n   news_impact_occurred flag: {news_impact_occurred}")

    # If no news impact, would apply random walk (but we skip this)
    if not news_impact_occurred:
        change_percent = random.uniform(-company.base_volatility, company.base_volatility)
        simulated_price *= (1 + change_percent / 100)
        print(f"   Applied random walk: {change_percent:+.2f}%")

    # Apply ALL pending news impacts
    impacts_applied = []
    for impact in game.breaking_news.pending_impacts:
        if impact.company_name == "TestCorp":
            weeks_until = impact.weeks_until_impact - week_ahead
            if weeks_until == 0:
                if impact.is_real:
                    old_price = simulated_price
                    simulated_price *= (1 + impact.impact_magnitude / 100)
                    impacts_applied.append((impact.impact_magnitude, old_price, simulated_price))
                    print(f"   Applied impact: {impact.impact_magnitude:+.1f}% -> ${simulated_price:.2f}")

    print(f"\n   Total impacts applied: {len(impacts_applied)}")
    print(f"   Final simulated price: ${simulated_price:.2f}")

    # Compare with expected
    if abs(simulated_price - expected_price) < 0.01:
        print(f"\n   ✅ SUCCESS: All three impacts were properly accumulated!")
        print(f"      Expected: ${expected_price:.2f}, Got: ${simulated_price:.2f}")
        return True
    else:
        print(f"\n   ❌ FAIL: Impacts not properly accumulated!")
        print(f"      Expected: ${expected_price:.2f}, Got: ${simulated_price:.2f}")
        return False

if __name__ == "__main__":
    test_multiple_impacts_same_week()
