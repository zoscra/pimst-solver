"""
Benchmark vs Soluciones Óptimas/LKH
===================================

Usa instancias con soluciones conocidas para medir gap real.
"""

import numpy as np
import time
from pimst.improved.sino import smart_solve
from pimst.algorithms import solve_tsp_smart


def generate_instances_with_optimal():
    """Generar instancias y calcular soluciones óptimas/near-optimal."""
    instances = []
    
    # Instancias de diferentes tamaños
    for n in [50, 100, 200, 300, 500]:
        for seed in [42, 123, 456]:
            np.random.seed(seed)
            coords = np.random.rand(n, 2) * 1000
            distances = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    distances[i][j] = np.linalg.norm(coords[i] - coords[j])
            
            instances.append({
                'name': f'random-{n}-seed{seed}',
                'n': n,
                'seed': seed,
                'coords': coords,
                'distances': distances
            })
    
    return instances


def get_best_known_solution(coords, distances, time_limit=60):
    """
    Obtener la mejor solución posible con múltiples estrategias.
    Esto simula tener una solución de referencia (como LKH).
    """
    from pimst.algorithms import multi_start_solver
    
    n = len(coords)
    
    # Múltiples intentos con diferentes configuraciones
    best_cost = float('inf')
    best_tour = None
    
    # Multi-start agresivo
    n_starts = min(50, max(10, 1000 // n))
    tour = multi_start_solver(coords, distances, n_starts=n_starts)
    cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
    
    if cost < best_cost:
        best_cost = cost
        best_tour = tour
    
    return best_tour.tolist(), best_cost


def run_benchmark():
    """Ejecutar benchmark completo."""
    print("="*80)
    print("  BENCHMARK vs SOLUCIONES ÓPTIMAS/NEAR-OPTIMAL")
    print("="*80)
    print()
    
    instances = generate_instances_with_optimal()
    results = []
    
    for inst in instances:
        print(f"\n{'='*80}")
        print(f"  {inst['name']} (n={inst['n']})")
        print(f"{'='*80}")
        
        coords = inst['coords']
        distances = inst['distances']
        n = inst['n']
        
        # 1. Calcular solución de referencia (óptima/near-optimal)
        print(f"\n🎯 Calculando solución de referencia...")
        start = time.time()
        ref_tour, ref_cost = get_best_known_solution(coords, distances)
        ref_time = time.time() - start
        print(f"   Costo referencia: {ref_cost:.2f}")
        print(f"   Tiempo: {ref_time:.1f}s")
        
        # 2. SiNo
        print(f"\n🔵 SiNo:")
        start = time.time()
        tour_sino, cost_sino = smart_solve(distances, coords)
        time_sino = time.time() - start
        print(f"   Costo: {cost_sino:.2f}")
        print(f"   Tiempo: {time_sino:.1f}s")
        
        # 3. Comparación
        gap = ((cost_sino - ref_cost) / ref_cost) * 100
        speedup = ref_time / time_sino
        
        print(f"\n📊 RESULTADOS:")
        print(f"   Gap vs óptimo: {gap:+.2f}%")
        print(f"   Speedup: {speedup:.2f}x")
        
        emoji = "✅" if gap < 5 else "⚠️" if gap < 10 else "❌"
        print(f"   Calidad: {emoji} {'Excelente' if gap < 5 else 'Buena' if gap < 10 else 'Mejorable'}")
        
        results.append({
            'instance': inst['name'],
            'n': n,
            'ref_cost': ref_cost,
            'sino_cost': cost_sino,
            'gap': gap,
            'ref_time': ref_time,
            'sino_time': time_sino,
            'speedup': speedup
        })
    
    # Resumen por tamaño
    print("\n" + "="*80)
    print("  📊 RESUMEN POR TAMAÑO")
    print("="*80)
    
    for n in [50, 100, 200, 300, 500]:
        subset = [r for r in results if r['n'] == n]
        if not subset:
            continue
        
        avg_gap = np.mean([r['gap'] for r in subset])
        avg_speedup = np.mean([r['speedup'] for r in subset])
        best_gap = min([r['gap'] for r in subset])
        worst_gap = max([r['gap'] for r in subset])
        
        print(f"\nn = {n}:")
        print(f"  Gap promedio: {avg_gap:+.2f}%")
        print(f"  Gap rango: [{best_gap:+.2f}%, {worst_gap:+.2f}%]")
        print(f"  Speedup promedio: {avg_speedup:.2f}x")
        
        emoji = "✅" if avg_gap < 5 else "⚠️" if avg_gap < 10 else "❌"
        print(f"  {emoji} {'Excelente' if avg_gap < 5 else 'Bueno' if avg_gap < 10 else 'Necesita mejora'}")
    
    return results


if __name__ == '__main__':
    results = run_benchmark()
