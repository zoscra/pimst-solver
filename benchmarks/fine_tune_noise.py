"""
Búsqueda fina de ruido óptimo - Incrementos de 0.5%
"""
import numpy as np
import sys
sys.path.insert(0, 'src')
from pathlib import Path
import time
import hashlib
from pimst.algorithms import (
    gravity_guided_tsp,
    lin_kernighan_lite,
    two_opt_improvement,
    nearest_neighbor
)

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

def test_noise_level(coords, distances, noise_level, time_budget=15.0):
    n = len(coords)
    start_time = time.time()
    solutions = []
    unique_tours = set()
    iteration = 0
    phase1_end = start_time + time_budget * 0.7
    
    while time.time() < phase1_end:
        iteration += 1
        quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
        np.random.seed(quantum_seed)
        noise_matrix = np.random.uniform(1 - noise_level, 1 + noise_level, distances.shape)
        noisy_distances = distances * noise_matrix
        noisy_distances = np.maximum(noisy_distances, 0.1)
        strategy = np.random.randint(0, 10)
        
        if strategy < 4:
            tour = gravity_guided_tsp(coords, noisy_distances)
        elif strategy < 8:
            start_node = np.random.randint(0, n)
            tour = nearest_neighbor(coords, noisy_distances, start=start_node)
        else:
            tour = np.random.permutation(n)
        
        for _ in range(np.random.randint(5, 15)):
            mut = np.random.randint(0, 3)
            if mut == 0:
                i, j = np.random.randint(0, n, 2)
                tour[i], tour[j] = tour[j], tour[i]
            elif mut == 1:
                i, j = sorted(np.random.randint(0, n, 2))
                tour[i:j] = tour[i:j][::-1]
            else:
                shift = np.random.randint(1, n)
                tour = np.roll(tour, shift)
        
        if np.random.random() > 0.3:
            tour, _ = two_opt_improvement(tour, distances)
        
        cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
        
        if tour_hash not in unique_tours:
            solutions.append((cost, tour))
            unique_tours.add(tour_hash)
    
    if len(solutions) == 0:
        tour = nearest_neighbor(coords, distances, start=0)
        cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        solutions.append((cost, tour))
    
    solutions.sort(key=lambda x: x[0])
    improved = []
    for cost, tour in solutions[:20]:
        if time.time() - start_time > time_budget * 0.95:
            break
        tour_lk = lin_kernighan_lite(coords, distances, max_iterations=500)
        cost_lk = sum(distances[tour_lk[i]][tour_lk[(i+1)%n]] for i in range(n))
        improved.append((cost_lk, tour_lk))
    
    all_solutions = solutions + improved
    all_solutions.sort(key=lambda x: x[0])
    best_cost = all_solutions[0][0]
    uniqueness = len(unique_tours) / iteration if iteration > 0 else 0
    return best_cost, uniqueness, len(unique_tours)

instances = {'berlin52': 7542, 'st70': 675, 'kroB100': 22141}

print("="*70)
print("  🔬 BÚSQUEDA FINA DE RUIDO ÓPTIMO (0.5% pasos)")
print("="*70)

noise_levels = [i * 0.005 for i in range(10, 31)]
all_results = []

for noise in noise_levels:
    print(f"\n{'='*70}")
    print(f"  PROBANDO RUIDO: {noise*100:.1f}%")
    print(f"{'='*70}")
    gaps = []
    
    for name, optimal in instances.items():
        filename = f"benchmarks/tsplib/{name}.tsp"
        if not Path(filename).exists():
            continue
        print(f"\n{name}: ", end='', flush=True)
        coords = parse_tsplib(filename)
        n = len(coords)
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distances[i][j] = np.linalg.norm(coords[i] - coords[j])
        
        cost, uniqueness, n_unique = test_noise_level(coords, distances, noise, time_budget=15.0)
        gap = ((cost - optimal) / optimal) * 100
        gaps.append(gap)
        print(f"gap={gap:+.2f}%, unique={n_unique}, ratio={uniqueness*100:.1f}%")
    
    avg_gap = np.mean(gaps)
    print(f"\n📊 Gap promedio con {noise*100:.1f}% ruido: {avg_gap:.2f}%")
    all_results.append({'noise': noise, 'avg_gap': avg_gap, 'gaps': gaps.copy()})

all_results.sort(key=lambda x: x['avg_gap'])
best = all_results[0]

print("\n" + "="*70)
print("  🎯 RESULTADOS COMPLETOS")
print("="*70)
print("\n🏆 TOP 5 MEJORES NIVELES DE RUIDO:\n")
for i, result in enumerate(all_results[:5], 1):
    print(f"{i}. {result['noise']*100:4.1f}% ruido → Gap: {result['avg_gap']:.2f}%")
    print(f"   berlin52: {result['gaps'][0]:+.2f}%, st70: {result['gaps'][1]:+.2f}%, kroB100: {result['gaps'][2]:+.2f}%")

print(f"\n🏆 NIVEL ÓPTIMO: {best['noise']*100:.1f}% ruido")
print(f"📊 Gap promedio: {best['avg_gap']:.2f}%")
print(f"\n💡 Comparación con 15.0% (baseline): 3.40%")

if best['avg_gap'] < 3.40:
    improvement = ((3.40 - best['avg_gap']) / 3.40) * 100
    print(f"\n✅ ¡MEJORA ENCONTRADA! {improvement:.1f}% mejor")
else:
    print(f"\n📊 El 15% sigue siendo competitivo")
print("\n" + "="*70)
