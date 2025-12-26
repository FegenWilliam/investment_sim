#!/usr/bin/env python3
"""Fix a save file by recalculating future prices with the corrected code"""

import sys
import json
from investment_sim import InvestmentGame

def fix_save_file(save_file, output_file=None, apply_two_stage_impacts=False):
    """Load a save file and recalculate future prices with fixed code

    Args:
        save_file: Path to the save file to fix
        output_file: Optional output path (defaults to <save_file>_fixed.json)
        apply_two_stage_impacts: If True, convert old single-stage impacts to new two-stage system
    """

    if output_file is None:
        output_file = save_file.replace('.json', '_fixed.json')

    print("="*70)
    print("FIXING SAVE FILE - RECALCULATING FUTURE PRICES")
    if apply_two_stage_impacts:
        print("               + APPLYING TWO-STAGE IMPACT SYSTEM")
    print("="*70)

    # Load the save file
    print(f"\nLoading: {save_file}")
    game = InvestmentGame.load_game(save_file)

    if game is None:
        print("Error: Could not load save file!")
        return

    print(f"Current Week: {game.week_number}")

    # Apply two-stage impact system if requested
    if apply_two_stage_impacts:
        print("\n🔄 Converting pending impacts to two-stage system...")
        impacts_converted = 0
        for impact in game.breaking_news.pending_impacts:
            if not impact.instant_impact_applied:
                # This is an old-style impact, convert it
                print(f"  Converting {impact.company_name}: {impact.impact_magnitude:+.1f}% impact")

                # Apply 20% instant impact to current price
                instant_impact_pct = impact.impact_magnitude * 0.20
                company = game.companies[impact.company_name]
                old_price = company.price
                company.price *= (1 + instant_impact_pct / 100)
                company.price = max(0.01, company.price)

                print(f"    Instant impact (20%): {instant_impact_pct:+.1f}% - Price: ${old_price:.2f} -> ${company.price:.2f}")

                # Adjust timing to 1-2 weeks if it was set to 3 weeks
                if impact.weeks_until_impact > 2:
                    old_weeks = impact.weeks_until_impact
                    impact.weeks_until_impact = 2
                    print(f"    Adjusted timing: {old_weeks} weeks -> 2 weeks")

                # Mark as converted
                impact.instant_impact_applied = True
                print(f"    Delayed impact (80%): {impact.impact_magnitude * 0.80:+.1f}% in {impact.weeks_until_impact} week(s)")

                impacts_converted += 1

        if impacts_converted > 0:
            print(f"\n✅ Converted {impacts_converted} pending impact(s) to two-stage system")
        else:
            print("\n✅ No old-style impacts found - all impacts already using two-stage system")

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
        print("Usage: python3 fix_save_file.py <save_file.json> [output_file.json] [--two-stage]")
        print("\nOptions:")
        print("  --two-stage    Convert old single-stage impacts to new two-stage system")
        print("                 (applies 20% instant impact, 80% delayed impact over 1-2 weeks)")
        print("\nExamples:")
        print("  python3 fix_save_file.py savegame.json savegame_fixed.json")
        print("  python3 fix_save_file.py savegame.json  (creates savegame_fixed.json)")
        print("  python3 fix_save_file.py savegame.json --two-stage")
        print("  python3 fix_save_file.py savegame.json savegame_fixed.json --two-stage")
        sys.exit(1)

    # Parse arguments
    save_file = sys.argv[1]
    apply_two_stage = '--two-stage' in sys.argv

    # Find output file (it's the argument that's not --two-stage and not the save file)
    output_file = None
    for arg in sys.argv[2:]:
        if arg != '--two-stage':
            output_file = arg
            break

    fix_save_file(save_file, output_file, apply_two_stage_impacts=apply_two_stage)
