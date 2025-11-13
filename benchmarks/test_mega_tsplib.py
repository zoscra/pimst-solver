import numpy as np
from pathlib import Path
from pimst.improved.sino.mega_solver import MegaSolver

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
    'kroB100': 22141,
    'st70': 675,
    'berlin52': 7542,
}

solver = MegaSolver()

print("="*70)
print("  MEGA SOLVER - TEST EN 3 INSTANCIAS DIFÍCILES")
print("="*70)

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
    
    tour, cost, meta = solver.solve(coords, distances, time_budget=10.0)
    gap = ((cost - optimal) / optimal) * 100
    
    print(f"\n🎯 Gap: {gap:+.2f}%")
    print(f"⏱️  Tiempo: {meta['total_time']:.2f}s")
