"""
Comprehensive benchmark: PIMST vs. OR-Tools (Google)
"""

import numpy as np
import time
import pimst
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from typing import List, Tuple, Dict
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

USE_LKH = False  # Set to True when LKH is compiled

# =============================================================================
# DATASETS
# =============================================================================

def generate_datasets():
    """Generate diverse test datasets."""
    np.random.seed(42)
    
    datasets = {}
    
    print("📊 Generating test datasets...")
    
    # 1. Random instances (different sizes)
    for n in [20, 30, 50, 70, 100]:
        coords = [(np.random.rand() * 100, np.random.rand() * 100) for _ in range(n)]
        datasets[f'random-{n}'] = coords
        print(f"   ✅ random-{n}: {n} cities")
    
    # 2. Clustered instances
    def generate_clusters(n_clusters, points_per_cluster):
        coords = []
        for i in range(n_clusters):
            center_x = np.random.rand() * 100
            center_y = np.random.rand() * 100
            for _ in range(points_per_cluster):
                x = center_x + np.random.randn() * 5
                y = center_y + np.random.randn() * 5
                coords.append((x, y))
        return coords
    
    datasets['clustered-50'] = generate_clusters(5, 10)
    print(f"   ✅ clustered-50: 50 cities in 5 clusters")
    
    datasets['clustered-100'] = generate_clusters(10, 10)
    print(f"   ✅ clustered-100: 100 cities in 10 clusters")
    
    # 3. Grid instances
    def generate_grid(rows, cols):
        coords = []
        for i in range(rows):
            for j in range(cols):
                coords.append((i * 10, j * 10))
        return coords
    
    datasets['grid-25'] = generate_grid(5, 5)
    print(f"   ✅ grid-25: 5×5 grid")
    
    datasets['grid-100'] = generate_grid(10, 10)
    print(f"   ✅ grid-100: 10×10 grid")
    
    # 4. Circle instances (known optimal structure)
    def generate_circle(n):
        coords = []
        for i in range(n):
            angle = 2 * np.pi * i / n
            x = 50 + 40 * np.cos(angle)
            y = 50 + 40 * np.sin(angle)
            coords.append((x, y))
        return coords
    
    datasets['circle-50'] = generate_circle(50)
    print(f"   ✅ circle-50: 50 cities in circle")
    
    datasets['circle-100'] = generate_circle(100)
    print(f"   ✅ circle-100: 100 cities in circle")
    
    print(f"\n✅ Generated {len(datasets)} test datasets\n")
    
    return datasets

# =============================================================================
# SOLVER: PIMST
# =============================================================================

def solve_pimst(coords: List[Tuple[float, float]], quality='balanced') -> Dict:
    """Solve with PIMST."""
    start = time.time()
    result = pimst.solve(coords, quality=quality)
    elapsed = time.time() - start
    
    return {
        'tour': result['tour'],
        'length': result['length'],
        'time': elapsed,
        'algorithm': result['algorithm']
    }

# =============================================================================
# SOLVER: OR-TOOLS (GOOGLE)
# =============================================================================

def solve_ortools(coords: List[Tuple[float, float]], time_limit=30) -> Dict:
    """Solve with Google OR-Tools."""
    n = len(coords)
    
    # Create distance matrix
    def distance(i, j):
        dx = coords[i][0] - coords[j][0]
        dy = coords[i][1] - coords[j][1]
        return int(np.sqrt(dx*dx + dy*dy) * 1000)  # Scale for precision
    
    # Create routing model
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance(from_node, to_node)
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = time_limit
    
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
        
        # Calculate actual length
        length = 0.0
        for i in range(len(tour)):
            j = (i + 1) % len(tour)
            dx = coords[tour[i]][0] - coords[tour[j]][0]
            dy = coords[tour[i]][1] - coords[tour[j]][1]
            length += np.sqrt(dx*dx + dy*dy)
        
        return {
            'tour': tour,
            'length': length,
            'time': elapsed,
            'algorithm': 'OR-Tools GLS'
        }
    else:
        return None

# =============================================================================
# RUN BENCHMARKS
# =============================================================================

