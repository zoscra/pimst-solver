"""
ATSP Benchmark Suite
====================

Comprehensive benchmarking for ATSP solvers.

Tests:
1. Random asymmetric matrices (different sizes)
2. Structured problems (flow shop, matrix patterns)
3. Real-world inspired (routing with one-way streets)
4. Comparison with lower bounds
5. Speed vs quality trade-offs
"""

import numpy as np
import time
import json
from typing import Dict, List, Tuple
from datetime import datetime
from atsp_solver import solve_atsp, validate_atsp_solution, compare_atsp_methods


def generate_random_atsp(n: int, asymmetry_level: float = 0.5, seed: int = None) -> np.ndarray:
    """
    Generate random asymmetric distance matrix.

    Args:
        n: Number of cities
        asymmetry_level: 0 = symmetric, 1 = highly asymmetric
        seed: Random seed for reproducibility

    Returns:
        Asymmetric distance matrix
    """
    if seed is not None:
        np.random.seed(seed)

    # Base symmetric matrix
    distances = np.random.rand(n, n) * 100
    distances = (distances + distances.T) / 2  # Make symmetric
    np.fill_diagonal(distances, 0)

    # Add asymmetry
    if asymmetry_level > 0:
        for i in range(n):
            for j in range(i+1, n):
                if np.random.random() < asymmetry_level:
                    # Make this edge asymmetric
                    factor = np.random.uniform(1.2, 3.0)
                    if np.random.random() < 0.5:
                        distances[i, j] *= factor
                    else:
                        distances[j, i] *= factor

    return distances


def generate_flow_shop_atsp(n_jobs: int, n_machines: int = 2, seed: int = None) -> np.ndarray:
    """
    Generate ATSP from flow shop scheduling problem.

    In flow shop, each job must visit machines in sequence.
    The ATSP distance represents setup times between jobs.

    Args:
        n_jobs: Number of jobs
        n_machines: Number of machines
        seed: Random seed

    Returns:
        Asymmetric distance matrix
    """
    if seed is not None:
        np.random.seed(seed)

    n = n_jobs
    distances = np.zeros((n, n))

    # Processing times for each job on each machine
    processing_times = np.random.randint(1, 20, size=(n_jobs, n_machines))

    # Setup time from job i to job j
    for i in range(n):
        for j in range(n):
            if i != j:
                # Setup depends on job characteristics (asymmetric)
                setup = np.abs(processing_times[i] - processing_times[j]).sum()
                setup += np.random.randint(1, 10)
                distances[i, j] = setup

    return distances


def generate_one_way_streets_atsp(n: int, one_way_prob: float = 0.3, seed: int = None) -> np.ndarray:
    """
    Generate ATSP simulating city with one-way streets.

    Args:
        n: Number of intersections
        one_way_prob: Probability of street being one-way
        seed: Random seed

    Returns:
        Asymmetric distance matrix
    """
    if seed is not None:
        np.random.seed(seed)

    # Generate coordinates
    coords = np.random.rand(n, 2) * 100

    # Euclidean distances
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist = np.linalg.norm(coords[i] - coords[j])
                distances[i, j] = dist
                distances[j, i] = dist

    # Add one-way streets (asymmetry)
    for i in range(n):
        for j in range(i+1, n):
            if np.random.random() < one_way_prob:
                # One-way street: one direction is blocked (very expensive)
                if np.random.random() < 0.5:
                    distances[i, j] = distances[i, j] * 10  # Blocked
                else:
                    distances[j, i] = distances[j, i] * 10  # Blocked

    return distances


def compute_assignment_lower_bound(distances: np.ndarray) -> float:
    """
    Compute lower bound for ATSP using Assignment Problem.

    The Assignment Problem is a relaxation of ATSP and provides
    a valid lower bound.

    Args:
        distances: Asymmetric distance matrix

    Returns:
        Lower bound (AP optimal cost)
    """
    n = len(distances)

    try:
        from scipy.optimize import linear_sum_assignment

        # Modify matrix to prevent self-assignment (diagonal should not be used)
        modified = distances.copy()
        np.fill_diagonal(modified, 1e10)

        row_ind, col_ind = linear_sum_assignment(modified)
        ap_cost = distances[row_ind, col_ind].sum()
        return ap_cost
    except:
        # Fallback: sum of minimum outgoing edges (excluding self)
        lb = 0.0
        for i in range(n):
            min_edge = np.min([distances[i][j] for j in range(n) if j != i])
            lb += min_edge
        return lb


