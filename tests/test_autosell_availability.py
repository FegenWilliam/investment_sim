#!/usr/bin/env python3
"""Test that Void Catalyst auto-sell properly consumes availability slot"""

import random
from investment_sim import Player, VoidCatalyst

def test_autosell_consumes_availability():
    """Test that when auto-sell triggers, player can't immediately retry"""

    # Set up
    player = Player("TestPlayer", starting_cash=200000)
    void_catalyst = VoidCatalyst()
    all_human_players = ["TestPlayer"]

    print("Initial state:")
    print(f"  Player cash: ${player.cash:,.2f}")
    print(f"  Void Catalyst price: ${void_catalyst.price:,.2f}")
    print(f"  Players in cycle: {void_catalyst.players_owned_this_cycle}")
    print()

    # Force auto-sell by setting random seed
    # We need to find a seed that triggers auto-sell (< 0.10)
    print("Attempting purchase that will auto-sell...")
    random.seed(1)  # This seed should trigger auto-sell

    # Try to buy - this should trigger auto-sell
    success, msg = player.buy_void_catalyst(void_catalyst, all_human_players)
    print(f"First purchase: {msg}")
    print(f"  Success: {success}")
    print(f"  Player owns: {player.void_catalyst_owned}")
    print(f"  Void Catalyst owned: {void_catalyst.is_owned}")
    print(f"  Players in cycle: {void_catalyst.players_owned_this_cycle}")
    print(f"  Player cash: ${player.cash:,.2f}")
    print()

    # Verify auto-sell happened (player doesn't own it)
    if player.void_catalyst_owned:
        print("ERROR: Auto-sell didn't trigger with seed 1, trying different seed...")
        # Try different seeds until we get auto-sell
        for seed in range(100):
            player = Player("TestPlayer", starting_cash=200000)
            void_catalyst = VoidCatalyst()
            random.seed(seed)
            success, msg = player.buy_void_catalyst(void_catalyst, all_human_players)
            if success and not player.void_catalyst_owned:
                print(f"Found auto-sell with seed {seed}")
                print(f"  Message: {msg}")
                print(f"  Players in cycle: {void_catalyst.players_owned_this_cycle}")
                break
        else:
            print("ERROR: Could not trigger auto-sell in 100 attempts!")
            return False
    print()

    # Now try to buy again IMMEDIATELY - this should be BLOCKED
    print("Attempting immediate retry after auto-sell...")
    can_buy, reason = void_catalyst.can_player_buy("TestPlayer", all_human_players)
    print(f"  Can buy: {can_buy}")
    print(f"  Reason: {reason}")
    print(f"  Players in cycle AFTER check: {void_catalyst.players_owned_this_cycle}")
    print()

    if can_buy:
        print("❌ FAIL: Player can immediately retry after auto-sell!")
        print("   This defeats the purpose of the availability system!")
        return False

    # Verify the cycle was reset by the previous check
    if len(void_catalyst.players_owned_this_cycle) > 0:
        print("❌ FAIL: Cycle was not reset after blocking the retry!")
        return False

    print("✓ First retry blocked correctly (cycle reset for next time)")
    print()

    # Now try AGAIN - this should be ALLOWED (cycle has been reset)
    print("Attempting second retry (cycle should be reset now)...")
    can_buy, reason = void_catalyst.can_player_buy("TestPlayer", all_human_players)
    print(f"  Can buy: {can_buy}")
    print(f"  Reason: {reason}")
    print()

    if not can_buy:
        print("❌ FAIL: Player can't buy after cycle reset!")
        return False

    print("✓ Second retry allowed correctly (cycle was reset)")
    print()
    print("="*60)
    print("✅ TEST PASSED: Auto-sell properly consumes availability!")
    print("   - Auto-sell triggers → player added to cycle")
    print("   - Immediate retry → BLOCKED (cycle resets but purchase blocked)")
    print("   - Second retry → ALLOWED (cycle is now clear)")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_autosell_consumes_availability()
    exit(0 if success else 1)
