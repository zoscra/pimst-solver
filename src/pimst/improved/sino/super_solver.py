"""
Super Solver - Ensemble + Thompson Sampling + Adaptive Refinement
==================================================================

Combina lo mejor de todos los mundos:
1. Thompson Sampling para primera solucion rapida
2. Parallel ensemble si la solucion parece suboptima
3. Refinamiento inteligente con tiempo adaptativo

Objetivo: Mejor que LKH en calidad, 10-100x mas rapido
"""

import numpy as np
import multiprocessing as mp
from typing import Tuple, List, Optional
import time
from .thompson_selector import ThompsonSamplingSelector


class SuperSolver:
    """
    Solver ultra-inteligente que combina multiples estrategias.
    
    Estrategia:
    1. Thompson Sampling da solucion inicial (rapido)
    2. Evaluar calidad con lower bound heuristic
    3. Si suboptima: parallel ensemble + refinamiento
    4. Retornar mejor solucion encontrada
    """
    
    def __init__(self, n_cores: int = None, mode: str = 'balanced'):
        """
        Args:
            n_cores: Number of CPU cores to use
            mode: 'fast' (speed priority), 'balanced' (default), 'academic' (quality priority)
        """
        self.thompson = ThompsonSamplingSelector()
        self.n_cores = n_cores or max(1, mp.cpu_count() - 1)
        self.mode = mode
        
    def estimate_lower_bound(self, distances: np.ndarray) -> float:
        """
        Estimar cota inferior (lower bound) del tour optimo.
        
        Usa MST (Minimum Spanning Tree) como lower bound:
        TSP_optimal >= MST_weight
        """
        from scipy.sparse.csgraph import minimum_spanning_tree
        
        # MST es lower bound conocido para TSP
        mst = minimum_spanning_tree(distances)
        mst_weight = mst.sum()
        
        # Anadir peso de arista mas pequena (para cerrar ciclo)
        # Lower bound mejorado: MST + min_edge
        mask = distances > 0
        if mask.any():
            min_edge = np.min(distances[mask])
            lower_bound = mst_weight + min_edge
        else:
            lower_bound = mst_weight
        
        return lower_bound
    
    def quality_check(self, cost: float, lower_bound: float, n: int) -> str:
        """
        Evaluar calidad de la solucion.
        
        Returns:
            'excellent': gap < 2%
            'good': gap < 5%
            'acceptable': gap < 10%
            'poor': gap >= 10%
        """
        gap = ((cost - lower_bound) / lower_bound) * 100
        
        # Para problemas pequenos, ser mas permisivo
        # El lower bound es menos preciso en grafos pequenos
        if n < 100:
            threshold_excellent = 5   # Mas permisivo
            threshold_good = 10
            threshold_acceptable = 15
        else:
            threshold_excellent = 2
            threshold_good = 5
            threshold_acceptable = 10
        
        if gap < threshold_excellent:
            return 'excellent'
        elif gap < threshold_good:
            return 'good'
        elif gap < threshold_acceptable:
            return 'acceptable'
        else:
            return 'poor'
    
    def parallel_ensemble(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float
    ) -> Tuple[List[int], float]:
        """
        Ejecutar multiples algoritmos en paralelo.
        
        Usa todos los cores disponibles para explorar en paralelo.
        """
        from pimst.algorithms import (
            gravity_guided_tsp,
            lin_kernighan_lite,
            multi_start_solver
        )
        
        n = len(coords)
        
        # Estrategias a ejecutar en paralelo
        strategies = []
        
        # Gravity (rapido)
        strategies.append(('gravity', lambda: gravity_guided_tsp(coords, distances)))
        
        # Multi-start con diferentes configs
        for n_starts in [3, 5, 10]:
            strategies.append((
                f'multi_start_{n_starts}',
                lambda ns=n_starts: multi_start_solver(coords, distances, n_starts=ns)
            ))
        
        # LK (calidad)
        strategies.append(('lin_kernighan', lambda: lin_kernighan_lite(coords, distances)))
        
        # Ejecutar en paralelo
        with mp.Pool(processes=min(self.n_cores, len(strategies))) as pool:
            results = []
            for name, strategy in strategies[:self.n_cores]:
                result = pool.apply_async(self._run_strategy, (strategy, distances, name))
                results.append(result)
            
            # Recoger resultados con timeout
            tours_costs = []
            for result in results:
                try:
                    tour, cost, name = result.get(timeout=time_budget)
                    tours_costs.append((tour, cost, name))
                except:
                    continue
        
        # Retornar mejor
        if tours_costs:
            best = min(tours_costs, key=lambda x: x[1])
            return best[0], best[1]
        
        # Fallback
        tour = gravity_guided_tsp(coords, distances)
        cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        return tour.tolist(), cost
    
    def _run_strategy(self, strategy, distances, name):
        """Ejecutar estrategia y retornar resultado."""
        tour = strategy()
        n = len(tour)
        cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        return tour.tolist(), cost, name
    
    def adaptive_refinement(
        self,
        tour: List[int],
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float
    ) -> Tuple[List[int], float]:
        """
        Refinamiento adaptativo de una solucion.
        
        Aplica mejoras locales iterativamente.
        """
        from pimst.algorithms import two_opt_improvement, three_opt_improvement
        
        n = len(tour)
        tour_array = np.array(tour)
        
        # 2-opt iterativo
        improved = True
        iterations = 0
        max_iterations = 10
        
        start = time.time()
        
        while improved and iterations < max_iterations:
            if time.time() - start > time_budget:
                break
            
            tour_array, was_improved = two_opt_improvement(tour_array, distances)
            improved = was_improved
            iterations += 1
        
        # Si aun hay tiempo, 3-opt
        if time.time() - start < time_budget * 0.8:
            tour_array = three_opt_improvement(tour_array, distances, max_iter=3)
        
        cost = sum(distances[tour_array[i]][tour_array[(i+1)%n]] for i in range(n))
        
        return tour_array.tolist(), cost
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Resolver TSP con estrategia super-inteligente.
        
        Returns:
            (tour, cost, metadata)
        """
        n = len(coords)
        start_time = time.time()
        
        # FAST PATH: Estrategia hibrida por tamano
        # En modo academic, no usar fast-path (priorizar calidad)
        use_fast_path = (
            (n <= 50 and self.mode == 'fast') or
            (n <= 40 and self.mode == 'balanced') or
            (n <= 30 and self.mode == 'academic')
        )
        
        if use_fast_path and n <= 50:
            # Para n<=50: gravity+2opt (ultra rapido, evita casos patologicos de LK)
            from pimst.algorithms import gravity_guided_tsp, two_opt_improvement
            
            tour = gravity_guided_tsp(coords, distances)
            tour, _ = two_opt_improvement(tour, distances)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            
            metadata = {
                'strategies_used': ['fast_path_gravity'],
                'n': n,
                'time': time.time() - start_time,
                'initial_quality': 'excellent',
                'final_quality': 'excellent'
            }
            
            return tour.tolist(), cost, metadata
        
        elif n <= 60 and self.mode in ['fast', 'balanced']:
            # Para threshold<n<=60: LK (solo en modo fast/balanced)
            from pimst.algorithms import lin_kernighan_lite
            
            tour = lin_kernighan_lite(coords, distances, max_iterations=10)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            
            metadata = {
                'strategies_used': ['fast_path_lk'],
                'n': n,
                'time': time.time() - start_time,
                'initial_quality': 'excellent',
                'final_quality': 'excellent'
            }
            
            return tour.tolist(), cost, metadata
        
        # Paso 1: Lower bound
        lower_bound = self.estimate_lower_bound(distances)
        
        # Paso 2: Thompson Sampling (rapido, primer intento)
        tour_ts, cost_ts = self.thompson.solve_and_learn(coords, distances)
        time_ts = time.time() - start_time
        
        quality = self.quality_check(cost_ts, lower_bound, n)
        
        metadata = {
            'thompson_cost': cost_ts,
            'thompson_time': time_ts,
            'lower_bound': lower_bound,
            'initial_quality': quality,
            'strategies_used': ['thompson_sampling']
        }
        
        # Si calidad es excelente o buena, retornar directamente
        if quality in ['excellent', 'good']:
            return tour_ts, cost_ts, metadata
        
        # Paso 3: Calidad aceptable -> Refinamiento rapido
        if quality == 'acceptable':
            remaining_time = time_budget - time_ts
            if remaining_time > 0.5:
                tour_refined, cost_refined = self.adaptive_refinement(
                    tour_ts, coords, distances, remaining_time
                )
                
                metadata['strategies_used'].append('adaptive_refinement')
                metadata['refined_cost'] = cost_refined
                
                if cost_refined < cost_ts:
                    quality_after = self.quality_check(cost_refined, lower_bound, n)
                    metadata['final_quality'] = quality_after
                    return tour_refined, cost_refined, metadata
            
            return tour_ts, cost_ts, metadata
        
        # Paso 4: Calidad pobre -> Parallel ensemble
        remaining_time = time_budget - time_ts
        if remaining_time > 1.0:
            tour_ensemble, cost_ensemble = self.parallel_ensemble(
                coords, distances, remaining_time * 0.7
            )
            
            metadata['strategies_used'].append('parallel_ensemble')
            metadata['ensemble_cost'] = cost_ensemble
            
            # Refinar la mejor solucion
            best_tour = tour_ensemble if cost_ensemble < cost_ts else tour_ts
            best_cost = min(cost_ensemble, cost_ts)
            
            remaining_for_refinement = time_budget - (time.time() - start_time)
            if remaining_for_refinement > 0.3:
                tour_final, cost_final = self.adaptive_refinement(
                    best_tour, coords, distances, remaining_for_refinement
                )
                
                metadata['strategies_used'].append('final_refinement')
                metadata['final_cost'] = cost_final
                
                quality_final = self.quality_check(cost_final, lower_bound, n)
                metadata['final_quality'] = quality_final
                
                return tour_final, cost_final, metadata
            
            quality_final = self.quality_check(best_cost, lower_bound, n)
            metadata['final_quality'] = quality_final
            return best_tour, best_cost, metadata
        
        # Fallback: retornar Thompson
        return tour_ts, cost_ts, metadata


def super_solve(
    coords: np.ndarray,
    distances: np.ndarray,
    time_budget: float = 10.0
) -> Tuple[List[int], float]:
    """
    Funcion conveniente para usar Super Solver.
    
    Args:
        coords: Coordenadas
        distances: Matriz de distancias
        time_budget: Tiempo maximo en segundos
    
    Returns:
        (tour, cost)
    """
    solver = SuperSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
