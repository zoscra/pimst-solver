"""
ATSP Solver - Unified API for Asymmetric TSP
=============================================

Provides a simple, unified interface to all ATSP solvers:
- Basic algorithms (Nearest Neighbor, Farthest Insertion, Lin-Kernighan)
- Advanced solvers (Complementary Quantum, Super Solver, Thompson Sampling)
- Smart selection based on problem size and quality requirements

Usage:
    from atsp_solver import solve_atsp

    # Simple usage
    distances = np.array([...])  # Asymmetric distance matrix
    tour, cost = solve_atsp(distances)

    # Advanced usage
    tour, cost, metadata = solve_atsp(
        distances,
        method='auto',  # or 'quantum', 'super', 'thompson', 'basic'
        quality='balanced',  # or 'fast', 'optimal'
        time_budget=10.0,
        verbose=True
    )
"""

import numpy as np
from typing import Tuple, Dict, Optional, Literal
import time

# Import all ATSP solvers
from src.pimst.atsp_algorithms import (
    nearest_neighbor_atsp,
    farthest_insertion_atsp,
    lin_kernighan_atsp,
    multi_start_atsp,
    calculate_atsp_tour_length,
    solve_atsp_smart
)
from src.pimst.atsp_complementary_quantum import (
    ComplementaryQuantumATSP,
    solve_atsp_complementary_quantum
)
from src.pimst.atsp_super_solver import (
    SuperSolverATSP,
    solve_atsp_super
)
from src.pimst.atsp_thompson_selector import (
    ThompsonSamplingATSP,
    solve_atsp_thompson
)


def solve_atsp(
    distances: np.ndarray,
    method: Literal['auto', 'basic', 'quantum', 'super', 'thompson'] = 'auto',
    quality: Literal['fast', 'balanced', 'optimal'] = 'balanced',
    time_budget: float = 10.0,
    verbose: bool = True,
    return_metadata: bool = False
) -> Tuple:
    """
    Solve an Asymmetric Traveling Salesman Problem.

    Args:
        distances: Asymmetric distance matrix (n x n)
                  distances[i][j] = cost to go from city i to city j
                  Note: distances[i][j] may != distances[j][i]

        method: Solver method to use:
            - 'auto': Automatically select best method based on problem size
            - 'basic': Use basic algorithms (fast, good for small problems)
            - 'quantum': Complementary Quantum Solver (3 orthogonal searches)
            - 'super': Super Solver (intelligent ensemble with quality checks)
            - 'thompson': Thompson Sampling (learns best algorithm adaptively)

        quality: Quality vs speed trade-off:
            - 'fast': Prioritize speed (good for n < 100)
            - 'balanced': Balance quality and speed (recommended)
            - 'optimal': Prioritize quality (good for n < 200)

        time_budget: Maximum time in seconds (soft limit)

        verbose: Print progress and results

        return_metadata: If True, return (tour, cost, metadata)
                        If False, return (tour, cost)

    Returns:
        If return_metadata=False:
            (tour, cost)
        If return_metadata=True:
            (tour, cost, metadata)

        where:
            tour: Array of city indices in visit order
            cost: Total tour cost
            metadata: Dict with solver information

    Example:
        >>> import numpy as np
        >>> from atsp_solver import solve_atsp
        >>>
        >>> # Create asymmetric distance matrix
        >>> n = 50
        >>> distances = np.random.rand(n, n) * 100
        >>> np.fill_diagonal(distances, 0)
        >>>
        >>> # Solve
        >>> tour, cost = solve_atsp(distances, method='auto', quality='balanced')
        >>> print(f"Tour cost: {cost:.2f}")
    """
    start_time = time.time()
    n = len(distances)

    # Validate input
    if distances.shape[0] != distances.shape[1]:
        raise ValueError("Distance matrix must be square")

    if n < 3:
        raise ValueError("Problem must have at least 3 cities")

    # Print header
    if verbose:
        print("\n" + "="*70)
        print("  ATSP SOLVER - Asymmetric Traveling Salesman Problem")
        print("="*70)
        print(f"  Problem size: n={n}")
        print(f"  Method: {method}")
        print(f"  Quality: {quality}")
        print(f"  Time budget: {time_budget:.1f}s")
        print("="*70 + "\n")

    # AUTO SELECTION
    if method == 'auto':
        # Smart selection based on problem size and quality
        if n < 50:
            if quality == 'fast':
                method = 'basic'
            else:
                method = 'thompson'
        elif n < 100:
            if quality == 'fast':
                method = 'thompson'
            else:
                method = 'super'
        elif n < 200:
            method = 'super'
        else:
            # Very large problems: quantum gives good diversity
            method = 'quantum'

        if verbose:
            print(f"  🎯 Auto-selected method: {method.upper()}\n")

    # SOLVE
    if method == 'basic':
        tour, cost = solve_atsp_smart(distances, quality)
        metadata = {
            'method': 'basic',
            'quality': quality,
            'time': time.time() - start_time
        }

    elif method == 'quantum':
        n_runs = 3 if quality == 'fast' else (5 if quality == 'optimal' else 3)
        tour, cost, meta = solve_atsp_complementary_quantum(
            distances,
            time_budget=time_budget,
            n_runs=n_runs,
            verbose=verbose
        )
        metadata = {
            'method': 'quantum',
            'quality': quality,
            **meta
        }

    elif method == 'super':
        mode_map = {'fast': 'fast', 'balanced': 'balanced', 'optimal': 'optimal'}
        tour, cost, meta = solve_atsp_super(
            distances,
            time_budget=time_budget,
            mode=mode_map[quality],
            verbose=verbose
        )
        metadata = {
            'method': 'super',
            'quality': quality,
            **meta
        }

    elif method == 'thompson':
        tour, cost, meta = solve_atsp_thompson(
            distances,
            time_budget=time_budget,
            verbose=verbose
        )
        metadata = {
            'method': 'thompson',
            'quality': quality,
            **meta
        }

    else:
        raise ValueError(f"Unknown method: {method}")

    # Print summary
    total_time = time.time() - start_time
    if verbose:
        print("\n" + "="*70)
        print("  RESULTADO FINAL")
        print("="*70)
        print(f"  💎 Costo del tour: {cost:.2f}")
        print(f"  🏃 Ciudades visitadas: {n}")
        print(f"  ⏱️  Tiempo total: {total_time:.3f}s")
        print(f"  🎯 Método usado: {method.upper()}")
        print("="*70 + "\n")

    # Return
    if return_metadata:
        return tour, cost, metadata
    else:
        return tour, cost


