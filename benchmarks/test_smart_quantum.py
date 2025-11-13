import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from pimst.improved.sino.smart_quantum_solver import SmartQuantumSolver

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
solver = SmartQuantumSolver()

print("="*70)
print("  💎 SMART QUANTUM - 'Calidad primero'")
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
    
    print(f"\n🎯 Gap: {gap:+.2f}%")
    results.append({'name': name, 'gap': gap})

print("\n" + "="*70)
print("  📊 RESUMEN")
print("="*70)

gaps = [r['gap'] for r in results]
print(f"\n🎯 Gap promedio: {np.mean(gaps):.2f}%")
print(f"   Mejor: {np.min(gaps):.2f}%")
print(f"   Peor: {np.max(gaps):.2f}%")

print(f"\n💡 Comparaciones:")
print(f"   Quantum (15% ruido): 3.40%")
print(f"   Fine-tune (6.5% ruido): 5.11%")
print(f"   Smart Quantum: {np.mean(gaps):.2f}%")

if np.mean(gaps) < 3.40:
    print(f"\n🏆 ¡NUEVO RÉCORD!")
else:
    print(f"\n📊 Progreso continuo...")

print("="*70)
