"""
Quantum Solver - Aleatoriedad extrema para escapar óptimos locales
===================================================================

Filosofía:
"La vida se formó por casualidad. La aguja dorada puede estar 
en cualquier configuración aleatoria."

Estrategia:
- NINGUNA iteración debe dar el mismo resultado
- Ruido en distancias, decisiones, perturbaciones
- Semillas aleatorias únicas por iteración
- Mutaciones estocásticas continuas
- Quantum jumps (saltos cuánticos) para escapar

"No hay dos universos paralelos iguales"
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


class QuantumSolver:
    """
    Solver con máxima aleatoriedad - cada solución es única.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Exploración cuántica con máxima aleatoriedad.
        """
        n = len(coords)
        start_time = time.time()
        
        print(f"   🎲 QUANTUM MODE: Aleatoriedad extrema")
        print(f"   💫 'La aguja dorada puede estar en cualquier lugar'")
        
        solutions = []
        unique_costs = set()
        iteration = 0
        
        # FASE 1: EXPLORACIÓN CUÁNTICA (70% tiempo)
        phase1_end = start_time + time_budget * 0.7
        
        print(f"   Fase 1: Exploración del multiverso...")
        
        while time.time() < phase1_end:
            iteration += 1
            
            # Semilla única para cada iteración
            quantum_seed = (int(time.time() * 1000000) + iteration) % (2**32)
            np.random.seed(quantum_seed)
            
            # RUIDO EN DISTANCIAS (aleatoriedad en percepción)
            noise_level = np.random.uniform(0.0, 0.15)  # 0-15% ruido
            noisy_distances = distances * (1 + np.random.uniform(-noise_level, noise_level, distances.shape))
            noisy_distances = np.maximum(noisy_distances, 0.1)  # Evitar negativos
            
            # Elegir estrategia aleatoriamente
            strategy = np.random.randint(0, 30)  # 30 estrategias
            
            if strategy < 5:
                # Gravity con parámetros aleatorios
                tour = self._quantum_gravity(coords, noisy_distances)
                strategy_name = "quantum_gravity"
                
            elif strategy < 10:
                # NN desde punto aleatorio con decisiones estocásticas
                tour = self._stochastic_nn(coords, noisy_distances)
                strategy_name = "stochastic_nn"
                
            elif strategy < 15:
                # Tour aleatorio con mejora local
                tour = np.random.permutation(n)
                # Mejora con ruido
                tour = self._noisy_2opt(tour, noisy_distances)
                strategy_name = "random_2opt"
                
            elif strategy < 18:
                # Greedy con decisiones probabilísticas
                tour = self._probabilistic_greedy(coords, noisy_distances)
                strategy_name = "prob_greedy"
                
            elif strategy < 21:
                # Inserción aleatoria
                tour = self._random_insertion(n, noisy_distances)
                strategy_name = "random_insertion"
                
            elif strategy < 24:
                # Construcción por swaps aleatorios
                tour = self._random_swap_construction(n, noisy_distances)
                strategy_name = "swap_construction"
                
            elif strategy < 27:
                # Simulated annealing casero
                tour = self._quantum_annealing(coords, noisy_distances)
                strategy_name = "quantum_annealing"
                
            else:
                # Mutaciones extremas
                tour = self._extreme_mutation(n, noisy_distances)
                strategy_name = "extreme_mutation"
            
            # MUTACIONES POST-CONSTRUCCIÓN (aleatoriedad adicional)
            mutation_type = np.random.randint(0, 5)
            
            if mutation_type == 0:
                # Swap múltiple aleatorio
                n_swaps = np.random.randint(2, 10)
                for _ in range(n_swaps):
                    i, j = np.random.randint(0, n, 2)
                    tour[i], tour[j] = tour[j], tour[i]
                    
            elif mutation_type == 1:
                # Reversal aleatorio
                i, j = sorted(np.random.randint(0, n, 2))
                tour[i:j] = tour[i:j][::-1]
                
            elif mutation_type == 2:
                # Scramble (mezclar segmento)
                i, j = sorted(np.random.randint(0, n, 2))
                segment = tour[i:j].copy()
                np.random.shuffle(segment)
                tour[i:j] = segment
                
            elif mutation_type == 3:
                # Rotation aleatoria
                shift = np.random.randint(0, n)
                tour = np.roll(tour, shift)
                
            else:
                # Inserción aleatoria de subsegmento
                i, j = sorted(np.random.randint(0, n, 2))
                if j > i:
                    segment = tour[i:j].copy()
                    tour = np.delete(tour, slice(i, j))
                    # k debe ser válido para el array reducido
                    k = np.random.randint(0, len(tour) + 1)
                    tour = np.insert(tour, k, segment)
            
            # Mejora local (con distancias originales)
            if np.random.random() > 0.3:  # 70% probabilidad
                tour, _ = two_opt_improvement(tour, distances)
            
            # Calcular costo REAL (sin ruido)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            
            # Guardar solo si es único
            cost_rounded = round(cost, 2)
            if cost_rounded not in unique_costs:
                solutions.append((cost, tour, f"{strategy_name}_q{iteration}"))
                unique_costs.add(cost_rounded)
            
            # Progress
            if iteration % 100 == 0:
                if solutions:
                    best = min(solutions, key=lambda x: x[0])[0]
                    print(f"      → {iteration} iteraciones, {len(solutions)} únicas, mejor: {best:.2f}")
        
        print(f"   ✅ {len(solutions)} soluciones ÚNICAS de {iteration} intentos")
        print(f"   📊 Ratio unicidad: {len(solutions)/iteration*100:.1f}%")
        
        if len(solutions) == 0:
            print("   ⚠️ No se generaron soluciones, usando NN básico")
            tour = nearest_neighbor(coords, distances, start=0)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, tour, "fallback_nn"))
        
        # FASE 2: REFINAMIENTO CUÁNTICO (30% tiempo)
        print(f"   Fase 2: Refinamiento con mutaciones...")
        
        # Ordenar y tomar top-30
        solutions.sort(key=lambda x: x[0])
        top_solutions = solutions[:30]
        
        improved = []
        for i, (cost, tour, name) in enumerate(top_solutions):
            if time.time() - start_time > time_budget * 0.95:
                break
            
            # Aplicar LK con probabilidad
            if np.random.random() > 0.5:
                tour_lk = lin_kernighan_lite(coords, distances, max_iterations=300)
                cost_lk = sum(distances[tour_lk[j]][tour_lk[(j+1)%n]] for j in range(n))
                improved.append((cost_lk, tour_lk, f"lk_quantum_{name}"))
            else:
                # O aplicar 3-opt agresivo
                tour_3opt = three_opt_improvement(tour, distances, max_iter=5)
                cost_3opt = sum(distances[tour_3opt[j]][tour_3opt[(j+1)%n]] for j in range(n))
                improved.append((cost_3opt, tour_3opt, f"3opt_quantum_{name}"))
        
        # Combinar todas
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])
        
        best_cost, best_tour, best_name = all_solutions[0]
        
        total_time = time.time() - start_time
        
        print(f"   ✅ FINAL: {best_cost:.2f} en {total_time:.2f}s")
        print(f"   🏆 Ganador: {best_name}")
        print(f"   💫 Multiverso explorado: {len(all_solutions)} universos")
        
        metadata = {
            'strategies_used': ['quantum_maximum_randomness'],
            'total_solutions': len(all_solutions),
            'unique_solutions': len(unique_costs),
            'uniqueness_ratio': len(solutions) / iteration if iteration > 0 else 0,
            'best_strategy': best_name,
            'total_time': total_time
        }
        
        return best_tour.tolist(), best_cost, metadata
    
    def _quantum_gravity(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """Gravity con parámetros aleatorios."""
        # Modificar coords con ruido
        noisy_coords = coords + np.random.normal(0, coords.std() * 0.1, coords.shape)
        return gravity_guided_tsp(noisy_coords, distances)
    
    def _stochastic_nn(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """NN con decisiones probabilísticas en lugar de determinísticas."""
        n = len(coords)
        start = np.random.randint(0, n)
        tour = [start]
        unvisited = set(range(n)) - {start}
        
        current = start
        while unvisited:
            # En lugar de elegir el más cercano, usar probabilidad inversa a distancia
            dists = np.array([distances[current][j] for j in unvisited])
            
            # Temperatura aleatoria
            temp = np.random.uniform(0.1, 2.0)
            
            # Probabilidad inversamente proporcional a distancia
            probs = np.exp(-dists / (temp * dists.mean()))
            probs = probs / probs.sum()
            
            # Elegir probabilísticamente
            next_city = np.random.choice(list(unvisited), p=probs)
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        
        return np.array(tour)
    
    def _noisy_2opt(self, tour: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """2-opt que acepta movimientos malos con probabilidad."""
        n = len(tour)
        improved = True
        
        iterations = 0
        max_iter = 50
        
        while improved and iterations < max_iter:
            improved = False
            iterations += 1
            
            for i in range(n - 1):
                for j in range(i + 2, n):
                    # Calcular cambio
                    current_cost = (distances[tour[i]][tour[i+1]] + 
                                  distances[tour[j]][tour[(j+1)%n]])
                    new_cost = (distances[tour[i]][tour[j]] + 
                              distances[tour[i+1]][tour[(j+1)%n]])
                    
                    # Aceptar si mejora O con probabilidad aleatoria
                    if new_cost < current_cost or np.random.random() < 0.1:
                        tour[i+1:j+1] = tour[i+1:j+1][::-1]
                        improved = True
                        break
                if improved:
                    break
        
        return tour
    
    def _probabilistic_greedy(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """Greedy que a veces elige opciones subóptimas."""
        n = len(coords)
        start = np.random.randint(0, n)
        tour = [start]
        unvisited = set(range(n)) - {start}
        
        current = start
        while unvisited:
            dists = [(distances[current][j], j) for j in unvisited]
            dists.sort()
            
            # Top-k candidatos
            k = min(5, len(dists))
            candidates = [j for _, j in dists[:k]]
            
            # Elegir aleatoriamente de top-k
            next_city = np.random.choice(candidates)
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        
        return np.array(tour)
    
    def _random_insertion(self, n: int, distances: np.ndarray) -> np.ndarray:
        """Construcción por inserción aleatoria."""
        # Empezar con triángulo aleatorio
        tour = list(np.random.choice(n, 3, replace=False))
        remaining = set(range(n)) - set(tour)
        
        while remaining:
            # Elegir nodo aleatorio
            node = np.random.choice(list(remaining))
            
            # Insertar en posición que minimiza costo (con ruido)
            best_pos = 0
            best_cost = float('inf')
            
            for i in range(len(tour)):
                cost = (distances[tour[i]][node] + 
                       distances[node][tour[(i+1)%len(tour)]] -
                       distances[tour[i]][tour[(i+1)%len(tour)]])
                
                # Agregar ruido a la decisión
                noisy_cost = cost * np.random.uniform(0.8, 1.2)
                
                if noisy_cost < best_cost:
                    best_cost = noisy_cost
                    best_pos = i + 1
            
            tour.insert(best_pos, node)
            remaining.remove(node)
        
        return np.array(tour)
    
    def _random_swap_construction(self, n: int, distances: np.ndarray) -> np.ndarray:
        """Empezar aleatorio y mejorar con swaps."""
        tour = np.random.permutation(n)
        
        # Múltiples pasadas de swaps
        for _ in range(10):
            i, j = np.random.randint(0, n, 2)
            
            # Calcular si swap mejora
            old_contrib = 0
            new_contrib = 0
            
            for k in [-1, 0, 1]:
                if i + k >= 0 and i + k < n:
                    old_contrib += distances[tour[i]][tour[(i+k)%n]]
                    new_contrib += distances[tour[j]][tour[(i+k)%n]]
                if j + k >= 0 and j + k < n:
                    old_contrib += distances[tour[j]][tour[(j+k)%n]]
                    new_contrib += distances[tour[i]][tour[(j+k)%n]]
            
            if new_contrib < old_contrib or np.random.random() < 0.2:
                tour[i], tour[j] = tour[j], tour[i]
        
        return tour
    
    def _quantum_annealing(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """Simulated annealing simple con temperatura aleatoria."""
        n = len(coords)
        current_tour = np.random.permutation(n)
        current_cost = sum(distances[current_tour[i]][current_tour[(i+1)%n]] for i in range(n))
        
        best_tour = current_tour.copy()
        best_cost = current_cost
        
        # Temperatura inicial aleatoria
        temp = np.random.uniform(1000, 5000)
        cooling = np.random.uniform(0.90, 0.99)
        
        for _ in range(100):
            # Movimiento aleatorio
            move_type = np.random.randint(0, 3)
            new_tour = current_tour.copy()
            
            if move_type == 0:
                # Swap
                i, j = np.random.randint(0, n, 2)
                new_tour[i], new_tour[j] = new_tour[j], new_tour[i]
            elif move_type == 1:
                # Reversal
                i, j = sorted(np.random.randint(0, n, 2))
                new_tour[i:j] = new_tour[i:j][::-1]
            else:
                # Insertion
                i, j = np.random.randint(0, n, 2)
                node = new_tour[i]
                new_tour = np.delete(new_tour, i)
                new_tour = np.insert(new_tour, j, node)
            
            new_cost = sum(distances[new_tour[i]][new_tour[(i+1)%n]] for i in range(n))
            
            # Aceptar con probabilidad
            delta = new_cost - current_cost
            if delta < 0 or np.random.random() < np.exp(-delta / temp):
                current_tour = new_tour
                current_cost = new_cost
                
                if current_cost < best_cost:
                    best_tour = current_tour.copy()
                    best_cost = current_cost
            
            temp *= cooling
        
        return best_tour
    
    def _extreme_mutation(self, n: int, distances: np.ndarray) -> np.ndarray:
        """Mutaciones extremas desde tour aleatorio."""
        tour = np.random.permutation(n)
        
        # Aplicar múltiples mutaciones aleatorias
        n_mutations = np.random.randint(5, 15)
        
        for _ in range(n_mutations):
            mut_type = np.random.randint(0, 4)
            
            if mut_type == 0:
                # Swap aleatorio
                i, j = np.random.randint(0, n, 2)
                tour[i], tour[j] = tour[j], tour[i]
            elif mut_type == 1:
                # Reversal aleatorio
                i, j = sorted(np.random.randint(0, n, 2))
                tour[i:j] = tour[i:j][::-1]
            elif mut_type == 2:
                # Scramble
                i, j = sorted(np.random.randint(0, n, 2))
                segment = tour[i:j].copy()
                np.random.shuffle(segment)
                tour[i:j] = segment
            else:
                # Rotation
                shift = np.random.randint(1, n)
                tour = np.roll(tour, shift)
        
        return tour


def quantum_solve(
    coords: np.ndarray,
    distances: np.ndarray,
    time_budget: float = 10.0
) -> Tuple[List[int], float]:
    """Función conveniente."""
    solver = QuantumSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
