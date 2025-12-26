#!/usr/bin/env python3
"""Debug script to trace what's happening with market impacts"""

import sys
import pickle
import json

def debug_pending_impacts(save_file):
    """Load a save file and show all pending impacts"""
    print("="*70)
    print("DEBUGGING PENDING MARKET IMPACTS")
    print("="*70)

    try:
        # Try JSON first, then pickle
        if save_file.endswith('.json'):
            with open(save_file, 'r') as f:
                save_data = json.load(f)
        else:
            with open(save_file, 'rb') as f:
                save_data = pickle.load(f)

        print(f"\nLoaded save file: {save_file}")
        print(f"Current week: {save_data['week_number']}")

        # Show current prices
        print(f"\nCurrent Stock Prices:")
        for name, company_data in save_data['companies'].items():
            print(f"  {name}: ${company_data['price']:.2f}")

        # Show all pending impacts
        print(f"\nPending Market Impacts:")
        if 'breaking_news' in save_data and 'pending_impacts' in save_data['breaking_news']:
            impacts = save_data['breaking_news']['pending_impacts']
            if not impacts:
                print("  None")
            else:
                # Group by company
                by_company = {}
                for impact in impacts:
                    company = impact['company_name']
                    if company not in by_company:
                        by_company[company] = []
                    by_company[company].append(impact)

                for company, company_impacts in by_company.items():
                    print(f"\n  {company}:")
                    for impact in company_impacts:
                        weeks = impact['weeks_until_impact']
                        magnitude = impact['impact_magnitude']
                        sentiment = impact['sentiment']
                        week_triggers = save_data['week_number'] + weeks

                        direction = "📈" if magnitude > 0 else "📉"
                        print(f"    {direction} {magnitude:+.1f}% impact")
                        print(f"       Triggers in {weeks} week(s) (Week {week_triggers})")
                        print(f"       News: {impact['news_text'][:60]}...")

        else:
            print("  No breaking news data found")

        # Show future prices if available
        if 'future_prices' in save_data:
            print(f"\nPrecompiled Future Prices (next 4 weeks):")
            for company, prices in save_data['future_prices'].items():
                if prices:
                    current = save_data['companies'][company]['price']
                    print(f"\n  {company}:")
                    print(f"    Current: ${current:.2f}")
                    for i, price in enumerate(prices[:4], 1):
                        change = ((price - current) / current) * 100
                        print(f"    Week +{i}: ${price:.2f} ({change:+.2f}%)")

    except FileNotFoundError:
        print(f"\nError: Save file '{save_file}' not found")
        return
    except Exception as e:
        print(f"\nError loading save file: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 debug_impacts.py <save_file.pkl>")
        print("\nExample: python3 debug_impacts.py save_game.pkl")
        sys.exit(1)

    debug_pending_impacts(sys.argv[1])