def benchmark_problem(
    distances: np.ndarray,
    problem_name: str,
    methods: List[str] = ['basic', 'super', 'thompson'],
    time_budget: float = 10.0
) -> Dict:
    """
    Benchmark a single ATSP problem with multiple methods.

    Args:
        distances: Distance matrix
        problem_name: Name for this problem
        methods: Methods to test
        time_budget: Time budget per method

    Returns:
        Benchmark results dict
    """
    n = len(distances)
    print(f"\n{'='*70}")
    print(f"  BENCHMARK: {problem_name}")
    print(f"  Size: n={n}")
    print(f"{'='*70}\n")

    # Compute lower bound
    print("  Computing lower bound...")
    lb = compute_assignment_lower_bound(distances)
    print(f"  📊 Assignment lower bound: {lb:.2f}\n")

    # Test each method
    results = {}
    for method in methods:
        print(f"\n  Testing {method.upper()}...")
        start = time.time()

        try:
            tour, cost, metadata = solve_atsp(
                distances,
                method=method,
                quality='balanced',
                time_budget=time_budget,
                verbose=False,
                return_metadata=True
            )

            elapsed = time.time() - start
            gap = ((cost - lb) / lb) * 100

            # Validate
            validation = validate_atsp_solution(tour, distances)

            results[method] = {
                'success': True,
                'cost': float(cost),
                'time': elapsed,
                'gap': gap,
                'valid': validation['valid'],
                'metadata': metadata
            }

            print(f"    ✓ Cost: {cost:.2f}")
            print(f"    📈 Gap vs LB: {gap:.2f}%")
            print(f"    ⏱️  Time: {elapsed:.3f}s")

        except Exception as e:
            results[method] = {
                'success': False,
                'error': str(e)
            }
            print(f"    ✗ Error: {e}")

    # Summary
    print(f"\n  {'='*70}")
    print(f"  SUMMARY for {problem_name}")
    print(f"  {'='*70}")

    successful = {k: v for k, v in results.items() if v.get('success', False)}
    if successful:
        best = min(successful.items(), key=lambda x: x[1]['cost'])
        fastest = min(successful.items(), key=lambda x: x[1]['time'])

        print(f"  🏆 Best cost: {best[0]} ({best[1]['cost']:.2f}, gap: {best[1]['gap']:.2f}%)")
        print(f"  ⚡ Fastest: {fastest[0]} ({fastest[1]['time']:.3f}s)")

    return {
        'problem_name': problem_name,
        'n': n,
        'lower_bound': float(lb),
        'methods': results
    }


def run_comprehensive_benchmark() -> Dict:
    """
    Run comprehensive ATSP benchmark suite.

    Returns:
        Complete benchmark results
    """
    print("\n" + "="*70)
    print("  COMPREHENSIVE ATSP BENCHMARK SUITE")
    print("="*70)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    all_results = []

    # TEST 1: Random problems (different sizes)
    print("\n\n" + "="*70)
    print("  TEST SUITE 1: Random Asymmetric Problems")
    print("="*70)

    for n in [20, 30, 50, 75, 100]:
        for asym in [0.3, 0.5, 0.7]:
            distances = generate_random_atsp(n, asymmetry_level=asym, seed=42+n)
            name = f"random_n{n}_asym{int(asym*100)}"
            result = benchmark_problem(
                distances,
                name,
                methods=['basic', 'super', 'thompson'],
                time_budget=10.0
            )
            all_results.append(result)

    # TEST 2: Flow shop problems
    print("\n\n" + "="*70)
    print("  TEST SUITE 2: Flow Shop Scheduling")
    print("="*70)

    for n_jobs in [20, 30, 50]:
        for n_machines in [2, 3]:
            distances = generate_flow_shop_atsp(n_jobs, n_machines, seed=123+n_jobs)
            name = f"flowshop_j{n_jobs}_m{n_machines}"
            result = benchmark_problem(
                distances,
                name,
                methods=['basic', 'super', 'thompson'],
                time_budget=10.0
            )
            all_results.append(result)

    # TEST 3: One-way streets
    print("\n\n" + "="*70)
    print("  TEST SUITE 3: One-Way Streets (Routing)")
    print("="*70)

    for n in [30, 50, 75]:
        for one_way in [0.2, 0.4]:
            distances = generate_one_way_streets_atsp(n, one_way_prob=one_way, seed=456+n)
            name = f"oneway_n{n}_p{int(one_way*100)}"
            result = benchmark_problem(
                distances,
                name,
                methods=['basic', 'super', 'thompson'],
                time_budget=10.0
            )
            all_results.append(result)

    # FINAL SUMMARY
    print("\n\n" + "="*70)
    print("  FINAL SUMMARY")
    print("="*70)

    # Aggregate by method
    method_stats = {}
    for result in all_results:
        for method, data in result['methods'].items():
            if data.get('success', False):
                if method not in method_stats:
                    method_stats[method] = {
                        'gaps': [],
                        'times': [],
                        'costs': []
                    }
                method_stats[method]['gaps'].append(data['gap'])
                method_stats[method]['times'].append(data['time'])
                method_stats[method]['costs'].append(data['cost'])

    print("\n  Average Performance by Method:")
    print("  " + "-"*70)
    for method, stats in sorted(method_stats.items()):
        avg_gap = np.mean(stats['gaps'])
        avg_time = np.mean(stats['times'])
        n_problems = len(stats['gaps'])
        print(f"  {method:<15} Avg Gap: {avg_gap:>6.2f}%  "
              f"Avg Time: {avg_time:>7.3f}s  "
              f"Problems: {n_problems}")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'atsp_benchmark_results_{timestamp}.json'

    output = {
        'timestamp': timestamp,
        'summary': {
            method: {
                'avg_gap': float(np.mean(stats['gaps'])),
                'avg_time': float(np.mean(stats['times'])),
                'n_problems': len(stats['gaps'])
            }
            for method, stats in method_stats.items()
        },
        'detailed_results': all_results
    }

    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n  💾 Results saved to: {filename}")
    print("="*70 + "\n")

    return output


def quick_benchmark():
    """Quick benchmark for testing."""
    print("\n🚀 Quick ATSP Benchmark\n")

    # One problem of each type
    problems = [
        (generate_random_atsp(30, 0.5, seed=42), "random_30_asym50"),
        (generate_flow_shop_atsp(20, 2, seed=123), "flowshop_20_2"),
        (generate_one_way_streets_atsp(30, 0.3, seed=456), "oneway_30_30")
    ]

    results = []
    for distances, name in problems:
        result = benchmark_problem(
            distances,
            name,
            methods=['basic', 'super', 'thompson'],
            time_budget=5.0
        )
        results.append(result)

    print("\n✅ Quick benchmark completed!\n")
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick test
        quick_benchmark()
    else:
        # Full benchmark
        run_comprehensive_benchmark()
