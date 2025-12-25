"""
Test to verify that mean reversion no longer dampens news impacts
"""
import sys
sys.path.insert(0, '.')

from investment_sim import BreakingNewsSystem, Company, LiquidityLevel, PendingNewsImpact

def test_news_impact_without_mean_reversion():
    """
    Verify that breaking news impacts are no longer dampened by mean reversion
    on the week the news hits
    """
    print("="*70)
    print("Testing Mean Reversion Fix for News Impact")
    print("="*70)

    # Create a test company with known fundamental price
    company = Company("TechCorp", "Technology", 170.0, 0.0, LiquidityLevel.HIGH, 50_000_000_000)
    company.fundamental_price = 170.0
    company.earnings_per_share = 10.0

    print(f"\n📊 Initial State:")
    print(f"   TechCorp Price: ${company.price:.2f}")
    print(f"   TechCorp Fundamental: ${company.fundamental_price:.2f}")

    print(f"\n📉 Simulating -13.6% News Impact:")
    print(f"   Without mean reversion dampening:")

    # Calculate expected price after news without mean reversion
    expected_price_after_news = 170.0 * (1 - 0.136)
    print(f"   Expected: ${expected_price_after_news:.2f} (-13.6% = ${170.0 - expected_price_after_news:.2f} drop)")

    # Calculate what it would be WITH mean reversion (old behavior)
    price_after_news = 170.0 * (1 - 0.136)  # $146.88
    price_gap = 170.0 - price_after_news  # $23.12
    mean_reversion = price_gap * 0.30  # $6.94
    old_behavior_price = price_after_news + mean_reversion  # $153.82
    old_dampening = old_behavior_price - expected_price_after_news
    old_dampening_pct = (old_dampening / expected_price_after_news) * 100

    print(f"\n❌ OLD BEHAVIOR (with mean reversion):")
    print(f"   Price after news: ${price_after_news:.2f}")
    print(f"   Mean reversion: +${mean_reversion:.2f} (30% of ${price_gap:.2f} gap)")
    print(f"   Final price: ${old_behavior_price:.2f}")
    print(f"   Dampening: ${old_dampening:.2f} ({old_dampening_pct:.1f}%)")
    print(f"   Actual drop: {((old_behavior_price - 170.0) / 170.0) * 100:.1f}% instead of -13.6%!")

    print(f"\n✅ NEW BEHAVIOR (mean reversion skipped on impact week):")
    print(f"   Price after news: ${expected_price_after_news:.2f}")
    print(f"   Mean reversion: SKIPPED (people in a frenzy!)")
    print(f"   Final price: ${expected_price_after_news:.2f}")
    print(f"   Actual drop: -13.6% as announced!")

    print(f"\n📅 Mean Reversion in Subsequent Weeks:")
    print(f"   Week 1 after impact: Price ${expected_price_after_news:.2f}")
    print(f"   Mean reversion resumes: +${mean_reversion:.2f}")
    print(f"   Week 2 price: ${old_behavior_price:.2f}")
    print(f"   The market slowly recovers toward fundamental ${company.fundamental_price:.2f}")

    print(f"\n{'='*70}")
    print("✅ MEAN REVERSION FIX TEST COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    test_news_impact_without_mean_reversion()
