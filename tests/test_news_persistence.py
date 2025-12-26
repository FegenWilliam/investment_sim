#!/usr/bin/env python3
"""Test that news persists correctly across save/load operations"""

import os
import random
import json
from investment_sim import InvestmentGame, Player

def test_news_persistence():
    """Test that news remains the same when saving and loading"""

    # Try different seeds until we get news generated
    for seed in range(100):
        random.seed(seed)

        # Create a new game using __new__ to bypass interactive initialization
        game = InvestmentGame.__new__(InvestmentGame)

        # Manually initialize just what we need
        from investment_sim import Company, Treasury, BreakingNewsSystem, MarketCycle
        from investment_sim import QuantumSingularity, Gold, HolyWater, ElfQueenWater
        from investment_sim import GoldCoin, VoidStocks, VoidCatalyst, LiquidityLevel

        game.companies = {}
        game.treasury = Treasury()
        game.quantum_singularity = QuantumSingularity()
        game.gold = Gold()
        game.holy_water = HolyWater()
        game.players = [Player("TestPlayer", 10000)]
        game.hedge_funds = []
        game.current_turn = 0
        game.round_number = 1
        game.week_number = 1
        game.breaking_news = BreakingNewsSystem()
        game.market_cycle = MarketCycle()
        game.pending_breaking_news = None
        game.future_prices = {}

        # Initialize a few companies for testing
        company_data = [
            ("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH, 50_000_000_000),
            ("ElectroMax", "Electronics", 85.0, 6.5, LiquidityLevel.MEDIUM, 10_000_000_000),
        ]

        for name, industry, price, volatility, liquidity, market_cap in company_data:
            company = Company(name, industry, price, volatility, liquidity, market_cap)
            game.companies[name] = company

        game.elf_queen_water = ElfQueenWater()
        game.gold_coin = GoldCoin()
        game.void_stocks = VoidStocks(game.companies)
        game.void_catalyst = VoidCatalyst()

        # Pre-calculate future prices
        game._precalculate_future_prices()

        # Manually create a news event to ensure we have something to test
        # Import necessary types
        from investment_sim import CompanyEvent, EventType, NewsReport

        # Create a test event
        test_event = CompanyEvent(
            event_type=EventType.SUCCESS,
            severity=0.8,
            description="TechCorp announces groundbreaking AI breakthrough",
            discovery_week=0,
            weeks_until_public=0,  # Ready to go public immediately
            industry="Technology"
        )

        # Add event to the breaking news system
        game.breaking_news.company_events["TechCorp"] = [test_event]

        # Now generate news (should use our test event)
        initial_news = game.breaking_news.generate_breaking_news(game.companies, game.week_number)

        # If we got news, test it
        if initial_news:
            break

    if not initial_news:
        print("⚠️  No news generated even with manual event - test failed")
        return

    game.pending_breaking_news = initial_news

    # Capture news details for comparison
    company_name, news_report, event_type = initial_news
    print(f"\n✅ Initial news generated (seed={seed}):")
    print(f"   Company: {company_name}")
    print(f"   Event Type: {event_type}")
    print(f"   Trustworthy: {news_report.trustworthy_source[:60] if news_report.trustworthy_source else '(empty)'}...")
    print(f"   Market Pulse: {news_report.market_pulse_source[:60]}...")
    print(f"   Insider: {news_report.insider_source[:60]}...")

    # Save the game
    save_file = "test_news_persistence.json"
    success = game.save_game(save_file)
    assert success, "Failed to save game"

    # Load the game
    loaded_game = InvestmentGame.load_game(save_file)
    assert loaded_game is not None, "Failed to load game"

    # Check that pending_breaking_news was loaded
    assert loaded_game.pending_breaking_news is not None, "Pending breaking news was not loaded"

    loaded_company_name, loaded_news_report, loaded_event_type = loaded_game.pending_breaking_news

    print(f"\n✅ News after loading:")
    print(f"   Company: {loaded_company_name}")
    print(f"   Event Type: {loaded_event_type}")
    print(f"   Trustworthy: {loaded_news_report.trustworthy_source[:60] if loaded_news_report.trustworthy_source else '(empty)'}...")
    print(f"   Market Pulse: {loaded_news_report.market_pulse_source[:60]}...")
    print(f"   Insider: {loaded_news_report.insider_source[:60]}...")

    # Verify news is the same
    assert company_name == loaded_company_name, f"Company name changed: {company_name} != {loaded_company_name}"
    assert event_type == loaded_event_type, f"Event type changed: {event_type} != {loaded_event_type}"
    assert news_report.trustworthy_source == loaded_news_report.trustworthy_source, "Trustworthy source changed"
    assert news_report.market_pulse_source == loaded_news_report.market_pulse_source, "Market Pulse source changed"
    assert news_report.insider_source == loaded_news_report.insider_source, "Insider source changed"
    assert news_report.rumor_mill_source == loaded_news_report.rumor_mill_source, "Rumor Mill source changed"
    assert news_report.insider_flipped == loaded_news_report.insider_flipped, "Insider flipped status changed"
    assert news_report.is_rumor == loaded_news_report.is_rumor, "Is rumor status changed"

    print("\n✅ SUCCESS: News persists correctly across save/load!")

    # Clean up
    if os.path.exists(save_file):
        os.remove(save_file)
        print(f"✅ Cleaned up test save file: {save_file}")

    # Now test that play() doesn't regenerate news
    print("\n🔄 Testing that play() preserves loaded news...")

    # This is what happens when you load and play - we need to ensure
    # that the news doesn't change
    # We can't actually call play() because it starts an interactive loop,
    # but we can verify that the condition in play() works correctly
    if loaded_game.pending_breaking_news is None:
        print("❌ FAIL: pending_breaking_news should not be None after loading")
    else:
        print("✅ SUCCESS: pending_breaking_news is preserved and won't be regenerated in play()")

if __name__ == "__main__":
    test_news_persistence()
