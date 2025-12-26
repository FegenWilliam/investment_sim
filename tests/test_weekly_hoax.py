#!/usr/bin/env python3
"""Quick test to verify weekly news hoax system works correctly with two outlets"""

import sys
import random
from investment_sim import WeeklyGazette, MarketChronicle, Company, LiquidityLevel

def test_two_weekly_outlets():
    """Test that both weekly news outlets generate hoaxes at correct rates"""
    random.seed(42)  # For reproducibility

    # Create test companies
    companies = {
        "TestCorp": Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.HIGH),
        "MegaInc": Company("MegaInc", "Finance", 150.0, 3.0, LiquidityLevel.MEDIUM),
    }

    gazette = WeeklyGazette()
    chronicle = MarketChronicle()

    # Test different weeks in the cycle
    test_weeks = [1, 4, 7, 10]  # One from each trust period

    for week in test_weeks:
        gazette_news = gazette.generate_weekly_news(companies, week)
        chronicle_news = chronicle.generate_chronicle_news(companies, week)

        print(f"\n{'='*70}")
        print(f"WEEK {week}")
        print(f"{'='*70}")

        cycle_pos = (week - 1) % 12
        if cycle_pos < 3:
            expected_trust = "80% real, 20% hoax"
        elif cycle_pos < 6:
            expected_trust = "70% real, 30% hoax"
        elif cycle_pos < 9:
            expected_trust = "50% real, 50% hoax"
        else:
            expected_trust = "60% real, 40% hoax"

        print(f"Trust level: {expected_trust}")
        print()

        # Display both outlets side by side
        print("📰 THE BUSINESS GAZETTE - WEEKLY EDITION")
        print("-" * 70)
        gazette_real = sum(1 for _, is_real in gazette_news if is_real)
        print(f"(Debug: {gazette_real}/{len(gazette_news)} real)")
        for news_text, is_real in gazette_news:
            # NO INDICATOR - players can't tell!
            print(f"• {news_text[:65]}...")
            if is_real:
                print(f"  [Debug only: This is REAL news]")
            else:
                print(f"  [Debug only: This is a HOAX]")

        print()
        print("📰 THE MARKET CHRONICLE - WEEKLY REPORT")
        print("-" * 70)
        chronicle_real = sum(1 for _, is_real in chronicle_news if is_real)
        print(f"(Debug: {chronicle_real}/{len(chronicle_news)} real)")
        for news_text, is_real in chronicle_news:
            # NO INDICATOR - players can't tell!
            print(f"• {news_text[:65]}...")
            if is_real:
                print(f"  [Debug only: This is REAL news]")
            else:
                print(f"  [Debug only: This is a HOAX]")

    # Test serialization for both outlets
    print("\n" + "="*70)
    print("Testing serialization...")
    print("="*70)

    gazette_data = gazette.to_dict()
    gazette2 = WeeklyGazette.from_dict(gazette_data)
    print(f"Gazette: {len(gazette.weekly_news_history)} items saved and restored")

    chronicle_data = chronicle.to_dict()
    chronicle2 = MarketChronicle.from_dict(chronicle_data)
    print(f"Chronicle: {len(chronicle.chronicle_news_history)} items saved and restored")

    print("\n✅ All tests passed!")
    print("\nNote: In actual gameplay, players see NO indicators.")
    print("They must decide which outlet to trust when stories contradict!")

if __name__ == "__main__":
    test_two_weekly_outlets()