def validate_atsp_solution(tour: np.ndarray, distances: np.ndarray) -> Dict:
    """
    Validate an ATSP solution and compute statistics.

    Args:
        tour: Tour as array of city indices
        distances: Distance matrix

    Returns:
        Dict with validation results:
            - valid: True if tour is valid
            - cost: Total tour cost
            - errors: List of validation errors
            - n_cities: Number of cities
    """
    n = len(distances)
    errors = []

    # Check 1: All cities visited exactly once
    if len(tour) != n:
        errors.append(f"Tour length {len(tour)} != n_cities {n}")

    if len(set(tour)) != n:
        errors.append("Some cities visited multiple times or not at all")

    # Check 2: All indices valid
    if np.any(tour < 0) or np.any(tour >= n):
        errors.append("Tour contains invalid city indices")

    # Check 3: Compute cost
    cost = calculate_atsp_tour_length(tour, distances)

    return {
        'valid': len(errors) == 0,
        'cost': cost,
        'errors': errors,
        'n_cities': n
    }


def compare_atsp_methods(
    distances: np.ndarray,
    methods: list = ['basic', 'quantum', 'super', 'thompson'],
    time_budget: float = 10.0
) -> Dict:
    """
    Compare different ATSP solving methods on the same problem.

    Args:
        distances: Asymmetric distance matrix
        methods: List of methods to compare
        time_budget: Time budget per method

    Returns:
        Dict with comparison results
    """
    n = len(distances)
    results = {}

    print("\n" + "="*70)
    print("  COMPARACIÓN DE MÉTODOS ATSP")
    print("="*70)
    print(f"  Problem size: n={n}")
    print(f"  Time budget per method: {time_budget:.1f}s")
    print("="*70 + "\n")

    for method in methods:
        print(f"\n{'='*70}")
        print(f"  Testing: {method.upper()}")
        print(f"{'='*70}")

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

            results[method] = {
                'success': True,
                'cost': cost,
                'time': elapsed,
                'metadata': metadata
            }

            print(f"  ✓ Cost: {cost:.2f}")
            print(f"  ✓ Time: {elapsed:.3f}s")

        except Exception as e:
            results[method] = {
                'success': False,
                'error': str(e)
            }
            print(f"  ✗ Error: {e}")

    # Summary
    print("\n" + "="*70)
    print("  RESUMEN")
    print("="*70)

    successful = {k: v for k, v in results.items() if v.get('success', False)}
    if successful:
        best_method = min(successful.items(), key=lambda x: x[1]['cost'])
        fastest_method = min(successful.items(), key=lambda x: x[1]['time'])

        print(f"  🏆 Mejor costo: {best_method[0].upper()} ({best_method[1]['cost']:.2f})")
        print(f"  ⚡ Más rápido: {fastest_method[0].upper()} ({fastest_method[1]['time']:.3f}s)")
        print()

        for method, result in sorted(successful.items(), key=lambda x: x[1]['cost']):
            cost_pct = ((result['cost'] / best_method[1]['cost']) - 1) * 100
            time_pct = ((result['time'] / fastest_method[1]['time']) - 1) * 100
            print(f"  {method:<15} Cost: {result['cost']:>10.2f} (+{cost_pct:>5.1f}%)  "
                  f"Time: {result['time']:>7.3f}s (+{time_pct:>5.1f}%)")

    print("="*70 + "\n")

    return results


# Main para testing rápido
if __name__ == "__main__":
    print("\n🧪 ATSP Solver - Quick Test\n")

    # Create random asymmetric problem
    np.random.seed(42)
    n = 50
    distances = np.random.rand(n, n) * 100
    np.fill_diagonal(distances, 0)

    # Make it asymmetric
    for i in range(n):
        for j in range(i+1, n):
            if np.random.random() < 0.3:
                # 30% of edges are significantly asymmetric
                factor = np.random.uniform(1.5, 3.0)
                if np.random.random() < 0.5:
                    distances[i, j] *= factor
                else:
                    distances[j, i] *= factor

    print(f"Created random asymmetric problem: n={n}")
    print(f"Asymmetry check: d[0,1]={distances[0,1]:.2f}, d[1,0]={distances[1,0]:.2f}\n")

    # Test single solve
    print("="*70)
    print("TEST 1: Single solve with auto method")
    print("="*70)
    tour, cost = solve_atsp(distances, method='auto', quality='balanced', verbose=True)

    # Validate
    validation = validate_atsp_solution(tour, distances)
    print(f"\nValidation: {'✓ VALID' if validation['valid'] else '✗ INVALID'}")
    if not validation['valid']:
        for error in validation['errors']:
            print(f"  ✗ {error}")

    # Test comparison
    print("\n" + "="*70)
    print("TEST 2: Compare all methods")
    print("="*70)
    compare_atsp_methods(distances, time_budget=5.0)

    print("\n✅ All tests completed!\n")
