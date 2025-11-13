"""
Complementary Quantum Solver - ATSP Version
============================================

Concepto: Dividir tiempo en múltiples runs con estrategias
que garantizan explorar regiones DIFERENTES del espacio.

Run 1: Construcción Diversa (diferentes heurísticas constructivas)
Run 2: Local Intensivo (LK intensivo, refinamiento profundo)
Run 3: Aleatorio (exploración máxima, chaos controlado)

Adaptado para ATSP: Sin coordenadas, solo matriz de distancias asimétrica.
"""

import numpy as np
import time
import hashlib
from typing import Tuple, List, Dict
from .atsp_algorithms import (
    nearest_neighbor_atsp,
    farthest_insertion_atsp,
    lin_kernighan_atsp,
    two_opt_atsp,
    three_opt_atsp,
    calculate_atsp_tour_length,
    multi_start_atsp
)


class ComplementaryQuantumATSP:
    """
    Solver que ejecuta múltiples búsquedas ortogonales para ATSP.
    """

    def solve(
        self,
        distances: np.ndarray,
        time_budget: float = 10.0,
        n_runs: int = 3,
        verbose: bool = True
    ) -> Tuple[np.ndarray, float, dict]:
        """
        Ejecutar n_runs con estrategias complementarias.

        Args:
            distances: Asymmetric distance matrix (n x n)
            time_budget: Total time budget in seconds
            n_runs: Number of orthogonal search runs
            verbose: Print progress

        Returns:
            (best_tour, best_cost, metadata)
        """
        n = len(distances)
        budget_per_run = time_budget / n_runs

        if verbose:
            print(f"   🎯 COMPLEMENTARY QUANTUM ATSP: {n_runs} búsquedas ortogonales")
            print(f"   ⏱️  {budget_per_run:.1f}s por búsqueda\n")

        all_solutions = []
        all_unique_tours = set()
        run_details = []

        for run_idx in range(n_runs):
            if verbose:
                print(f"   {'='*60}")
                print(f"   RUN {run_idx+1}/{n_runs}: ", end='')

            # ESTRATEGIA ESPECÍFICA POR RUN
            if run_idx == 0:
                if verbose:
                    print("CONSTRUCCIÓN DIVERSA (Múltiples heurísticas)")
                tour, cost, meta = self._diverse_construction_run(
                    distances, budget_per_run
                )
            elif run_idx == 1:
                if verbose:
                    print("LOCAL INTENSIVO (LK + Refinamiento)")
                tour, cost, meta = self._local_intensive_run(
                    distances, budget_per_run
                )
            else:
                if verbose:
                    print("ALEATORIO (Exploración máxima)")
                tour, cost, meta = self._chaos_run(
                    distances, budget_per_run
                )

            # Guardar
            all_solutions.append((cost, tour, meta))
            run_details.append({
                'run': run_idx + 1,
                'strategy': meta['strategy'],
                'cost': cost,
                'unique_solutions': meta.get('unique_solutions', 0)
            })

            # Tracking unicidad global
            for t in meta.get('all_tours', [tour]):
                tour_hash = tuple(t)
                all_unique_tours.add(tour_hash)

            if verbose:
                print(f"      Costo: {cost:.2f}")
                print(f"      Soluciones únicas: {meta.get('unique_solutions', 1)}")

        # Seleccionar mejor
        all_solutions.sort(key=lambda x: x[0])
        best_cost, best_tour, best_meta = all_solutions[0]
        winner_run = [d for d in run_details if d['cost'] == best_cost][0]['run']

        if verbose:
            print(f"\n   {'='*60}")
            print(f"   🏆 GANADOR: Run {winner_run}")
            print(f"   💎 Mejor costo: {best_cost:.2f}")
            print(f"   🎲 Tours únicos totales: {len(all_unique_tours)}")
            print(f"   {'='*60}")

        metadata = {
            'winner_run': winner_run,
            'all_runs': run_details,
            'unique_tours_explored': len(all_unique_tours),
            'time_budget': time_budget,
            'n_runs': n_runs
        }

        return best_tour, best_cost, metadata

    def _diverse_construction_run(
        self,
        distances: np.ndarray,
        time_budget: float
    ) -> Tuple[np.ndarray, float, Dict]:
        """
        Run 1: Probar múltiples heurísticas constructivas.

        Estrategias:
        - Nearest Neighbor desde diferentes nodos
        - Farthest Insertion desde diferentes nodos
        - Combinaciones

        Args:
            distances: Distance matrix
            time_budget: Time budget for this run

        Returns:
            (best_tour, best_cost, metadata)
        """
        n = len(distances)
        start_time = time.time()
        all_tours = []
        best_tour = None
        best_cost = np.inf

        # Distribuir tiempo entre estrategias
        n_starts = max(3, int(n * 0.1))  # 10% of cities as starts
        time_per_start = time_budget / (n_starts * 2)  # NN + FI

        for i in range(n_starts):
            if time.time() - start_time > time_budget:
                break

            start_city = int((i * n) / n_starts)

            # Estrategia 1: Nearest Neighbor
            tour = nearest_neighbor_atsp(distances, start_city)
            tour = lin_kernighan_atsp(distances, tour, max_iterations=20)
            cost = calculate_atsp_tour_length(tour, distances)
            all_tours.append(tour)

            if cost < best_cost:
                best_cost = cost
                best_tour = tour

            if time.time() - start_time > time_budget:
                break

            # Estrategia 2: Farthest Insertion
            tour = farthest_insertion_atsp(distances, start_city)
            tour = lin_kernighan_atsp(distances, tour, max_iterations=20)
            cost = calculate_atsp_tour_length(tour, distances)
            all_tours.append(tour)

            if cost < best_cost:
                best_cost = cost
                best_tour = tour

        # Count unique tours
        unique_tours = len(set(tuple(t) for t in all_tours))

        metadata = {
            'strategy': 'diverse_construction',
            'starts_tried': n_starts,
            'all_tours': all_tours,
            'unique_solutions': unique_tours,
            'time_used': time.time() - start_time
        }

        return best_tour, best_cost, metadata

    def _local_intensive_run(
        self,
        distances: np.ndarray,
        time_budget: float
    ) -> Tuple[np.ndarray, float, Dict]:
        """
        Run 2: Búsqueda local intensiva desde buena solución inicial.

        Estrategia:
        - Empezar con mejor heurística (Farthest Insertion)
        - Aplicar Lin-Kernighan con muchas iteraciones
        - Intentar perturbaciones y refinamiento

        Args:
            distances: Distance matrix
            time_budget: Time budget for this run

        Returns:
            (best_tour, best_cost, metadata)
        """
        n = len(distances)
        start_time = time.time()

        # Inicialización de alta calidad
        tour = farthest_insertion_atsp(distances, 0)
        tour = lin_kernighan_atsp(distances, tour, max_iterations=100)
        best_tour = tour.copy()
        best_cost = calculate_atsp_tour_length(tour, distances)

        improvements = 0
        iterations = 0

        # Búsqueda intensiva con tiempo restante
        while time.time() - start_time < time_budget:
            iterations += 1

            # Perturbación: intercambiar 2 segmentos aleatorios
            tour = self._perturb_tour(best_tour)

            # Refinamiento intensivo
            tour = lin_kernighan_atsp(distances, tour, max_iterations=50)
            cost = calculate_atsp_tour_length(tour, distances)

            if cost < best_cost:
                best_tour = tour
                best_cost = cost
                improvements += 1

            # Break si no hay mejoras en muchas iteraciones
            if iterations > 20 and improvements == 0:
                break

        metadata = {
            'strategy': 'local_intensive',
            'iterations': iterations,
            'improvements': improvements,
            'all_tours': [best_tour],
            'unique_solutions': 1,
            'time_used': time.time() - start_time
        }

        return best_tour, best_cost, metadata

    def _chaos_run(
        self,
        distances: np.ndarray,
        time_budget: float
    ) -> Tuple[np.ndarray, float, Dict]:
        """
        Run 3: Exploración aleatoria máxima.

        Estrategia:
        - Muchas inicializaciones aleatorias
        - Refinamiento rápido
        - Maximizar diversidad

        Args:
            distances: Distance matrix
            time_budget: Time budget for this run

        Returns:
            (best_tour, best_cost, metadata)
        """
        n = len(distances)
        start_time = time.time()
        all_tours = []
        best_tour = None
        best_cost = np.inf
        iterations = 0

        while time.time() - start_time < time_budget:
            iterations += 1

            # Inicialización aleatoria
            tour = self._random_tour(n)

            # Refinamiento rápido
            tour = two_opt_atsp(tour, distances, max_iterations=10)
            cost = calculate_atsp_tour_length(tour, distances)
            all_tours.append(tour)

            if cost < best_cost:
                best_cost = cost
                best_tour = tour

            # Cada 5 iteraciones, refinar mejor solución intensivamente
            if iterations % 5 == 0:
                tour = lin_kernighan_atsp(distances, best_tour, max_iterations=30)
                cost = calculate_atsp_tour_length(tour, distances)
                if cost < best_cost:
                    best_cost = cost
                    best_tour = tour

        # Count unique tours
        unique_tours = len(set(tuple(t) for t in all_tours))

        metadata = {
            'strategy': 'chaos_random',
            'iterations': iterations,
            'all_tours': all_tours,
            'unique_solutions': unique_tours,
            'time_used': time.time() - start_time
        }

        return best_tour, best_cost, metadata

    def _perturb_tour(self, tour: np.ndarray) -> np.ndarray:
        """
        Perturbar tour para escapar de óptimo local.

        Estrategia: Double-bridge move
        """
        n = len(tour)
        new_tour = tour.copy()

        # Seleccionar 4 puntos de corte aleatorios
        cuts = sorted(np.random.choice(range(1, n), size=4, replace=False))
        i, j, k, l = cuts

        # Reconstruir tour: [0:i] + [k:l] + [j:k] + [i:j] + [l:n]
        new_tour = np.concatenate([
            tour[:i],
            tour[k:l],
            tour[j:k],
            tour[i:j],
            tour[l:]
        ])

        return new_tour

    def _random_tour(self, n: int) -> np.ndarray:
        """
        Generar tour aleatorio.
        """
        tour = np.arange(n, dtype=np.int32)
        np.random.shuffle(tour)
        return tour


# Función de conveniencia
def solve_atsp_complementary_quantum(
    distances: np.ndarray,
    time_budget: float = 10.0,
    n_runs: int = 3,
    verbose: bool = True
) -> Tuple[np.ndarray, float, dict]:
    """
    Resolver ATSP usando Complementary Quantum Solver.

    Args:
        distances: Asymmetric distance matrix
        time_budget: Total time budget in seconds
        n_runs: Number of orthogonal runs
        verbose: Print progress

    Returns:
        (best_tour, best_cost, metadata)
    """
    solver = ComplementaryQuantumATSP()
    return solver.solve(distances, time_budget, n_runs, verbose)
