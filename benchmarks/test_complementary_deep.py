import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from pimst.improved.sino.quantum_solver import QuantumSolver
from pimst.improved.sino.complementary_quantum import ComplementaryQuantumSolver

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

print("="*70)
print("  ⚔️  QUANTUM ORIGINAL vs COMPLEMENTARY QUANTUM")
print("="*70)

all_results = []

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
    
    # QUANTUM ORIGINAL (30s)
    print("🔷 Quantum Original (30s single run):\n")
    solver_orig = QuantumSolver()
    tour_orig, cost_orig, meta_orig = solver_orig.solve(coords, distances, time_budget=30.0)
    gap_orig = ((cost_orig - optimal) / optimal) * 100
    print(f"\n   📊 Gap: {gap_orig:+.2f}%")
    print(f"   🎲 Soluciones únicas: {meta_orig['unique_solutions']}")
    
    # COMPLEMENTARY QUANTUM (3×10s = 30s)
    print(f"\n{'─'*70}\n")
    print("⚡ Complementary Quantum (3 runs × 10s = 30s):\n")
    solver_comp = ComplementaryQuantumSolver()
    tour_comp, cost_comp, meta_comp = solver_comp.solve(coords, distances, time_budget=30.0, n_runs=3)
    gap_comp = ((cost_comp - optimal) / optimal) * 100
    print(f"\n   📊 Gap: {gap_comp:+.2f}%")
    print(f"   🎲 Tours únicos totales: {sum(d['unique_solutions'] for d in meta_comp['run_details'])}")
    print(f"   🏆 Ganador: Run {meta_comp['winner_run']}")
    
    # COMPARACIÓN
    print(f"\n{'='*70}")
    print("  📈 COMPARACIÓN")
    print(f"{'='*70}")
    
    if gap_comp < gap_orig:
        improvement = ((gap_orig - gap_comp) / abs(gap_orig)) * 100
        print(f"\n✅ Complementary GANA: {improvement:.1f}% mejor")
        winner = "Complementary"
    elif gap_comp > gap_orig:
        degradation = ((gap_comp - gap_orig) / abs(gap_orig)) * 100
        print(f"\n⚠️ Original mejor: {degradation:.1f}% diferencia")
        winner = "Original"
    else:
        print(f"\n⚖️  EMPATE")
        winner = "Tie"
    
    all_results.append({
        'name': name,
        'gap_orig': gap_orig,
        'gap_comp': gap_comp,
        'winner': winner
    })

# RESUMEN FINAL
print("\n" + "="*70)
print("  🎯 RESUMEN GLOBAL")
print("="*70)

gaps_orig = [r['gap_orig'] for r in all_results]
gaps_comp = [r['gap_comp'] for r in all_results]

print(f"\n📊 Gap promedio:")
print(f"   Original:       {np.mean(gaps_orig):.2f}%")
print(f"   Complementary:  {np.mean(gaps_comp):.2f}%")

if np.mean(gaps_comp) < np.mean(gaps_orig):
    improvement = ((np.mean(gaps_orig) - np.mean(gaps_comp)) / np.mean(gaps_orig)) * 100
    print(f"\n🏆 COMPLEMENTARY ES MEJOR: {improvement:.1f}% mejora promedio")
    print(f"\n✅ RECOMENDACIÓN: Usar Complementary Quantum como solver principal")
    print(f"   La exploración ortogonal encuentra mejores soluciones!")
else:
    diff = ((np.mean(gaps_comp) - np.mean(gaps_orig)) / np.mean(gaps_orig)) * 100
    print(f"\n📊 Original sigue siendo mejor: {diff:.1f}% diferencia")
    print(f"\n✅ RECOMENDACIÓN: Mantener Quantum Original")
    print(f"   El overhead de múltiples runs no compensa")

print("\n" + "="*70)
