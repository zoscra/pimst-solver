"""
Mega Solver - Máxima diversificación con velocidad PIMST
=========================================================

Estrategia:
1. Exploración ultra-diversa (0.5s):
   - 10x Nearest Neighbor (desde diferentes puntos)
   - 5x Gravity (con perturbaciones)
   
2. Mejora de top-5 (2s):
   - Aplicar LK a las 5 mejores
   
3. Refinamiento final (1s):
   - 3-opt en la mejor

Total: ~3.5s con máxima calidad
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


class MegaSolver:
    """
    Solver que maximiza diversidad usando velocidad extrema de PIMST.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Resolver TSP con máxima diversificación.
        """
        n = len(coords)
        start_time = time.time()
        
        candidates = []
        
        # FASE 1: EXPLORACIÓN DIVERSA (usar velocidad extrema)
        print(f"   Fase 1: Exploración diversa...")
        
        # 1a. Nearest Neighbor desde TODOS los puntos posibles
        # NN es rápido (0.18s), podemos hacer muchos
        nn_points = min(n, 20)  # Hasta 20 diferentes starting points
        for i in range(0, n, max(1, n // nn_points)):
            if time.time() - start_time > time_budget * 0.3:
                break
            
            tour = nearest_neighbor(coords, distances, start=i)
            tour, _ = two_opt_improvement(tour, distances)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            candidates.append(('nn_from_' + str(i), tour, cost))
        
        # 1b. Gravity con perturbaciones
        # Gravity es ultra-rápido (0.0007s), podemos hacer MUCHOS
        for seed in range(10):
            if time.time() - start_time > time_budget * 0.35:
                break
            
            np.random.seed(seed)
            tour = gravity_guided_tsp(coords, distances)
            
            # Perturbar con random swaps
            for _ in range(3):
                i, j = np.random.randint(0, n, 2)
                if i > j:
                    i, j = j, i
                tour[i:j+1] = tour[i:j+1][::-1]
            
            tour, _ = two_opt_improvement(tour, distances)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            candidates.append(('gravity_seed_' + str(seed), tour, cost))
        
        print(f"   → {len(candidates)} candidatos generados")
        
        # FASE 2: MEJORA DE LOS MEJORES
        print(f"   Fase 2: Mejorando top candidatos...")
        
        # Ordenar y tomar top-10
        candidates.sort(key=lambda x: x[2])
        top_candidates = candidates[:10]
        
        improved_candidates = []
        
        for name, tour, cost in top_candidates:
            if time.time() - start_time > time_budget * 0.8:
                break
            
            # Aplicar LK
            tour_improved = lin_kernighan_lite(coords, distances, max_iterations=200)
            cost_improved = sum(distances[tour_improved[i]][tour_improved[(i+1)%n]] for i in range(n))
            
            improved_candidates.append(('lk_from_' + name, tour_improved, cost_improved))
        
        # Combinar con candidatos originales
        all_candidates = candidates + improved_candidates
        all_candidates.sort(key=lambda x: x[2])
        
        print(f"   → Mejor hasta ahora: {all_candidates[0][2]:.2f}")
        
        # FASE 3: REFINAMIENTO INTENSIVO DEL MEJOR
        print(f"   Fase 3: Refinamiento final...")
        
        best_name, best_tour, best_cost = all_candidates[0]
        
        # 3-opt (más potente que 2-opt)
        remaining_time = time_budget - (time.time() - start_time)
        if remaining_time > 0.5:
            max_3opt_iter = int(remaining_time / 0.1)  # Estimar iteraciones
            best_tour = three_opt_improvement(best_tour, distances, max_iter=max_3opt_iter)
            best_cost = sum(distances[best_tour[i]][best_tour[(i+1)%n]] for i in range(n))
        
        total_time = time.time() - start_time
        
        metadata = {
            'strategies_used': ['mega_diversification'],
            'n_candidates': len(all_candidates),
            'best_strategy': best_name,
            'total_time': total_time
        }
        
        print(f"   ✅ Final: {best_cost:.2f} en {total_time:.2f}s")
        
        return best_tour.tolist(), best_cost, metadata


def mega_solve(
    coords: np.ndarray,
    distances: np.ndarray,
    time_budget: float = 10.0
) -> Tuple[List[int], float]:
    """Función conveniente."""
    solver = MegaSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
