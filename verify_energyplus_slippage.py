#!/usr/bin/env python3
"""Verify EnergyPlus trade slippage calculation"""

# Simulate the slippage calculation for EnergyPlus
# EnergyPlus params: price=$106.33, volatility=9.0, liquidity=LOW, market_cap=$5B

def calculate_slippage_factor(shares, price, market_cap, volatility, is_low_liquidity=True):
    """Calculate slippage factor for a trade"""

    # Daily volume for LOW liquidity
    daily_volume_pct = 0.005  # 0.5% of market cap
    estimated_daily_volume = market_cap * daily_volume_pct

    # Trade value and percentage
    trade_value = shares * price
    trade_pct_of_daily_volume = trade_value / estimated_daily_volume

    # Minimum trade percentage
    min_trade_pct = 0.00005
    effective_trade_pct = max(trade_pct_of_daily_volume, min_trade_pct)

    # Base coefficient
    base_coefficient = 0.35
    if is_low_liquidity:
        base_coefficient *= 1.5  # 0.525

    # Calculate slippage
    slippage = (effective_trade_pct ** 0.5) * base_coefficient

    # Volatility adjustment
    baseline_vol = 7.5
    vol_adjustment = volatility / baseline_vol
    vol_adjustment = max(0.6, min(vol_adjustment, 1.6))
    slippage *= vol_adjustment

    # Notional dampener
    notional_dampener = min(1.0, trade_value / 1_000_000)
    slippage *= notional_dampener

    # Cap at 25%
    slippage = min(slippage, 0.25)

    # Return slippage factor (for buy)
    return 1 + slippage

def calculate_market_impact(shares, price, market_cap, volatility, is_low_liquidity=True):
    """Calculate market impact multiplier"""

    # Daily volume for LOW liquidity
    daily_volume_pct = 0.005
    estimated_daily_volume = market_cap * daily_volume_pct

    # Trade value and percentage
    trade_value = shares * price
    trade_pct_of_daily_volume = trade_value / estimated_daily_volume

    # Minimum trade percentage
    min_trade_pct = 0.00005
    effective_trade_pct = max(trade_pct_of_daily_volume, min_trade_pct)

    # Base impact coefficient
    base_impact_coefficient = 0.25
    if is_low_liquidity:
        base_impact_coefficient *= 1.5  # 0.375

    # Calculate impact
    impact_multiplier = (effective_trade_pct ** 0.5) * base_impact_coefficient

    # Volatility adjustment
    baseline_vol = 7.5
    vol_adjustment = volatility / baseline_vol
    vol_adjustment = max(0.6, min(vol_adjustment, 1.6))
    impact_multiplier *= vol_adjustment

    # Notional dampener
    notional_dampener = min(1.0, trade_value / 1_000_000)
    impact_multiplier *= notional_dampener

    # Cap at 5%
    impact_multiplier = min(impact_multiplier, 0.05)

    return impact_multiplier

# EnergyPlus parameters
initial_price = 106.33
market_cap = 5_000_000_000  # $5B
volatility = 9.0
total_investment = 2_000_000  # $2M (with 2x leverage)

print("EnergyPlus Trade Verification")
print("="*60)
print(f"Initial price: ${initial_price:.2f}")
print(f"Market cap: ${market_cap:,.0f}")
print(f"Volatility: {volatility}")
print(f"Liquidity: LOW")
print(f"Total investment: ${total_investment:,.2f}")
print()

# Iterative calculation to find shares (same as buy_stock function)
shares = total_investment / initial_price
print(f"Initial share estimate: {shares:.4f}")
print()

# Iterate to converge
for i in range(5):
    slippage_factor = calculate_slippage_factor(shares, initial_price, market_cap, volatility)
    effective_price = initial_price * slippage_factor
    new_shares = total_investment / effective_price
    print(f"Iteration {i+1}:")
    print(f"  Slippage factor: {slippage_factor:.6f}")
    print(f"  Effective price: ${effective_price:.2f}")
    print(f"  Shares: {new_shares:.4f}")
    shares = new_shares

print()
print("Final calculation:")
print("-"*60)

# Final slippage calculation
slippage_factor = calculate_slippage_factor(shares, initial_price, market_cap, volatility)
effective_price = initial_price * slippage_factor
actual_cost = effective_price * shares

print(f"Shares purchased: {shares:.4f}")
print(f"Slippage factor: {slippage_factor:.6f}")
print(f"Effective price: ${effective_price:.2f}")
print(f"Actual cost: ${actual_cost:.2f}")
print()

# Calculate slippage cost
slippage_cost = (effective_price - initial_price) * shares
print(f"Price slippage cost: ${slippage_cost:,.2f}")
print(f"  Formula: (${effective_price:.2f} - ${initial_price:.2f}) * {shares:.4f}")
print()

# Calculate market impact
impact_multiplier = calculate_market_impact(shares, initial_price, market_cap, volatility)
new_price = initial_price * (1 + impact_multiplier)
price_change = new_price - initial_price

print(f"Market impact:")
print(f"  Impact multiplier: {impact_multiplier:.6f} ({impact_multiplier*100:.4f}%)")
print(f"  New price: ${new_price:.2f}")
print(f"  Price change: +${price_change:.2f}")
print()

print("User's reported values:")
print("-"*60)
print(f"Shares: 16143.7519")
print(f"Price slippage: $283,386.47")
print(f"Price moved: $106.33 to $111.65 (+$5.32)")
print()

print("Comparison:")
print("-"*60)
print(f"Shares - Calculated: {shares:.4f}, Reported: 16143.7519")
print(f"  Difference: {abs(shares - 16143.7519):.4f}")
print()
print(f"Slippage - Calculated: ${slippage_cost:,.2f}, Reported: $283,386.47")
print(f"  Difference: ${abs(slippage_cost - 283386.47):,.2f}")
print()
print(f"New price - Calculated: ${new_price:.2f}, Reported: $111.65")
print(f"  Difference: ${abs(new_price - 111.65):.2f}")
