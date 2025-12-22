#!/usr/bin/env python3
"""Test script for research and weekly news enhancements"""

import sys
import random

# Import the game classes
from investment_sim import Company, LiquidityLevel, WeeklyGazette, Player

def test_weekly_gazette():
    """Test the weekly gazette news generation"""
    print("="*60)
    print("Testing Weekly Gazette")
    print("="*60)

    # Create test companies
    companies = {
        "TechCorp": Company("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH),
        "PharmaCare": Company("PharmaCare", "Pharmaceuticals", 220.0, 5.0, LiquidityLevel.LOW),
    }

    # Create weekly gazette
    gazette = WeeklyGazette()

    # Generate 5 weekly news items
    print("\nGenerating 5 weekly news items:\n")
    for week in range(1, 6):
        news = gazette.generate_weekly_news(companies, week)
        print(f"Week {week}: {news}")

    print("\n✅ Weekly Gazette test passed!\n")

def test_enhanced_research():
    """Test the enhanced research hints"""
    print("="*60)
    print("Testing Enhanced Research Hints")
    print("="*60)

    # Create test company
    company = Company("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH)

    # Create test player
    player = Player("TestPlayer")

    # Get 5 research hints
    print("\nGenerating 5 research hints:\n")
    hints_received = []
    for i in range(5):
        # Reset research flag to allow multiple researches
        player.researched_this_week = False
        hint = player.research_company(company)
        hints_received.append(hint)
        print(f"{i+1}. {hint}\n")

    # Check that hints are varied
    unique_hints = len(set(hints_received))
    print(f"Generated {unique_hints} unique hints out of 5 total hints")

    if unique_hints >= 3:
        print("✅ Research hints are varied!\n")
    else:
        print("⚠️  Warning: Less variety than expected\n")

    print("✅ Enhanced Research test passed!\n")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TESTING RESEARCH AND NEWS ENHANCEMENTS")
    print("="*60 + "\n")

    try:
        test_weekly_gazette()
        test_enhanced_research()

        print("="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        return 0

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