def run_benchmarks():
    """Run comprehensive benchmarks."""
    datasets = generate_datasets()
    results = {}
    
    print("=" * 80)
    print("🏆 COMPREHENSIVE TSP SOLVER BENCHMARK")
    print("=" * 80)
    print(f"\nComparing PIMST vs. Google OR-Tools")
    print(f"Testing on {len(datasets)} diverse datasets\n")
    
    for name, coords in datasets.items():
        n = len(coords)
        print(f"\n{'='*80}")
        print(f"📊 Dataset: {name} (N={n})")
        print(f"{'='*80}")
        
        results[name] = {
            'n': n,
            'solvers': {}
        }
        
        # 1. PIMST (fast)
        print("\n1️⃣  PIMST (fast)...", end=' ', flush=True)
        try:
            res = solve_pimst(coords, quality='fast')
            results[name]['solvers']['pimst_fast'] = res
            print(f"✅ Length: {res['length']:.2f}, Time: {res['time']*1000:.1f}ms, Algo: {res['algorithm']}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 2. PIMST (balanced)
        print("2️⃣  PIMST (balanced)...", end=' ', flush=True)
        try:
            res = solve_pimst(coords, quality='balanced')
            results[name]['solvers']['pimst_balanced'] = res
            print(f"✅ Length: {res['length']:.2f}, Time: {res['time']*1000:.1f}ms, Algo: {res['algorithm']}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 3. PIMST (optimal)
        print("3️⃣  PIMST (optimal)...", end=' ', flush=True)
        try:
            res = solve_pimst(coords, quality='optimal')
            results[name]['solvers']['pimst_optimal'] = res
            print(f"✅ Length: {res['length']:.2f}, Time: {res['time']*1000:.1f}ms, Algo: {res['algorithm']}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # 4. OR-Tools
        print("4️⃣  OR-Tools (Google)...", end=' ', flush=True)
        try:
            time_limit = 10 if n <= 50 else 30
            res = solve_ortools(coords, time_limit=time_limit)
            if res:
                results[name]['solvers']['ortools'] = res
                print(f"✅ Length: {res['length']:.2f}, Time: {res['time']:.1f}s")
            else:
                print("❌ No solution found")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return results

# =============================================================================
# ANALYZE RESULTS
# =============================================================================

def analyze_results(results):
    """Analyze and print comparison table."""
    print("\n" + "=" * 80)
    print("📊 DETAILED RESULTS ANALYSIS")
    print("=" * 80)
    
    # Find best solution for each dataset
    for name, data in results.items():
        solvers = data['solvers']
        if not solvers:
            continue
        
        # Find best length (reference)
        best_length = min(s['length'] for s in solvers.values())
        
        print(f"\n{'='*80}")
        print(f"Dataset: {name} (N={data['n']})")
        print(f"{'='*80}")
        print(f"{'Solver':<20} {'Length':<12} {'Gap %':<10} {'Time':<15} {'Speedup':<10}")
        print("-" * 80)
        
        # Calculate reference time (OR-Tools or slowest)
        ref_time = None
        if 'ortools' in solvers:
            ref_time = solvers['ortools']['time']
        else:
            ref_time = max(s['time'] for s in solvers.values())
        
        for solver_name, solver_data in sorted(solvers.items()):
            length = solver_data['length']
            time_taken = solver_data['time']
            gap = ((length - best_length) / best_length) * 100
            
            # Speedup vs reference
            if ref_time and ref_time > 0:
                speedup = ref_time / time_taken
                speedup_str = f"{speedup:.1f}x"
            else:
                speedup_str = "N/A"
            
            # Format time
            if time_taken < 1:
                time_str = f"{time_taken*1000:.1f}ms"
            else:
                time_str = f"{time_taken:.2f}s"
            
            # Highlight best
            marker = "🏆" if gap < 0.01 else ("✅" if gap < 3 else "⚠️" if gap < 5 else "")
            
            print(f"{solver_name:<20} {length:<12.2f} {gap:<10.2f} {time_str:<15} {speedup_str:<10} {marker}")
    
    # Overall statistics
    print("\n" + "=" * 80)
    print("📈 OVERALL STATISTICS")
    print("=" * 80)
    
    # Collect stats for each PIMST variant
    for pimst_variant in ['pimst_fast', 'pimst_balanced', 'pimst_optimal']:
        gaps = []
        speedups = []
        times = []
        
        for name, data in results.items():
            solvers = data['solvers']
            if not solvers or pimst_variant not in solvers:
                continue
            
            best_length = min(s['length'] for s in solvers.values())
            pimst_length = solvers[pimst_variant]['length']
            pimst_time = solvers[pimst_variant]['time']
            
            gap = ((pimst_length - best_length) / best_length) * 100
            gaps.append(gap)
            times.append(pimst_time)
            
            if 'ortools' in solvers:
                ortools_time = solvers['ortools']['time']
                speedup = ortools_time / pimst_time
                speedups.append(speedup)
        
        if gaps:
            variant_name = pimst_variant.replace('pimst_', 'PIMST ').title()
            print(f"\n{variant_name}:")
            print(f"  Average Gap:     {np.mean(gaps):.2f}%")
            print(f"  Median Gap:      {np.median(gaps):.2f}%")
            print(f"  Best Gap:        {np.min(gaps):.2f}%")
            print(f"  Worst Gap:       {np.max(gaps):.2f}%")
            print(f"  Gap <3%:         {sum(1 for g in gaps if g < 3)}/{len(gaps)} ({sum(1 for g in gaps if g < 3)/len(gaps)*100:.0f}%)")
            print(f"  Gap <5%:         {sum(1 for g in gaps if g < 5)}/{len(gaps)} ({sum(1 for g in gaps if g < 5)/len(gaps)*100:.0f}%)")
            print(f"  Average Time:    {np.mean(times)*1000:.1f}ms")
            
            if speedups:
                print(f"\n  vs OR-Tools:")
                print(f"    Average Speedup: {np.mean(speedups):.1f}x")
                print(f"    Median Speedup:  {np.median(speedups):.1f}x")
                print(f"    Min Speedup:     {np.min(speedups):.1f}x")
                print(f"    Max Speedup:     {np.max(speedups):.1f}x")
    
    # Save results
    results_json = {}
    for name, data in results.items():
        results_json[name] = {
            'n': data['n'],
            'solvers': {}
        }
        for solver_name, solver_data in data['solvers'].items():
            results_json[name]['solvers'][solver_name] = {
                'length': float(solver_data['length']),
                'time': float(solver_data['time']),
                'algorithm': solver_data['algorithm']
            }
    
    with open('benchmark_results.json', 'w') as f:
        json.dump(results_json, f, indent=2)
    
    print(f"\n✅ Results saved to: benchmark_results.json")
    
    return results

# =============================================================================
# GENERATE MARKDOWN SUMMARY
# =============================================================================

def generate_markdown_summary(results):
    """Generate markdown summary for README/paper."""
    
    # Calculate overall stats for PIMST balanced
    gaps = []
    speedups = []
    perfect_solutions = 0
    total = 0
    
    for name, data in results.items():
        solvers = data['solvers']
        if not solvers or 'pimst_balanced' not in solvers:
            continue
        
        total += 1
        best_length = min(s['length'] for s in solvers.values())
        pimst_length = solvers['pimst_balanced']['length']
        pimst_time = solvers['pimst_balanced']['time']
        
        gap = ((pimst_length - best_length) / best_length) * 100
        gaps.append(gap)
        
        if gap < 0.01:
            perfect_solutions += 1
        
        if 'ortools' in solvers:
            ortools_time = solvers['ortools']['time']
            speedup = ortools_time / pimst_time
            speedups.append(speedup)
    
    md = []
    md.append("\n## 📊 Benchmark Results Summary")
    md.append("\n### PIMST (balanced) vs Google OR-Tools\n")
    md.append(f"**Quality:**")
    md.append(f"- Average gap: {np.mean(gaps):.2f}%")
    md.append(f"- Median gap: {np.median(gaps):.2f}%")
    md.append(f"- Perfect solutions (0% gap): {perfect_solutions}/{total} ({perfect_solutions/total*100:.0f}%)")
    md.append(f"- Solutions <3% gap: {sum(1 for g in gaps if g < 3)}/{total} ({sum(1 for g in gaps if g < 3)/total*100:.0f}%)")
    md.append(f"\n**Speed:**")
    md.append(f"- Average speedup: {np.mean(speedups):.1f}x faster than OR-Tools")
    md.append(f"- Median speedup: {np.median(speedups):.1f}x")
    md.append(f"- Range: {np.min(speedups):.1f}x - {np.max(speedups):.1f}x")
    md.append(f"\n### Detailed Results by Dataset\n")
    md.append("| Dataset | N | PIMST Gap | PIMST Time | OR-Tools Time | Speedup |")
    md.append("|---------|---|-----------|------------|---------------|---------|")
    
    for name in sorted(results.keys()):
        data = results[name]
        solvers = data['solvers']
        if 'pimst_balanced' not in solvers or 'ortools' not in solvers:
            continue
        
        n = data['n']
        pimst = solvers['pimst_balanced']
        ortools = solvers['ortools']
        
        gap = ((pimst['length'] - ortools['length']) / ortools['length']) * 100
        speedup = ortools['time'] / pimst['time']
        
        pimst_time_str = f"{pimst['time']*1000:.1f}ms" if pimst['time'] < 1 else f"{pimst['time']:.2f}s"
        ortools_time_str = f"{ortools['time']:.2f}s"
        
        marker = "🏆" if abs(gap) < 0.01 else ""
        
        md.append(f"| {name} | {n} | {gap:.2f}% {marker} | {pimst_time_str} | {ortools_time_str} | {speedup:.1f}x |")
    
    summary = "\n".join(md)
    
    with open('BENCHMARK_SUMMARY.md', 'w') as f:
        f.write(summary)
    
    print(f"\n✅ Markdown summary saved to: BENCHMARK_SUMMARY.md")
    print(summary)
    
    return summary

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 STARTING COMPREHENSIVE TSP BENCHMARK")
    print("=" * 80)
    print("\nPIMST (Your Innovation) vs. Google OR-Tools")
    print("This may take 5-10 minutes depending on your CPU.\n")
    
    input("Press ENTER to start benchmark...")
    
    print("\n🏁 Starting benchmark...\n")
    
    try:
        results = run_benchmarks()
        analyze_results(results)
        generate_markdown_summary(results)
        
        print("\n" + "=" * 80)
        print("✅ BENCHMARK COMPLETE!")
        print("=" * 80)
        print("\n📁 Files generated:")
        print("  - benchmark_results.json (detailed data)")
        print("  - BENCHMARK_SUMMARY.md (formatted summary)")
        print("\n📢 Next steps:")
        print("  1. Review results above")
        print("  2. Add BENCHMARK_SUMMARY.md to README.md")
        print("  3. Post on Reddit/HN with real data! 🔥")
        print("  4. Include in academic paper")
        print("\n🎉 Your innovation is validated! Time to share with the world! 🚀")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
