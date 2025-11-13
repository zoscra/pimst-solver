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
    'st70': 675,      # El difícil (9.40% gap antes)
    'berlin52': 7542,  # Moderado
    'kroB100': 22141, # Ya era bueno (1.39%)
}

solver = HotspotGuidedSolver()

print("="*70)
print("  HOTSPOT-GUIDED SOLVER vs TSPLIB")
print("="*70)

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
    
    tour, cost, meta = solver.solve(coords, distances, time_budget=5.0)
    gap = ((cost - optimal) / optimal) * 100
    
    print(f"\n🎯 RESULTADO:")
    print(f"   Gap: {gap:+.2f}%")
    print(f"   Hotspots: {meta['hotspots']}")
    print(f"   Soluciones: {meta['total_solutions']}")

print("\n" + "="*70)
