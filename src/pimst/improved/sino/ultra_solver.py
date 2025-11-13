"""
Ultra Solver - Aprovechar velocidad extrema de PIMST
=====================================================

Estrategia:
1. Gravity (0.0007s) → warm-start ultra-rápido
2. LK múltiple (3 runs × 0.06s = 0.18s) → exploración
3. Tomar mejor resultado

Total: ~0.2s con calidad competitiva
"""

import numpy as np
import time
from typing import Tuple, List
from pimst.algorithms import (
    gravity_guided_tsp,
    lin_kernighan_lite,
    two_opt_improvement,
    nearest_neighbor
)


class UltraSolver:
    """
    Solver que aprovecha la velocidad extrema de PIMST.
    
    Usa múltiples estrategias rápidas en paralelo.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Resolver TSP con estrategia ultra-rápida.
        
        Returns:
            (tour, cost, metadata)
        """
        n = len(coords)
        start_time = time.time()
        
        # Estrategia 1: Inicialización ultra-rápida con Gravity
        tours_and_costs = []
        
        # 1. Gravity (warm-start)
        tour_gravity = gravity_guided_tsp(coords, distances)
        tour_gravity, _ = two_opt_improvement(tour_gravity, distances)
        cost_gravity = sum(distances[tour_gravity[i]][tour_gravity[(i+1)%n]] for i in range(n))
        tours_and_costs.append(('gravity+2opt', tour_gravity, cost_gravity))
        
        # 2. Múltiples runs de LK con diferentes inicializaciones
        # LK es tan rápido (0.06s) que podemos hacer muchos runs
        max_lk_runs = int((time_budget - 0.5) / 0.07)  # Estimar cuántos caben
        max_lk_runs = max(3, min(max_lk_runs, 20))  # Entre 3 y 20 runs
        
        for run in range(max_lk_runs):
            if time.time() - start_time > time_budget * 0.9:
                break
            
            # Inicializar con nearest neighbor desde diferentes puntos
            start_node = (run * n // max_lk_runs) % n
            tour_init = nearest_neighbor(coords, distances, start=start_node)
            
            # Aplicar LK
            tour_lk = lin_kernighan_lite(coords, distances, max_iterations=100)
            cost_lk = sum(distances[tour_lk[i]][tour_lk[(i+1)%n]] for i in range(n))
            
            tours_and_costs.append((f'lk_run_{run}', tour_lk, cost_lk))
        
        # 3. Tomar mejor resultado
        best_name, best_tour, best_cost = min(tours_and_costs, key=lambda x: x[2])
        
        # 4. Refinamiento final si hay tiempo
        elapsed = time.time() - start_time
        if elapsed < time_budget * 0.9:
            best_tour, _ = two_opt_improvement(best_tour, distances)
            best_cost = sum(distances[best_tour[i]][best_tour[(i+1)%n]] for i in range(n))
        
        metadata = {
            'strategies_used': ['ultra_multi_lk'],
            'n_lk_runs': len([x for x in tours_and_costs if 'lk_run' in x[0]]),
            'best_strategy': best_name,
            'total_time': time.time() - start_time
        }
        
        return best_tour.tolist(), best_cost, metadata


def ultra_solve(
    coords: np.ndarray,
    distances: np.ndarray,
    time_budget: float = 10.0
) -> Tuple[List[int], float]:
    """
    Función conveniente para Ultra Solver.
    """
    solver = UltraSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
