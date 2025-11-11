"""
Benchmark Super Solver vs LKH-like baseline
"""

import numpy as np
import time
from pimst.improved.sino.super_solver import SuperSolver
from pimst.algorithms import multi_start_solver


def benchmark_super():
    print("="*70)
    print("  BENCHMARK: Super Solver vs LKH-like (50-start)")
    print("="*70)
    
    solver = SuperSolver()
    results = []
    
    # Test exhaustivo
    for seed in [42, 123, 456, 789, 999]:
        for n in [50, 100, 200, 300]:
            print(f"\n{'='*70}")
            print(f"  n={n}, seed={seed}")
            print(f"{'='*70}")
            
            np.random.seed(seed)
            coords = np.random.rand(n, 2) * 1000
            distances = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    distances[i][j] = np.linalg.norm(coords[i] - coords[j])
            
            # Super Solver
            print("\n🚀 Super Solver:")
            start = time.time()
            tour_super, cost_super, metadata = solver.solve(coords, distances, time_budget=10.0)
            time_super = time.time() - start
            
            print(f"   Costo: {cost_super:.2f}")
            print(f"   Tiempo: {time_super:.2f}s")
            print(f"   Estrategias: {', '.join(metadata['strategies_used'])}")
            print(f"   Calidad final: {metadata.get('final_quality', metadata['initial_quality'])}")
            
            # LKH-like baseline (50 starts)
            print("\n📊 LKH-like (50-start):")
            start = time.time()
            tour_ref = multi_start_solver(coords, distances, n_starts=50)
            cost_ref = sum(distances[tour_ref[i]][tour_ref[(i+1)%n]] for i in range(n))
            time_ref = time.time() - start
            
            print(f"   Costo: {cost_ref:.2f}")
            print(f"   Tiempo: {time_ref:.2f}s")
            
            # Comparación
            gap = ((cost_super - cost_ref) / cost_ref) * 100
            speedup = time_ref / time_super
            
            print(f"\n🎯 RESULTADO:")
            print(f"   Gap: {gap:+.2f}%")
            print(f"   Speedup: {speedup:.2f}x")
            
            if gap <= 0:
                print(f"   ✅ MEJOR QUE LKH-LIKE")
            elif gap < 2:
                print(f"   ✅ CASI IGUAL A LKH-LIKE")
            elif gap < 5:
                print(f"   ⚠️ ACEPTABLE")
            else:
                print(f"   ❌ NECESITA MEJORA")
            
            results.append({
                'n': n,
                'seed': seed,
                'gap': gap,
                'speedup': speedup,
                'quality': metadata.get('final_quality', metadata['initial_quality'])
            })
    
    # RESUMEN FINAL
    print("\n" + "="*70)
    print("  📊 RESUMEN FINAL")
    print("="*70)
    
    gaps = [r['gap'] for r in results]
    speedups = [r['speedup'] for r in results]
    
    print(f"\n🎯 Gap vs LKH-like:")
    print(f"   Promedio: {np.mean(gaps):+.2f}%")
    print(f"   Mediana:  {np.median(gaps):+.2f}%")
    print(f"   Mejor:    {np.min(gaps):+.2f}%")
    print(f"   Peor:     {np.max(gaps):+.2f}%")
    
    print(f"\n⚡ Speedup:")
    print(f"   Promedio: {np.mean(speedups):.2f}x")
    print(f"   Mediana:  {np.median(speedups):.2f}x")
    print(f"   Rango:    [{np.min(speedups):.2f}x, {np.max(speedups):.2f}x]")
    
    # Contar victorias
    better = sum(1 for r in results if r['gap'] <= 0)
    similar = sum(1 for r in results if 0 < r['gap'] < 2)
    acceptable = sum(1 for r in results if 2 <= r['gap'] < 5)
    poor = sum(1 for r in results if r['gap'] >= 5)
    
    total = len(results)
    
    print(f"\n📈 Distribución de Calidad:")
    print(f"   Mejor que LKH:     {better}/{total} ({100*better/total:.1f}%)")
    print(f"   Similar a LKH:     {similar}/{total} ({100*similar/total:.1f}%)")
    print(f"   Aceptable (<5%):   {acceptable}/{total} ({100*acceptable/total:.1f}%)")
    print(f"   Necesita mejora:   {poor}/{total} ({100*poor/total:.1f}%)")
    
    # VEREDICTO
    print("\n" + "="*70)
    avg_gap = np.mean(gaps)
    avg_speedup = np.mean(speedups)
    
    if avg_gap < 0:
        print("🏆 OBJETIVO LOGRADO: ¡MEJOR QUE LKH CON GRAN VELOCIDAD!")
    elif avg_gap < 2 and avg_speedup > 10:
        print("✅ EXCELENTE: Calidad competitiva con LKH, mucho más rápido")
    elif avg_gap < 5:
        print("✅ BUENO: Cerca del objetivo, necesita ajustes menores")
    else:
        print("⚠️ MEJORABLE: Necesita más trabajo")
    
    print("="*70)


if __name__ == '__main__':
    benchmark_super()
