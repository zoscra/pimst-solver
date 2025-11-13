"""
Super Solver ATSP - Ensemble + Adaptive Refinement
===================================================

Combina lo mejor de todos los mundos para ATSP:
1. Solución inicial rápida con mejor heurística
2. Evaluación de calidad con lower bound (Held-Karp)
3. Parallel ensemble si la solución parece subóptima
4. Refinamiento inteligente con tiempo adaptativo

Objetivo: Mejor que algoritmos tradicionales en calidad, 10-100x más rápido.
"""

import numpy as np
import multiprocessing as mp
from typing import Tuple, List, Optional, Dict
import time
from .atsp_algorithms import (
    nearest_neighbor_atsp,
    farthest_insertion_atsp,
    lin_kernighan_atsp,
    multi_start_atsp,
    calculate_atsp_tour_length,
    solve_atsp_smart
)


class SuperSolverATSP:
    """
    Solver ultra-inteligente para ATSP que combina múltiples estrategias.

    Estrategia:
    1. Solución inicial rápida con mejor heurística
    2. Evaluar calidad con lower bound estimado
    3. Si subóptima: parallel ensemble + refinamiento
    4. Retornar mejor solución encontrada
    """

    def __init__(self, n_cores: int = None, mode: str = 'balanced'):
        """
        Args:
            n_cores: Number of CPU cores to use
            mode: 'fast' (speed priority), 'balanced' (default), 'optimal' (quality priority)
        """
        self.n_cores = n_cores or max(1, mp.cpu_count() - 1)
        self.mode = mode

    def estimate_lower_bound(self, distances: np.ndarray) -> float:
        """
        Estimar cota inferior (lower bound) del tour óptimo de ATSP.

        Usa Assignment Problem (AP) como lower bound:
        ATSP_optimal >= AP_optimal

        El Assignment Problem se puede resolver en O(n³) con Hungarian algorithm.
        Aquí usamos aproximación rápida: suma de n mínimos por fila.

        Args:
            distances: Asymmetric distance matrix

        Returns:
            Estimated lower bound
        """
        n = len(distances)

        # Approximation: sum of minimum outgoing edge from each city
        # This is a valid lower bound (pero no muy tight)
        lower_bound = 0.0
        for i in range(n):
            # Minimum edge from city i (excluding self-loop)
            mask = np.ones(n, dtype=bool)
            mask[i] = False
            min_edge = np.min(distances[i][mask])
            lower_bound += min_edge

        # Better bound: usar scipy si está disponible
        try:
            from scipy.optimize import linear_sum_assignment
            # Assignment problem: cada ciudad asigna a exactamente una
            # Esto da un lower bound más tight
            row_ind, col_ind = linear_sum_assignment(distances)
            ap_cost = distances[row_ind, col_ind].sum()
            lower_bound = max(lower_bound, ap_cost)
        except:
            pass  # Use simple bound if scipy not available

        return lower_bound

    def quality_check(self, cost: float, lower_bound: float, n: int) -> str:
        """
        Evaluar calidad de la solución.

        Returns:
            'excellent': gap < 2%
            'good': gap < 5%
            'acceptable': gap < 10%
            'poor': gap >= 10%
        """
        gap = ((cost - lower_bound) / lower_bound) * 100

        # Para problemas pequeños, ser más permisivo
        if n < 50:
            threshold_excellent = 5
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
        distances: np.ndarray,
        time_budget: float,
        n_runs: int = None
    ) -> Tuple[np.ndarray, float]:
        """
        Ejecutar ensemble paralelo de solvers.

        Args:
            distances: Distance matrix
            time_budget: Time budget
            n_runs: Number of parallel runs (default: n_cores)

        Returns:
            (best_tour, best_cost)
        """
        if n_runs is None:
            n_runs = self.n_cores

        n = len(distances)
        best_tour = None
        best_cost = np.inf

        # Para ATSP, diferentes estrategias
        strategies = []
        for i in range(n_runs):
            start_city = int((i * n) / n_runs)
            if i % 3 == 0:
                strategies.append(('nearest_neighbor', start_city))
            elif i % 3 == 1:
                strategies.append(('farthest_insertion', start_city))
            else:
                strategies.append(('multi_start', start_city))

        # Ejecutar en paralelo (simulado aquí con secuencial)
        # En producción, usar multiprocessing.Pool
        for strategy_type, start_city in strategies:
            if strategy_type == 'nearest_neighbor':
                tour = nearest_neighbor_atsp(distances, start_city)
                tour = lin_kernighan_atsp(distances, tour, max_iterations=50)
            elif strategy_type == 'farthest_insertion':
                tour = farthest_insertion_atsp(distances, start_city)
                tour = lin_kernighan_atsp(distances, tour, max_iterations=50)
            else:
                tour, _ = multi_start_atsp(distances, n_starts=3, strategy='balanced')

            cost = calculate_atsp_tour_length(tour, distances)

            if cost < best_cost:
                best_cost = cost
                best_tour = tour

        return best_tour, best_cost

    def solve(
        self,
        distances: np.ndarray,
        time_budget: float = 10.0,
        verbose: bool = True
    ) -> Tuple[np.ndarray, float, Dict]:
        """
        Resolver ATSP con estrategia super inteligente.

        Args:
            distances: Asymmetric distance matrix
            time_budget: Maximum time in seconds
            verbose: Print progress

        Returns:
            (tour, cost, metadata)
        """
        start_time = time.time()
        n = len(distances)

        if verbose:
            print(f"\n{'='*70}")
            print(f"  SUPER SOLVER ATSP - Mode: {self.mode}")
            print(f"{'='*70}")
            print(f"  Problem size: n={n}")
            print(f"  Time budget: {time_budget:.1f}s")
            print(f"  Cores: {self.n_cores}\n")

        # FASE 1: Solución inicial rápida
        if verbose:
            print("  [FASE 1] Solución inicial...")

        phase1_start = time.time()

        # Mejor heurística: Farthest Insertion
        tour = farthest_insertion_atsp(distances, 0)
        tour = lin_kernighan_atsp(distances, tour, max_iterations=30)
        cost = calculate_atsp_tour_length(tour, distances)

        phase1_time = time.time() - phase1_start

        if verbose:
            print(f"    ✓ Costo inicial: {cost:.2f}")
            print(f"    ⏱️  Tiempo: {phase1_time:.3f}s\n")

        # FASE 2: Evaluar calidad
        if verbose:
            print("  [FASE 2] Evaluando calidad...")

        lower_bound = self.estimate_lower_bound(distances)
        quality = self.quality_check(cost, lower_bound, n)
        gap = ((cost - lower_bound) / lower_bound) * 100

        if verbose:
            print(f"    📊 Lower bound: {lower_bound:.2f}")
            print(f"    📈 Gap estimado: {gap:.2f}%")
            print(f"    🎯 Calidad: {quality.upper()}\n")

        # FASE 3: Decidir estrategia
        remaining_time = time_budget - (time.time() - start_time)

        if quality in ['excellent', 'good'] or remaining_time < 1.0:
            # Solución ya es buena o no hay tiempo
            if verbose:
                print(f"  [FASE 3] ✓ Solución suficientemente buena o tiempo agotado")
                print(f"  🎉 Solución final: {cost:.2f}\n")

            metadata = {
                'phases': 2,
                'initial_cost': cost,
                'final_cost': cost,
                'lower_bound': lower_bound,
                'gap': gap,
                'quality': quality,
                'time_used': time.time() - start_time
            }

            return tour, cost, metadata

        else:
            # Necesitamos mejorar
            if verbose:
                print(f"  [FASE 3] Mejorando con ensemble paralelo...")
                print(f"    ⏱️  Tiempo restante: {remaining_time:.1f}s\n")

            # Ensemble paralelo
            n_runs = min(self.n_cores, int(remaining_time / 0.5))
            ensemble_tour, ensemble_cost = self.parallel_ensemble(
                distances, remaining_time, n_runs
            )

            # Comparar
            if ensemble_cost < cost:
                tour = ensemble_tour
                cost = ensemble_cost
                improved = True
            else:
                improved = False

            # Recalcular gap
            gap = ((cost - lower_bound) / lower_bound) * 100
            quality = self.quality_check(cost, lower_bound, n)

            if verbose:
                print(f"  [RESULTADO]")
                print(f"    {'✓ Mejorado' if improved else '○ No mejorado'}")
                print(f"    💎 Costo final: {cost:.2f}")
                print(f"    📈 Gap final: {gap:.2f}%")
                print(f"    🎯 Calidad final: {quality.upper()}")
                print(f"    ⏱️  Tiempo total: {time.time() - start_time:.3f}s\n")

            metadata = {
                'phases': 3,
                'initial_cost': cost if not improved else ensemble_cost,
                'final_cost': cost,
                'lower_bound': lower_bound,
                'gap': gap,
                'quality': quality,
                'improved': improved,
                'ensemble_runs': n_runs,
                'time_used': time.time() - start_time
            }

            return tour, cost, metadata


# Función de conveniencia
def solve_atsp_super(
    distances: np.ndarray,
    time_budget: float = 10.0,
    mode: str = 'balanced',
    n_cores: int = None,
    verbose: bool = True
) -> Tuple[np.ndarray, float, Dict]:
    """
    Resolver ATSP usando Super Solver.

    Args:
        distances: Asymmetric distance matrix
        time_budget: Maximum time in seconds
        mode: 'fast', 'balanced', or 'optimal'
        n_cores: Number of cores (default: auto)
        verbose: Print progress

    Returns:
        (tour, cost, metadata)
    """
    solver = SuperSolverATSP(n_cores=n_cores, mode=mode)
    return solver.solve(distances, time_budget, verbose)
