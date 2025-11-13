"""
Ultra Quantum Solver - Aleatoriedad extrema++
==============================================

Filosofía mejorada:
"No solo casualidad - CAOS PURO"

Cada decisión, cada operación, cada bit tiene ruido.
IMPOSIBLE que dos soluciones sean iguales.
"""

import numpy as np
import time
import hashlib
from typing import Tuple, List
from pimst.algorithms import (
    gravity_guided_tsp,
    lin_kernighan_lite,
    two_opt_improvement,
    three_opt_improvement,
    nearest_neighbor
)


class UltraQuantumSolver:
    """
    Máxima aleatoriedad posible - CERO repeticiones garantizadas.
    """
    
    @staticmethod
    def _safe_random_choice(items, probs):
        """Elige aleatoriamente con probabilidades seguras."""
        prob_sum = probs.sum()
        if prob_sum > 1e-10:
            probs = probs / prob_sum
            # Asegurar suma exacta de 1.0
            probs = probs / probs.sum()
            return np.random.choice(items, p=probs)
        else:
            return np.random.choice(items)
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Exploración ultra-cuántica con caos garantizado.
        """
        n = len(coords)
        start_time = time.time()
        
        print(f"   🌪️  ULTRA-QUANTUM MODE: Caos total")
        print(f"   ∞ 'Cada átomo del universo es único'")
        
        solutions = []
        unique_costs = set()
        unique_tours = set()  # Hash de tours para verificar unicidad
        iteration = 0
        
        # FASE 1: CAOS TOTAL (70% tiempo)
        phase1_end = start_time + time_budget * 0.7
        
        print(f"   Fase 1: Generando universos paralelos infinitos...")
        
        while time.time() < phase1_end:
            iteration += 1
            
            # SEMILLA ULTRA-ÚNICA (nanosegundos + hash + iteración)
            nano_time = int(time.time() * 1000000000)
            chaos_hash = int(hashlib.md5(f"{nano_time}{iteration}".encode()).hexdigest()[:8], 16)
            quantum_seed = (nano_time + chaos_hash + iteration * 997) % (2**32)
            np.random.seed(quantum_seed)
            
            # RUIDO EXTREMO EN DISTANCIAS (0-30% aleatorio por celda)
            noise_matrix = np.random.uniform(0.7, 1.3, distances.shape)
            ultra_noisy_distances = distances * noise_matrix
            ultra_noisy_distances = np.maximum(ultra_noisy_distances, 0.1)
            
            # RUIDO EN COORDENADAS TAMBIÉN
            coord_noise = np.random.normal(0, coords.std() * 0.2, coords.shape)
            noisy_coords = coords + coord_noise
            
            # 50 ESTRATEGIAS DIFERENTES
            strategy = np.random.randint(0, 50)
            
            if strategy < 5:
                # Gravity ultra-ruidoso
                tour = self._ultra_quantum_gravity(noisy_coords, ultra_noisy_distances)
                strategy_name = "ultra_gravity"
                
            elif strategy < 10:
                # NN totalmente estocástico
                tour = self._ultra_stochastic_nn(noisy_coords, ultra_noisy_distances)
                strategy_name = "ultra_stochastic_nn"
                
            elif strategy < 13:
                # Tour random + mejora caótica
                tour = np.random.permutation(n)
                tour = self._chaotic_improvement(tour, ultra_noisy_distances)
                strategy_name = "random_chaos"
                
            elif strategy < 16:
                # Greedy con probabilidad inversa
                tour = self._reverse_greedy(noisy_coords, ultra_noisy_distances)
                strategy_name = "reverse_greedy"
                
            elif strategy < 19:
                # Construcción desde múltiples puntos
                tour = self._multi_start_construction(n, ultra_noisy_distances)
                strategy_name = "multi_construction"
                
            elif strategy < 22:
                # Spiral construction (espiral)
                tour = self._spiral_construction(noisy_coords)
                strategy_name = "spiral"
                
            elif strategy < 25:
                # Zigzag construction
                tour = self._zigzag_construction(noisy_coords)
                strategy_name = "zigzag"
                
            elif strategy < 28:
                # Random walk + optimization
                tour = self._random_walk_tour(n, ultra_noisy_distances)
                strategy_name = "random_walk"
                
            elif strategy < 31:
                # Cluster-based random
                tour = self._cluster_random(noisy_coords, ultra_noisy_distances)
                strategy_name = "cluster_random"
                
            elif strategy < 34:
                # Genetic-style mutation
                tour = self._genetic_mutation(n, ultra_noisy_distances)
                strategy_name = "genetic"
                
            elif strategy < 37:
                # Particle swarm inspired
                tour = self._swarm_inspired(noisy_coords, ultra_noisy_distances)
                strategy_name = "swarm"
                
            elif strategy < 40:
                # Ant colony inspired
                tour = self._ant_inspired(noisy_coords, ultra_noisy_distances)
                strategy_name = "ant"
                
            elif strategy < 43:
                # Simulated annealing extremo
                tour = self._extreme_annealing(n, ultra_noisy_distances)
                strategy_name = "extreme_annealing"
                
            elif strategy < 46:
                # Chaos theory inspired
                tour = self._chaos_theory(noisy_coords)
                strategy_name = "chaos_theory"
                
            else:
                # Quantum tunneling (saltos cuánticos)
                tour = self._quantum_tunneling(n, ultra_noisy_distances)
                strategy_name = "quantum_tunnel"
            
            # MUTACIONES MÚLTIPLES POST-CONSTRUCCIÓN (5-15 mutaciones)
            n_mutations = np.random.randint(5, 15)
            
            for _ in range(n_mutations):
                mutation = np.random.randint(0, 10)
                
                if mutation == 0:
                    # Swap aleatorio múltiple
                    for _ in range(np.random.randint(1, 5)):
                        i, j = np.random.randint(0, n, 2)
                        tour[i], tour[j] = tour[j], tour[i]
                        
                elif mutation == 1:
                    # Reversal con ruido
                    i, j = sorted(np.random.randint(0, n, 2))
                    if np.random.random() > 0.3:
                        tour[i:j] = tour[i:j][::-1]
                        
                elif mutation == 2:
                    # Scramble agresivo
                    i, j = sorted(np.random.randint(0, n, 2))
                    segment = tour[i:j].copy()
                    np.random.shuffle(segment)
                    tour[i:j] = segment
                    
                elif mutation == 3:
                    # Rotation aleatoria
                    shift = np.random.randint(1, n)
                    tour = np.roll(tour, shift)
                    
                elif mutation == 4:
                    # Inserción aleatoria
                    i = np.random.randint(0, n)
                    j = np.random.randint(0, n)
                    node = tour[i]
                    tour = np.delete(tour, i)
                    tour = np.insert(tour, j, node)
                    
                elif mutation == 5:
                    # Swap de segmentos
                    size = np.random.randint(2, n//4)
                    i = np.random.randint(0, n-size)
                    j = np.random.randint(0, n-size)
                    tour[i:i+size], tour[j:j+size] = tour[j:j+size].copy(), tour[i:i+size].copy()
                    
                elif mutation == 6:
                    # Transposición
                    i, j, k = sorted(np.random.choice(n, 3, replace=False))
                    tour = np.concatenate([tour[:i], tour[j:k], tour[i:j], tour[k:]])
                    
                elif mutation == 7:
                    # Mirror (espejo)
                    i, j = sorted(np.random.randint(0, n, 2))
                    tour[i:j] = tour[i:j][::-1]
                    
                elif mutation == 8:
                    # Rotate segment
                    i, j = sorted(np.random.randint(0, n, 2))
                    segment = tour[i:j].copy()
                    shift = np.random.randint(1, len(segment)) if len(segment) > 1 else 0
                    tour[i:j] = np.roll(segment, shift)
                    
                else:
                    # Random perturbation
                    for _ in range(np.random.randint(2, 6)):
                        i, j = sorted(np.random.randint(0, n, 2))
                        if np.random.random() > 0.5:
                            tour[i:j] = tour[i:j][::-1]
            
            # Mejora local SOLO con probabilidad (50%)
            if np.random.random() > 0.5:
                tour = self._chaotic_improvement(tour, distances)
            
            # Calcular costo REAL
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            
            # Hash del tour para verificar unicidad absoluta
            tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
            
            # Solo guardar si es TOTALMENTE único
            cost_rounded = round(cost, 3)  # Más precisión
            if tour_hash not in unique_tours:
                solutions.append((cost, tour, f"{strategy_name}_uq{iteration}"))
                unique_costs.add(cost_rounded)
                unique_tours.add(tour_hash)
            
            # Progress
            if iteration % 100 == 0:
                if solutions:
                    best = min(solutions, key=lambda x: x[0])[0]
                    ratio = len(solutions) / iteration * 100
                    print(f"      → {iteration} intentos, {len(solutions)} únicas ({ratio:.1f}%), mejor: {best:.2f}")
        
        print(f"   ✅ {len(solutions)} universos ÚNICOS de {iteration} intentos")
        print(f"   🎲 Unicidad: {len(solutions)/iteration*100:.1f}%")
        
        if len(solutions) == 0:
            print("   ⚠️ Generando solución fallback")
            tour = nearest_neighbor(coords, distances, start=0)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, tour, "fallback"))
        
        # FASE 2: REFINAMIENTO (30% tiempo)
        print(f"   Fase 2: Colapso de función de onda cuántica...")
        
        solutions.sort(key=lambda x: x[0])
        top_solutions = solutions[:30]
        
        improved = []
        for i, (cost, tour, name) in enumerate(top_solutions):
            if time.time() - start_time > time_budget * 0.95:
                break
            
            # Refinamiento aleatorio
            refine_method = np.random.randint(0, 3)
            
            if refine_method == 0:
                # LK clásico
                tour_ref = lin_kernighan_lite(coords, distances, max_iterations=400)
                cost_ref = sum(distances[tour_ref[j]][tour_ref[(j+1)%n]] for j in range(n))
                improved.append((cost_ref, tour_ref, f"lk_{name}"))
                
            elif refine_method == 1:
                # 3-opt agresivo
                tour_ref = three_opt_improvement(tour, distances, max_iter=10)
                cost_ref = sum(distances[tour_ref[j]][tour_ref[(j+1)%n]] for j in range(n))
                improved.append((cost_ref, tour_ref, f"3opt_{name}"))
                
            else:
                # Mejora caótica
                tour_ref = self._chaotic_improvement(tour, distances)
                cost_ref = sum(distances[tour_ref[j]][tour_ref[(j+1)%n]] for j in range(n))
                improved.append((cost_ref, tour_ref, f"chaos_{name}"))
        
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])
        
        best_cost, best_tour, best_name = all_solutions[0]
        
        total_time = time.time() - start_time
        
        print(f"   ✅ COLAPSO: {best_cost:.2f} en {total_time:.2f}s")
        print(f"   🏆 Universo ganador: {best_name}")
        
        metadata = {
            'strategies_used': ['ultra_quantum_chaos'],
            'total_solutions': len(all_solutions),
            'unique_solutions': len(unique_tours),
            'uniqueness_ratio': len(solutions) / iteration if iteration > 0 else 0,
            'best_strategy': best_name,
            'total_time': total_time
        }
        
        return best_tour.tolist(), best_cost, metadata
    
    def _ultra_quantum_gravity(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """Gravity con ruido extremo."""
        ultra_noisy = coords + np.random.normal(0, coords.std() * 0.3, coords.shape)
        return gravity_guided_tsp(ultra_noisy, distances)
    
    def _ultra_stochastic_nn(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """NN con máxima estocasticidad."""
        n = len(coords)
        start = np.random.randint(0, n)
        tour = [start]
        unvisited = set(range(n)) - {start}
        
        current = start
        while unvisited:
            dists = np.array([distances[current][j] for j in unvisited])
            
            # Temperatura muy aleatoria
            temp = np.random.uniform(0.01, 5.0)
            
            # Exponente aleatorio
            exp = np.random.uniform(0.5, 3.0)
            
            # Probabilidad con ruido extremo
            probs = np.exp(-dists**exp / (temp * dists.mean() + 1e-10))
            prob_sum = probs.sum()
            if prob_sum > 1e-10:
                probs = probs / prob_sum
                # Normalizar para que sumen exactamente 1.0
                probs = probs / probs.sum()
                next_city = np.random.choice(list(unvisited), p=probs)
            else:
                next_city = np.random.choice(list(unvisited))
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        
        return np.array(tour)
    
    def _chaotic_improvement(self, tour: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """2-opt pero acepta movimientos malos frecuentemente."""
        n = len(tour)
        
        for _ in range(np.random.randint(10, 30)):
            i, j = sorted(np.random.choice(n, 2, replace=False))
            
            if j > i + 1:
                # Probabilidad alta de aceptar cualquier movimiento
                if np.random.random() > 0.3:
                    tour[i+1:j+1] = tour[i+1:j+1][::-1]
        
        return tour
    
    def _reverse_greedy(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """Greedy que prefiere los LEJANOS."""
        n = len(coords)
        start = np.random.randint(0, n)
        tour = [start]
        unvisited = set(range(n)) - {start}
        
        current = start
        while unvisited:
            dists = [(distances[current][j], j) for j in unvisited]
            dists.sort(reverse=True)  # Los más LEJANOS primero
            
            # Top-k lejanos
            k = min(5, len(dists))
            candidates = [j for _, j in dists[:k]]
            
            next_city = np.random.choice(candidates)
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        
        return np.array(tour)
    
    def _multi_start_construction(self, n: int, distances: np.ndarray) -> np.ndarray:
        """Construcción desde múltiples semillas."""
        seeds = np.random.choice(n, min(5, n), replace=False)
        tour = list(seeds)
        remaining = set(range(n)) - set(seeds)
        
        while remaining:
            # Insertar en posición aleatoria-ish
            node = np.random.choice(list(remaining))
            pos = np.random.randint(0, len(tour) + 1)
            tour.insert(pos, node)
            remaining.remove(node)
        
        return np.array(tour)
    
    def _spiral_construction(self, coords: np.ndarray) -> np.ndarray:
        """Construcción en espiral desde el centro."""
        center = np.mean(coords, axis=0)
        angles = np.arctan2(coords[:, 1] - center[1], coords[:, 0] - center[0])
        
        # Agregar ruido a los ángulos
        noisy_angles = angles + np.random.normal(0, 0.5, len(angles))
        
        return np.argsort(noisy_angles)
    
    def _zigzag_construction(self, coords: np.ndarray) -> np.ndarray:
        """Zigzag con ruido."""
        x_sorted = np.argsort(coords[:, 0] + np.random.normal(0, coords[:, 0].std() * 0.2, len(coords)))
        return x_sorted
    
    def _random_walk_tour(self, n: int, distances: np.ndarray) -> np.ndarray:
        """Random walk con sesgo hacia cerca."""
        start = np.random.randint(0, n)
        tour = [start]
        unvisited = set(range(n)) - {start}
        
        current = start
        while unvisited:
            # 70% probabilidad de ir a uno cercano, 30% a cualquiera
            if np.random.random() < 0.7 and unvisited:
                dists = [(distances[current][j], j) for j in unvisited]
                dists.sort()
                k = min(10, len(dists))
                next_city = dists[np.random.randint(0, k)][1]
            else:
                next_city = np.random.choice(list(unvisited))
            
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        
        return np.array(tour)
    
    def _cluster_random(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """Agrupar aleatoriamente y conectar."""
        n = len(coords)
        n_clusters = np.random.randint(3, 10)
        
        # Asignar aleatoriamente a clusters
        clusters = [[] for _ in range(n_clusters)]
        for i in range(n):
            clusters[np.random.randint(0, n_clusters)].append(i)
        
        # Construir tour visitando clusters aleatoriamente
        tour = []
        np.random.shuffle(clusters)
        for cluster in clusters:
            np.random.shuffle(cluster)
            tour.extend(cluster)
        
        return np.array(tour)
    
    def _genetic_mutation(self, n: int, distances: np.ndarray) -> np.ndarray:
        """Mutación estilo genético."""
        tour = np.arange(n)
        np.random.shuffle(tour)
        
        # Múltiples tipos de mutación
        for _ in range(np.random.randint(5, 15)):
            mut = np.random.randint(0, 3)
            if mut == 0:
                # Swap
                i, j = np.random.randint(0, n, 2)
                tour[i], tour[j] = tour[j], tour[i]
            elif mut == 1:
                # Inversion
                i, j = sorted(np.random.randint(0, n, 2))
                tour[i:j] = tour[i:j][::-1]
            else:
                # Scramble
                i, j = sorted(np.random.randint(0, n, 2))
                segment = tour[i:j].copy()
                np.random.shuffle(segment)
                tour[i:j] = segment
        
        return tour
    
    def _swarm_inspired(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """Inspirado en particle swarm."""
        # Tour aleatorio con perturbaciones hacia 'mejor' dirección
        tour = np.random.permutation(len(coords))
        
        # Aplicar 'velocidades' aleatorias
        for _ in range(np.random.randint(3, 10)):
            i, j = sorted(np.random.choice(len(tour), 2, replace=False))
            if np.random.random() > 0.5:
                tour[i:j] = tour[i:j][::-1]
        
        return tour
    
    def _ant_inspired(self, coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
        """Inspirado en colonias de hormigas."""
        n = len(coords)
        
        # Feromonas aleatorias
        pheromones = np.random.uniform(0.1, 1.0, (n, n))
        
        start = np.random.randint(0, n)
        tour = [start]
        unvisited = set(range(n)) - {start}
        
        current = start
        while unvisited:
            # Probabilidad basada en feromona / distancia
            probs = []
            cities = list(unvisited)
            for j in cities:
                prob = pheromones[current][j] / (distances[current][j] + 1e-10)
                probs.append(prob)
            
            probs = np.array(probs)
            prob_sum = probs.sum()
            if prob_sum > 0:
                probs = probs / prob_sum
                # Asegurar que sumen exactamente 1
                probs = probs / probs.sum()
                next_city = np.random.choice(cities, p=probs)
            else:
                # Fallback: elegir uniformemente
                next_city = np.random.choice(cities)
            tour.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        
        return np.array(tour)
    
    def _extreme_annealing(self, n: int, distances: np.ndarray) -> np.ndarray:
        """Annealing con parámetros extremos."""
        tour = np.random.permutation(n)
        
        temp = np.random.uniform(5000, 20000)
        cooling = np.random.uniform(0.85, 0.98)
        
        for _ in range(np.random.randint(50, 150)):
            i, j = sorted(np.random.randint(0, n, 2))
            new_tour = tour.copy()
            new_tour[i:j] = new_tour[i:j][::-1]
            
            # Siempre aceptar con alta probabilidad
            if np.random.random() < np.exp(-1/temp) or np.random.random() < 0.3:
                tour = new_tour
            
            temp *= cooling
        
        return tour
    
    def _chaos_theory(self, coords: np.ndarray) -> np.ndarray:
        """Basado en teoría del caos."""
        n = len(coords)
        
        # Mapa logístico para generar secuencia caótica
        x = np.random.random()
        r = np.random.uniform(3.57, 4.0)  # Región caótica
        
        sequence = []
        for _ in range(n):
            x = r * x * (1 - x)
            sequence.append(x)
        
        # Ordenar índices por secuencia caótica
        return np.argsort(sequence)
    
    def _quantum_tunneling(self, n: int, distances: np.ndarray) -> np.ndarray:
        """Saltos cuánticos (tunneling)."""
        tour = np.random.permutation(n)
        
        # Múltiples 'túneles cuánticos'
        for _ in range(np.random.randint(10, 30)):
            # Teleportar segmento a nueva posición
            i, j = sorted(np.random.randint(0, n, 2))
            if j > i:
                segment = tour[i:j].copy()
                tour = np.delete(tour, slice(i, j))
                k = np.random.randint(0, len(tour) + 1)
                tour = np.insert(tour, k, segment)
        
        return tour


def ultra_quantum_solve(
    coords: np.ndarray,
    distances: np.ndarray,
    time_budget: float = 10.0
) -> Tuple[List[int], float]:
    """Función conveniente."""
    solver = UltraQuantumSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
