"""
ATSP Complete Benchmark vs LKH and OR-Tools
============================================

Comprehensive comparison of ATSP solvers:
- Our ATSP solvers (Basic, Quantum, Super, Thompson)
- LKH-3 ATSP mode
- Google OR-Tools

Tests multiple problem types and sizes.
"""

import numpy as np
import time
import json
import subprocess
import tempfile
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path


def compute_assignment_lower_bound_fixed(distances: np.ndarray) -> float:
    """
    Compute tight lower bound for ATSP using Assignment Problem.

    Properly handles the constraint that d[i,i] should not be used.
    """
    n = len(distances)

    try:
        from scipy.optimize import linear_sum_assignment

        # Create modified matrix with very high diagonal to prevent self-assignment
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


def generate_atsp_problem(n: int, problem_type: str, seed: int = None) -> np.ndarray:
    """Generate ATSP problem of different types."""
    if seed is not None:
        np.random.seed(seed)

    if problem_type == 'random':
        # Random asymmetric
        distances = np.random.rand(n, n) * 100
        np.fill_diagonal(distances, 0)

        # Make 40% edges asymmetric
        for i in range(n):
            for j in range(i+1, n):
                if np.random.random() < 0.4:
                    distances[i, j] *= np.random.uniform(1.5, 3.0)

    elif problem_type == 'flow_shop':
        # Flow shop scheduling
        distances = np.zeros((n, n))
        processing_times = np.random.randint(1, 20, size=(n, 2))

        for i in range(n):
            for j in range(n):
                if i != j:
                    setup = np.abs(processing_times[i] - processing_times[j]).sum()
                    setup += np.random.randint(1, 10)
                    distances[i, j] = setup

    elif problem_type == 'one_way':
        # One-way streets
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
            for j in range(i+1, n):
                if np.random.random() < 0.3:
                    if np.random.random() < 0.5:
                        distances[i, j] *= 10
                    else:
                        distances[j, i] *= 10

    elif problem_type == 'structured':
        # Structured with patterns
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Create asymmetric pattern
                    if i < j:
                        distances[i, j] = abs(j - i) * 10 + np.random.rand() * 5
                    else:
                        distances[i, j] = abs(j - i) * 15 + np.random.rand() * 5

    return distances


def write_atsp_file(distances: np.ndarray, filename: str):
    """Write ATSP in TSPLIB format for LKH."""
    n = len(distances)

    with open(filename, 'w') as f:
        f.write(f"NAME: atsp_problem\n")
        f.write(f"TYPE: ATSP\n")
        f.write(f"DIMENSION: {n}\n")
        f.write(f"EDGE_WEIGHT_TYPE: EXPLICIT\n")
        f.write(f"EDGE_WEIGHT_FORMAT: FULL_MATRIX\n")
        f.write(f"EDGE_WEIGHT_SECTION\n")

        for i in range(n):
            row = ' '.join([f"{int(distances[i, j]*10000)}" if i != j else "999999"
                           for j in range(n)])
            f.write(f"{row}\n")

        f.write("EOF\n")


