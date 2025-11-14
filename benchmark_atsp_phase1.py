"""
ATSP Benchmark - Phase 1 Improvements
======================================

Compares original PIMST-ATSP vs Phase 1 improved version.

Expected results:
- Original: ~20% gap
- Phase 1:  ~12-15% gap  (target)

Improvements:
1. Better construction (Farthest Insertion, Cheapest Insertion)
2. 3-opt operator (much more powerful than 2-opt/or-opt)
3. Longer search times (60-120s vs 10-40s, fair comparison with LKH)

Author: PIMST Project
Date: 2025-11-14
"""

import numpy as np
import time
import json
from datetime import datetime
from pathlib import Path

# Import original solver
try:
    from src.pimst import atsp_solver
    solve_original = atsp_solver.solve_atsp
except:
    # Fallback
    def solve_original(distances, method='quantum', quality='balanced'):
        from src.pimst.atsp_complementary_quantum import solve_atsp_complementary_quantum
        tour, cost, _ = solve_atsp_complementary_quantum(distances)
        return tour, cost, {}

# Import improved solver
from src.pimst.atsp_solver_improved import solve_atsp_improved, solve_atsp_multi_start_improved


def compute_assignment_lower_bound(distances):
    """Compute Assignment Problem lower bound."""
    n = len(distances)
    try:
        from scipy.optimize import linear_sum_assignment
        modified = distances.copy()
        np.fill_diagonal(modified, 1e10)
        row_ind, col_ind = linear_sum_assignment(modified)
        return distances[row_ind, col_ind].sum()
    except:
        # Fallback
        return np.sum([np.min([distances[i][j] for j in range(n) if j != i]) for i in range(n)])


