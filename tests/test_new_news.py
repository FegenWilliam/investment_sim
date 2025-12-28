#!/usr/bin/env python3
"""Test the new rumor generation system"""

import random
from investment_sim import BreakingNewsSystem, Company, LiquidityLevel

def test_news_generation():
    """Test that all outlets generate news independently"""
    random.seed(42)

    # Create test companies
    companies = {
        "TechCorp": Company("TechCorp", "Technology", 100.0, 5.0, LiquidityLevel.HIGH),
        "PharmaCare": Company("PharmaCare", "Pharmaceuticals", 150.0, 3.0, LiquidityLevel.MEDIUM),
        "EnergyPlus": Company("EnergyPlus", "Energy", 120.0, 4.0, LiquidityLevel.LOW),
    }

    news_system = BreakingNewsSystem()

    print("="*80)
    print("TESTING NEW NEWS SYSTEM")
    print("="*80)
    print()

    # Run multiple weeks to see variety
    for week in range(1, 11):
        print(f"\n{'='*80}")
        print(f"WEEK {week}")
        print(f"{'='*80}\n")

        result = news_system.generate_breaking_news(companies, week)

        if result:
            company_name, news_report, event_type = result

            print("📊 Financial Times (70% Accurate)")
            print("-" * 80)
            if news_report.financial_times:
                print(f"  {news_report.financial_times}")
            else:
                print("  [No reports at this time]")
            print()

            print("📈 Market Watch (70% Accurate)")
            print("-" * 80)
            if news_report.market_watch:
                print(f"  {news_report.market_watch}")
            else:
                print("  [No reports at this time]")
            print()

            print("📉 Bloomberg (70% Accurate)")
            print("-" * 80)
            if news_report.bloomberg:
                print(f"  {news_report.bloomberg}")
            else:
                print("  [No reports at this time]")
            print()

            if company_name:
                print(f"Market-Moving Event: {company_name} | Event Type: {event_type.value}")

        else:
            print("No news this week from any outlet.")

        # Show event status for debugging
        print(f"\n[DEBUG] Active Events:")
        for comp_name, events in news_system.company_events.items():
            if events:
                for event in events:
                    weeks_elapsed = week - event.discovery_week
                    weeks_remaining = event.weeks_until_public - weeks_elapsed
                    status = "CONFIRMED" if weeks_elapsed >= event.weeks_until_public else f"PENDING ({weeks_remaining}w until public)"
                    print(f"  - {comp_name}: {event.event_type.value} (Severity: {event.severity:.2f}) [{status}]")

    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")
    print("\nKey Observations to Check:")
    print("✓ All three outlets should have 70% accuracy")
    print("✓ Early reports should be marked with 'RUMOR:'")
    print("✓ Outlets may agree or disagree on events")
    print("✓ Market movements are independent of outlet reporting")

if __name__ == "__main__":
    test_news_generation()
