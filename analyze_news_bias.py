#!/usr/bin/env python3
"""Analysis of news generation bias"""

def calculate_event_probabilities(strength):
    """Calculate event type probabilities for a given company strength"""
    success_prob = strength * 0.4
    problem_prob = 0.3
    scandal_prob = 1.0 - success_prob - problem_prob

    return {
        'SUCCESS (positive)': success_prob,
        'PROBLEM (negative)': problem_prob,
        'SCANDAL (negative)': scandal_prob,
        'Total Negative': problem_prob + scandal_prob
    }

print("Current News Generation Probabilities")
print("=" * 60)
print("\nCompany Strength | SUCCESS | PROBLEM | SCANDAL | Total Negative")
print("-" * 60)

strengths = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
for strength in strengths:
    probs = calculate_event_probabilities(strength)
    print(f"{strength:^16.1f} | {probs['SUCCESS (positive)']:>6.1%} | {probs['PROBLEM (negative)']:>6.1%} | "
          f"{probs['SCANDAL (negative)']:>6.1%} | {probs['Total Negative']:>13.1%}")

avg_strength = 0.6
avg_probs = calculate_event_probabilities(avg_strength)
print("\n" + "=" * 60)
print(f"Average Company (strength {avg_strength}):")
print(f"  Positive News: {avg_probs['SUCCESS (positive)']:.1%}")
print(f"  Negative News: {avg_probs['Total Negative']:.1%}")
print("\n🚨 ISSUE: News is heavily biased toward negative (76% negative for avg company)")
print("\nProbability of 8 consecutive negative news:")
print(f"  0.76^8 = {0.76**8:.1%} (quite likely to happen!)")
