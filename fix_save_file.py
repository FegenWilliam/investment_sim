#!/usr/bin/env python3
"""Fix a save file by recalculating future prices with the corrected code"""

import sys
import json
from investment_sim import InvestmentGame

def fix_save_file(save_file, output_file=None):
    """Load a save file and recalculate future prices with fixed code"""

    if output_file is None:
        output_file = save_file.replace('.json', '_fixed.json')

    print("="*70)
    print("FIXING SAVE FILE - RECALCULATING FUTURE PRICES")
    print("="*70)

    # Load the save file
    print(f"\nLoading: {save_file}")
    game = InvestmentGame.load_game(save_file)

    if game is None:
        print("Error: Could not load save file!")
        return

    print(f"Current Week: {game.week_number}")

    # Show current future prices (the buggy ones)
    print("\nOLD (Buggy) Future Prices for Week +1:")
    for company_name in ['Blue Energy Industries', 'Out of This World Enterprises', 'ElectroMax']:
        if company_name in game.companies:
            current = game.companies[company_name].price
            future = game.future_prices.get(company_name, [None])[0]
            if future:
                change = ((future - current) / current) * 100
                print(f"  {company_name}: ${future:.2f} ({change:+.2f}%)")

    # Recalculate future prices with the FIXED code
    print("\n🔧 Recalculating future prices with FIXED code...")
    game._precalculate_future_prices()

    # Show new future prices (the correct ones)
    print("\nNEW (Fixed) Future Prices for Week +1:")
    for company_name in ['Blue Energy Industries', 'Out of This World Enterprises', 'ElectroMax']:
        if company_name in game.companies:
            current = game.companies[company_name].price
            future = game.future_prices.get(company_name, [None])[0]
            if future:
                change = ((future - current) / current) * 100
                print(f"  {company_name}: ${future:.2f} ({change:+.2f}%)")

                # Show which impacts will trigger
                impacts_next_week = [
                    imp for imp in game.breaking_news.pending_impacts
                    if imp.company_name == company_name and imp.weeks_until_impact == 1
                ]
                if impacts_next_week:
                    print(f"    Impacts: ", end="")
                    print(", ".join([f"{imp.impact_magnitude:+.1f}%" for imp in impacts_next_week]))

    # Save the fixed game
    print(f"\n💾 Saving fixed game to: {output_file}")
    game.save_game(output_file)

    print("\n✅ Done! Load the fixed save file and the prices should be correct.")
    print(f"   Original: {save_file}")
    print(f"   Fixed:    {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix_save_file.py <save_file.json> [output_file.json]")
        print("\nExample: python3 fix_save_file.py savegame.json savegame_fixed.json")
        print("         python3 fix_save_file.py savegame.json  (creates savegame_fixed.json)")
        sys.exit(1)

    save_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fix_save_file(save_file, output_file)
