"""
Turbo Solver - PIMST puro con velocidad extrema
================================================

Usa SOLO algoritmos PIMST nativos:
- Gravity: 20,928x speedup (warm-start)
- LK: 227x speedup (calidad)
- NN: 80x speedup (diversidad)
- 2-opt/3-opt: mejoras locales

Estrategia: Generar 100+ soluciones en 1 segundo, mejorar las mejores
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


class TurboSolver:
    """
    Solver ultra-agresivo usando solo velocidad PIMST.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Resolver con máxima agresividad.
        """
        n = len(coords)
        start_time = time.time()
        
        solutions = []
        
        print(f"   🚀 TURBO MODE ACTIVADO")
        
        # FASE 1: BOMBARDEO DE SOLUCIONES RÁPIDAS (30% tiempo)
        phase1_budget = time_budget * 0.3
        phase1_end = start_time + phase1_budget
        
        print(f"   Fase 1: Generación masiva (objetivo: 50+ soluciones)...")
        
        iteration = 0
        while time.time() < phase1_end:
            iteration += 1
            
            # Alternar entre diferentes estrategias
            if iteration % 3 == 0:
                # Gravity (ultra-rápido)
                tour = gravity_guided_tsp(coords, distances)
            elif iteration % 3 == 1:
                # NN desde punto aleatorio
                start_point = np.random.randint(0, n)
                tour = nearest_neighbor(coords, distances, start=start_point)
            else:
                # NN desde punto estratégico
                start_point = (iteration * 7) % n
                tour = nearest_neighbor(coords, distances, start=start_point)
            
            # Mejora rápida con 2-opt
            tour, _ = two_opt_improvement(tour, distances)
            
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, tour, f'phase1_iter_{iteration}'))
            
            if iteration % 10 == 0:
                best_so_far = min(solutions, key=lambda x: x[0])[0]
                print(f"      → {iteration} soluciones, mejor: {best_so_far:.2f}")
        
        print(f"   ✅ {len(solutions)} soluciones generadas")
        
        # FASE 2: MEJORA INTENSIVA DE LAS MEJORES (50% tiempo)
        phase2_budget = time_budget * 0.5
        phase2_end = time.time() + phase2_budget
        
        print(f"   Fase 2: Mejora intensiva de top-20...")
        
        # Ordenar y tomar top-20
        solutions.sort(key=lambda x: x[0])
        top_solutions = solutions[:20]
        
        improved = []
        for i, (cost, tour, name) in enumerate(top_solutions):
            if time.time() >= phase2_end:
                break
            
            # Aplicar LK (el mejor algoritmo)
            tour_lk = lin_kernighan_lite(coords, distances, max_iterations=500)
            cost_lk = sum(distances[tour_lk[i]][tour_lk[(i+1)%n]] for i in range(n))
            
            improved.append((cost_lk, tour_lk, f'lk_from_{name}'))
            
            if (i + 1) % 5 == 0:
                best = min(improved, key=lambda x: x[0])[0]
                print(f"      → {i+1}/20 mejorados, mejor: {best:.2f}")
        
        # Combinar todas las soluciones
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])
        
        print(f"   ✅ Total: {len(all_solutions)} soluciones exploradas")
        
        # FASE 3: REFINAMIENTO EXTREMO DEL MEJOR (20% tiempo)
        remaining = time_budget - (time.time() - start_time)
        
        if remaining > 0.5:
            print(f"   Fase 3: Refinamiento extremo ({remaining:.1f}s restantes)...")
            
            # Tomar top-3 y refinar cada uno
            top3 = all_solutions[:3]
            
            ultra_refined = []
            for cost, tour, name in top3:
                # 3-opt agresivo
                tour_refined = three_opt_improvement(
                    tour, 
                    distances, 
                    max_iter=int(remaining * 10)
                )
                cost_refined = sum(distances[tour_refined[i]][tour_refined[(i+1)%n]] for i in range(n))
                
                ultra_refined.append((cost_refined, tour_refined, f'refined_{name}'))
            
            all_solutions.extend(ultra_refined)
            all_solutions.sort(key=lambda x: x[0])
        
        # Mejor solución final
        best_cost, best_tour, best_name = all_solutions[0]
        
        total_time = time.time() - start_time
        
        print(f"   ✅ FINAL: {best_cost:.2f} en {total_time:.2f}s")
        print(f"   📊 Estrategia ganadora: {best_name}")
        
        metadata = {
            'strategies_used': ['turbo_multi_strategy'],
            'total_solutions': len(all_solutions),
            'best_strategy': best_name,
            'total_time': total_time
        }
        
        return best_tour.tolist(), best_cost, metadata


def turbo_solve(
    coords: np.ndarray,
    distances: np.ndarray,
    time_budget: float = 10.0
) -> Tuple[List[int], float]:
    """Función conveniente."""
    solver = TurboSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