def solve_with_lkh_atsp(distances: np.ndarray, time_limit: float = 10.0) -> Tuple[Optional[List[int]], Optional[float], Dict]:
    """
    Solve ATSP using LKH-3.

    Returns:
        (tour, cost, metadata)
    """
    n = len(distances)

    # Check if LKH is available
    lkh_paths = ['LKH', 'lkh', './LKH', './lkh', 'LKH-3', 'lkh-3']
    lkh_exe = None

    for path in lkh_paths:
        try:
            result = subprocess.run([path, '--version'], capture_output=True, timeout=1)
            lkh_exe = path
            break
        except:
            continue

    if lkh_exe is None:
        return None, None, {'error': 'LKH not found', 'available': False}

    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        problem_file = os.path.join(tmpdir, 'problem.atsp')
        param_file = os.path.join(tmpdir, 'params.par')
        tour_file = os.path.join(tmpdir, 'tour.txt')

        # Write problem
        write_atsp_file(distances, problem_file)

        # Write parameters
        with open(param_file, 'w') as f:
            f.write(f"PROBLEM_FILE = {problem_file}\n")
            f.write(f"OUTPUT_TOUR_FILE = {tour_file}\n")
            f.write(f"RUNS = 1\n")
            f.write(f"TIME_LIMIT = {time_limit}\n")

        # Run LKH
        start = time.time()
        try:
            result = subprocess.run(
                [lkh_exe, param_file],
                capture_output=True,
                timeout=time_limit + 5,
                text=True
            )
            elapsed = time.time() - start

            # Parse tour
            if os.path.exists(tour_file):
                with open(tour_file, 'r') as f:
                    lines = f.readlines()

                tour = []
                reading = False
                for line in lines:
                    if 'TOUR_SECTION' in line:
                        reading = True
                        continue
                    if reading and line.strip() not in ['-1', 'EOF', '']:
                        try:
                            tour.append(int(line.strip()) - 1)  # Convert to 0-indexed
                        except:
                            pass

                if tour and tour[-1] == -2:
                    tour = tour[:-1]

                # Calculate cost
                from src.pimst.atsp_algorithms import calculate_atsp_tour_length
                tour_array = np.array(tour, dtype=np.int32)
                cost = calculate_atsp_tour_length(tour_array, distances)

                return tour, cost, {
                    'time': elapsed,
                    'available': True,
                    'output': result.stdout
                }
            else:
                return None, None, {
                    'error': 'No tour file produced',
                    'available': True,
                    'output': result.stdout
                }

        except subprocess.TimeoutExpired:
            return None, None, {'error': 'Timeout', 'available': True}
        except Exception as e:
            return None, None, {'error': str(e), 'available': True}


def solve_with_ortools(distances: np.ndarray, time_limit: float = 10.0) -> Tuple[Optional[List[int]], Optional[float], Dict]:
    """
    Solve ATSP using Google OR-Tools.

    Returns:
        (tour, cost, metadata)
    """
    try:
        from ortools.constraint_solver import routing_enums_pb2
        from ortools.constraint_solver import pywrapcp
    except ImportError:
        return None, None, {'error': 'OR-Tools not installed', 'available': False}

    n = len(distances)

    # Create routing model
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distances[from_node, to_node] * 10000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = int(time_limit)

    # Solve
    start = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    elapsed = time.time() - start

    if solution:
        # Extract tour
        tour = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            tour.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))

        # Calculate cost
        from src.pimst.atsp_algorithms import calculate_atsp_tour_length
        tour_array = np.array(tour, dtype=np.int32)
        cost = calculate_atsp_tour_length(tour_array, distances)

        return tour, cost, {
            'time': elapsed,
            'available': True,
            'objective': solution.ObjectiveValue() / 10000
        }
    else:
        return None, None, {
            'error': 'No solution found',
            'available': True,
            'time': elapsed
        }


def solve_with_our_method(distances: np.ndarray, method: str, time_budget: float = 10.0) -> Tuple[List[int], float, Dict]:
    """Solve with our ATSP solver."""
    from atsp_solver import solve_atsp

    start = time.time()
    tour, cost, metadata = solve_atsp(
        distances,
        method=method,
        quality='balanced',
        time_budget=time_budget,
        verbose=False,
        return_metadata=True
    )
    elapsed = time.time() - start

    metadata['time'] = elapsed
    metadata['available'] = True

    return tour.tolist() if hasattr(tour, 'tolist') else tour, cost, metadata


