import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from pimst.improved.sino.geometric_hotspots import HotspotGuidedSolver

def parse_tsplib(filename):
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

instances = {
    'st70': 675,       # El más difícil
    'berlin52': 7542,  # Ya mejoró
    'kroB100': 22141,  # Ya bueno
}

solver = HotspotGuidedSolver()

print("="*70)
print("  HOTSPOT-GUIDED SOLVER - FINAL TEST (10s budget)")
print("="*70)

results = []

for name, optimal in instances.items():
    filename = f"benchmarks/tsplib/{name}.tsp"
    if not Path(filename).exists():
        continue
    
    print(f"\n{'='*70}")
    print(f"  {name.upper()} (óptimo: {optimal})")
    print(f"{'='*70}\n")
    
    coords = parse_tsplib(filename)
    n = len(coords)
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = np.linalg.norm(coords[i] - coords[j])
    
    # 10 segundos de budget
    tour, cost, meta = solver.solve(coords, distances, time_budget=10.0)
    gap = ((cost - optimal) / optimal) * 100
    
    print(f"\n🎯 RESULTADO:")
    print(f"   Gap: {gap:+.2f}%")
    print(f"   Tiempo: {meta['total_time']:.2f}s")
    print(f"   Soluciones: {meta['total_solutions']}")
    print(f"   Mejor estrategia: {meta['best_strategy']}")
    
    results.append({'name': name, 'gap': gap, 'time': meta['total_time']})

# RESUMEN
print("\n" + "="*70)
print("  📊 RESUMEN FINAL")
print("="*70)

gaps = [r['gap'] for r in results]

print(f"\n🎯 Gap promedio: {np.mean(gaps):.2f}%")
print(f"   Mediana: {np.median(gaps):.2f}%")
print(f"   Mejor: {np.min(gaps):.2f}%")
print(f"   Peor: {np.max(gaps):.2f}%")

print("\n" + "="*70)

if np.mean(gaps) < 5.0:
    print("✅ OBJETIVO LOGRADO: Gap promedio < 5%")
else:
    print(f"⚠️ Gap promedio: {np.mean(gaps):.2f}% (objetivo: <5%)")
