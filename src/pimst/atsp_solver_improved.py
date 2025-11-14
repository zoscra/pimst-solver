"""
Improved ATSP Solver - Phase 1 Enhancements
============================================

Integrates advanced operators and constructions for better ATSP solutions.

Target: Reduce gap from 20% to 12-15% (Phase 1 of state-of-the-art roadmap).

Key improvements:
1. Better construction heuristics (Farthest Insertion, etc.)
2. Powerful 3-opt operator
3. Longer search times (60-120s vs 10-40s)
4. Sequential application of multiple operators

Author: PIMST Project
Date: 2025-11-14
"""

import numpy as np
import time
from typing import Tuple, Dict, Optional

# Import our new advanced modules
try:
    from .atsp_construction_heuristics import (
        farthest_insertion_atsp,
        cheapest_insertion_atsp,
        get_best_construction
    )
    from .atsp_local_search_advanced import (
        three_opt_atsp,
        three_opt_first_improvement,
        optimize_tour_advanced,
        calculate_tour_cost_numba
    )
    from .atsp_local_search import (
        variable_neighborhood_descent_atsp,
        or_opt_atsp,
        node_insertion_atsp
    )
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from atsp_construction_heuristics import (
        farthest_insertion_atsp,
        cheapest_insertion_atsp,
        get_best_construction
    )
    from atsp_local_search_advanced import (
        three_opt_atsp,
        three_opt_first_improvement,
        optimize_tour_advanced,
        calculate_tour_cost_numba
    )
    from atsp_local_search import (
        variable_neighborhood_descent_atsp,
        or_opt_atsp,
        node_insertion_atsp
    )


def solve_atsp_improved(
    dist_matrix: np.ndarray,
    time_limit: float = 60.0,
    use_advanced_construction: bool = True,
    use_3opt: bool = True,
    verbose: bool = False
) -> Tuple[np.ndarray, float, Dict]:
    """
    Improved ATSP solver using Phase 1 enhancements.

    This is the main entry point for improved solving.

    Parameters
    ----------
    dist_matrix : ndarray
        Asymmetric distance matrix (n x n)
    time_limit : float
        Total time budget in seconds (default: 60s)
    use_advanced_construction : bool
        If True, try multiple construction heuristics
    use_3opt : bool
        If True, use 3-opt operator (slower but better)
    verbose : bool
        If True, print progress information

    Returns
    -------
    tour : ndarray
        Best tour found
    cost : float
        Tour cost
    metadata : dict
        Solver statistics
    """
    start_time = time.time()
    n = len(dist_matrix)

    if verbose:
        print(f"Improved ATSP Solver - n={n}, time_limit={time_limit}s")
        print(f"Advanced construction: {use_advanced_construction}")
        print(f"Using 3-opt: {use_3opt}")

    # Phase 1: Construction
    construction_time = min(time_limit * 0.1, 5.0)  # Max 5s for construction
    construction_start = time.time()

    if use_advanced_construction:
        if verbose:
            print("\nPhase 1: Advanced construction...")

        best_tour, best_cost, method = get_best_construction(
            dist_matrix,
            methods=['farthest_insertion', 'cheapest_insertion', 'nearest_addition'],
            time_limit=construction_time
        )

        if verbose:
            print(f"  Best method: {method}")
            print(f"  Initial cost: {best_cost:.2f}")
    else:
        # Fallback to simple farthest insertion
        best_tour, best_cost = farthest_insertion_atsp(dist_matrix)

        if verbose:
            print(f"\nPhase 1: Farthest insertion")
            print(f"  Initial cost: {best_cost:.2f}")

    construction_elapsed = time.time() - construction_start

    # Phase 2: Local search improvement
    improvement_time = time_limit - construction_elapsed - 1.0  # Reserve 1s buffer
    improvement_start = time.time()

    if verbose:
        print(f"\nPhase 2: Local search (time budget: {improvement_time:.1f}s)...")

    if use_3opt and improvement_time > 0:
        # Use advanced operators
        improved_tour, ls_metadata = optimize_tour_advanced(
            best_tour,
            dist_matrix,
            time_limit=improvement_time
        )

        if verbose:
            print(f"  Improvement: {ls_metadata['total_improvement']:.2f} ({ls_metadata['improvement_percent']:.2f}%)")
            print(f"  Final cost: {ls_metadata['final_cost']:.2f}")
            print(f"  Time: {ls_metadata['time']:.2f}s")

        best_tour = improved_tour
        best_cost = ls_metadata['final_cost']

    elif improvement_time > 0:
        # Fallback: use VND from existing module
        if verbose:
            print("  Using Variable Neighborhood Descent...")

        improved_tour, improvement = variable_neighborhood_descent_atsp(
            best_tour,
            dist_matrix,
            max_time=improvement_time
        )

        improved_cost = calculate_tour_cost_numba(improved_tour, dist_matrix)

        if verbose:
            print(f"  Improvement: {improvement:.2f}")
            print(f"  Final cost: {improved_cost:.2f}")

        best_tour = improved_tour
        best_cost = improved_cost

    total_time = time.time() - start_time

    metadata = {
        'algorithm': 'ATSP-Improved-Phase1',
        'n': n,
        'time': total_time,
        'construction_time': construction_elapsed,
        'improvement_time': time.time() - improvement_start,
        'construction_method': method if use_advanced_construction else 'farthest_insertion',
        'used_3opt': use_3opt,
        'final_cost': best_cost
    }

    if verbose:
        print(f"\n{'='*60}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Final cost: {best_cost:.2f}")
        print(f"{'='*60}")

    return best_tour, best_cost, metadata


