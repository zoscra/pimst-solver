"""
Test de velocidad y calidad de todos los algoritmos PIMST
"""
import numpy as np
import time
import pimst.algorithms as alg

# Crear instancia de test
np.random.seed(42)
n = 100
coords = np.random.rand(n, 2) * 1000
distances = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        distances[i][j] = np.linalg.norm(coords[i] - coords[j])

print("="*70)
print(f"  TEST: n={n} ciudades")
print("="*70)

# Óptimo conocido (aproximado con LK)
print("\n🎯 Calculando referencia con multi_start (50 runs)...")
ref_start = time.time()
ref_tour = alg.multi_start_solver(coords, distances, n_starts=50)
ref_cost = sum(distances[ref_tour[i]][ref_tour[(i+1)%n]] for i in range(n))
ref_time = time.time() - ref_start
print(f"   Referencia: {ref_cost:.2f} en {ref_time:.2f}s")

print("\n" + "="*70)
print("  ALGORITMOS DISPONIBLES")
print("="*70)

# Lista de algoritmos a probar
algorithms = [
    ('gravity_guided_tsp', lambda: alg.gravity_guided_tsp(coords, distances)),
    ('lin_kernighan_lite', lambda: alg.lin_kernighan_lite(coords, distances)),
    ('multi_start_3', lambda: alg.multi_start_solver(coords, distances, n_starts=3)),
    ('multi_start_5', lambda: alg.multi_start_solver(coords, distances, n_starts=5)),
    ('multi_start_10', lambda: alg.multi_start_solver(coords, distances, n_starts=10)),
]

# Intentar otros algoritmos que puedan existir
potential = [
    'nearest_neighbor',
    'greedy_tsp',
    'simulated_annealing',
    'genetic_algorithm',
    'ant_colony',
    'particle_swarm',
]

for name in potential:
    if hasattr(alg, name):
        func = getattr(alg, name)
        algorithms.append((name, lambda f=func: f(coords, distances)))

results = []

for name, algo in algorithms:
    print(f"\n🔬 {name}:")
    try:
        # Ejecutar 3 veces y tomar promedio
        times = []
        costs = []
        
        for run in range(3):
            start = time.time()
            tour = algo()
            elapsed = time.time() - start
            
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            
            times.append(elapsed)
            costs.append(cost)
        
        avg_time = np.mean(times)
        avg_cost = np.mean(costs)
        gap = ((avg_cost - ref_cost) / ref_cost) * 100
        speedup = ref_time / avg_time
        
        print(f"   Costo: {avg_cost:.2f}")
        print(f"   Gap: {gap:+.2f}%")
        print(f"   Tiempo: {avg_time:.4f}s")
        print(f"   Speedup: {speedup:.1f}x")
        
        results.append({
            'name': name,
            'cost': avg_cost,
            'gap': gap,
            'time': avg_time,
            'speedup': speedup
        })
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Resumen
print("\n" + "="*70)
print("  📊 RANKING POR CALIDAD")
print("="*70)

results.sort(key=lambda x: x['gap'])
for i, r in enumerate(results[:5], 1):
    print(f"{i}. {r['name']}: gap={r['gap']:+.2f}%, time={r['time']:.4f}s, speedup={r['speedup']:.1f}x")

print("\n" + "="*70)
print("  ⚡ RANKING POR VELOCIDAD")
print("="*70)

results.sort(key=lambda x: x['time'])
for i, r in enumerate(results[:5], 1):
    print(f"{i}. {r['name']}: time={r['time']:.4f}s, gap={r['gap']:+.2f}%, speedup={r['speedup']:.1f}x")

print("\n" + "="*70)
print("  🎯 MEJOR BALANCE (gap < 5% y speedup > 5x)")
print("="*70)

balanced = [r for r in results if r['gap'] < 5 and r['speedup'] > 5]
balanced.sort(key=lambda x: x['gap'])
for r in balanced:
    print(f"✅ {r['name']}: gap={r['gap']:+.2f}%, speedup={r['speedup']:.1f}x")

