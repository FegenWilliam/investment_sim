#!/usr/bin/env python3
"""Test the new breaking news system"""

import sys
sys.path.insert(0, '..')

from investment_sim import BreakingNewsSystem, Company, LiquidityLevel, EventType

# Create test companies
companies = {
    "TechCorp": Company("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH, 50_000_000_000),
    "PharmaCare": Company("PharmaCare", "Pharmaceuticals", 220.0, 5.0, LiquidityLevel.LOW, 8_000_000_000),
    "Blue Energy": Company("Blue Energy", "Mana Extraction", 125.0, 9.5, LiquidityLevel.MEDIUM, 3_000_000_000),
    "AutoDrive": Company("AutoDrive", "Automotive", 95.0, 7.0, LiquidityLevel.LOW, 2_000_000_000),
}

# Create breaking news system
breaking_news = BreakingNewsSystem()

print("Testing Breaking News System")
print("=" * 80)
print()

# Simulate several weeks to generate events and news
for week in range(1, 11):
    print(f"\n--- Week {week} ---")

    # Generate breaking news
    result = breaking_news.generate_breaking_news(companies, week)

    if result:
        company_name, news_report, event_type = result
        print(f"\n🚨 BREAKING NEWS for {company_name}!")
        print(f"Event Type: {event_type.value}")
        print()

        # Display the 3 reputable news outlets (each 70% accurate)
        print("📊 Financial Times (70% accurate - may report rumors or wrong info):")
        if news_report.financial_times:
            print(f"   {news_report.financial_times}")
        else:
            print("   [No reports at this time]")
        print()

        print("📈 Market Watch (70% accurate - may report rumors or wrong info):")
        if news_report.market_watch:
            print(f"   {news_report.market_watch}")
        else:
            print("   [No reports at this time]")
        print()

        print("📉 Bloomberg (70% accurate - may report rumors or wrong info):")
        if news_report.bloomberg:
            print(f"   {news_report.bloomberg}")
        else:
            print("   [No reports at this time]")
    else:
        print("No breaking news this week")

    # Update pending impacts
    impact_messages = breaking_news.update_pending_impacts(companies)
    if impact_messages:
        print("\n💰 Market Impacts:")
        for msg in impact_messages:
            print(f"   {msg}")

    # Show company events still pending
    pending_count = sum(len(events) for events in breaking_news.company_events.values())
    print(f"\nInternal events pending publication: {pending_count}")

print("\n" + "=" * 80)
print("Test completed!")
print()

# Show statistics
print("News System Statistics:")
print(f"Total breaking news stories published: {len(breaking_news.news_history)}")
print(f"Pending impacts: {len(breaking_news.pending_impacts)}")

# Show sample company prices
print("\nFinal Company Prices:")
for name, company in companies.items():
    print(f"  {name}: ${company.price:.2f}")
