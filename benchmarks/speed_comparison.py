"""
Benchmark de Velocidad: PIMST Complementary vs LKH
===================================================

Pregunta: ¿Cuánto tiempo toma cada solver para alcanzar X% de calidad?
"""

import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
import time
from pimst.improved.sino.complementary_quantum import ComplementaryQuantumSolver
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

instances = {
    'berlin52': 7542,
    'st70': 675,
    'kroB100': 22141,
    'pr107': 44303,
    'pr124': 59030,
    'kroA150': 26524,
    'kroB150': 26130
}

print("="*80)
print("  ⚡ BENCHMARK DE VELOCIDAD: Complementary PIMST vs LKH")
print("="*80)
print("\nObjetivo: ¿Cuánto tiempo para alcanzar gaps específicos?\n")

all_results = []

for name, optimal in instances.items():
    filename = f"benchmarks/tsplib/{name}.tsp"
    if not Path(filename).exists():
        print(f"⚠️  {name} no encontrado, saltando...")
        continue
    
    print(f"\n{'='*80}")
    print(f"  {name.upper()} (óptimo: {optimal}, n={name})")
    print(f"{'='*80}")
    
    coords = parse_tsplib(filename)
    n = len(coords)
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = np.linalg.norm(coords[i] - coords[j])
    
    # ═══════════════════════════════════════════════════════════
    # COMPLEMENTARY PIMST - Progresivo
    # ═══════════════════════════════════════════════════════════
    print(f"\n🚀 Complementary PIMST:")
    
    pimst_results = {}
    solver = ComplementaryQuantumSolver()
    
    for budget in [10, 20, 30, 60]:
        start = time.time()
        tour, cost, meta = solver.solve(coords, distances, time_budget=budget, n_runs=3)
        actual_time = time.time() - start
        gap = ((cost - optimal) / optimal) * 100
        
        pimst_results[budget] = {
            'time': actual_time,
            'gap': gap,
            'cost': cost
        }
        
        print(f"   {budget:2d}s → Gap: {gap:5.2f}% (tiempo real: {actual_time:.1f}s)")
    
    # ═══════════════════════════════════════════════════════════
    # LKH - Progresivo (iteraciones crecientes)
    # ═══════════════════════════════════════════════════════════
    print(f"\n🔷 LKH (Lin-Kernighan):")
    
    lkh_results = {}
    
    # Diferentes presupuestos de iteraciones para LKH
    iteration_budgets = [500, 1000, 2000, 5000]
    
    for max_iter in iteration_budgets:
        start = time.time()
        tour = lin_kernighan_lite(coords, distances, max_iterations=max_iter)
        actual_time = time.time() - start
        cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        gap = ((cost - optimal) / optimal) * 100
        
        lkh_results[max_iter] = {
            'time': actual_time,
            'gap': gap,
            'cost': cost
        }
        
        print(f"   {max_iter:4d} iter → Gap: {gap:5.2f}% (tiempo: {actual_time:.1f}s)")
    
    # ═══════════════════════════════════════════════════════════
    # ANÁLISIS: ¿Quién es más rápido para cada nivel de calidad?
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'─'*80}")
    print("  ⚡ ANÁLISIS DE VELOCIDAD")
    print(f"{'─'*80}\n")
    
    # Encontrar mejor resultado de cada uno
    best_pimst = min(pimst_results.values(), key=lambda x: x['gap'])
    best_lkh = min(lkh_results.values(), key=lambda x: x['gap'])
    
    print(f"Mejor PIMST: {best_pimst['gap']:.2f}% en {best_pimst['time']:.1f}s")
    print(f"Mejor LKH:   {best_lkh['gap']:.2f}% en {best_lkh['time']:.1f}s")
    
    # Comparar para alcanzar gap similar al mejor de LKH
    target_gap = best_lkh['gap'] + 0.5  # Tolerancia de 0.5%
    
    pimst_to_match = None
    for budget, result in pimst_results.items():
        if result['gap'] <= target_gap:
            pimst_to_match = result
            break
    
    if pimst_to_match:
        speedup = best_lkh['time'] / pimst_to_match['time']
        print(f"\n🎯 Para alcanzar ~{target_gap:.1f}% gap:")
        print(f"   PIMST: {pimst_to_match['time']:.1f}s")
        print(f"   LKH:   {best_lkh['time']:.1f}s")
        print(f"   ⚡ PIMST es {speedup:.1f}x MÁS RÁPIDO")
    
    # Comparar a mismo tiempo (~30s)
    pimst_30s = pimst_results.get(30, pimst_results[max(pimst_results.keys())])
    
    # LKH más cercano a 30s
    lkh_30s = min(lkh_results.values(), key=lambda x: abs(x['time'] - 30))
    
    print(f"\n🕐 A ~30 segundos:")
    print(f"   PIMST: {pimst_30s['gap']:.2f}% gap")
    print(f"   LKH:   {lkh_30s['gap']:.2f}% gap")
    
    if pimst_30s['gap'] < lkh_30s['gap']:
        improvement = ((lkh_30s['gap'] - pimst_30s['gap']) / lkh_30s['gap']) * 100
        print(f"   ✅ PIMST {improvement:.1f}% MEJOR en mismo tiempo")
    else:
        degradation = ((pimst_30s['gap'] - lkh_30s['gap']) / pimst_30s['gap']) * 100
        print(f"   ⚠️ LKH {degradation:.1f}% mejor en mismo tiempo")
    
    all_results.append({
        'name': name,
        'n': n,
        'optimal': optimal,
        'pimst': pimst_results,
        'lkh': lkh_results,
        'best_pimst': best_pimst,
        'best_lkh': best_lkh
    })