def benchmark_single_problem(
    distances: np.ndarray,
    problem_name: str,
    size: int,
    problem_type: str,
    time_limit: float = 30.0
) -> Dict:
    """Benchmark a single problem with all solvers."""

    print(f"\n{'='*80}")
    print(f"  PROBLEM: {problem_name} (n={size}, type={problem_type})")
    print(f"{'='*80}")

    # Compute lower bound
    lb = compute_assignment_lower_bound_fixed(distances)
    print(f"  📊 Assignment Lower Bound: {lb:.2f}\n")

    results = {
        'problem_name': problem_name,
        'size': size,
        'problem_type': problem_type,
        'lower_bound': float(lb),
        'solvers': {}
    }

    # Test each solver
    solvers = [
        ('PIMST-Basic', lambda: solve_with_our_method(distances, 'basic', time_limit)),
        ('PIMST-Super', lambda: solve_with_our_method(distances, 'super', time_limit)),
        ('PIMST-Quantum', lambda: solve_with_our_method(distances, 'quantum', time_limit)),
        ('OR-Tools', lambda: solve_with_ortools(distances, time_limit)),
        ('LKH-3', lambda: solve_with_lkh_atsp(distances, time_limit)),
    ]

    for solver_name, solve_func in solvers:
        print(f"  Testing {solver_name}...")

        try:
            tour, cost, metadata = solve_func()

            if tour is not None and cost is not None:
                gap = ((cost - lb) / lb * 100) if lb > 0 else float('inf')

                results['solvers'][solver_name] = {
                    'success': True,
                    'cost': float(cost),
                    'time': metadata.get('time', 0),
                    'gap': float(gap),
                    'metadata': metadata
                }

                print(f"    ✓ Cost: {cost:.2f}, Gap: {gap:.2f}%, Time: {metadata.get('time', 0):.3f}s")
            else:
                results['solvers'][solver_name] = {
                    'success': False,
                    'error': metadata.get('error', 'Unknown error'),
                    'available': metadata.get('available', False)
                }
                print(f"    ✗ Failed: {metadata.get('error', 'Unknown')}")

        except Exception as e:
            results['solvers'][solver_name] = {
                'success': False,
                'error': str(e),
                'available': False
            }
            print(f"    ✗ Error: {e}")

    # Summary
    successful = {k: v for k, v in results['solvers'].items() if v.get('success', False)}
    if successful:
        best = min(successful.items(), key=lambda x: x[1]['cost'])
        fastest = min(successful.items(), key=lambda x: x[1]['time'])

        print(f"\n  🏆 Best quality: {best[0]} (cost: {best[1]['cost']:.2f}, gap: {best[1]['gap']:.2f}%)")
        print(f"  ⚡ Fastest: {fastest[0]} (time: {fastest[1]['time']:.3f}s)")

    return results


