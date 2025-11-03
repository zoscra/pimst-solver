"""
Basic example of using PIMST to solve a TSP instance.
"""

import pimst
import time

# Define a simple TSP instance (8 cities)
coordinates = [
    (0, 0),    # City 0
    (1, 5),    # City 1
    (5, 2),    # City 2
    (8, 3),    # City 3
    (3, 1),    # City 4
    (7, 6),    # City 5
    (2, 4),    # City 6
    (6, 1),    # City 7
]

print("=" * 60)
print("PIMST - Ultra-Fast TSP Solver")
print("=" * 60)
print(f"\nSolving TSP with {len(coordinates)} cities...")

# Solve with default settings (balanced quality)
result = pimst.solve(coordinates)

print(f"\n✅ Solution found!")
print(f"   Tour: {result['tour']}")
print(f"   Length: {result['length']:.2f}")
print(f"   Time: {result['time']*1000:.1f}ms")
print(f"   Algorithm: {result['algorithm']}")

# Try different quality settings
print("\n" + "=" * 60)
print("Comparing quality settings:")
print("=" * 60)

for quality in ['fast', 'balanced', 'optimal']:
    result = pimst.solve(coordinates, quality=quality)
    print(f"\n{quality.upper():8s}: length={result['length']:.2f}, "
          f"time={result['time']*1000:.1f}ms, "
          f"algo={result['algorithm']}")

# Solve with detailed metrics
print("\n" + "=" * 60)
print("Detailed solution:")
print("=" * 60)

result = pimst.solve_with_details(coordinates, quality='optimal')
print(f"\nTour length: {result['length']:.2f}")
print(f"Estimated gap: {result['gap_estimate']:.1%}")
print(f"Computation time: {result['time']*1000:.1f}ms")
print(f"Algorithm: {result['algorithm']}")
print(f"Improvement: {result['improvement']:.1f}%")

print("\n" + "=" * 60)
print("✅ Example completed successfully!")
print("=" * 60)
