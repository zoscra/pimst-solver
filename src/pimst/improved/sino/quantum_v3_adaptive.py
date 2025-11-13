"""
Quantum Solver V3.1 - Filtros adaptativos
==========================================

Corrección de V3: Filtros más inteligentes y adaptativos.
"""

import numpy as np
import time
import hashlib
from typing import Tuple, List
from pimst.algorithms import (
    gravity_guided_tsp,
    lin_kernighan_lite,
    multi_start_solver,
    two_opt_improvement,
    three_opt_improvement,
    nearest_neighbor
)


def segments_intersect(p1, p2, p3, p4):
    """Verificar si dos segmentos se intersectan."""
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)


def remove_crossings_fast(tour, coords, distances):
    """Eliminar cruces con 2-opt limitado."""
    n = len(tour)
    improved = True
    iterations = 0
    
    while improved and iterations < 20:  # Límite bajo
        improved = False
        iterations += 1
        
        best_delta = 0
        best_i, best_j = -1, -1
        
        for i in range(n - 1):
            for j in range(i + 2, min(i + 20, n)):  # Ventana limitada
                if j == n - 1 and i == 0:
                    continue
                
                # Calcular delta sin verificar cruce geométrico
                current_dist = distances[tour[i]][tour[i+1]] + distances[tour[j]][tour[(j+1)%n]]
                new_dist = distances[tour[i]][tour[j]] + distances[tour[i+1]][tour[(j+1)%n]]
                delta = new_dist - current_dist
                
                if delta < best_delta:
                    best_delta = delta
                    best_i, best_j = i, j
        
        if best_delta < -0.01:  # Mejora significativa
            tour[best_i+1:best_j+1] = tour[best_i+1:best_j+1][::-1]
            improved = True
    
    return tour


class QuantumV3AdaptiveSolver:
    """
    Quantum con post-procesamiento geométrico en lugar de filtrado.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Quantum + post-procesamiento geométrico.
        """
        n = len(coords)
        start_time = time.time()
        
        print(f"   🎯 QUANTUM V3.1: Post-procesamiento adaptativo")
        print(f"   ⚡ Generar diversidad + Limpiar geometría después")
        
        solutions = []
        unique_tours = set()
        iteration = 0
        noise_level = 0.15
        
        # FASE 1: EXPLORACIÓN PURA (sin filtros) - 60%
        phase1_end = start_time + time_budget * 0.6
        
        print(f"   Fase 1: Exploración sin restricciones...")
        
        while time.time() < phase1_end:
            iteration += 1
            quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
            np.random.seed(quantum_seed)
            
            noise_matrix = np.random.uniform(1 - noise_level, 1 + noise_level, distances.shape)
            noisy_distances = distances * noise_matrix
            noisy_distances = np.maximum(noisy_distances, 0.1)
            
            strategy = np.random.randint(0, 40)
            
            if strategy < 8:
                if np.random.random() > 0.5:
                    coord_noise = np.random.normal(0, coords.std() * noise_level, coords.shape)
                    noisy_coords = coords + coord_noise
                    tour = gravity_guided_tsp(noisy_coords, noisy_distances)
                else:
                    tour = gravity_guided_tsp(coords, noisy_distances)
                strategy_name = "gravity"
            elif strategy < 16:
                start_node = np.random.randint(0, n)
                tour = nearest_neighbor(coords, noisy_distances, start=start_node)
                strategy_name = "nn"
            elif strategy < 20:
                n_starts = np.random.choice([2, 3, 5])
                tour = multi_start_solver(coords, noisy_distances, n_starts=n_starts)
                strategy_name = f"multistart"
            elif strategy < 24:
                tour = lin_kernighan_lite(coords, noisy_distances, max_iterations=100)
                strategy_name = "lk_noisy"
            else:
                tour = np.random.permutation(n)
                strategy_name = "random"
            
            # Mutaciones
            for _ in range(np.random.randint(5, 15)):
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
                    tour = np.roll(tour, np.random.randint(1, n))
                else:
                    i, j = np.random.randint(0, n, 2)
                    node = tour[i]
                    tour = np.delete(tour, i)
                    tour = np.insert(tour, j, node)
            
            if np.random.random() > 0.3:
                tour, _ = two_opt_improvement(tour, distances)
            
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
            
            if tour_hash not in unique_tours:
                solutions.append((cost, tour, strategy_name))
                unique_tours.add(tour_hash)
            
            if iteration % 100 == 0 and solutions:
                best = min(solutions, key=lambda x: x[0])[0]
                print(f"      → {iteration} iter, {len(solutions)} únicas, mejor: {best:.2f}")
        
        print(f"   ✅ {len(solutions)} soluciones generadas")
        
        if len(solutions) == 0:
            tour = nearest_neighbor(coords, distances, start=0)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, tour, "fallback"))
        
        # FASE 2: REFINAMIENTO + LIMPIEZA GEOMÉTRICA (40%)
        print(f"   Fase 2: Refinamiento con limpieza geométrica...")
        
        solutions.sort(key=lambda x: x[0])
        top_solutions = solutions[:40]
        
        improved = []
        for i, (cost, tour, name) in enumerate(top_solutions):
            if time.time() - start_time > time_budget * 0.95:
                break
            
            # Limpieza geométrica ligera
            tour_clean = remove_crossings_fast(tour.copy(), coords, distances)
            
            # LK
            if np.random.random() > 0.3:
                tour_ref = lin_kernighan_lite(coords, distances, max_iterations=500)
            else:
                tour_temp = three_opt_improvement(tour_clean, distances, max_iter=10)
                tour_ref = lin_kernighan_lite(coords, distances, max_iterations=300)
            
            # Limpieza final
            tour_ref = remove_crossings_fast(tour_ref, coords, distances)
            
            cost_ref = sum(distances[tour_ref[i]][tour_ref[(i+1)%n]] for i in range(n))
            improved.append((cost_ref, tour_ref, f"clean_{name}"))
            
            if (i + 1) % 10 == 0:
                best = min(improved, key=lambda x: x[0])[0]
                print(f"      → {i+1}/{len(top_solutions)} refinados, mejor: {best:.2f}")
        
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])
        
        best_cost, best_tour, best_name = all_solutions[0]
        total_time = time.time() - start_time
        
        print(f"   ✅ FINAL: {best_cost:.2f} en {total_time:.2f}s")
        print(f"   🏆 Ganador: {best_name}")
        
        metadata = {
            'strategies_used': ['quantum_v3_adaptive'],
            'total_solutions': len(all_solutions),
            'unique_solutions': len(unique_tours),
            'best_strategy': best_name,
            'total_time': total_time
        }
        
        return best_tour.tolist(), best_cost, metadata


def quantum_v3_adaptive_solve(coords, distances, time_budget=10.0):
    """Función conveniente."""
    solver = QuantumV3AdaptiveSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
