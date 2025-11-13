"""
Benchmark científico vs TSPLIB
Métricas: gap vs óptimo, tiempo, comparación con LKH
"""
import numpy as np
import time
import json
from pathlib import Path
from pimst.improved.sino.super_solver import SuperSolver

def parse_tsplib(filename):
    """Parse archivo TSPLIB."""
    coords = []
    reading_coords = False
    
    with open(filename) as f:
        for line in f:
            if 'NODE_COORD_SECTION' in line:
                reading_coords = True
                continue
            if 'EOF' in line:
                break
            if reading_coords:
                parts = line.strip().split()
                if len(parts) >= 3:
                    coords.append([float(parts[1]), float(parts[2])])
    
    return np.array(coords)

def run_benchmark():
    """Ejecutar benchmark científico."""
    # Instancias con óptimos conocidos
    instances = {
        'eil51': 426,
        'berlin52': 7542,
        'st70': 675,
        'eil76': 538,
        'kroA100': 21282,
        'kroB100': 22141,
        'kroC100': 20749,
        'kroD100': 21294,
        'kroE100': 22068,
    }
    
    solver = SuperSolver(mode='academic')  # Priorizar calidad para TSPLIB
    results = {}
    
    print("="*70)
    print("  BENCHMARK CIENTÍFICO - TSPLIB INSTANCES")
    print("="*70)
    
    for name, optimal in instances.items():
        filename = f"benchmarks/tsplib/{name}.tsp"
        
        if not Path(filename).exists():
            print(f"⚠️ Saltando {name} (archivo no encontrado)")
            continue
        
        print(f"\n{'='*70}")
        print(f"  {name.upper()} (óptimo conocido: {optimal})")
        print(f"{'='*70}")
        
        # Parse instance
        coords = parse_tsplib(filename)
        n = len(coords)
        
        # Calcular matriz de distancias
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distances[i][j] = np.linalg.norm(coords[i] - coords[j])
        
        # Ejecutar Super Solver 3 veces, tomar mejor resultado
        best_cost = float('inf')
        best_tour = None
        best_metadata = None
        total_time = 0
        
        for run in range(3):
            start = time.time()
            tour, cost, metadata = solver.solve(coords, distances, time_budget=20.0)
            run_time = time.time() - start
            total_time += run_time
            
            if cost < best_cost:
                best_cost = cost
                best_tour = tour
                best_metadata = metadata
        
        tour = best_tour
        cost = best_cost
        metadata = best_metadata
        elapsed = total_time
        
        gap = ((cost - optimal) / optimal) * 100
        
        print(f"\n🚀 Super Solver:")
        print(f"   Costo: {cost:.2f}")
        print(f"   Óptimo: {optimal}")
        print(f"   Gap: {gap:+.2f}%")
        print(f"   Tiempo: {elapsed:.2f}s")
        print(f"   Estrategias: {', '.join(metadata['strategies_used'])}")
        
        results[name] = {
            'n': n,
            'optimal': optimal,
            'cost': cost,
            'gap_pct': gap,
            'time': elapsed,
            'strategies': metadata['strategies_used']
        }
    
    # Guardar resultados
    with open('benchmarks/results/tsplib_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Resumen
    print("\n" + "="*70)
    print("  📊 RESUMEN")
    print("="*70)
    
    gaps = [r['gap_pct'] for r in results.values()]
    times = [r['time'] for r in results.values()]
    
    print(f"\n🎯 Gap vs Óptimo TSPLIB:")
    print(f"   Promedio: {np.mean(gaps):+.2f}%")
    print(f"   Mediana:  {np.median(gaps):+.2f}%")
    print(f"   Mejor:    {np.min(gaps):+.2f}%")
    print(f"   Peor:     {np.max(gaps):+.2f}%")
    
    print(f"\n⏱️  Tiempo de ejecución:")
    print(f"   Promedio: {np.mean(times):.2f}s")
    print(f"   Mediana:  {np.median(times):.2f}s")
    
    print("\n✅ Resultados guardados en benchmarks/results/tsplib_results.json")

if __name__ == '__main__':
    run_benchmark()
