import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from pimst.improved.sino.quantum_solver import QuantumSolver

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
    'st70': 675,       # El problemático  
    'berlin52': 7542,  # Convergía a 8107.55
    'kroB100': 22141,
}

solver = QuantumSolver()

print("="*70)
print("  🎲 QUANTUM SOLVER - 'La Aguja Dorada por Casualidad'")
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
    
    tour, cost, meta = solver.solve(coords, distances, time_budget=15.0)
    gap = ((cost - optimal) / optimal) * 100
    
    print(f"\n🎯 RESULTADO:")
    print(f"   Gap: {gap:+.2f}%")
    print(f"   Unicidad: {meta['uniqueness_ratio']*100:.1f}%")
    print(f"   Ganador: {meta['best_strategy']}")
    
    results.append({'name': name, 'gap': gap})

# RESUMEN
print("\n" + "="*70)
print("  📊 RESUMEN QUANTUM")
print("="*70)

gaps = [r['gap'] for r in results]
print(f"\n🎯 Gap promedio: {np.mean(gaps):.2f}%")
print(f"   Mejor: {np.min(gaps):.2f}%")
print(f"   Peor: {np.max(gaps):.2f}%")

if np.mean(gaps) < 5.0:
    print("\n🎉 ¡LA CASUALIDAD GANÓ!")
elif np.mean(gaps) < np.mean([9.40, 7.50, 1.39]):  # Referencia anterior
    print("\n✅ ¡MEJORA DETECTADA!")
else:
    print("\n📊 Explorando el multiverso...")

print("="*70)
