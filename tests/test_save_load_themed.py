#!/usr/bin/env python3
"""Test save/load functionality for themed investments"""

import sys
sys.path.insert(0, '/home/user/investment_sim')

from investment_sim import Player

def test_save_load_themed():
    print("Testing Save/Load for Themed Investments")
    print("="*60)

    # Create a player with themed investments
    print("\n1. Creating player with themed investments")
    player = Player("TestPlayer", 50000.0)
    player.quantum_singularity_units = 5
    player.elf_queen_water_vials = 20
    player.void_stocks_shares = 10

    print("  Player holdings:")
    print(f"  Quantum Singularity: {player.quantum_singularity_units} units")
    print(f"  Elf Queen's Water: {player.elf_queen_water_vials} vials")
    print(f"  Void Stocks: {player.void_stocks_shares} shares")

    # Save to dict
    print("\n2. Saving to dictionary")
    player_dict = player.to_dict()

    assert 'quantum_singularity_units' in player_dict, "quantum_singularity_units missing from save!"
    assert 'elf_queen_water_vials' in player_dict, "elf_queen_water_vials missing from save!"
    assert 'void_stocks_shares' in player_dict, "void_stocks_shares missing from save!"

    print("  All themed investment fields present in save")

    # Load from dict
    print("\n3. Loading from dictionary")
    loaded_player = Player.from_dict(player_dict)

    print("  Loaded player holdings:")
    print(f"  Quantum Singularity: {loaded_player.quantum_singularity_units} units")
    print(f"  Elf Queen's Water: {loaded_player.elf_queen_water_vials} vials")
    print(f"  Void Stocks: {loaded_player.void_stocks_shares} shares")

    # Verify
    print("\n4. Verifying data integrity")
    assert loaded_player.quantum_singularity_units == player.quantum_singularity_units, \
        f"QS mismatch: {loaded_player.quantum_singularity_units} != {player.quantum_singularity_units}"
    assert loaded_player.elf_queen_water_vials == player.elf_queen_water_vials, \
        f"EQW mismatch: {loaded_player.elf_queen_water_vials} != {player.elf_queen_water_vials}"
    assert loaded_player.void_stocks_shares == player.void_stocks_shares, \
        f"Void Stocks mismatch: {loaded_player.void_stocks_shares} != {player.void_stocks_shares}"

    print("  All data matches!")

    # Test backward compatibility (loading old save without themed investments)
    print("\n5. Testing backward compatibility")
    old_save = {
        'name': 'OldPlayer',
        'cash': 10000.0,
        'portfolio': {},
        'treasury_bonds': 0,
        'borrowed_amount': 0.0,
        'max_leverage_ratio': 5.0,
        'interest_rate_weekly': 0.115,
    }

    old_player = Player.from_dict(old_save)
    print(f"  Loaded old save:")
    print(f"  Quantum Singularity: {old_player.quantum_singularity_units} units (should be 0)")
    print(f"  Elf Queen's Water: {old_player.elf_queen_water_vials} vials (should be 0)")
    print(f"  Void Stocks: {old_player.void_stocks_shares} shares (should be 0)")

    assert old_player.quantum_singularity_units == 0, "Old save should default to 0 QS"
    assert old_player.elf_queen_water_vials == 0, "Old save should default to 0 EQW"
    assert old_player.void_stocks_shares == 0, "Old save should default to 0 Void Stocks"

    print("  Backward compatibility works!")

    print("\n" + "="*60)
    print("All tests passed!")

if __name__ == "__main__":
    test_save_load_themed()
