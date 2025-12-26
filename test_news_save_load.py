#!/usr/bin/env python3
"""Test that news is properly saved and restored"""

import random
import json
from investment_sim import BreakingNewsSystem, Company, LiquidityLevel, NewsReport

def test_news_save_load():
    """Test that news with multiple items is saved and loaded correctly"""
    random.seed(42)

    # Create test companies
    companies = {
        "TechCorp": Company("TechCorp", "Technology", 100.0, 5.0, LiquidityLevel.HIGH),
        "PharmaCare": Company("PharmaCare", "Pharmaceuticals", 150.0, 3.0, LiquidityLevel.MEDIUM),
    }

    news_system = BreakingNewsSystem()

    print("="*80)
    print("TESTING NEWS SAVE/LOAD")
    print("="*80)
    print()

    # Generate news for a few weeks
    print("Generating news for week 3...")
    for week in range(1, 4):
        result = news_system.generate_breaking_news(companies, week)

    # Get the news from week 3
    if result:
        company_name, news_report, event_type = result

        print("\n📰 ORIGINAL NEWS (Week 3):")
        print("-" * 80)
        print(f"\n📊 Financial Times:")
        print(news_report.trustworthy_source if news_report.trustworthy_source else "[No report]")
        print(f"\n📢 Market Pulse Daily:")
        print(news_report.market_pulse_source)
        print(f"\n🔍 Insider Tip:")
        print(news_report.insider_source if news_report.insider_source else "[No tips]")
        print(f"\n📣 Rumor Mill:")
        print(news_report.rumor_mill_source)

        # Save to dict
        print("\n" + "="*80)
        print("SAVING NEWS TO DICT...")
        news_dict = news_report.to_dict()

        # Simulate JSON save/load
        json_str = json.dumps(news_dict, indent=2)
        print(f"\nSerialized JSON ({len(json_str)} characters):")
        print(json_str[:200] + "..." if len(json_str) > 200 else json_str)

        # Load from dict
        print("\n" + "="*80)
        print("LOADING NEWS FROM DICT...")
        loaded_dict = json.loads(json_str)
        loaded_news = NewsReport.from_dict(loaded_dict)

        print("\n📰 LOADED NEWS (After Save/Load):")
        print("-" * 80)
        print(f"\n📊 Financial Times:")
        print(loaded_news.trustworthy_source if loaded_news.trustworthy_source else "[No report]")
        print(f"\n📢 Market Pulse Daily:")
        print(loaded_news.market_pulse_source)
        print(f"\n🔍 Insider Tip:")
        print(loaded_news.insider_source if loaded_news.insider_source else "[No tips]")
        print(f"\n📣 Rumor Mill:")
        print(loaded_news.rumor_mill_source)

        # Verify they match
        print("\n" + "="*80)
        print("VERIFICATION:")
        print("-" * 80)

        checks = [
            ("Financial Times", news_report.trustworthy_source == loaded_news.trustworthy_source),
            ("Market Pulse", news_report.market_pulse_source == loaded_news.market_pulse_source),
            ("Insider Tip", news_report.insider_source == loaded_news.insider_source),
            ("Rumor Mill", news_report.rumor_mill_source == loaded_news.rumor_mill_source),
            ("Insider Flipped", news_report.insider_flipped == loaded_news.insider_flipped),
            ("Is Rumor", news_report.is_rumor == loaded_news.is_rumor),
        ]

        all_passed = True
        for name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {name}")
            if not passed:
                all_passed = False

        print("\n" + "="*80)
        if all_passed:
            print("✅ ALL TESTS PASSED - News saves and loads correctly!")
        else:
            print("❌ SOME TESTS FAILED")
        print("="*80)

    else:
        print("No news generated for week 3")

if __name__ == "__main__":
    test_news_save_load()
