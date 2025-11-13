import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from pimst.improved.sino.adaptive_quantum_solver import AdaptiveQuantumSolver

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
    'berlin52': 7542,
    'st70': 675,
    'kroB100': 22141,
}

solver = AdaptiveQuantumSolver()

print("="*70)
print("  🎯 ADAPTIVE QUANTUM - 'Balance perfecto'")
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
    print(f"   Ruido final: {meta['final_noise_level']:.3f}")
    
    results.append({'name': name, 'gap': gap})

print("\n" + "="*70)
print("  📊 ADAPTIVE QUANTUM RESUMEN")
print("="*70)

gaps = [r['gap'] for r in results]
print(f"\n🎯 Gap promedio: {np.mean(gaps):.2f}%")
print(f"   Mejor: {np.min(gaps):.2f}%")

if np.mean(gaps) < 3.40:
    print("\n🎉 ¡NUEVO RÉCORD!")
elif np.mean(gaps) < 6.10:
    print("\n✅ Mejor que Ultra-Quantum")
else:
    print("\n📊 Explorando...")

print("="*70)
