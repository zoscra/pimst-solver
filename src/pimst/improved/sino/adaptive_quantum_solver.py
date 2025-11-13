"""
Adaptive Quantum Solver - Balance perfecto entre unicidad y calidad
====================================================================

Filosofía:
"Ruido justo - no demasiado, no muy poco"

Estrategia adaptativa:
- Empezar con poco ruido (5%)
- Si detectamos repeticiones → aumentar ruido
- Si calidad es mala → reducir ruido
- Encontrar el punto dulce dinámicamente
"""

import numpy as np
import time
import hashlib
from typing import Tuple, List
from pimst.algorithms import (
    gravity_guided_tsp,
    lin_kernighan_lite,
    two_opt_improvement,
    three_opt_improvement,
    nearest_neighbor
)


class AdaptiveQuantumSolver:
    """
    Ruido adaptativo para maximizar unicidad sin sacrificar calidad.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Exploración cuántica con ruido adaptativo.
        """
        n = len(coords)
        start_time = time.time()
        
        print(f"   🎯 ADAPTIVE QUANTUM MODE: Balance dinámico")
        print(f"   ⚖️  'Ruido óptimo = máxima exploración sin romper calidad'")
        
        solutions = []
        unique_tours = set()
        iteration = 0
        
        # RUIDO ADAPTATIVO
        noise_level = 0.05  # Empezar con 5%
        min_noise = 0.02
        max_noise = 0.20
        
        repetitions_detected = 0
        last_10_costs = []
        
        # FASE 1: EXPLORACIÓN ADAPTATIVA (70% tiempo)
        phase1_end = start_time + time_budget * 0.7
        
        print(f"   Fase 1: Explorando con ruido adaptativo...")
        
        while time.time() < phase1_end:
            iteration += 1
            
            # Semilla única
            quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
            np.random.seed(quantum_seed)
            
            # Ruido adaptativo en distancias
            noise_matrix = np.random.uniform(1 - noise_level, 1 + noise_level, distances.shape)
            noisy_distances = distances * noise_matrix
            noisy_distances = np.maximum(noisy_distances, 0.1)
            
            # Estrategia aleatoria (30 variantes)
            strategy = np.random.randint(0, 30)
            
            if strategy < 8:
                # Gravity variants
                if np.random.random() > 0.5:
                    coord_noise = np.random.normal(0, coords.std() * noise_level, coords.shape)
                    noisy_coords = coords + coord_noise
                    tour = gravity_guided_tsp(noisy_coords, noisy_distances)
                else:
                    tour = gravity_guided_tsp(coords, noisy_distances)
                strategy_name = "adaptive_gravity"
                
            elif strategy < 16:
                # NN variants
                start = np.random.randint(0, n)
                tour = self._adaptive_nn(coords, noisy_distances, start, noise_level)
                strategy_name = "adaptive_nn"
                
            elif strategy < 20:
                # Random + mejora
                tour = np.random.permutation(n)
                tour, _ = two_opt_improvement(tour, noisy_distances)
                strategy_name = "random_2opt"
                
            elif strategy < 24:
                # Greedy probabilístico
                tour = self._prob_greedy(coords, noisy_distances, noise_level)
                strategy_name = "prob_greedy"
                
            elif strategy < 27:
                # Inserción
                tour = self._adaptive_insertion(n, noisy_distances, noise_level)
                strategy_name = "adaptive_insertion"
                
            else:
                # Construcciones geométricas
                if np.random.random() > 0.5:
                    tour = self._spiral(coords, noise_level)
                else:
                    tour = self._zigzag(coords, noise_level)
                strategy_name = "geometric"
            
            # Mutaciones (cantidad según ruido)
            n_mutations = int(5 + noise_level * 50)  # 5-15 mutaciones
            
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
            
            # Mejora local (probabilidad según ruido)
            if np.random.random() > noise_level:
                tour, _ = two_opt_improvement(tour, distances)
            
            # Calcular costo REAL
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            
            # Hash para unicidad
            tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
            
            # Detectar repeticiones
            if tour_hash in unique_tours:
                repetitions_detected += 1
            else:
                solutions.append((cost, tour, f"{strategy_name}_a{iteration}"))
                unique_tours.add(tour_hash)
                last_10_costs.append(cost)
                if len(last_10_costs) > 10:
                    last_10_costs.pop(0)
            
            # ADAPTAR RUIDO cada 50 iteraciones
            if iteration % 50 == 0:
                repetition_rate = repetitions_detected / 50
                
                # Calcular calidad relativa
                if len(last_10_costs) >= 5:
                    # Referencia simple: nearest neighbor desde 0
                    ref_tour = nearest_neighbor(coords, distances, start=0)
                    ref_cost = sum(distances[ref_tour[i]][ref_tour[(i+1)%n]] for i in range(n))
                    avg_cost = np.mean(last_10_costs)
                    quality_ratio = avg_cost / ref_cost
                else:
                    quality_ratio = 1.0
                
                # REGLAS DE ADAPTACIÓN
                if repetition_rate > 0.2:  # >20% repeticiones
                    # Aumentar ruido
                    noise_level = min(noise_level * 1.2, max_noise)
                    adjustment = "↑ Más ruido"
                elif quality_ratio > 1.5:  # Calidad muy mala
                    # Reducir ruido
                    noise_level = max(noise_level * 0.8, min_noise)
                    adjustment = "↓ Menos ruido"
                elif repetition_rate < 0.05 and quality_ratio < 1.2:
                    # Perfecto balance, reducir un poco para calidad
                    noise_level = max(noise_level * 0.95, min_noise)
                    adjustment = "→ Refinando"
                else:
                    adjustment = "→ Mantener"
                
                if solutions:
                    best = min(solutions, key=lambda x: x[0])[0]
                    print(f"      → {iteration} iter, {len(solutions)} únicas ({len(solutions)/iteration*100:.1f}%), "
                          f"mejor: {best:.2f}, ruido: {noise_level:.3f} {adjustment}")
                
                repetitions_detected = 0
        
        print(f"   ✅ {len(solutions)} soluciones únicas")
        print(f"   🎲 Unicidad: {len(solutions)/iteration*100:.1f}%")
        print(f"   ⚖️  Ruido final: {noise_level:.3f}")
        
        if len(solutions) == 0:
            tour = nearest_neighbor(coords, distances, start=0)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, tour, "fallback"))
        
        # FASE 2: REFINAMIENTO (30% tiempo)
        print(f"   Fase 2: Refinamiento inteligente...")
        
        solutions.sort(key=lambda x: x[0])
        top_solutions = solutions[:20]
        
        improved = []
        for i, (cost, tour, name) in enumerate(top_solutions):
            if time.time() - start_time > time_budget * 0.95:
                break
            
            # Refinamiento con LK
            tour_lk = lin_kernighan_lite(coords, distances, max_iterations=500)
            cost_lk = sum(distances[tour_lk[j]][tour_lk[(j+1)%n]] for j in range(n))
            improved.append((cost_lk, tour_lk, f"lk_{name}"))
        
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])
        
        best_cost, best_tour, best_name = all_solutions[0]
        
        total_time = time.time() - start_time
        
        print(f"   ✅ FINAL: {best_cost:.2f} en {total_time:.2f}s")
        
        metadata = {
            'strategies_used': ['adaptive_quantum'],
            'total_solutions': len(all_solutions),
            'unique_solutions': len(unique_tours),
            'uniqueness_ratio': len(solutions) / iteration if iteration > 0 else 0,
            'final_noise_level': noise_level,
            'best_strategy': best_name,
            'total_time': total_time
        }
        
        return best_tour.tolist(), best_cost, metadata
    
    def _adaptive_nn(self, coords, distances, start, noise):
        """NN con decisiones probabilísticas adaptativas."""
        n = len(coords)
        tour = [start]
        unvisited = set(range(n)) - {start}
        
        current = start
        while unvisited:
            dists = np.array([distances[current][j] for j in unvisited])
            
            # Temperatura proporcional al ruido
            temp = 0.5 + noise * 2.0
            
            probs = np.exp(-dists / (temp * dists.mean() + 1e-10))
            probs = probs / probs.sum()
            
            next_city = np.random.choice(list(unvisited), p=probs)
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        
        return np.array(tour)
    
    def _prob_greedy(self, coords, distances, noise):
        """Greedy probabilístico."""
        n = len(coords)
        start = np.random.randint(0, n)
        tour = [start]
        unvisited = set(range(n)) - {start}
        
        current = start
        while unvisited:
            dists = [(distances[current][j], j) for j in unvisited]
            dists.sort()
            
            # Top-k según ruido
            k = max(2, min(int(5 + noise * 20), len(dists)))
            candidates = [j for _, j in dists[:k]]
            
            next_city = np.random.choice(candidates)
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        
        return np.array(tour)
    
    def _adaptive_insertion(self, n, distances, noise):
        """Inserción con ruido adaptativo."""
        tour = list(np.random.choice(n, 3, replace=False))
        remaining = set(range(n)) - set(tour)
        
        while remaining:
            node = np.random.choice(list(remaining))
            
            best_pos = 0
            best_cost = float('inf')
            
            for i in range(len(tour)):
                cost = (distances[tour[i]][node] +
                       distances[node][tour[(i+1)%len(tour)]] -
                       distances[tour[i]][tour[(i+1)%len(tour)]])
                
                # Ruido en decisión
                noisy_cost = cost * np.random.uniform(1 - noise, 1 + noise)
                
                if noisy_cost < best_cost:
                    best_cost = noisy_cost
                    best_pos = i + 1
            
            tour.insert(best_pos, node)
            remaining.remove(node)
        
        return np.array(tour)
    
    def _spiral(self, coords, noise):
        """Espiral con ruido."""
        center = np.mean(coords, axis=0)
        angles = np.arctan2(coords[:, 1] - center[1], coords[:, 0] - center[0])
        noisy_angles = angles + np.random.normal(0, noise * 2, len(angles))
        return np.argsort(noisy_angles)
    
    def _zigzag(self, coords, noise):
        """Zigzag con ruido."""
        noisy_x = coords[:, 0] + np.random.normal(0, coords[:, 0].std() * noise, len(coords))
        return np.argsort(noisy_x)


def adaptive_quantum_solve(coords, distances, time_budget=10.0):
    """Función conveniente."""
    solver = AdaptiveQuantumSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
