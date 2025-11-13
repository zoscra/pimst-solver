"""
Benchmark en instancias grandes (300-600 ciudades)
===================================================

Objetivo: Encontrar el "crossover point" donde LKH supera a PIMST
"""

import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
import time
import json
from pimst.improved.sino.quantum_solver import QuantumSolver
from pimst.algorithms import lin_kernighan_lite


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


# Instancias grandes con óptimos conocidos
large_instances = {
    'a280': 2579,
    'pr299': 48191,
    'lin318': 42029,
    'rd400': 15281,
    'fl417': 11861,
    'pr439': 107217,
    'pcb442': 50778,
    'd493': 35002,
    'u574': 36905,
    'rat575': 6773,
}

# Presupuestos de tiempo progresivos
time_budgets = [60, 120, 180, 240]  # 1-4 minutos

quantum_solver = QuantumSolver()

print("="*80)
print("  🔬 BENCHMARK INSTANCIAS GRANDES - PIMST vs LKH")
print("="*80)
print(f"\n📊 Instancias: {len(large_instances)}")
print(f"⏱️  Presupuestos: {time_budgets}s")
print(f"🎯 Objetivo: Encontrar crossover point\n")

all_results = []

for name, optimal in sorted(large_instances.items(), key=lambda x: x[1]):
    filename = f"benchmarks/tsplib/{name}.tsp.gz"
    
    if not Path(filename).exists():
        print(f"⚠️  {name}: Archivo no encontrado, saltando...")
        continue
    
    print(f"\n{'='*80}")
    print(f"  {name.upper()} (óptimo: {optimal})")
    print(f"{'='*80}")
    
    # Leer instancia
    try:
        import gzip
        with gzip.open(filename, 'rt') as f:
            content = f.read()
        
        # Guardar temporalmente descomprimido
        temp_file = f"benchmarks/tsplib/{name}_temp.tsp"
        with open(temp_file, 'w') as f:
            f.write(content)
        
        coords = parse_tsplib(temp_file)
        Path(temp_file).unlink()
        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        continue
    
    n = len(coords)
    print(f"   Ciudades: {n}")
    
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = np.linalg.norm(coords[i] - coords[j])
    
    instance_results = {
        'name': name,
        'n': n,
        'optimal': optimal,
        'quantum': {},
        'lkh_baseline': None
    }
    
    # LKH BASELINE (60s fijo para comparación)
    print(f"\n🔷 LKH baseline (60s)...", end=' ', flush=True)
    start = time.time()
    tour_lkh = lin_kernighan_lite(coords, distances, max_iterations=2000)
    lkh_time = time.time() - start
    cost_lkh = sum(distances[tour_lkh[i]][tour_lkh[(i+1)%n]] for i in range(n))
    gap_lkh = ((cost_lkh - optimal) / optimal) * 100
    
    instance_results['lkh_baseline'] = {
        'cost': cost_lkh,
        'gap': gap_lkh,
        'time': lkh_time
    }
    print(f"Gap: {gap_lkh:+.2f}%, Tiempo: {lkh_time:.1f}s")
    
    # QUANTUM con diferentes presupuestos
    for budget in time_budgets:
        print(f"\n⚡ Quantum ({budget}s)...", end=' ', flush=True)
        
        tour_q, cost_q, meta_q = quantum_solver.solve(
            coords, distances, time_budget=budget
        )
        gap_q = ((cost_q - optimal) / optimal) * 100
        
        instance_results['quantum'][budget] = {
            'cost': cost_q,
            'gap': gap_q,
            'unique_solutions': meta_q['unique_solutions'],
            'time': meta_q['total_time']
        }
        
        # Comparación con LKH
        if gap_q < gap_lkh:
            improvement = ((gap_lkh - gap_q) / abs(gap_lkh)) * 100
            print(f"Gap: {gap_q:+.2f}%, ✅ {improvement:.1f}% mejor que LKH")
        elif gap_q > gap_lkh:
            degradation = ((gap_q - gap_lkh) / abs(gap_lkh)) * 100
            print(f"Gap: {gap_q:+.2f}%, ❌ {degradation:.1f}% peor que LKH")
        else:
            print(f"Gap: {gap_q:+.2f}%, ⚖️  igual que LKH")
    
    all_results.append(instance_results)
    
    # Mini resumen
    best_quantum = min(instance_results['quantum'].items(), key=lambda x: x[1]['gap'])
    print(f"\n   Mejor Quantum: {best_quantum[0]}s → {best_quantum[1]['gap']:+.2f}%")
    print(f"   LKH baseline: {gap_lkh:+.2f}%")
    
    if best_quantum[1]['gap'] < gap_lkh:
        print(f"   🏆 Quantum gana en esta instancia")
    else:
        print(f"   ⚠️  LKH gana en esta instancia")