# ═══════════════════════════════════════════════════════════
# RESUMEN GLOBAL
# ═══════════════════════════════════════════════════════════
print(f"\n{'='*80}")
print("  📊 RESUMEN GLOBAL DE VELOCIDAD")
print(f"{'='*80}\n")

print("Comparación a ~30 segundos:\n")

pimst_wins = 0
lkh_wins = 0
ties = 0

for result in all_results:
    name = result['name']
    
    # PIMST a 30s
    pimst_30 = result['pimst'].get(30)
    if not pimst_30:
        continue
    
    # LKH más cercano a 30s
    lkh_near_30 = min(result['lkh'].values(), key=lambda x: abs(x['time'] - 30))
    
    pimst_gap = pimst_30['gap']
    lkh_gap = lkh_near_30['gap']
    
    if abs(pimst_gap - lkh_gap) < 0.1:
        verdict = "⚖️  Empate"
        ties += 1
    elif pimst_gap < lkh_gap:
        improvement = ((lkh_gap - pimst_gap) / lkh_gap) * 100
        verdict = f"✅ PIMST {improvement:.0f}% mejor"
        pimst_wins += 1
    else:
        degradation = ((pimst_gap - lkh_gap) / pimst_gap) * 100
        verdict = f"❌ LKH {degradation:.0f}% mejor"
        lkh_wins += 1
    
    print(f"{name:12s} → PIMST: {pimst_gap:5.2f}% | LKH: {lkh_gap:5.2f}% | {verdict}")

print(f"\n{'─'*80}")
print(f"Instancias probadas: {len(all_results)}")
print(f"PIMST gana: {pimst_wins} ({pimst_wins/len(all_results)*100:.0f}%)")
print(f"LKH gana: {lkh_wins} ({lkh_wins/len(all_results)*100:.0f}%)")
print(f"Empates: {ties} ({ties/len(all_results)*100:.0f}%)")

if pimst_wins > lkh_wins:
    print(f"\n🏆 PIMST ES MÁS RÁPIDO Y MEJOR")
else:
    print(f"\n⚖️  Competitivos en velocidad")

# Análisis de speedup promedio
print(f"\n{'='*80}")
print("  ⚡ ANÁLISIS DE SPEEDUP")
print(f"{'='*80}\n")

speedups = []
for result in all_results:
    best_pimst = result['best_pimst']
    best_lkh = result['best_lkh']
    
    # Encontrar tiempo PIMST para alcanzar calidad de LKH
    target_gap = best_lkh['gap']
    
    for budget, pimst_result in result['pimst'].items():
        if pimst_result['gap'] <= target_gap:
            speedup = best_lkh['time'] / pimst_result['time']
            speedups.append(speedup)
            print(f"{result['name']:12s}: PIMST {speedup:.1f}x más rápido para alcanzar {target_gap:.2f}%")
            break

if speedups:
    avg_speedup = np.mean(speedups)
    print(f"\n⚡ SPEEDUP PROMEDIO: {avg_speedup:.1f}x")
    print(f"   PIMST alcanza misma calidad que LKH en 1/{avg_speedup:.1f} del tiempo")

print("\n" + "="*80)
