"""
Benchmark Completo TSPLIB - PIMST vs LKH
=========================================

Instancias de diferentes tamaños con múltiples presupuestos de tiempo.
"""

import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
import time
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


# Instancias TSPLIB con óptimos conocidos
instances = {
    # Pequeñas (< 100)
    'berlin52': 7542,
    'st70': 675,
    'eil76': 538,
    'pr76': 108159,
    'rat99': 1211,
    
    # Medianas (100-200)
    'kroA100': 21282,
    'kroB100': 22141,
    'kroC100': 20749,
    'kroD100': 21294,
    'kroE100': 22068,
    'rd100': 7910,
    'eil101': 629,
    'lin105': 14379,
    'pr107': 44303,
    'pr124': 59030,
    'bier127': 118282,
    'ch130': 6110,
    'pr136': 96772,
    'pr144': 58537,
    'ch150': 6528,
    'kroA150': 26524,
    'kroB150': 26130,
    'pr152': 73682,
    'u159': 42080,
    'rat195': 2323,
    'd198': 15780,
    
    # Grandes (200-300)
    'kroA200': 29368,
    'kroB200': 29437,
    'ts225': 126643,
    'tsp225': 3916,
    'pr226': 80369,
    'gil262': 2378,
    'pr264': 49135,
    'a280': 2579,
    'pr299': 48191,
}

# Presupuestos de tiempo a probar
time_budgets = [30, 60, 90, 120]  # segundos

quantum_solver = QuantumSolver()

print("="*80)
print("  🔬 BENCHMARK COMPLETO TSPLIB - PIMST vs LKH")
print("="*80)
print(f"\n📊 Instancias a probar: {len(instances)}")
print(f"⏱️  Presupuestos de tiempo: {time_budgets}s")
print(f"🎯 Algoritmos: Quantum Solver + LKH baseline\n")

all_results = []

for name, optimal in sorted(instances.items(), key=lambda x: x[1]):  # Ordenar por tamaño
    filename = f"benchmarks/tsplib/{name}.tsp"
    if not Path(filename).exists():
        print(f"⚠️  {name}: Archivo no encontrado, saltando...")
        continue
    
    print(f"\n{'='*80}")
    print(f"  {name.upper()} (n={name[-3:]}, óptimo: {optimal})")
    print(f"{'='*80}")
    
    # Leer instancia
    coords = parse_tsplib(filename)
    n = len(coords)
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
    
    # LKH BASELINE (30s como referencia)
    print(f"\n🔷 LKH baseline (30s)...", end=' ', flush=True)
    start = time.time()
    tour_lkh = lin_kernighan_lite(coords, distances, max_iterations=1000)
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
        improvement_vs_lkh = ((gap_lkh - gap_q) / abs(gap_lkh)) * 100 if gap_lkh != 0 else 0
        
        print(f"Gap: {gap_q:+.2f}%, ", end='')
        if gap_q < gap_lkh:
            print(f"✅ {improvement_vs_lkh:.1f}% mejor que LKH", end='')
        elif gap_q > gap_lkh:
            print(f"❌ {-improvement_vs_lkh:.1f}% peor que LKH", end='')
        else:
            print(f"⚖️  igual que LKH", end='')
        print(f", {meta_q['unique_solutions']} sol.")
    
    all_results.append(instance_results)
    
    # Mini resumen de esta instancia
    best_quantum = min(instance_results['quantum'].items(), key=lambda x: x[1]['gap'])
    print(f"\n   Mejor Quantum: {best_quantum[0]}s → {best_quantum[1]['gap']:+.2f}%")
    print(f"   LKH baseline: {gap_lkh:+.2f}%")

# RESUMEN COMPLETO
print("\n" + "="*80)
print("  📊 RESUMEN COMPLETO DEL BENCHMARK")
print("="*80)

# Tabla por tamaño
size_categories = {
    'Pequeñas (< 100)': lambda n: n < 100,
    'Medianas (100-200)': lambda n: 100 <= n < 200,
    'Grandes (200-300)': lambda n: 200 <= n < 300,
}

