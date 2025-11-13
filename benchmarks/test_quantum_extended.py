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

instances = {'berlin52': 7542, 'st70': 675, 'kroB100': 22141}
solver = QuantumSolver()

print("="*70)
print("  🏆 QUANTUM ORIGINAL - Con más tiempo")
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
    
    # 30 SEGUNDOS de tiempo
    tour, cost, meta = solver.solve(coords, distances, time_budget=30.0)
    gap = ((cost - optimal) / optimal) * 100
    
    print(f"\n🎯 Gap: {gap:+.2f}%")
    print(f"   Soluciones únicas: {meta['unique_solutions']}")
    results.append({'name': name, 'gap': gap, 'unique': meta['unique_solutions']})

print("\n" + "="*70)
print("  📊 RESUMEN CON 30 SEGUNDOS")
print("="*70)

gaps = [r['gap'] for r in results]
uniques = [r['unique'] for r in results]

print(f"\n🎯 Gap promedio: {np.mean(gaps):.2f}%")
print(f"   Mejor: {np.min(gaps):.2f}%")
print(f"   Peor: {np.max(gaps):.2f}%")

print(f"\n🎲 Soluciones únicas:")
for r in results:
    print(f"   {r['name']}: {r['unique']}")

print(f"\n💡 Comparación:")
print(f"   Quantum 15s: 3.40%")
print(f"   Quantum 30s: {np.mean(gaps):.2f}%")

if np.mean(gaps) < 3.40:
    improvement = ((3.40 - np.mean(gaps)) / 3.40) * 100
    print(f"\n🏆 ¡MEJORA CON MÁS TIEMPO! {improvement:.1f}% mejor")
    print(f"\n✅ CONCLUSIÓN: El Quantum original es el mejor,")
    print(f"   solo necesita más tiempo para explorar.")
else:
    print(f"\n📊 El 15s ya era óptimo para el presupuesto")

print("="*70)
