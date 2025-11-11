"""
Benchmark Thompson Sampling vs Baseline
"""

import numpy as np
import time
from pimst.improved.sino.thompson_selector import ThompsonSamplingSelector
from pimst.algorithms import multi_start_solver


def benchmark_thompson():
    """Compare Thompson Sampling against multi-start baseline."""
    
    print("="*70)
    print("  BENCHMARK: Thompson Sampling vs Baseline")
    print("="*70)
    
    selector = ThompsonSamplingSelector()
    
    results = []
    
    # Test on multiple instances
    for seed in [42, 123, 456, 789, 999]:
        for n in [50, 100, 200]:
            print(f"\n{'='*70}")
            print(f"  n={n}, seed={seed}")
            print(f"{'='*70}")
            
            np.random.seed(seed)
            coords = np.random.rand(n, 2) * 1000
            distances = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    distances[i][j] = np.linalg.norm(coords[i] - coords[j])
            
            # Thompson Sampling
            print("\n🧠 Thompson Sampling (adaptativo):")
            start = time.time()
            tour_ts, cost_ts = selector.solve_and_learn(coords, distances)
            time_ts = time.time() - start
            print(f"   Costo: {cost_ts:.2f}")
            print(f"   Tiempo: {time_ts:.2f}s")
            
            # Baseline (multi-start 50)
            print("\n📊 Baseline (multi-start 50):")
            start = time.time()
            tour_ref = multi_start_solver(coords, distances, n_starts=50)
            cost_ref = sum(distances[tour_ref[i]][tour_ref[(i+1)%n]] for i in range(n))
            time_ref = time.time() - start
            print(f"   Costo: {cost_ref:.2f}")
            print(f"   Tiempo: {time_ref:.2f}s")
            
            # Compare
            gap = ((cost_ts - cost_ref) / cost_ref) * 100
            speedup = time_ref / time_ts
            
            print(f"\n📊 Resultado:")
            print(f"   Gap: {gap:+.2f}%")
            print(f"   Speedup: {speedup:.2f}x")
            
            results.append({
                'n': n,
                'seed': seed,
                'gap': gap,
                'speedup': speedup,
                'time_ts': time_ts,
                'time_ref': time_ref
            })
    
    # Summary
    print("\n" + "="*70)
    print("  RESUMEN")
    print("="*70)
    
    gaps = [r['gap'] for r in results]
    speedups = [r['speedup'] for r in results]
    
    print(f"\n🎯 Gap vs Baseline:")
    print(f"   Promedio: {np.mean(gaps):+.2f}%")
    print(f"   Mediana:  {np.median(gaps):+.2f}%")
    print(f"   Rango:    [{np.min(gaps):+.2f}%, {np.max(gaps):+.2f}%]")
    
    print(f"\n⚡ Speedup:")
    print(f"   Promedio: {np.mean(speedups):.2f}x")
    print(f"   Mediana:  {np.median(speedups):.2f}x")
    print(f"   Rango:    [{np.min(speedups):.2f}x, {np.max(speedups):.2f}x]")
    
    # Show learned preferences
    print("\n")
    selector.print_stats()
    
    # Verdict
    print("\n" + "="*70)
    avg_gap = np.mean(gaps)
    avg_speedup = np.mean(speedups)
    
    if avg_gap < 3 and avg_speedup > 5:
        print("✅ EXCELENTE: Thompson Sampling mantiene calidad con gran speedup")
    elif avg_gap < 5:
        print("✅ BUENO: Thompson Sampling balancea bien calidad/velocidad")
    else:
        print("⚠️ MEJORABLE: Necesita más entrenamiento o ajustes")


if __name__ == '__main__':
    benchmark_thompson()
