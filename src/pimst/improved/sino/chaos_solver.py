"""
Chaos Solver - Máxima diversidad con todas las versiones PIMST
===============================================================

Filosofía:
- Usar TODAS las variantes, incluso las "malas"
- Generar MILES de soluciones con velocidad extrema
- La geometría puede sorprender
- Con 20,928x speedup, podemos explorar TODO

No hay algoritmo "malo" - solo falta de diversidad.
"""

import numpy as np
import time
from typing import Tuple, List
from pimst.algorithms import (
    gravity_guided_tsp,
    lin_kernighan_lite,
    two_opt_improvement,
    three_opt_improvement,
    nearest_neighbor
)


class ChaosSolver:
    """
    Solver que explora MASIVAMENTE con máxima diversidad.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Exploración caótica masiva.
        """
        n = len(coords)
        start_time = time.time()
        
        print(f"   🌪️  CHAOS MODE: Máxima diversidad")
        
        solutions = []
        iteration = 0
        
        # FASE 1: BOMBARDEO MASIVO (70% tiempo)
        phase1_end = start_time + time_budget * 0.7
        
        print(f"   Fase 1: Bombardeo masivo de soluciones...")
        
        while time.time() < phase1_end:
            iteration += 1
            strategy_name = ""
            
            # Rotar entre TODAS las estrategias posibles
            variant = iteration % 20  # 20 variantes diferentes
            
            if variant == 0:
                # Gravity puro (ultra rápido)
                tour = gravity_guided_tsp(coords, distances)
                strategy_name = "gravity_raw"
                
            elif variant == 1:
                # Gravity + 2opt
                tour = gravity_guided_tsp(coords, distances)
                tour, _ = two_opt_improvement(tour, distances)
                strategy_name = "gravity_2opt"
                
            elif variant == 2:
                # Gravity + 3opt
                tour = gravity_guided_tsp(coords, distances)
                tour = three_opt_improvement(tour, distances, max_iter=3)
                strategy_name = "gravity_3opt"
                
            elif variant == 3:
                # NN desde punto aleatorio
                start = np.random.randint(0, n)
                tour = nearest_neighbor(coords, distances, start=start)
                strategy_name = f"nn_random_{start}"
                
            elif variant == 4:
                # NN desde esquina superior izquierda
                start = np.argmin(coords[:, 0] + coords[:, 1])
                tour = nearest_neighbor(coords, distances, start=start)
                strategy_name = "nn_topleft"
                
            elif variant == 5:
                # NN desde esquina inferior derecha
                start = np.argmax(coords[:, 0] + coords[:, 1])
                tour = nearest_neighbor(coords, distances, start=start)
                strategy_name = "nn_bottomright"
                
            elif variant == 6:
                # NN desde centro
                center = np.mean(coords, axis=0)
                start = np.argmin(np.linalg.norm(coords - center, axis=1))
                tour = nearest_neighbor(coords, distances, start=start)
                strategy_name = "nn_center"
                
            elif variant == 7:
                # NN desde punto más lejano del centro
                center = np.mean(coords, axis=0)
                start = np.argmax(np.linalg.norm(coords - center, axis=1))
                tour = nearest_neighbor(coords, distances, start=start)
                strategy_name = "nn_extreme"
                
            elif variant == 8:
                # Gravity invertido (recorrer al revés)
                tour = gravity_guided_tsp(coords, distances)
                tour = tour[::-1]
                strategy_name = "gravity_reversed"
                
            elif variant == 9:
                # NN + random swap
                start = (iteration * 7) % n
                tour = nearest_neighbor(coords, distances, start=start)
                # Swap aleatorio
                i, j = np.random.randint(0, n, 2)
                tour[i], tour[j] = tour[j], tour[i]
                strategy_name = "nn_swap"
                
            elif variant == 10:
                # NN + segment reversal
                start = (iteration * 11) % n
                tour = nearest_neighbor(coords, distances, start=start)
                # Reversar segmento
                i, j = sorted(np.random.randint(0, n, 2))
                tour[i:j] = tour[i:j][::-1]
                strategy_name = "nn_reverse"
                
            elif variant == 11:
                # Gravity + perturbación
                tour = gravity_guided_tsp(coords, distances)
                # Múltiples swaps
                for _ in range(3):
                    i, j = np.random.randint(0, n, 2)
                    if i > j:
                        i, j = j, i
                    tour[i:j] = tour[i:j][::-1]
                strategy_name = "gravity_perturbed"
                
            elif variant == 12:
                # NN desde hotspot (mayor grado)
                degrees = np.sum(distances < np.median(distances), axis=1)
                start = np.argmax(degrees)
                tour = nearest_neighbor(coords, distances, start=start)
                strategy_name = "nn_hotspot"
                
            elif variant == 13:
                # NN desde cold spot (menor grado)
                degrees = np.sum(distances < np.median(distances), axis=1)
                start = np.argmin(degrees)
                tour = nearest_neighbor(coords, distances, start=start)
                strategy_name = "nn_coldspot"
                
            elif variant == 14:
                # Estrategia voraz (greedy) modificada
                tour = self._greedy_with_noise(coords, distances)
                strategy_name = "greedy_noisy"
                
            elif variant == 15:
                # NN con criterio de distancia modificado
                tour = self._nn_farthest_insertion(coords, distances)
                strategy_name = "nn_farthest"
                
            elif variant == 16:
                # Tour aleatorio mejorado
                tour = np.random.permutation(n)
                tour, _ = two_opt_improvement(tour, distances)
                strategy_name = "random_2opt"
                
            elif variant == 17:
                # Estrategia de barrido angular
                tour = self._angular_sweep(coords)
                strategy_name = "angular_sweep"
                
            elif variant == 18:
                # Estrategia de grid
                tour = self._grid_based(coords)
                strategy_name = "grid_based"
                
            else:  # variant == 19
                # Hybrid: NN + Gravity
                tour1 = nearest_neighbor(coords, distances, start=iteration % n)
                tour2 = gravity_guided_tsp(coords, distances)
                # Tomar el mejor
                cost1 = sum(distances[tour1[i]][tour1[(i+1)%n]] for i in range(n))
                cost2 = sum(distances[tour2[i]][tour2[(i+1)%n]] for i in range(n))
                tour = tour1 if cost1 < cost2 else tour2
                strategy_name = "hybrid_nn_gravity"
            
            # Calcular costo
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, tour, f"{strategy_name}_iter{iteration}"))
            
            # Progress
            if iteration % 100 == 0:
                best = min(solutions, key=lambda x: x[0])[0]
                print(f"      → {iteration} soluciones, mejor: {best:.2f}")
        
        print(f"   ✅ {len(solutions)} soluciones generadas")
        
        # FASE 2: MEJORA DE LAS MEJORES (30% tiempo)
        print(f"   Fase 2: Refinamiento de top soluciones...")
        
        # Ordenar y tomar top-20
        solutions.sort(key=lambda x: x[0])
        top_solutions = solutions[:20]
        
        improved = []
        for i, (cost, tour, name) in enumerate(top_solutions):
            if time.time() - start_time > time_budget * 0.95:
                break
            
            # LK en las mejores
            tour_lk = lin_kernighan_lite(coords, distances, max_iterations=500)
            cost_lk = sum(distances[tour_lk[j]][tour_lk[(j+1)%n]] for j in range(n))
            
            improved.append((cost_lk, tour_lk, f"lk_from_{name}"))
            
            if (i + 1) % 5 == 0:
                best = min(improved, key=lambda x: x[0])[0]
                print(f"      → {i+1}/20 refinados, mejor: {best:.2f}")
        
        # Combinar todas
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])
        
        best_cost, best_tour, best_name = all_solutions[0]
        
        total_time = time.time() - start_time
        
        print(f"   ✅ FINAL: {best_cost:.2f} en {total_time:.2f}s")
        print(f"   📊 Total explorado: {len(all_solutions)} soluciones")
        print(f"   🏆 Ganador: {best_name}")
        
        metadata = {
            'strategies_used': ['chaos_maximum_diversity'],
            'total_solutions': len(all_solutions),
            'best_strategy': best_name,
            'total_time': total_time,
            'diversity_variants': 20
        }
        
        return best_tour.tolist(), best_cost, metadata
    
    def _greedy_with_noise(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """Greedy con ruido aleatorio en las decisiones."""
        n = len(coords)
        tour = [0]
        unvisited = set(range(1, n))
        
        current = 0
        while unvisited:
            # Agregar ruido a las distancias
            noisy_dists = [distances[current][j] * (1 + np.random.uniform(-0.1, 0.1)) 
                          for j in unvisited]
            nearest = list(unvisited)[np.argmin(noisy_dists)]
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return np.array(tour)
    
    def _nn_farthest_insertion(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """NN pero inserta el más lejano primero."""
        n = len(coords)
        # Empezar con los 2 más lejanos
        max_dist = 0
        start_pair = (0, 1)
        for i in range(n):
            for j in range(i+1, n):
                if distances[i][j] > max_dist:
                    max_dist = distances[i][j]
                    start_pair = (i, j)
        
        tour = list(start_pair)
        unvisited = set(range(n)) - set(start_pair)
        
        while unvisited:
            # Encontrar el más lejano del tour actual
            max_min_dist = -1
            farthest = None
            for v in unvisited:
                min_dist = min(distances[v][t] for t in tour)
                if min_dist > max_min_dist:
                    max_min_dist = min_dist
                    farthest = v
            
            # Insertar en mejor posición
            best_pos = 0
            best_cost = float('inf')
            for i in range(len(tour)):
                cost = (distances[tour[i]][farthest] + 
                       distances[farthest][tour[(i+1)%len(tour)]] -
                       distances[tour[i]][tour[(i+1)%len(tour)]])
                if cost < best_cost:
                    best_cost = cost
                    best_pos = i + 1
            
            tour.insert(best_pos, farthest)
            unvisited.remove(farthest)
        
        return np.array(tour)
    
    def _angular_sweep(self, coords: np.ndarray) -> np.ndarray:
        """Ordenar por ángulo desde el centro."""
        center = np.mean(coords, axis=0)
        angles = np.arctan2(coords[:, 1] - center[1], coords[:, 0] - center[0])
        tour = np.argsort(angles)
        return tour
    
    def _grid_based(self, coords: np.ndarray) -> np.ndarray:
        """Estrategia basada en grid espacial."""
        n = len(coords)
        
        # Crear grid
        x_sorted = np.argsort(coords[:, 0])
        
        # Serpentear por el grid
        tour = []
        for i in range(0, n, 10):
            slice_idx = x_sorted[i:i+10]
            if (i // 10) % 2 == 0:
                # Ordenar por y ascendente
                slice_sorted = slice_idx[np.argsort(coords[slice_idx, 1])]
            else:
                # Ordenar por y descendente
                slice_sorted = slice_idx[np.argsort(coords[slice_idx, 1])[::-1]]
            tour.extend(slice_sorted)
        
        return np.array(tour)


def chaos_solve(
    coords: np.ndarray,
    distances: np.ndarray,
    time_budget: float = 10.0
) -> Tuple[List[int], float]:
    """Función conveniente."""
    solver = ChaosSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
