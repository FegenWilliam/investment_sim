"""Test selling treasury bonds functionality"""
import sys
sys.path.insert(0, '/home/user/investment_sim')

from investment_sim import Player, Treasury

def test_sell_treasury():
    """Test that we can buy and sell treasury bonds"""
    player = Player("Test Player", 10000)
    treasury = Treasury()

    # Test buying bonds
    print("Initial cash:", player.cash)
    print("Initial bonds:", player.treasury_bonds)

    success = player.buy_treasury(treasury, 10)
    assert success, "Should be able to buy 10 bonds"
    assert player.treasury_bonds == 10, "Should have 10 bonds"
    assert player.cash == 10000 - (10 * 100), "Cash should be reduced by 1000"
    print(f"After buying 10 bonds: cash={player.cash}, bonds={player.treasury_bonds}")

    # Test selling bonds
    success, msg = player.sell_treasury(treasury, 5)
    assert success, "Should be able to sell 5 bonds"
    assert player.treasury_bonds == 5, "Should have 5 bonds left"
    assert player.cash == 10000 - (10 * 100) + (5 * 100), "Cash should increase by 500"
    print(f"After selling 5 bonds: cash={player.cash}, bonds={player.treasury_bonds}")
    print(f"Message: {msg}")

    # Test selling more bonds than owned
    success, msg = player.sell_treasury(treasury, 10)
    assert not success, "Should not be able to sell 10 bonds when only 5 owned"
    assert "don't own" in msg.lower(), "Error message should indicate insufficient bonds"
    print(f"Trying to sell too many: success={success}, msg={msg}")

    # Test selling all remaining bonds
    success, msg = player.sell_treasury(treasury, 5)
    assert success, "Should be able to sell remaining 5 bonds"
    assert player.treasury_bonds == 0, "Should have 0 bonds"
    assert player.cash == 10000, "Cash should be back to initial amount"
    print(f"After selling all bonds: cash={player.cash}, bonds={player.treasury_bonds}")

    # Test selling when no bonds owned
    success, msg = player.sell_treasury(treasury, 1)
    assert not success, "Should not be able to sell when no bonds owned"
    print(f"Trying to sell with no bonds: success={success}, msg={msg}")

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_sell_treasury()