# ANÁLISIS COMPLETO
print("\n" + "="*80)
print("  📊 ANÁLISIS CROSSOVER POINT")
print("="*80)

# Agrupar por tamaño
size_ranges = {
    '280-350': lambda n: 280 <= n < 350,
    '350-450': lambda n: 350 <= n < 450,
    '450-600': lambda n: 450 <= n <= 600,
}

for size_range, filter_fn in size_ranges.items():
    category_results = [r for r in all_results if filter_fn(r['n'])]
    if not category_results:
        continue
    
    print(f"\n🔷 Rango {size_range} ciudades ({len(category_results)} instancias)")
    print(f"{'─'*80}")
    
    for budget in time_budgets:
        gaps_quantum = [r['quantum'][budget]['gap'] for r in category_results if budget in r['quantum']]
        if not gaps_quantum:
            continue
        
        gaps_lkh = [r['lkh_baseline']['gap'] for r in category_results]
        
        avg_gap_q = np.mean(gaps_quantum)
        avg_gap_lkh = np.mean(gaps_lkh)
        
        if avg_gap_q < avg_gap_lkh:
            improvement = ((avg_gap_lkh - avg_gap_q) / abs(avg_gap_lkh)) * 100
            verdict = f"✅ Quantum {improvement:+.1f}% mejor"
        else:
            degradation = ((avg_gap_q - avg_gap_lkh) / abs(avg_gap_lkh)) * 100
            verdict = f"❌ LKH {degradation:+.1f}% mejor"
        
        print(f"  {budget:3d}s: Quantum {avg_gap_q:6.2f}% | LKH {avg_gap_lkh:6.2f}% | {verdict}")

# ANÁLISIS POR INSTANCIA
print(f"\n{'='*80}")
print("  🎯 GANADOR POR INSTANCIA")
print(f"{'='*80}\n")

quantum_wins = 0
lkh_wins = 0

for result in all_results:
    best_q = min(result['quantum'].values(), key=lambda x: x['gap'])
    gap_lkh = result['lkh_baseline']['gap']
    
    if best_q['gap'] < gap_lkh:
        winner = "Quantum"
        quantum_wins += 1
        symbol = "✅"
    else:
        winner = "LKH"
        lkh_wins += 1
        symbol = "❌"
    
    print(f"{symbol} {result['name']:<10} (n={result['n']:3d}): "
          f"Quantum {best_q['gap']:5.2f}% vs LKH {gap_lkh:5.2f}% → {winner}")

print(f"\n{'='*80}")
print(f"  📈 RESUMEN GLOBAL")
print(f"{'='*80}\n")

print(f"Instancias probadas: {len(all_results)}")
print(f"Quantum gana: {quantum_wins} ({quantum_wins/len(all_results)*100:.1f}%)")
print(f"LKH gana: {lkh_wins} ({lkh_wins/len(all_results)*100:.1f}%)")

if quantum_wins > lkh_wins:
    print(f"\n🏆 QUANTUM DOMINA incluso en instancias grandes!")
elif quantum_wins == lkh_wins:
    print(f"\n⚖️  EMPATE - Competitivos en instancias grandes")
else:
    print(f"\n⚠️  LKH mejor en instancias grandes (crossover ~{np.mean([r['n'] for r in all_results]):.0f} ciudades)")

# Guardar resultados
output_file = 'benchmarks/large_instances_results.json'
with open(output_file, 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\n💾 Resultados guardados: {output_file}")
print("="*80)
