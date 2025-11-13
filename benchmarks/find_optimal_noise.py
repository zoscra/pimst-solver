"""
Búsqueda de ruido óptimo - Incrementos de 1%
=============================================

Probaremos diferentes niveles de ruido para encontrar el sweet spot.
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


def test_noise_level(coords, distances, noise_level, time_budget=10.0):
    """
    Probar un nivel de ruido específico.
    """
    n = len(coords)
    start_time = time.time()
    
    solutions = []
    unique_tours = set()
    iteration = 0
    
    # Exploración (70% tiempo)
    phase1_end = start_time + time_budget * 0.7
    
    while time.time() < phase1_end:
        iteration += 1
        
        # Semilla única
        quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
        np.random.seed(quantum_seed)
        
        # Ruido en distancias
        noise_matrix = np.random.uniform(1 - noise_level, 1 + noise_level, distances.shape)
        noisy_distances = distances * noise_matrix
        noisy_distances = np.maximum(noisy_distances, 0.1)
        
        # Estrategia aleatoria
        strategy = np.random.randint(0, 30)
        
        if strategy < 8:
            # Gravity
            if np.random.random() > 0.5:
                coord_noise = np.random.normal(0, coords.std() * noise_level, coords.shape)
                noisy_coords = coords + coord_noise
                tour = gravity_guided_tsp(noisy_coords, noisy_distances)
            else:
                tour = gravity_guided_tsp(coords, noisy_distances)
        elif strategy < 16:
            # NN estocástico
            start = np.random.randint(0, n)
            tour = nearest_neighbor(coords, noisy_distances, start=start)
        else:
            # Random + mejora
            tour = np.random.permutation(n)
        
        # Mutaciones
        n_mutations = np.random.randint(5, 15)
        for _ in range(n_mutations):
            mut = np.random.randint(0, 5)
            if mut == 0:
                i, j = np.random.randint(0, n, 2)
                tour[i], tour[j] = tour[j], tour[i]
            elif mut == 1:
                i, j = sorted(np.random.randint(0, n, 2))
                tour[i:j] = tour[i:j][::-1]
            elif mut == 2:
                i, j = sorted(np.random.randint(0, n, 2))
                segment = tour[i:j].copy()
                np.random.shuffle(segment)
                tour[i:j] = segment
            elif mut == 3:
                shift = np.random.randint(1, n)
                tour = np.roll(tour, shift)
            else:
                i = np.random.randint(0, n)
                j = np.random.randint(0, n)
                node = tour[i]
                tour = np.delete(tour, i)
                tour = np.insert(tour, j, node)
        
        # Mejora local
        if np.random.random() > 0.3:
            tour, _ = two_opt_improvement(tour, distances)
        
        # Calcular costo
        cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        
        # Hash para unicidad
        tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
        
        if tour_hash not in unique_tours:
            solutions.append((cost, tour))
            unique_tours.add(tour_hash)
    
    if len(solutions) == 0:
        tour = nearest_neighbor(coords, distances, start=0)
        cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        solutions.append((cost, tour))
    
    # Refinamiento (30% tiempo)
    solutions.sort(key=lambda x: x[0])
    top_solutions = solutions[:20]
    
    improved = []
    for cost, tour in top_solutions:
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


# Instancias de prueba
instances = {
    'berlin52': 7542,
    'st70': 675,
    'kroB100': 22141,
}

print("="*70)
print("  🔬 BÚSQUEDA DE RUIDO ÓPTIMO")
print("="*70)

# Probar niveles de ruido de 16% a 25%
noise_levels = [0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25]

best_overall_gap = float('inf')
best_noise = 0.15

for noise in noise_levels:
    print(f"\n{'='*70}")
    print(f"  PROBANDO RUIDO: {noise*100:.0f}%")
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
        
        cost, uniqueness, n_unique = test_noise_level(coords, distances, noise, time_budget=10.0)
        gap = ((cost - optimal) / optimal) * 100
        gaps.append(gap)
        
        print(f"gap={gap:+.2f}%, unique={n_unique}, ratio={uniqueness*100:.1f}%")
    
    avg_gap = np.mean(gaps)
    print(f"\n📊 Gap promedio con {noise*100:.0f}% ruido: {avg_gap:.2f}%")
    
    if avg_gap < best_overall_gap:
        best_overall_gap = avg_gap
        best_noise = noise
        print(f"   🏆 ¡NUEVO MEJOR RUIDO!")

print("\n" + "="*70)
print("  🎯 RESULTADO FINAL")
print("="*70)
print(f"\n🏆 Mejor nivel de ruido: {best_noise*100:.0f}%")
print(f"📊 Gap promedio: {best_overall_gap:.2f}%")
print(f"\n💡 Comparación con 15% (baseline): 3.40%")

if best_overall_gap < 3.40:
    improvement = ((3.40 - best_overall_gap) / 3.40) * 100
    print(f"✅ Mejora: {improvement:.1f}% mejor que baseline!")
else:
    print(f"⚠️ No superó el baseline de 15% ruido")

print("\n" + "="*70)
