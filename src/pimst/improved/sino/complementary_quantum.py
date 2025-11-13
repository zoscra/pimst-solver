"""
Complementary Quantum Solver - Exploración Ortogonal
=====================================================

Concepto: Dividir tiempo en múltiples runs con estrategias
que garantizan explorar regiones DIFERENTES del espacio.

Run 1: Geométrico (gravity, construcciones espaciales)
Run 2: Local (LK intensivo, refinamiento)
Run 3: Aleatorio (máxima exploración, caos controlado)
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


class ComplementaryQuantumSolver:
    """
    Solver que ejecuta múltiples búsquedas ortogonales.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0,
        n_runs: int = 3
    ) -> Tuple[List[int], float, dict]:
        """
        Ejecutar n_runs con estrategias complementarias.
        """
        n = len(coords)
        budget_per_run = time_budget / n_runs
        
        print(f"   🎯 COMPLEMENTARY QUANTUM: {n_runs} búsquedas ortogonales")
        print(f"   ⏱️  {budget_per_run:.1f}s por búsqueda\n")
        
        all_solutions = []
        all_unique_tours = set()
        run_details = []
        
        for run_idx in range(n_runs):
            print(f"   {'='*60}")
            print(f"   RUN {run_idx+1}/{n_runs}: ", end='')
            
            # ESTRATEGIA ESPECÍFICA POR RUN
            if run_idx == 0:
                print("GEOMÉTRICO (Gravity + Espacial)")
                tour, cost, meta = self._geometric_run(
                    coords, distances, budget_per_run
                )
            elif run_idx == 1:
                print("LOCAL (LK + Refinamiento intensivo)")
                tour, cost, meta = self._local_run(
                    coords, distances, budget_per_run
                )
            else:
                print("ALEATORIO (Exploración máxima)")
                tour, cost, meta = self._chaos_run(
                    coords, distances, budget_per_run
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
            
            print(f"      Costo: {cost:.2f}")
            print(f"      Soluciones únicas: {meta.get('unique_solutions', 1)}")
        
        # Seleccionar mejor
        all_solutions.sort(key=lambda x: x[0])
        best_cost, best_tour, best_meta = all_solutions[0]
        winner_run = [d for d in run_details if d['cost'] == best_cost][0]['run']
        
        print(f"\n   {'='*60}")
        print(f"   🏆 GANADOR: Run {winner_run}")
        print(f"   💎 Mejor costo: {best_cost:.2f}")
        print(f"   🎲 Tours únicos totales: {len(all_unique_tours)}")
        print(f"   {'='*60}")
        
        metadata = {
            'strategies_used': ['complementary_quantum'],
            'n_runs': n_runs,
            'run_details': run_details,
            'all_costs': [s[0] for s in all_solutions],
            'diversity_ratio': len(all_unique_tours) / sum(d['unique_solutions'] for d in run_details),
            'winner_run': winner_run,
            'best_cost': best_cost
        }
        
        return best_tour, best_cost, metadata
    
    def _geometric_run(self, coords, distances, time_budget):
        """
        Run 1: Favorece construcciones geométricas.
        """
        n = len(coords)
        start_time = time.time()
        solutions = []
        unique_tours = set()
        iteration = 0
        noise_level = 0.15
        
        # Fase 1: 70% tiempo - SOLO estrategias geométricas
        phase1_end = start_time + time_budget * 0.7
        
        while time.time() < phase1_end:
            iteration += 1
            quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
            np.random.seed(quantum_seed)
            
            noise_matrix = np.random.uniform(1 - noise_level, 1 + noise_level, distances.shape)
            noisy_distances = distances * noise_matrix
            noisy_distances = np.maximum(noisy_distances, 0.1)
            
            # ESTRATEGIAS GEOMÉTRICAS (100% del tiempo)
            strategy = np.random.randint(0, 10)
            
            if strategy < 5:
                # Gravity (50%)
                if np.random.random() > 0.5:
                    coord_noise = np.random.normal(0, coords.std() * noise_level, coords.shape)
                    noisy_coords = coords + coord_noise
                    tour = gravity_guided_tsp(noisy_coords, noisy_distances)
                else:
                    tour = gravity_guided_tsp(coords, noisy_distances)
            elif strategy < 8:
                # Multi-start (30%)
                n_starts = np.random.choice([2, 3, 5])
                tour = multi_start_solver(coords, noisy_distances, n_starts=n_starts)
            else:
                # NN desde puntos estratégicos (20%)
                # Elegir punto extremo (esquina)
                center = np.mean(coords, axis=0)
                distances_from_center = np.array([np.linalg.norm(coords[i] - center) for i in range(n)])
                start_node = np.argmax(distances_from_center)
                tour = nearest_neighbor(coords, noisy_distances, start=start_node)
            
            # Mutaciones geométricas (preservan estructura espacial)
            for _ in range(3):  # Pocas mutaciones para preservar geometría
                mut = np.random.randint(0, 2)
                if mut == 0:
                    i, j = sorted(np.random.randint(0, n, 2))
                    tour[i:j] = tour[i:j][::-1]
                else:
                    shift = np.random.randint(1, n)
                    tour = np.roll(tour, shift)
            
            # 2-opt (preserva geometría)
            tour, _ = two_opt_improvement(tour, distances)
            
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
            
            if tour_hash not in unique_tours:
                solutions.append((cost, tour))
                unique_tours.add(tour_hash)
        
        if not solutions:
            tour = nearest_neighbor(coords, distances, start=0)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, tour))
        
        # Fase 2: 30% tiempo - LK en mejores
        solutions.sort(key=lambda x: x[0])
        for cost, tour in solutions[:20]:
            if time.time() - start_time > time_budget * 0.95:
                break
            tour_lk = lin_kernighan_lite(coords, distances, max_iterations=300)
            cost_lk = sum(distances[tour_lk[i]][tour_lk[(i+1)%n]] for i in range(n))
            solutions.append((cost_lk, tour_lk))
        
        solutions.sort(key=lambda x: x[0])
        best_cost, best_tour = solutions[0]
        
        return best_tour, best_cost, {
            'strategy': 'geometric',
            'unique_solutions': len(unique_tours),
            'all_tours': [s[1] for s in solutions]
        }
    
    def _local_run(self, coords, distances, time_budget):
        """
        Run 2: Favorece optimización local intensiva.
        """
        n = len(coords)
        start_time = time.time()
        solutions = []
        unique_tours = set()
        iteration = 0
        noise_level = 0.10  # Menos ruido = más local
        
        # Fase 1: 50% tiempo - Generación rápida
        phase1_end = start_time + time_budget * 0.5
        
        while time.time() < phase1_end:
            iteration += 1
            quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
            np.random.seed(quantum_seed)
            
            noise_matrix = np.random.uniform(1 - noise_level, 1 + noise_level, distances.shape)
            noisy_distances = distances * noise_matrix
            noisy_distances = np.maximum(noisy_distances, 0.1)
            
            # ESTRATEGIAS DIVERSAS para base
            strategy = np.random.randint(0, 5)
            
            if strategy < 2:
                tour = multi_start_solver(coords, noisy_distances, n_starts=3)
            elif strategy < 4:
                start_node = np.random.randint(0, n)
                tour = nearest_neighbor(coords, noisy_distances, start=start_node)
            else:
                tour = np.random.permutation(n)
            
            # Mejora local inmediata
            tour, _ = two_opt_improvement(tour, distances)
            
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
            
            if tour_hash not in unique_tours:
                solutions.append((cost, tour))
                unique_tours.add(tour_hash)
        
        if not solutions:
            tour = nearest_neighbor(coords, distances, start=0)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, tour))
        
        # Fase 2: 50% tiempo - REFINAMIENTO INTENSIVO
        solutions.sort(key=lambda x: x[0])
        
        for cost, tour in solutions[:30]:
            if time.time() - start_time > time_budget * 0.95:
                break
            
            # LK MUY intensivo
            tour_lk1 = lin_kernighan_lite(coords, distances, max_iterations=1000)
            cost_lk1 = sum(distances[tour_lk1[i]][tour_lk1[(i+1)%n]] for i in range(n))
            solutions.append((cost_lk1, tour_lk1))
            
            # 3-opt + LK
            if time.time() - start_time < time_budget * 0.9:
                tour_3opt = three_opt_improvement(tour, distances, max_iter=20)
                tour_lk2 = lin_kernighan_lite(coords, distances, max_iterations=500)
                cost_lk2 = sum(distances[tour_lk2[i]][tour_lk2[(i+1)%n]] for i in range(n))
                solutions.append((cost_lk2, tour_lk2))
        
        solutions.sort(key=lambda x: x[0])
        best_cost, best_tour = solutions[0]
        
        return best_tour, best_cost, {
            'strategy': 'local_intensive',
            'unique_solutions': len(unique_tours),
            'all_tours': [s[1] for s in solutions]
        }
    
    def _chaos_run(self, coords, distances, time_budget):
        """
        Run 3: Máxima aleatorización y exploración.
        """
        n = len(coords)
        start_time = time.time()
        solutions = []
        unique_tours = set()
        iteration = 0
        noise_level = 0.20  # MÁS ruido = más caos
        
        # Fase 1: 70% tiempo - CAOS TOTAL
        phase1_end = start_time + time_budget * 0.7
        
        while time.time() < phase1_end:
            iteration += 1
            quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
            np.random.seed(quantum_seed)
            
            # RUIDO ALTO
            noise_matrix = np.random.uniform(1 - noise_level, 1 + noise_level, distances.shape)
            noisy_distances = distances * noise_matrix
            noisy_distances = np.maximum(noisy_distances, 0.1)
            
            # ESTRATEGIAS ALEATORIAS (todas por igual)
            strategy = np.random.randint(0, 40)
            
            if strategy < 10:
                tour = np.random.permutation(n)
            elif strategy < 20:
                start_node = np.random.randint(0, n)
                tour = nearest_neighbor(coords, noisy_distances, start=start_node)
            elif strategy < 25:
                tour = gravity_guided_tsp(coords, noisy_distances)
            elif strategy < 30:
                tour = multi_start_solver(coords, noisy_distances, n_starts=2)
            else:
                tour = lin_kernighan_lite(coords, noisy_distances, max_iterations=50)
            
            # MUTACIONES AGRESIVAS (muchas)
            n_mutations = np.random.randint(10, 25)
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
                    i, j = np.random.randint(0, n, 2)
                    node = tour[i]
                    tour = np.delete(tour, i)
                    tour = np.insert(tour, j, node)
            
            # 2-opt a veces (no siempre)
            if np.random.random() > 0.5:
                tour, _ = two_opt_improvement(tour, distances)
            
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
            
            if tour_hash not in unique_tours:
                solutions.append((cost, tour))
                unique_tours.add(tour_hash)
        
        if not solutions:
            tour = np.random.permutation(n)
            tour, _ = two_opt_improvement(tour, distances)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, tour))
        
        # Fase 2: 30% tiempo - LK en mejores
        solutions.sort(key=lambda x: x[0])
        for cost, tour in solutions[:25]:
            if time.time() - start_time > time_budget * 0.95:
                break
            tour_lk = lin_kernighan_lite(coords, distances, max_iterations=400)
            cost_lk = sum(distances[tour_lk[i]][tour_lk[(i+1)%n]] for i in range(n))
            solutions.append((cost_lk, tour_lk))
        
        solutions.sort(key=lambda x: x[0])
        best_cost, best_tour = solutions[0]
        
        return best_tour, best_cost, {
            'strategy': 'chaos',
            'unique_solutions': len(unique_tours),
            'all_tours': [s[1] for s in solutions]
        }


def complementary_quantum_solve(coords, distances, time_budget=10.0, n_runs=3):
    """Función conveniente."""
    solver = ComplementaryQuantumSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget, n_runs)
    return tour, cost
