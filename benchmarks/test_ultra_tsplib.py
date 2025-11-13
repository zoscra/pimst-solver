"""
Test Ultra Solver vs TSPLIB
"""
import numpy as np
import time
from pathlib import Path
from pimst.improved.sino.ultra_solver import UltraSolver

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

# Instancias
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

solver = UltraSolver()

print("="*70)
print("  ULTRA SOLVER vs TSPLIB")
print("="*70)

results = []

for name, optimal in instances.items():
    filename = f"benchmarks/tsplib/{name}.tsp"
    
    if not Path(filename).exists():
        continue
    
    print(f"\n{'='*70}")
    print(f"  {name.upper()} (óptimo: {optimal})")
    print(f"{'='*70}")
    
    coords = parse_tsplib(filename)
    n = len(coords)
    
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = np.linalg.norm(coords[i] - coords[j])
    
    # Ultra Solver
    tour, cost, metadata = solver.solve(coords, distances, time_budget=10.0)
    
    gap = ((cost - optimal) / optimal) * 100
    
    print(f"\n🚀 Ultra Solver:")
    print(f"   Costo: {cost:.2f}")
    print(f"   Óptimo: {optimal}")
    print(f"   Gap: {gap:+.2f}%")
    print(f"   Tiempo: {metadata['total_time']:.2f}s")
    print(f"   LK runs: {metadata['n_lk_runs']}")
    print(f"   Mejor: {metadata['best_strategy']}")
    
    results.append({'name': name, 'gap': gap, 'time': metadata['total_time']})

# Resumen
print("\n" + "="*70)
print("  📊 RESUMEN")
print("="*70)

gaps = [r['gap'] for r in results]
times = [r['time'] for r in results]

print(f"\n🎯 Gap vs Óptimo:")
print(f"   Promedio: {np.mean(gaps):+.2f}%")
print(f"   Mediana:  {np.median(gaps):+.2f}%")
print(f"   Mejor:    {np.min(gaps):+.2f}%")
print(f"   Peor:     {np.max(gaps):+.2f}%")

print(f"\n⏱️  Tiempo:")
print(f"   Promedio: {np.mean(times):.2f}s")
print(f"   Mediana:  {np.median(times):.2f}s")

