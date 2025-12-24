#!/usr/bin/env python3
"""
Analyze slippage calculation to understand the pricing discrepancy
"""

# Your trade example
total_investment = 25000.00
leverage = 2.0
shares_bought = 165.5005
old_price = 150.00
new_price = 151.19  # After market impact
shown_slippage = 174.92

print("="*80)
print("SLIPPAGE ANALYSIS - Your Trade")
print("="*80)
print(f"Total investment: ${total_investment:,.2f}")
print(f"Shares bought: {shares_bought:.4f}")
print(f"Market price before: ${old_price:.2f}")
print(f"Market price after: ${new_price:.2f}")
print(f"Shown slippage cost: ${shown_slippage:.2f}")

print("\n" + "="*80)
print("CALCULATION BREAKDOWN")
print("="*80)

# What you actually paid per share
effective_price = total_investment / shares_bought
print(f"\n1. Effective price paid: ${total_investment:,.2f} / {shares_bought:.4f} = ${effective_price:.2f}")

# Current calculation (relative to OLD price)
slippage_vs_old = (effective_price - old_price) * shares_bought
print(f"\n2. Slippage vs OLD price ($150.00):")
print(f"   ({effective_price:.2f} - {old_price:.2f}) × {shares_bought:.4f}")
print(f"   = ${slippage_vs_old:.2f} ✓ (matches shown slippage)")

# What user might expect (relative to NEW price)
slippage_vs_new = (effective_price - new_price) * shares_bought
print(f"\n3. Slippage vs NEW price ($151.19):")
print(f"   ({effective_price:.2f} - {new_price:.2f}) × {shares_bought:.4f}")
print(f"   = ${slippage_vs_new:.2f} (negative - you paid LESS than market)")

# Market impact cost
market_impact_cost = (new_price - old_price) * shares_bought
print(f"\n4. Market impact cost:")
print(f"   ({new_price:.2f} - {old_price:.2f}) × {shares_bought:.4f}")
print(f"   = ${market_impact_cost:.2f}")

# Total extra cost vs original price
total_extra_cost = (new_price - old_price) * shares_bought
if_no_slippage_at_old_price = old_price * shares_bought
actual_paid = effective_price * shares_bought
print(f"\n5. Cost comparison:")
print(f"   At old price ($150): {shares_bought:.4f} × $150 = ${if_no_slippage_at_old_price:.2f}")
print(f"   Actually paid: ${actual_paid:.2f}")
print(f"   Extra paid: ${actual_paid - if_no_slippage_at_old_price:.2f}")

# What if slippage used the average of old and new price?
avg_price = (old_price + new_price) / 2
slippage_vs_avg = (effective_price - avg_price) * shares_bought
print(f"\n6. Slippage vs AVERAGE price (${avg_price:.2f}):")
print(f"   ({effective_price:.2f} - {avg_price:.2f}) × {shares_bought:.4f}")
print(f"   = ${slippage_vs_avg:.2f}")

print("\n" + "="*80)
print("QUESTION: What should 'slippage' represent?")
print("="*80)
print("\nOption A (CURRENT): Slippage = what you paid vs starting price")
print(f"  → ${slippage_vs_old:.2f}")
print("\nOption B: Slippage = what you paid vs ending price")
print(f"  → ${slippage_vs_new:.2f} (negative - doesn't make sense)")
print("\nOption C: Slippage = what you paid vs average execution price")
print(f"  → ${slippage_vs_avg:.2f}")
print("\nOption D: Show TOTAL cost (slippage + market impact)")
print(f"  → ${slippage_vs_old:.2f} + ${market_impact_cost:.2f} = ${slippage_vs_old + market_impact_cost:.2f}")

print("\n" + "="*80)
print("USER EXPECTATION: ~$190")
print("="*80)
print(f"Market impact cost alone: ${market_impact_cost:.2f}")
print(f"Close to $190! User might expect to see this as 'slippage'")
print("\nInterpretation: User may expect 'slippage' to include market impact")
print("(i.e., total price movement caused by the trade)")
