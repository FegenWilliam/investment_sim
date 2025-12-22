#!/usr/bin/env python3
"""Test that themed investments are properly saved and loaded"""

import os
import sys
from investment_sim import Player, QuantumSingularity, Gold, HolyWater

def test_save_load_themed_investments():
    """Test that themed investments survive save/load cycle"""
    print("Testing themed investments save/load...")

    # Create a player with themed investments
    player = Player("TestPlayer", 10000)
    player.quantum_singularity_units = 5
    player.gold_ounces = 10
    player.holy_water_vials = 20
    player.borrowed_amount = 1000

    print(f"Original player:")
    print(f"  Quantum Singularity: {player.quantum_singularity_units} units")
    print(f"  Gold: {player.gold_ounces} oz")
    print(f"  Holy Water: {player.holy_water_vials} vials")
    print(f"  Borrowed: ${player.borrowed_amount:.2f}")

    # Serialize to dict
    player_dict = player.to_dict()

    # Check that themed investments are in the dict
    assert 'quantum_singularity_units' in player_dict, "quantum_singularity_units missing from save!"
    assert 'gold_ounces' in player_dict, "gold_ounces missing from save!"
    assert 'holy_water_vials' in player_dict, "holy_water_vials missing from save!"

    print("\n✓ Themed investments found in serialized dict")

    # Deserialize from dict
    loaded_player = Player.from_dict(player_dict)

    print(f"\nLoaded player:")
    print(f"  Quantum Singularity: {loaded_player.quantum_singularity_units} units")
    print(f"  Gold: {loaded_player.gold_ounces} oz")
    print(f"  Holy Water: {loaded_player.holy_water_vials} vials")
    print(f"  Borrowed: ${loaded_player.borrowed_amount:.2f}")

    # Verify all values match
    assert loaded_player.quantum_singularity_units == player.quantum_singularity_units, \
        f"Quantum Singularity mismatch: {loaded_player.quantum_singularity_units} != {player.quantum_singularity_units}"
    assert loaded_player.gold_ounces == player.gold_ounces, \
        f"Gold mismatch: {loaded_player.gold_ounces} != {player.gold_ounces}"
    assert loaded_player.holy_water_vials == player.holy_water_vials, \
        f"Holy Water mismatch: {loaded_player.holy_water_vials} != {player.holy_water_vials}"
    assert loaded_player.borrowed_amount == player.borrowed_amount, \
        f"Borrowed amount mismatch: {loaded_player.borrowed_amount} != {player.borrowed_amount}"

    print("\n✓ All themed investments and borrowed amount correctly loaded!")

    # Test backwards compatibility (loading old saves without themed investments)
    old_save_dict = {
        'name': 'OldPlayer',
        'cash': 5000,
        'portfolio': {},
        'treasury_bonds': 0,
        'borrowed_amount': 500,
        'max_leverage_ratio': 5.0,
        'interest_rate_weekly': 0.115,
        'short_positions': {},
        'short_borrow_fee_weekly': 0.02,
        'researched_this_week': False,
        'research_history': {}
    }

    old_player = Player.from_dict(old_save_dict)
    print(f"\nOld save (backwards compatibility test):")
    print(f"  Quantum Singularity: {old_player.quantum_singularity_units} units (should be 0)")
    print(f"  Gold: {old_player.gold_ounces} oz (should be 0)")
    print(f"  Holy Water: {old_player.holy_water_vials} vials (should be 0)")

    assert old_player.quantum_singularity_units == 0, "Old save should default to 0 quantum units"
    assert old_player.gold_ounces == 0, "Old save should default to 0 gold"
    assert old_player.holy_water_vials == 0, "Old save should default to 0 holy water"

    print("\n✓ Backwards compatibility test passed!")
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)

if __name__ == "__main__":
    test_save_load_themed_investments()