def run_comprehensive_benchmark():
    """Run complete benchmark suite."""

    print("\n" + "="*80)
    print("  COMPREHENSIVE ATSP BENCHMARK")
    print("  Comparing: PIMST vs LKH-3 vs OR-Tools")
    print("="*80)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    all_results = []

    # Test configuration
    test_cases = [
        # (size, problem_type, time_limit)
        (20, 'random', 10),
        (30, 'random', 15),
        (50, 'random', 30),
        (75, 'random', 45),
        (100, 'random', 60),

        (30, 'flow_shop', 15),
        (50, 'flow_shop', 30),
        (75, 'flow_shop', 45),

        (30, 'one_way', 15),
        (50, 'one_way', 30),
        (75, 'one_way', 45),

        (30, 'structured', 15),
        (50, 'structured', 30),
    ]

    for idx, (size, ptype, tlimit) in enumerate(test_cases, 1):
        print(f"\n\n{'='*80}")
        print(f"  TEST {idx}/{len(test_cases)}")
        print(f"{'='*80}")

        # Generate problem
        distances = generate_atsp_problem(size, ptype, seed=42 + idx)
        problem_name = f"{ptype}_{size}_{idx}"

        # Benchmark
        result = benchmark_single_problem(distances, problem_name, size, ptype, tlimit)
        all_results.append(result)

    # Aggregate results
    print("\n\n" + "="*80)
    print("  FINAL SUMMARY")
    print("="*80)

    # Group by solver
    solver_stats = {}
    for result in all_results:
        for solver, data in result['solvers'].items():
            if data.get('success', False):
                if solver not in solver_stats:
                    solver_stats[solver] = {
                        'gaps': [],
                        'times': [],
                        'costs': [],
                        'wins': 0
                    }
                solver_stats[solver]['gaps'].append(data['gap'])
                solver_stats[solver]['times'].append(data['time'])
                solver_stats[solver]['costs'].append(data['cost'])

    # Count wins (best cost per problem)
    for result in all_results:
        successful = {k: v for k, v in result['solvers'].items() if v.get('success', False)}
        if successful:
            best_solver = min(successful.items(), key=lambda x: x[1]['cost'])[0]
            if best_solver in solver_stats:
                solver_stats[best_solver]['wins'] += 1

    # Print summary table
    print("\n  Performance by Solver:")
    print("  " + "-"*80)
    print(f"  {'Solver':<20} {'Avg Gap':<12} {'Avg Time':<12} {'Wins':<8} {'Problems':<10}")
    print("  " + "-"*80)

    for solver in sorted(solver_stats.keys()):
        stats = solver_stats[solver]
        avg_gap = np.mean(stats['gaps'])
        avg_time = np.mean(stats['times'])
        wins = stats['wins']
        n_problems = len(stats['gaps'])

        print(f"  {solver:<20} {avg_gap:>10.2f}% {avg_time:>10.3f}s {wins:>6} {n_problems:>8}")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'atsp_complete_benchmark_{timestamp}.json'

    output = {
        'timestamp': timestamp,
        'test_cases': len(test_cases),
        'summary': {
            solver: {
                'avg_gap': float(np.mean(stats['gaps'])),
                'avg_time': float(np.mean(stats['times'])),
                'wins': stats['wins'],
                'problems_solved': len(stats['gaps'])
            }
            for solver, stats in solver_stats.items()
        },
        'detailed_results': all_results
    }

    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n  💾 Results saved to: {filename}")
    print("="*80 + "\n")

    # Generate markdown report
    md_filename = f'atsp_benchmark_report_{timestamp}.md'
    generate_markdown_report(output, md_filename)
    print(f"  📄 Report saved to: {md_filename}\n")

    return output


def generate_markdown_report(results: Dict, filename: str):
    """Generate markdown report from results."""

    with open(filename, 'w') as f:
        f.write("# ATSP Benchmark Report\n\n")
        f.write(f"**Generated:** {results['timestamp']}\n\n")
        f.write(f"**Test Cases:** {results['test_cases']}\n\n")

        f.write("## Summary\n\n")
        f.write("| Solver | Avg Gap | Avg Time | Wins | Problems Solved |\n")
        f.write("|--------|---------|----------|------|----------------|\n")

        for solver, stats in sorted(results['summary'].items(), key=lambda x: x[1]['avg_gap']):
            f.write(f"| {solver} | {stats['avg_gap']:.2f}% | {stats['avg_time']:.3f}s | "
                   f"{stats['wins']} | {stats['problems_solved']} |\n")

        f.write("\n## Detailed Results\n\n")

        for result in results['detailed_results']:
            f.write(f"### {result['problem_name']}\n\n")
            f.write(f"- **Size:** n={result['size']}\n")
            f.write(f"- **Type:** {result['problem_type']}\n")
            f.write(f"- **Lower Bound:** {result['lower_bound']:.2f}\n\n")

            f.write("| Solver | Cost | Gap | Time |\n")
            f.write("|--------|------|-----|------|\n")

            for solver, data in result['solvers'].items():
                if data.get('success', False):
                    f.write(f"| {solver} | {data['cost']:.2f} | {data['gap']:.2f}% | {data['time']:.3f}s |\n")
                else:
                    f.write(f"| {solver} | Failed | - | - |\n")

            f.write("\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        print("\n🚀 Quick comparison test\n")

        # Single problem
        distances = generate_atsp_problem(30, 'random', seed=42)
        result = benchmark_single_problem(distances, 'test_30_random', 30, 'random', 20)

        print("\n✅ Quick test completed!")
    else:
        # Full benchmark
        run_comprehensive_benchmark()
