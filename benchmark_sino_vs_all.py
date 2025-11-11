"""
Benchmark: SiNo vs OR-Tools
============================
"""

import numpy as np
import time
from typing import List, Tuple, Dict
import json
from datetime import datetime

from pimst.improved.sino import smart_solve, SmartSelector


def solve_with_ortools(distances: np.ndarray, time_limit: int = 30) -> Tuple[List[int], float, float]:
    """Resolver con OR-Tools."""
    try:
        from ortools.constraint_solver import routing_enums_pb2, pywrapcp
    except ImportError:
        return None, float('inf'), 0.0
    
    n = len(distances)
    
    # Crear índices
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    
    # ARREGLADO: usar to_node en lugar de to_index
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distances[from_node][to_node] * 10000)
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Parámetros de búsqueda
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = time_limit
    
    # Resolver
    start = time.time()
    try:
        solution = routing.SolveWithParameters(search_parameters)
        elapsed = time.time() - start
        
        if solution:
            tour = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                tour.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            return tour, cost, elapsed
        else:
            return None, float('inf'), elapsed
    except Exception as e:
        elapsed = time.time() - start
        print(f"[OR-Tools exception: {e}]", end=" ")
        return None, float('inf'), elapsed


def solve_with_sino(distances: np.ndarray, coordinates=None) -> Tuple[List[int], float, float]:
    """Resolver con SiNo."""
    start = time.time()
    tour, cost = smart_solve(distances, coordinates)
    elapsed = time.time() - start
    return tour, cost, elapsed


def generate_test_instances():
    """Generar instancias de prueba."""
    instances = []
    
    # 1. Circles (donde SiNo debería dominar)
    for n in [20, 50, 100]:
        angles = np.linspace(0, 2*np.pi, n, endpoint=False)
        coords = np.column_stack([np.cos(angles), np.sin(angles)])
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distances[i][j] = np.linalg.norm(coords[i] - coords[j])
        
        instances.append({
            'name': f'circle-{n}',
            'type': 'circle',
            'n': n,
            'distances': distances,
            'coordinates': coords
        })
    
    # 2. Random
    for n in [20, 50, 100]:
        np.random.seed(42 + n)
        coords = np.random.rand(n, 2) * 100
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distances[i][j] = np.linalg.norm(coords[i] - coords[j])
        
        instances.append({
            'name': f'random-{n}',
            'type': 'random',
            'n': n,
            'distances': distances,
            'coordinates': coords
        })
    
    # 3. Clustered
    for n in [20, 50, 100]:
        np.random.seed(100 + n)
        n_clusters = 4
        coords = []
        
        nodes_per_cluster = n // n_clusters
        remainder = n % n_clusters
        
        for i in range(n_clusters):
            center = np.random.rand(2) * 100
            size = nodes_per_cluster + (1 if i < remainder else 0)
            cluster = center + np.random.randn(size, 2) * 5
            coords.extend(cluster.tolist())
        
        coords = np.array(coords)
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distances[i][j] = np.linalg.norm(coords[i] - coords[j])
        
        instances.append({
            'name': f'clustered-{n}',
            'type': 'clustered',
            'n': n,
            'distances': distances,
            'coordinates': coords
        })
    
    return instances


def run_benchmark():
    """Ejecutar benchmark completo."""
    print("="*70)
    print("  BENCHMARK: SiNo vs OR-Tools")
    print("="*70)
    print()
    
    instances = generate_test_instances()
    results = []
    
    for inst in instances:
        print(f"\n{inst['name']} (n={inst['n']}, type={inst['type']})")
        print("-" * 70)
        
        distances = inst['distances']
        coords = inst.get('coordinates')
        
        result = {
            'instance': inst['name'],
            'type': inst['type'],
            'n': inst['n']
        }
        
        # 1. SiNo
        print("  SiNo...", end=" ", flush=True)
        try:
            tour_sino, cost_sino, time_sino = solve_with_sino(distances, coords)
            print(f"Cost: {cost_sino:.2f}, Time: {time_sino*1000:.1f}ms")
            result['sino'] = {
                'cost': float(cost_sino),
                'time': float(time_sino),
                'success': True
            }
        except Exception as e:
            print(f"Error: {e}")
            result['sino'] = {'success': False, 'error': str(e)}
        
        # 2. OR-Tools
        print("  OR-Tools...", end=" ", flush=True)
        try:
            tour_or, cost_or, time_or = solve_with_ortools(distances, time_limit=30)
            if tour_or:
                print(f"Cost: {cost_or:.2f}, Time: {time_or*1000:.1f}ms")
                result['ortools'] = {
                    'cost': float(cost_or),
                    'time': float(time_or),
                    'success': True
                }
            else:
                print("No solution")
                result['ortools'] = {'success': False}
        except Exception as e:
            print(f"Error: {e}")
            result['ortools'] = {'success': False, 'error': str(e)}
        
        # 3. Comparison
        if result.get('sino', {}).get('success') and result.get('ortools', {}).get('success'):
            gap = ((result['sino']['cost'] - result['ortools']['cost']) / result['ortools']['cost']) * 100
            speedup = result['ortools']['time'] / result['sino']['time']
            
            emoji = "🚀🚀" if speedup > 10 else "🚀" if speedup > 1 else ""
            print(f"  -> Gap: {gap:+.2f}%, Speedup: {speedup:.2f}x {emoji}")
            
            result['comparison'] = {
                'gap_percent': float(gap),
                'speedup': float(speedup)
            }
        
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("  RESUMEN")
    print("="*70)
    
    for inst_type in ['circle', 'random', 'clustered']:
        type_results = [r for r in results if r['type'] == inst_type]
        if not type_results:
            continue
        
        print(f"\n{inst_type.upper()}:")
        
        gaps = [r['comparison']['gap_percent'] for r in type_results if 'comparison' in r]
        speedups = [r['comparison']['speedup'] for r in type_results if 'comparison' in r]
        
        if gaps and speedups:
            print(f"  Gap: avg={np.mean(gaps):+.2f}%, best={min(gaps):+.2f}%, worst={max(gaps):+.2f}%")
            print(f"  Speedup: avg={np.mean(speedups):.2f}x, best={max(speedups):.2f}x, worst={min(speedups):.2f}x")
        else:
            print("  (No hay comparaciones disponibles)")
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({'timestamp': timestamp, 'results': results}, f, indent=2)
    
    print(f"\n✅ Resultados guardados: {filename}")
    
    return results


if __name__ == '__main__':
    results = run_benchmark()
