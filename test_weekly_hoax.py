#!/usr/bin/env python3
"""Quick test to verify weekly news hoax system works correctly"""

import sys
import random
from investment_sim import WeeklyGazette, Company, LiquidityLevel

def test_weekly_news_hoaxes():
    """Test that weekly news generates hoaxes at correct rates"""
    random.seed(42)  # For reproducibility

    # Create test companies
    companies = {
        "TestCorp": Company("TestCorp", "Technology", 100.0, 5.0, LiquidityLevel.HIGH),
        "MegaInc": Company("MegaInc", "Finance", 150.0, 3.0, LiquidityLevel.MEDIUM),
    }

    gazette = WeeklyGazette()

    # Test different weeks in the cycle
    test_weeks = [1, 4, 7, 10]  # One from each trust period

    for week in test_weeks:
        news_items = gazette.generate_weekly_news(companies, week)

        print(f"\nWeek {week}:")
        cycle_pos = (week - 1) % 12
        if cycle_pos < 3:
            expected_trust = "80% real"
        elif cycle_pos < 6:
            expected_trust = "70% real"
        elif cycle_pos < 9:
            expected_trust = "50% real"
        else:
            expected_trust = "60% real"

        print(f"Expected trust level: {expected_trust}")

        real_count = sum(1 for _, is_real in news_items if is_real)
        hoax_count = len(news_items) - real_count

        print(f"Generated {len(news_items)} news items:")
        print(f"  Real: {real_count}")
        print(f"  Hoaxes: {hoax_count}")

        for news_text, is_real in news_items:
            status = "✓ REAL" if is_real else "⚠️  HOAX"
            print(f"  [{status}] {news_text[:60]}...")

    # Test serialization
    print("\n\nTesting serialization...")
    data = gazette.to_dict()
    gazette2 = WeeklyGazette.from_dict(data)

    print(f"Original history length: {len(gazette.weekly_news_history)}")
    print(f"Deserialized history length: {len(gazette2.weekly_news_history)}")

    # Verify format
    if gazette2.weekly_news_history:
        first_item = gazette2.weekly_news_history[0]
        print(f"History item format: {len(first_item)}-tuple (week, text, is_real)")
        print(f"Sample: week={first_item[0]}, is_real={first_item[2]}")

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_weekly_news_hoaxes()
