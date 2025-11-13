"""
Hybrid Quantum Solver - Lo mejor de ambos mundos
=================================================

Estrategia:
- 50% Smart Quantum (calidad)
- 50% Quantum original (exploración)
- Tomar el mejor resultado
"""

import numpy as np
import time
from typing import Tuple, List
from pimst.improved.sino.smart_quantum_solver import SmartQuantumSolver


class HybridQuantumSolver:
    """
    Combina Smart Quantum y Quantum original.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Ejecutar ambos solvers en paralelo temporal.
        """
        n = len(coords)
        print(f"   🌟 HYBRID QUANTUM: Mejor de ambos mundos")
        print(f"   ⚖️  Smart (calidad) + Quantum (exploración)")
        
        # PARTE 1: Smart Quantum (50% tiempo)
        print(f"\n   Ejecutando Smart Quantum ({time_budget*0.5:.1f}s)...")
        smart_solver = SmartQuantumSolver()
        tour_smart, cost_smart, meta_smart = smart_solver.solve(
            coords, distances, time_budget=time_budget * 0.5
        )
        
        # PARTE 2: Quantum original (50% tiempo)
        print(f"\n   Ejecutando Quantum original ({time_budget*0.5:.1f}s)...")
        tour_quantum, cost_quantum = self._quantum_original(
            coords, distances, time_budget=time_budget * 0.5
        )
        
        # SELECCIONAR MEJOR
        if cost_smart < cost_quantum:
            print(f"\n   🏆 Smart ganó: {cost_smart:.2f} vs {cost_quantum:.2f}")
            best_tour = tour_smart
            best_cost = cost_smart
            winner = "smart"
        else:
            print(f"\n   🏆 Quantum ganó: {cost_quantum:.2f} vs {cost_smart:.2f}")
            best_tour = tour_quantum
            best_cost = cost_quantum
            winner = "quantum"
        
        metadata = {
            'strategies_used': ['hybrid_smart_quantum'],
            'smart_cost': cost_smart,
            'quantum_cost': cost_quantum,
            'winner': winner,
            'best_cost': best_cost
        }
        
        return best_tour, best_cost, metadata
    
    def _quantum_original(self, coords, distances, time_budget):
        """
        Implementación del Quantum Solver original.
        """
        import hashlib
        from pimst.algorithms import (
            gravity_guided_tsp,
            lin_kernighan_lite,
            two_opt_improvement,
            nearest_neighbor
        )
        
        n = len(coords)
        start_time = time.time()
        
        solutions = []
        unique_tours = set()
        iteration = 0
        
        noise_level = 0.15  # 15% óptimo
        
        # Fase 1: Exploración (70%)
        phase1_end = start_time + time_budget * 0.7
        
        while time.time() < phase1_end:
            iteration += 1
            quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
            np.random.seed(quantum_seed)
            
            # Ruido
            noise_matrix = np.random.uniform(1 - noise_level, 1 + noise_level, distances.shape)
            noisy_distances = distances * noise_matrix
            noisy_distances = np.maximum(noisy_distances, 0.1)
            
            # Estrategia
            strategy = np.random.randint(0, 30)
            
            if strategy < 8:
                if np.random.random() > 0.5:
                    coord_noise = np.random.normal(0, coords.std() * noise_level, coords.shape)
                    noisy_coords = coords + coord_noise
                    tour = gravity_guided_tsp(noisy_coords, noisy_distances)
                else:
                    tour = gravity_guided_tsp(coords, noisy_distances)
            elif strategy < 16:
                start_node = np.random.randint(0, n)
                tour = nearest_neighbor(coords, noisy_distances, start=start_node)
            else:
                tour = np.random.permutation(n)
            
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
                    shift = np.random.randint(1, n)
                    tour = np.roll(tour, shift)
                else:
                    i = np.random.randint(0, n)
                    j = np.random.randint(0, n)
                    node = tour[i]
                    tour = np.delete(tour, i)
                    tour = np.insert(tour, j, node)
            
            if np.random.random() > 0.3:
                tour, _ = two_opt_improvement(tour, distances)
            
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
            
            if tour_hash not in unique_tours:
                solutions.append((cost, tour))
                unique_tours.add(tour_hash)
        
        if len(solutions) == 0:
            tour = nearest_neighbor(coords, distances, start=0)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            return tour.tolist(), cost
        
        # Fase 2: Refinamiento (30%)
        solutions.sort(key=lambda x: x[0])
        
        improved = []
        for cost, tour in solutions[:30]:
            if time.time() - start_time > time_budget * 0.95:
                break
            tour_lk = lin_kernighan_lite(coords, distances, max_iterations=500)
            cost_lk = sum(distances[tour_lk[i]][tour_lk[(i+1)%n]] for i in range(n))
            improved.append((cost_lk, tour_lk))
        
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])
        
        best_tour, best_cost = all_solutions[0][1], all_solutions[0][0]
        
        return best_tour.tolist(), best_cost


def hybrid_quantum_solve(coords, distances, time_budget=10.0):
    """Función conveniente."""
    solver = HybridQuantumSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
