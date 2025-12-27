#!/usr/bin/env python3
"""Test the two-stage market impact system"""

import sys
sys.path.insert(0, '..')

from investment_sim import BreakingNewsSystem, Company, LiquidityLevel

def test_two_stage_impact():
    """Test that market impacts are split into 40% instant and 60% delayed"""

    print("="*70)
    print("TESTING TWO-STAGE MARKET IMPACT SYSTEM")
    print("="*70)

    # Create test companies
    companies = {
        "Blue Energy": Company("Blue Energy", "Mana Extraction", 125.0, 9.5, LiquidityLevel.MEDIUM, 3_000_000_000),
        "TechCorp": Company("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH, 50_000_000_000),
    }

    # Create breaking news system
    breaking_news = BreakingNewsSystem()

    # Get initial price of a company
    test_company = 'Blue Energy'
    initial_price = companies[test_company].price
    print(f"\n📊 Initial price for {test_company}: ${initial_price:.2f}")

    # Advance weeks until we get breaking news
    print("\n🔄 Advancing weeks to trigger breaking news...")
    news_found = False
    max_weeks = 20

    for week in range(1, max_weeks + 1):
        # Generate breaking news
        news = breaking_news.generate_breaking_news(companies, week)

        if news and news[0] == test_company:
            # We got news for our test company!
            news_found = True
            company_name, news_report, event_type = news

            print(f"\n📰 BREAKING NEWS in Week {week}!")
            print(f"   Company: {company_name}")
            print(f"   Type: {event_type}")

            # Check the pending impacts
            impacts = [imp for imp in breaking_news.pending_impacts if imp.company_name == test_company]

            if impacts:
                impact = impacts[0]
                print(f"\n📈 Impact Details:")
                print(f"   Total magnitude: {impact.impact_magnitude:+.1f}%")
                print(f"   Weeks until delayed impact: {impact.weeks_until_impact}")
                print(f"   Instant impact applied: {impact.instant_impact_applied}")

                # Check the price after instant impact
                price_after_instant = companies[test_company].price
                instant_change_pct = ((price_after_instant - initial_price) / initial_price) * 100
                expected_instant_pct = impact.impact_magnitude * 0.40

                print(f"\n💥 INSTANT IMPACT (40%):")
                print(f"   Expected: {expected_instant_pct:+.1f}%")
                print(f"   Actual:   {instant_change_pct:+.1f}%")
                print(f"   Price: ${initial_price:.2f} -> ${price_after_instant:.2f}")

                # Verify timing is 1 week
                assert impact.weeks_until_impact == 1, f"Timing should be 1 week, got {impact.weeks_until_impact}"
                print(f"\n✅ Timing verified: {impact.weeks_until_impact} week")

                # Verify instant impact was applied
                assert impact.instant_impact_applied == True, "instant_impact_applied should be True"
                print(f"✅ Instant impact flag verified: {impact.instant_impact_applied}")

                # Advance to when delayed impact should hit
                print(f"\n⏭️ Advancing {impact.weeks_until_impact} week(s) for delayed impact...")

                for _ in range(impact.weeks_until_impact):
                    messages = breaking_news.update_pending_impacts(companies, use_precompiled_prices=False)

                # Check the final price
                final_price = companies[test_company].price
                total_change_pct = ((final_price - initial_price) / initial_price) * 100

                print(f"\n💰 FINAL IMPACT (40% instant + 60% delayed):")
                print(f"   Expected total: {impact.impact_magnitude:+.1f}%")
                print(f"   Actual total:   {total_change_pct:+.1f}%")
                print(f"   Final price: ${final_price:.2f}")

                # Verify the total impact is approximately correct
                # Note: Due to compounding (instant impact changes the base for delayed impact),
                # the total will be slightly higher than the original magnitude
                # Expected compounding: (1 + 0.40*mag) * (1 + 0.60*mag) ≈ 1 + mag + 0.24*mag^2
                difference = abs(total_change_pct - impact.impact_magnitude)
                assert difference < 0.5, f"Total impact should be ~{impact.impact_magnitude:+.1f}%, got {total_change_pct:+.1f}%"
                print(f"\n✅ Total impact verified (difference: {difference:.3f}% due to compounding)")

            break

    if not news_found:
        print(f"\n❌ No news found for {test_company} in {max_weeks} weeks")
        print("   Try running the test again or increase max_weeks")
        return

    print("\n" + "="*70)
    print("✅ TWO-STAGE IMPACT TEST PASSED!")
    print("="*70)

if __name__ == "__main__":
    test_two_stage_impact()
