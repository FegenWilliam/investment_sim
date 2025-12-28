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
        print(news_report.financial_times if news_report.financial_times else "[No report]")
        print(f"\n📈 Market Watch:")
        print(news_report.market_watch if news_report.market_watch else "[No report]")
        print(f"\n📉 Bloomberg:")
        print(news_report.bloomberg if news_report.bloomberg else "[No report]")

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
        print(loaded_news.financial_times if loaded_news.financial_times else "[No report]")
        print(f"\n📈 Market Watch:")
        print(loaded_news.market_watch if loaded_news.market_watch else "[No report]")
        print(f"\n📉 Bloomberg:")
        print(loaded_news.bloomberg if loaded_news.bloomberg else "[No report]")

        # Verify they match
        print("\n" + "="*80)
        print("VERIFICATION:")
        print("-" * 80)

        checks = [
            ("Financial Times", news_report.financial_times == loaded_news.financial_times),
            ("Market Watch", news_report.market_watch == loaded_news.market_watch),
            ("Bloomberg", news_report.bloomberg == loaded_news.bloomberg),
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
