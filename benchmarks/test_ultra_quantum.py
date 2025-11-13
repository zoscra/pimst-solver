import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from pimst.improved.sino.ultra_quantum_solver import UltraQuantumSolver

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
    'berlin52': 7542,  # Era 1.37%, ¿podemos mejorar?
    'st70': 675,       # Era 7.46%
    'kroB100': 22141,  # Era 1.39%
}

solver = UltraQuantumSolver()

print("="*70)
print("  🌪️  ULTRA-QUANTUM - 'Caos infinito, cero repeticiones'")
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
    
    results.append({'name': name, 'gap': gap, 'unique': meta['uniqueness_ratio']})

# RESUMEN
print("\n" + "="*70)
print("  📊 ULTRA-QUANTUM RESUMEN")
print("="*70)

gaps = [r['gap'] for r in results]
uniques = [r['unique'] for r in results]

print(f"\n🎯 Gap promedio: {np.mean(gaps):.2f}%")
print(f"   Mejor: {np.min(gaps):.2f}%")
print(f"   Peor: {np.max(gaps):.2f}%")
print(f"\n🎲 Unicidad promedio: {np.mean(uniques)*100:.1f}%")
print(f"   Min: {np.min(uniques)*100:.1f}%")

if np.mean(gaps) < 3.40:
    print("\n🎉 ¡NUEVO RÉCORD! Superamos Quantum Solver")
elif np.mean(uniques) > 0.998:
    print("\n✨ ¡UNICIDAD PERFECTA! Casi 100% soluciones diferentes")
else:
    print("\n🌪️  Explorando el caos infinito...")

print("="*70)