def generate_atsp_problem(n, problem_type, seed=None):
    """Generate ATSP test instance."""
    if seed is not None:
        np.random.seed(seed)

    if problem_type == 'random':
        distances = np.random.rand(n, n) * 100
        np.fill_diagonal(distances, 0)

        # Make asymmetric
        for i in range(n):
            for j in range(i + 1, n):
                if np.random.random() < 0.4:
                    distances[i, j] *= np.random.uniform(1.5, 3.0)

    elif problem_type == 'flow_shop':
        distances = np.zeros((n, n))
        processing_times = np.random.randint(1, 20, size=(n, 2))

        for i in range(n):
            for j in range(n):
                if i != j:
                    setup = np.abs(processing_times[i] - processing_times[j]).sum()
                    setup += np.random.randint(1, 10)
                    distances[i, j] = setup

    elif problem_type == 'one_way':
        coords = np.random.rand(n, 2) * 100
        distances = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = np.linalg.norm(coords[i] - coords[j])
                    distances[i, j] = dist
                    distances[j, i] = dist

        # Add one-way streets
        for i in range(n):
            for j in range(i + 1, n):
                if np.random.random() < 0.3:
                    if np.random.random() < 0.5:
                        distances[i, j] *= 10
                    else:
                        distances[j, i] *= 10

    elif problem_type == 'structured':
        # Grid-like structure with asymmetry
        coords = []
        grid_size = int(np.ceil(np.sqrt(n)))
        for i in range(n):
            x = (i % grid_size) * 10
            y = (i // grid_size) * 10
            coords.append([x, y])

        coords = np.array(coords)
        distances = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    distances[i, j] = np.linalg.norm(coords[i] - coords[j])

        # Add directional bias
        for i in range(n):
            for j in range(n):
                if i < j:
                    distances[i, j] *= 0.8  # Prefer forward direction
                elif i > j:
                    distances[i, j] *= 1.3  # Penalize backward

    return distances


def benchmark_problem(distances, problem_name, size, problem_type):
    """Benchmark a single problem."""
    print(f"\n{'='*80}")
    print(f"  PROBLEM: {problem_name} (n={size}, type={problem_type})")
    print(f"{'='*80}")

    # Lower bound
    lb = compute_assignment_lower_bound(distances)
    print(f"  📊 Assignment Lower Bound: {lb:.2f}\n")

    results = {
        'problem_name': problem_name,
        'size': size,
        'type': problem_type,
        'lower_bound': float(lb),
        'solvers': {}
    }

    # Adjusted time limits (60-120s for fair comparison)
    if size <= 30:
        time_limit = 60.0
    elif size <= 50:
        time_limit = 90.0
    elif size <= 75:
        time_limit = 120.0
    else:
        time_limit = 180.0

    # Test Original PIMST-Quantum (baseline)
    print(f"  Testing Original PIMST-Quantum (time: {time_limit}s)...")
    try:
        start = time.time()
        tour_orig, cost_orig, meta_orig = solve_original(
            distances,
            method='quantum',
            quality='balanced'
        )
        elapsed_orig = time.time() - start

        gap_orig = ((cost_orig - lb) / lb * 100) if lb > 0 else float('inf')

        results['solvers']['Original-PIMST-Quantum'] = {
            'cost': float(cost_orig),
            'time': elapsed_orig,
            'gap': float(gap_orig)
        }

        print(f"    ✓ Cost: {cost_orig:.2f}, Gap: {gap_orig:.2f}%, Time: {elapsed_orig:.3f}s")

    except Exception as e:
        print(f"    ✗ Failed: {e}")
        results['solvers']['Original-PIMST-Quantum'] = {'error': str(e)}

    # Test Improved Single Run
    print(f"  Testing Improved PIMST (Single, time: {time_limit}s)...")
    try:
        tour_imp, cost_imp, meta_imp = solve_atsp_improved(
            distances,
            time_limit=time_limit,
            use_advanced_construction=True,
            use_3opt=True,
            verbose=False
        )

        gap_imp = ((cost_imp - lb) / lb * 100) if lb > 0 else float('inf')

        results['solvers']['Improved-PIMST-Single'] = {
            'cost': float(cost_imp),
            'time': meta_imp['time'],
            'gap': float(gap_imp),
            'construction_method': meta_imp['construction_method']
        }

        print(f"    ✓ Cost: {cost_imp:.2f}, Gap: {gap_imp:.2f}%, Time: {meta_imp['time']:.3f}s")

    except Exception as e:
        print(f"    ✗ Failed: {e}")
        results['solvers']['Improved-PIMST-Single'] = {'error': str(e)}

    # Test Improved Multi-Start (3 runs)
    multi_start_time = time_limit * 2  # Double time for 3 runs
    print(f"  Testing Improved PIMST (Multi-Start, time: {multi_start_time}s)...")
    try:
        tour_ms, cost_ms, meta_ms = solve_atsp_multi_start_improved(
            distances,
            n_starts=3,
            time_limit=multi_start_time,
            verbose=False
        )

        gap_ms = ((cost_ms - lb) / lb * 100) if lb > 0 else float('inf')

        results['solvers']['Improved-PIMST-MultiStart'] = {
            'cost': float(cost_ms),
            'time': meta_ms['time'],
            'gap': float(gap_ms),
            'avg_cost': float(meta_ms['avg_cost']),
            'std_cost': float(meta_ms['std_cost'])
        }

        print(f"    ✓ Cost: {cost_ms:.2f}, Gap: {gap_ms:.2f}%, Time: {meta_ms['time']:.3f}s")

    except Exception as e:
        print(f"    ✗ Failed: {e}")
        results['solvers']['Improved-PIMST-MultiStart'] = {'error': str(e)}

    # Summary
    successful = {k: v for k, v in results['solvers'].items() if 'error' not in v}
    if successful:
        best = min(successful.items(), key=lambda x: x[1]['cost'])
        print(f"\n  🏆 Best quality: {best[0]} (cost: {best[1]['cost']:.2f}, gap: {best[1]['gap']:.2f}%)")

    return results


def run_phase1_benchmark():
    """Run Phase 1 improvement benchmark."""
    print("\n" + "="*80)
    print("  ATSP PHASE 1 IMPROVEMENT BENCHMARK")
    print("  Comparing: Original vs Improved (3-opt + better construction)")
    print("="*80)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    all_results = []

    # Test cases (smaller set for faster testing)
    test_cases = [
        (30, 'random', 1),
        (50, 'random', 2),
        (75, 'random', 3),
        (30, 'flow_shop', 4),
        (50, 'one_way', 5),
    ]

    for idx, (size, ptype, seed) in enumerate(test_cases, 1):
        print(f"\n\n{'='*80}")
        print(f"  TEST {idx}/{len(test_cases)}")
        print(f"{'='*80}")

        distances = generate_atsp_problem(size, ptype, seed=42 + seed)
        problem_name = f"{ptype}_{size}_{idx}"

        result = benchmark_problem(distances, problem_name, size, ptype)
        all_results.append(result)

    # Final summary
    print("\n\n" + "="*80)
    print("  FINAL SUMMARY")
    print("="*80)

    solver_stats = {}
    for result in all_results:
        for solver, data in result['solvers'].items():
            if 'error' not in data:
                if solver not in solver_stats:
                    solver_stats[solver] = {'gaps': [], 'times': [], 'costs': []}

                solver_stats[solver]['gaps'].append(data['gap'])
                solver_stats[solver]['times'].append(data['time'])
                solver_stats[solver]['costs'].append(data['cost'])

    print("\n  Performance by Solver:")
    print("  " + "-"*76)
    print(f"  {'Solver':<35s} {'Avg Gap':>12s} {'Avg Time':>12s} {'Problems':>8s}")
    print("  " + "-"*76)

    for solver, stats in solver_stats.items():
        avg_gap = np.mean(stats['gaps'])
        avg_time = np.mean(stats['times'])
        n_problems = len(stats['gaps'])

        print(f"  {solver:<35s} {avg_gap:>11.2f}% {avg_time:>11.2f}s {n_problems:>8d}")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"atsp_phase1_benchmark_{timestamp}.json"

    output = {
        'benchmark': 'ATSP-Phase1-Improvements',
        'timestamp': timestamp,
        'test_cases': len(test_cases),
        'results': all_results,
        'summary': {
            solver: {
                'avg_gap': float(np.mean(stats['gaps'])),
                'avg_time': float(np.mean(stats['times'])),
                'min_gap': float(np.min(stats['gaps'])),
                'max_gap': float(np.max(stats['gaps']))
            }
            for solver, stats in solver_stats.items()
        }
    }

    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n  💾 Results saved to: {filename}")
    print("="*80)


if __name__ == '__main__':
    run_phase1_benchmark()
