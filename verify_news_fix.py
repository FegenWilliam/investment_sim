#!/usr/bin/env python3
"""Verify the news generation fix"""

def calculate_event_probabilities(strength, multiplier):
    """Calculate event type probabilities for a given company strength"""
    success_prob = strength * multiplier
    problem_prob = 0.3
    scandal_prob = 1.0 - success_prob - problem_prob

    return {
        'SUCCESS (positive)': success_prob,
        'PROBLEM (negative)': problem_prob,
        'SCANDAL (negative)': scandal_prob,
        'Total Negative': problem_prob + scandal_prob
    }

print("News Generation Fix Comparison")
print("=" * 80)

print("\nBEFORE (multiplier = 0.4):")
print("-" * 80)
print("Strength | SUCCESS | PROBLEM | SCANDAL | Total Negative")
print("-" * 80)
strengths = [0.3, 0.6, 0.9]
for strength in strengths:
    probs = calculate_event_probabilities(strength, 0.4)
    print(f"  {strength:.1f}   | {probs['SUCCESS (positive)']:>6.1%} | {probs['PROBLEM (negative)']:>6.1%} | "
          f"{probs['SCANDAL (negative)']:>6.1%} | {probs['Total Negative']:>13.1%}")

print("\nAFTER (multiplier = 0.7):")
print("-" * 80)
print("Strength | SUCCESS | PROBLEM | SCANDAL | Total Negative")
print("-" * 80)
for strength in strengths:
    probs = calculate_event_probabilities(strength, 0.7)
    print(f"  {strength:.1f}   | {probs['SUCCESS (positive)']:>6.1%} | {probs['PROBLEM (negative)']:>6.1%} | "
          f"{probs['SCANDAL (negative)']:>6.1%} | {probs['Total Negative']:>13.1%}")

print("\n" + "=" * 80)
print("IMPACT ON AVERAGE COMPANY (strength 0.6):")
print("-" * 80)
before = calculate_event_probabilities(0.6, 0.4)
after = calculate_event_probabilities(0.6, 0.7)
print(f"Before: {before['SUCCESS (positive)']:.1%} positive, {before['Total Negative']:.1%} negative")
print(f"After:  {after['SUCCESS (positive)']:.1%} positive, {after['Total Negative']:.1%} negative")
print(f"\nImprovement: {(after['SUCCESS (positive)'] - before['SUCCESS (positive)']):.1%} more positive news!")

print("\n8 consecutive negative news probability:")
print(f"  Before: {before['Total Negative']**8:.1%}")
print(f"  After:  {after['Total Negative']**8:.1%}")
print(f"  Reduction: {((before['Total Negative']**8 - after['Total Negative']**8) / before['Total Negative']**8):.1%}")
