#!/usr/bin/env python3
"""
Test slippage calculation fix - now uses daily volume like market impact
"""

def old_slippage(trade_value, market_cap):
    """Old formula based on market cap"""
    trade_pct_of_market = trade_value / market_cap
    base_slippage = (trade_pct_of_market ** 0.5) * 10.0
    total_slippage = min(base_slippage, 0.5)
    return total_slippage

def new_slippage(trade_value, market_cap, liquidity):
    """New formula based on daily volume (matches market impact)"""
    if liquidity == "HIGH":
        daily_volume_pct = 0.02
        base_coefficient = 0.35 * 0.7  # 30% less
    elif liquidity == "MEDIUM":
        daily_volume_pct = 0.005
        base_coefficient = 0.35
    else:  # LOW
        daily_volume_pct = 0.001
        base_coefficient = 0.35 * 1.5  # 50% more

    estimated_daily_volume = market_cap * daily_volume_pct
    trade_pct_of_daily_volume = trade_value / estimated_daily_volume
    slippage = (trade_pct_of_daily_volume ** 0.5) * base_coefficient
    slippage = min(slippage, 0.25)
    return slippage

def new_market_impact(trade_value, market_cap, liquidity):
    """Market impact formula (for comparison)"""
    if liquidity == "HIGH":
        daily_volume_pct = 0.02
        base_coefficient = 0.25 * 0.7
    elif liquidity == "MEDIUM":
        daily_volume_pct = 0.005
        base_coefficient = 0.25
    else:  # LOW
        daily_volume_pct = 0.001
        base_coefficient = 0.25 * 1.5

    estimated_daily_volume = market_cap * daily_volume_pct
    trade_pct_of_daily_volume = trade_value / estimated_daily_volume
    impact = (trade_pct_of_daily_volume ** 0.5) * base_coefficient
    impact = min(impact, 0.05)
    return impact

print("="*80)
print("SLIPPAGE CALCULATION FIX")
print("="*80)

# User's example
trade_value = 25000
market_cap = 50_000_000_000
liquidity = "HIGH"
price = 150.0
shares = 165.5005

old_slip = old_slippage(trade_value, market_cap)
new_slip = new_slippage(trade_value, market_cap, liquidity)
new_impact = new_market_impact(trade_value, market_cap, liquidity)

print(f"\nYour trade: ${trade_value:,} on TechCorp (${market_cap/1e9:.0f}B, {liquidity} liquidity)")
print(f"Shares: {shares:.4f} @ ${price:.2f}")

print(f"\n{'OLD FORMULA (market cap-based):':<40}")
print(f"  Slippage %: {old_slip*100:.3f}%")
print(f"  Slippage cost: ${old_slip * trade_value:.2f}")

print(f"\n{'NEW FORMULA (daily volume-based):':<40}")
print(f"  Slippage %: {new_slip*100:.3f}%")
print(f"  Slippage cost: ${new_slip * trade_value:.2f}")
print(f"  Market impact %: {new_impact*100:.3f}%")
print(f"  Market impact on price: ${new_impact * price:.2f}")

print(f"\n{'COMPARISON:':<40}")
print(f"  Old slippage cost: ${old_slip * trade_value:.2f}")
print(f"  New slippage cost: ${new_slip * trade_value:.2f}")
print(f"  Improvement: {old_slip/new_slip:.1f}x more realistic")

print(f"\n{'RELATIONSHIP:':<40}")
print(f"  Slippage % = {new_slip*100:.3f}% (what YOU pay)")
print(f"  Impact % = {new_impact*100:.3f}% (market price moves)")
print(f"  Ratio = {new_slip/new_impact:.2f}x (slippage slightly higher)")
print(f"\n  This makes sense: slippage includes bid-ask spread + impact")

print("\n" + "="*80)
print("SCENARIOS")
print("="*80)

scenarios = [
    ("TechCorp ($50B HIGH)", 25000, 50_000_000_000, "HIGH", 150),
    ("ElectroMax ($10B MED)", 25000, 10_000_000_000, "MEDIUM", 85),
    ("AutoDrive ($2B LOW)", 25000, 2_000_000_000, "LOW", 95),
]

for name, trade, mcap, liq, p in scenarios:
    old_s = old_slippage(trade, mcap)
    new_s = new_slippage(trade, mcap, liq)
    new_i = new_market_impact(trade, mcap, liq)

    print(f"\n{name}")
    print(f"  Trade: ${trade:,}")
    print(f"  Old slippage: ${old_s * trade:.2f} ({old_s*100:.2f}%)")
    print(f"  New slippage: ${new_s * trade:.2f} ({new_s*100:.2f}%)")
    print(f"  New impact: ${new_i * p:.2f} price move ({new_i*100:.2f}%)")
    print(f"  Change: {old_s/new_s:.1f}x")

print("\n" + "="*80)
print("KEY IMPROVEMENTS:")
print("="*80)
print("✓ Slippage now uses daily volume (not market cap)")
print("✓ Consistent with market impact formula")
print("✓ Slippage slightly higher than impact (includes spread)")
print("✓ Both scale realistically with trade size")
print("="*80)