for category, filter_fn in size_categories.items():
    category_results = [r for r in all_results if filter_fn(r['n'])]
    if not category_results:
        continue
    
    print(f"\n🔷 {category} ({len(category_results)} instancias)")
    print(f"{'─'*80}")
    
    for budget in time_budgets:
        gaps_quantum = [r['quantum'][budget]['gap'] for r in category_results]
        avg_gap_q = np.mean(gaps_quantum)
        
        gaps_lkh = [r['lkh_baseline']['gap'] for r in category_results]
        avg_gap_lkh = np.mean(gaps_lkh)
        
        improvement = ((avg_gap_lkh - avg_gap_q) / abs(avg_gap_lkh)) * 100 if avg_gap_lkh != 0 else 0
        
        print(f"  {budget:3d}s: Quantum {avg_gap_q:6.2f}% | LKH {avg_gap_lkh:6.2f}% | ", end='')
        if improvement > 0:
            print(f"✅ {improvement:+.1f}%")
        else:
            print(f"❌ {improvement:+.1f}%")

# ANÁLISIS DE ESCALABILIDAD
print(f"\n{'='*80}")
print("  📈 ANÁLISIS DE ESCALABILIDAD")
print(f"{'='*80}")

for budget in time_budgets:
    print(f"\n⏱️  Con {budget} segundos:")
    
    # Agrupar por tamaño
    small = [r for r in all_results if r['n'] < 100]
    medium = [r for r in all_results if 100 <= r['n'] < 200]
    large = [r for r in all_results if 200 <= r['n'] < 300]
    
    for group, label in [(small, '< 100'), (medium, '100-200'), (large, '200-300')]:
        if group:
            gaps = [r['quantum'][budget]['gap'] for r in group]
            avg = np.mean(gaps)
            best = np.min(gaps)
            worst = np.max(gaps)
            print(f"   {label:8s} ciudades: promedio {avg:5.2f}% (mejor {best:.2f}%, peor {worst:.2f}%)")

# MEJORES RESULTADOS
print(f"\n{'='*80}")
print("  🏆 TOP 10 MEJORES RESULTADOS")
print(f"{'='*80}")

all_quantum_results = []
for r in all_results:
    for budget, data in r['quantum'].items():
        all_quantum_results.append({
            'name': r['name'],
            'n': r['n'],
            'budget': budget,
            'gap': data['gap'],
            'optimal': r['optimal']
        })

all_quantum_results.sort(key=lambda x: x['gap'])

print(f"\n{'Instancia':<15} {'n':>4} {'Tiempo':>6} {'Gap':>8} {'vs LKH'}")
print(f"{'─'*60}")

for i, res in enumerate(all_quantum_results[:10], 1):
    # Encontrar resultado LKH correspondiente
    instance_data = next(r for r in all_results if r['name'] == res['name'])
    lkh_gap = instance_data['lkh_baseline']['gap']
    
    improvement = ((lkh_gap - res['gap']) / abs(lkh_gap)) * 100 if lkh_gap != 0 else 0
    
    print(f"{i:2d}. {res['name']:<12} {res['n']:4d} {res['budget']:4d}s {res['gap']:+7.2f}% ", end='')
    if improvement > 0:
        print(f"✅ {improvement:+.1f}%")
    else:
        print(f"❌ {improvement:+.1f}%")

# EXPORTAR RESULTADOS
print(f"\n{'='*80}")
print("  💾 Guardando resultados...")

import json
with open('benchmarks/tsplib_comprehensive_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"  ✅ Resultados guardados en: benchmarks/tsplib_comprehensive_results.json")
print(f"{'='*80}")

print(f"\n🎯 CONCLUSIÓN:")
print(f"   Total instancias probadas: {len(all_results)}")
print(f"   Presupuestos de tiempo: {time_budgets}")
print(f"   Algoritmo ganador: [Análisis en tabla superior]")
print(f"\n{'='*80}")