def solve_atsp_multi_start_improved(
    dist_matrix: np.ndarray,
    n_starts: int = 5,
    time_limit: float = 120.0,
    verbose: bool = False
) -> Tuple[np.ndarray, float, Dict]:
    """
    Multi-start version of improved ATSP solver.

    Runs multiple constructions + local search and returns best result.

    Parameters
    ----------
    dist_matrix : ndarray
        Asymmetric distance matrix
    n_starts : int
        Number of independent runs
    time_limit : float
        Total time budget for all runs
    verbose : bool
        Print progress

    Returns
    -------
    tour : ndarray
        Best tour found
    cost : float
        Tour cost
    metadata : dict
        Solver statistics
    """
    start_time = time.time()
    time_per_start = time_limit / n_starts

    best_tour = None
    best_cost = np.inf
    all_costs = []

    if verbose:
        print(f"Multi-Start Improved ATSP Solver")
        print(f"  Runs: {n_starts}")
        print(f"  Time per run: {time_per_start:.1f}s")
        print(f"  Total budget: {time_limit}s")

    for run in range(n_starts):
        remaining_time = time_limit - (time.time() - start_time)
        if remaining_time <= 0:
            break

        run_time = min(time_per_start, remaining_time)

        if verbose:
            print(f"\n--- Run {run+1}/{n_starts} ---")

        # Randomize start city for diversity
        np.random.seed(run)

        tour, cost, meta = solve_atsp_improved(
            dist_matrix,
            time_limit=run_time,
            use_advanced_construction=True,
            use_3opt=True,
            verbose=verbose
        )

        all_costs.append(cost)

        if cost < best_cost:
            best_cost = cost
            best_tour = tour

            if verbose:
                print(f"  ★ New best: {best_cost:.2f}")

    total_time = time.time() - start_time

    metadata = {
        'algorithm': 'ATSP-MultiStart-Improved',
        'n_starts': n_starts,
        'n_completed': len(all_costs),
        'best_cost': best_cost,
        'worst_cost': max(all_costs) if all_costs else np.inf,
        'avg_cost': np.mean(all_costs) if all_costs else np.inf,
        'std_cost': np.std(all_costs) if all_costs else 0.0,
        'time': total_time
    }

    if verbose:
        print(f"\n{'='*60}")
        print(f"Multi-Start Results:")
        print(f"  Best: {best_cost:.2f}")
        print(f"  Avg:  {metadata['avg_cost']:.2f}")
        print(f"  Std:  {metadata['std_cost']:.2f}")
        print(f"  Time: {total_time:.2f}s")
        print(f"{'='*60}")

    return best_tour, best_cost, metadata


if __name__ == '__main__':
    # Test improved solver
    print("Testing Improved ATSP Solver (Phase 1)")
    print("=" * 60)

    # Generate test instance
    n = 50
    np.random.seed(42)

    dist_matrix = np.random.rand(n, n) * 100
    np.fill_diagonal(dist_matrix, 0)

    # Make asymmetric
    for i in range(n):
        for j in range(i + 1, n):
            if np.random.random() < 0.4:
                dist_matrix[i, j] *= np.random.uniform(1.5, 3.0)

    print(f"\nTest instance: n={n}")

    # Test single run
    print("\n" + "=" * 60)
    print("Single Run Test (60s)")
    print("=" * 60)

    tour, cost, metadata = solve_atsp_improved(
        dist_matrix,
        time_limit=60.0,
        use_advanced_construction=True,
        use_3opt=True,
        verbose=True
    )

    # Test multi-start
    print("\n" + "=" * 60)
    print("Multi-Start Test (120s, 3 runs)")
    print("=" * 60)

    tour_ms, cost_ms, metadata_ms = solve_atsp_multi_start_improved(
        dist_matrix,
        n_starts=3,
        time_limit=120.0,
        verbose=True
    )

    print("\n" + "=" * 60)
    print("Comparison:")
    print(f"  Single run:    {cost:.2f}")
    print(f"  Multi-start:   {cost_ms:.2f}")
    print(f"  Improvement:   {cost - cost_ms:.2f} ({(cost - cost_ms)/cost * 100:.2f}%)")
    print("=" * 60)
