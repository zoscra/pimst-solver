"""
Smart Quantum Solver - Calidad primero, luego diversidad
=========================================================

Filosofía:
"Empezar con soluciones de alta calidad, luego explorar variantes"

Estrategia:
1. Usar algoritmos PIMST fuertes (LK, multi-start) como base
2. Aplicar perturbaciones controladas
3. Refinamiento agresivo de candidatos prometedores
4. Calidad > Unicidad
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


class SmartQuantumSolver:
    """
    Solver que prioriza calidad usando algoritmos PIMST fuertes.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Resolver con énfasis en calidad.
        """
        n = len(coords)
        start_time = time.time()
        
        print(f"   🎯 SMART QUANTUM: Calidad primero")
        print(f"   💎 'Mejores soluciones base → mejores resultados finales'")
        
        solutions = []
        unique_tours = set()
        iteration = 0
        
        # FASE 1: GENERACIÓN DE BASES DE ALTA CALIDAD (40% tiempo)
        phase1_end = start_time + time_budget * 0.4
        
        print(f"   Fase 1: Generando bases de alta calidad...")
        
        while time.time() < phase1_end:
            iteration += 1
            quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
            np.random.seed(quantum_seed)
            
            # ESTRATEGIAS DE ALTA CALIDAD (no aleatorias puras)
            strategy = iteration % 10
            
            if strategy == 0:
                # Multi-start con 3 inicios (MUY BUENO según benchmarks)
                tour = multi_start_solver(coords, distances, n_starts=3)
                name = "multi_start_3"
                
            elif strategy == 1:
                # Multi-start con 5 inicios
                tour = multi_start_solver(coords, distances, n_starts=5)
                name = "multi_start_5"
                
            elif strategy == 2:
                # LK directo (el mejor en benchmarks)
                tour = lin_kernighan_lite(coords, distances, max_iterations=200)
                name = "lk_direct"
                
            elif strategy == 3:
                # Gravity + LK
                tour_g = gravity_guided_tsp(coords, distances)
                tour_g, _ = two_opt_improvement(tour_g, distances)
                tour = lin_kernighan_lite(coords, distances, max_iterations=100)
                # Tomar el mejor
                cost_g = sum(distances[tour_g[i]][tour_g[(i+1)%n]] for i in range(n))
                cost_lk = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
                tour = tour_g if cost_g < cost_lk else tour
                name = "gravity_vs_lk"
                
            elif strategy == 4:
                # NN desde mejor posición + mejora intensiva
                best_nn = None
                best_nn_cost = float('inf')
                # Probar 5 starting points
                for sp in range(0, n, max(1, n//5)):
                    tour_nn = nearest_neighbor(coords, distances, start=sp)
                    tour_nn, _ = two_opt_improvement(tour_nn, distances)
                    cost_nn = sum(distances[tour_nn[i]][tour_nn[(i+1)%n]] for i in range(n))
                    if cost_nn < best_nn_cost:
                        best_nn_cost = cost_nn
                        best_nn = tour_nn
                tour = best_nn
                name = "best_nn_5"
                
            elif strategy == 5:
                # LK con perturbación leve
                tour_base = lin_kernighan_lite(coords, distances, max_iterations=100)
                # Perturbar levemente
                for _ in range(3):
                    i, j = sorted(np.random.randint(0, n, 2))
                    tour_base[i:j] = tour_base[i:j][::-1]
                tour, _ = two_opt_improvement(tour_base, distances)
                name = "lk_perturbed"
                
            elif strategy == 6:
                # Multi-start + 3-opt
                tour = multi_start_solver(coords, distances, n_starts=3)
                tour = three_opt_improvement(tour, distances, max_iter=5)
                name = "multistart_3opt"
                
            elif strategy == 7:
                # Gravity mejorado con 3-opt
                tour = gravity_guided_tsp(coords, distances)
                tour = three_opt_improvement(tour, distances, max_iter=10)
                name = "gravity_3opt"
                
            elif strategy == 8:
                # Construcción híbrida: mejor de 3 métodos
                tour1 = gravity_guided_tsp(coords, distances)
                tour2 = nearest_neighbor(coords, distances, start=np.random.randint(0, n))
                tour3 = multi_start_solver(coords, distances, n_starts=2)
                
                cost1 = sum(distances[tour1[i]][tour1[(i+1)%n]] for i in range(n))
                cost2 = sum(distances[tour2[i]][tour2[(i+1)%n]] for i in range(n))
                cost3 = sum(distances[tour3[i]][tour3[(i+1)%n]] for i in range(n))
                
                tour = tour1 if cost1 <= min(cost2, cost3) else (tour2 if cost2 <= cost3 else tour3)
                name = "hybrid_best_3"
                
            else:  # strategy == 9
                # LK con ruido moderado (solo 5%)
                noise = 0.05
                noise_matrix = np.random.uniform(1 - noise, 1 + noise, distances.shape)
                noisy_distances = distances * noise_matrix
                tour = lin_kernighan_lite(coords, noisy_distances, max_iterations=150)
                # Evaluar con distancias reales
                name = "lk_noise5"
            
            # Calcular costo
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            
            # Hash
            tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
            
            if tour_hash not in unique_tours:
                solutions.append((cost, tour, name))
                unique_tours.add(tour_hash)
        
        print(f"   ✅ {len(solutions)} soluciones base de alta calidad")
        
        # FASE 2: PERTURBACIÓN INTELIGENTE (30% tiempo)
        phase2_end = start_time + time_budget * 0.7
        
        print(f"   Fase 2: Explorando variantes inteligentes...")
        
        # Tomar top-20 soluciones
        solutions.sort(key=lambda x: x[0])
        top_solutions = solutions[:20]
        
        variant_count = 0
        for cost, tour, name in top_solutions:
            if time.time() >= phase2_end:
                break
            
            # Generar 3 variantes de cada solución buena
            for variant in range(3):
                quantum_seed = (int(time.time() * 1000000000) + variant * 997) % (2**32)
                np.random.seed(quantum_seed)
                
                tour_var = tour.copy()
                
                # Perturbaciones controladas
                pert_type = variant
                
                if pert_type == 0:
                    # 2-opt moves aleatorios
                    for _ in range(3):
                        i, j = sorted(np.random.randint(0, n, 2))
                        tour_var[i:j] = tour_var[i:j][::-1]
                        
                elif pert_type == 1:
                    # Swap de segmentos pequeños
                    size = np.random.randint(2, 5)
                    i = np.random.randint(0, n-size)
                    j = np.random.randint(0, n-size)
                    tour_var[i:i+size], tour_var[j:j+size] = tour_var[j:j+size].copy(), tour_var[i:i+size].copy()
                    
                else:  # pert_type == 2
                    # Inserción de subsegmento
                    i, j = sorted(np.random.randint(0, n, 2))
                    if j > i:
                        segment = tour_var[i:j].copy()
                        tour_var = np.delete(tour_var, slice(i, j))
                        k = np.random.randint(0, len(tour_var) + 1)
                        tour_var = np.insert(tour_var, k, segment)
                
                # Mejora local agresiva
                tour_var, _ = two_opt_improvement(tour_var, distances)
                
                cost_var = sum(distances[tour_var[i]][tour_var[(i+1)%n]] for i in range(n))
                tour_hash = hashlib.md5(tour_var.tobytes()).hexdigest()
                
                if tour_hash not in unique_tours:
                    solutions.append((cost_var, tour_var, f"variant_{name}_{pert_type}"))
                    unique_tours.add(tour_hash)
                    variant_count += 1
        
        print(f"   ✅ {variant_count} variantes inteligentes generadas")
        
        # FASE 3: REFINAMIENTO EXTREMO (30% tiempo)
        print(f"   Fase 3: Refinamiento extremo de los mejores...")
        
        # Ordenar todas las soluciones
        solutions.sort(key=lambda x: x[0])
        
        # Refinar top-30 con LK potente
        improved = []
        for i, (cost, tour, name) in enumerate(solutions[:30]):
            if time.time() - start_time > time_budget * 0.95:
                break
            
            # LK con más iteraciones
            tour_lk = lin_kernighan_lite(coords, distances, max_iterations=500)
            cost_lk = sum(distances[tour_lk[i]][tour_lk[(i+1)%n]] for i in range(n))
            
            improved.append((cost_lk, tour_lk, f"lk_refined_{name}"))
            
            if (i + 1) % 10 == 0:
                best = min(improved, key=lambda x: x[0])[0]
                print(f"      → {i+1}/30 refinados, mejor: {best:.2f}")
        
        # Combinar todas
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])
        
        best_cost, best_tour, best_name = all_solutions[0]
        
        total_time = time.time() - start_time
        
        print(f"   ✅ FINAL: {best_cost:.2f} en {total_time:.2f}s")
        print(f"   🏆 Ganador: {best_name}")
        
        metadata = {
            'strategies_used': ['smart_quantum_quality_first'],
            'total_solutions': len(all_solutions),
            'unique_solutions': len(unique_tours),
            'best_strategy': best_name,
            'total_time': total_time
        }
        
        return best_tour.tolist(), best_cost, metadata


def smart_quantum_solve(coords, distances, time_budget=10.0):
    """Función conveniente."""
    solver = SmartQuantumSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
