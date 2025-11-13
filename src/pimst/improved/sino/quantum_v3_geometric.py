"""
Quantum Solver V3 - Con principios geométricos
===============================================

Mejoras basadas en patrones universales de tours óptimos:
1. Sin cruces (eliminación automática)
2. Aristas locales (k-nearest neighbors)
3. Respeto a convex hull
4. Giros suaves (ángulos >60°)
5. Filtrado por quality score geométrico
"""

import numpy as np
import time
import hashlib
from typing import Tuple, List
from scipy.spatial import ConvexHull, Delaunay
from pimst.algorithms import (
    gravity_guided_tsp,
    lin_kernighan_lite,
    multi_start_solver,
    two_opt_improvement,
    three_opt_improvement,
    nearest_neighbor
)


def segments_intersect(p1, p2, p3, p4):
    """Verificar si dos segmentos se intersectan."""
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    
    return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)


def remove_crossings(tour, coords):
    """Eliminar todos los cruces mediante 2-opt."""
    n = len(tour)
    improved = True
    iterations = 0
    max_iterations = 100
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        for i in range(n - 1):
            for j in range(i + 2, n):
                if j == n - 1 and i == 0:
                    continue
                
                # Verificar si las aristas se cruzan
                p1 = coords[tour[i]]
                p2 = coords[tour[i+1]]
                p3 = coords[tour[j]]
                p4 = coords[tour[(j+1) % n]]
                
                if segments_intersect(p1, p2, p3, p4):
                    # Invertir segmento para eliminar cruce
                    tour[i+1:j+1] = tour[i+1:j+1][::-1]
                    improved = True
                    break
            
            if improved:
                break
    
    return tour


def count_crossings(tour, coords):
    """Contar número de cruces en el tour."""
    n = len(tour)
    crossings = 0
    
    for i in range(n - 1):
        for j in range(i + 2, n):
            if j == n - 1 and i == 0:
                continue
            
            p1 = coords[tour[i]]
            p2 = coords[tour[i+1]]
            p3 = coords[tour[j]]
            p4 = coords[tour[(j+1) % n]]
            
            if segments_intersect(p1, p2, p3, p4):
                crossings += 1
    
    return crossings


def check_local_quality(tour, distances, k=7):
    """Verificar qué porcentaje de aristas son locales."""
    n = len(tour)
    local_edges = 0
    
    for i in range(n):
        current = tour[i]
        next_city = tour[(i+1) % n]
        
        # k vecinos más cercanos
        neighbors = np.argsort(distances[current])[:k+1]  # +1 porque incluye a sí mismo
        
        if next_city in neighbors:
            local_edges += 1
    
    return local_edges / n


def calculate_turn_angle(p1, p2, p3):
    """Calcular ángulo de giro en p2."""
    v1 = p1 - p2
    v2 = p3 - p2
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 < 1e-10 or norm2 < 1e-10:
        return 180.0
    
    cos_angle = np.dot(v1, v2) / (norm1 * norm2)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle = np.arccos(cos_angle)
    
    return np.degrees(angle)


def penalize_sharp_turns(tour, coords):
    """Penalizar giros bruscos (<60°)."""
    n = len(tour)
    penalty = 0
    sharp_turns = 0
    
    for i in range(n):
        p1 = coords[tour[i-1]]
        p2 = coords[tour[i]]
        p3 = coords[tour[(i+1) % n]]
        
        angle = calculate_turn_angle(p1, p2, p3)
        
        if angle < 60:
            sharp_turns += 1
            penalty += (60 - angle)
    
    return penalty, sharp_turns


def calculate_edge_balance(tour, distances):
    """Calcular coeficiente de variación de longitudes."""
    n = len(tour)
    edge_lengths = []
    
    for i in range(n):
        length = distances[tour[i]][tour[(i+1) % n]]
        edge_lengths.append(length)
    
    mean = np.mean(edge_lengths)
    std = np.std(edge_lengths)
    
    if mean < 1e-10:
        return 0.0
    
    return std / mean


def quality_score(tour, coords, distances):
    """
    Score de calidad geométrica.
    Menor = mejor.
    """
    n = len(tour)
    
    # 1. Cruces (peso MUY alto - esto es fatal)
    crossings = count_crossings(tour, coords)
    
    # 2. Aristas locales (queremos ratio alto)
    local_ratio = check_local_quality(tour, distances, k=7)
    
    # 3. Giros bruscos
    turn_penalty, sharp_turns = penalize_sharp_turns(tour, coords)
    
    # 4. Balance de aristas
    cv = calculate_edge_balance(tour, distances)
    
    # Combinar (ajustar pesos según importancia)
    score = (
        10000 * crossings +           # Cruces son inaceptables
        500 * (1 - local_ratio) +     # Preferir aristas locales
        50 * turn_penalty +           # Giros suaves
        200 * cv                      # Balance moderado
    )
    
    return score, {
        'crossings': crossings,
        'local_ratio': local_ratio,
        'sharp_turns': sharp_turns,
        'cv': cv
    }


class QuantumV3Solver:
    """
    Quantum Solver con validación geométrica.
    """
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Quantum con filtros geométricos.
        """
        n = len(coords)
        start_time = time.time()
        
        print(f"   🎯 QUANTUM V3: Principios geométricos")
        print(f"   📐 Sin cruces + Aristas locales + Giros suaves")
        
        solutions = []
        unique_tours = set()
        iteration = 0
        
        noise_level = 0.15
        
        # Stats
        rejected_crossings = 0
        rejected_quality = 0
        
        # FASE 1: EXPLORACIÓN CON FILTROS (60% tiempo)
        phase1_end = start_time + time_budget * 0.6
        
        print(f"   Fase 1: Exploración con validación geométrica...")
        
        while time.time() < phase1_end:
            iteration += 1
            quantum_seed = (int(time.time() * 1000000000) + iteration * 997) % (2**32)
            np.random.seed(quantum_seed)
            
            # Ruido en distancias
            noise_matrix = np.random.uniform(1 - noise_level, 1 + noise_level, distances.shape)
            noisy_distances = distances * noise_matrix
            noisy_distances = np.maximum(noisy_distances, 0.1)
            
            # Estrategia (40 variantes)
            strategy = np.random.randint(0, 40)
            
            if strategy < 8:
                if np.random.random() > 0.5:
                    coord_noise = np.random.normal(0, coords.std() * noise_level, coords.shape)
                    noisy_coords = coords + coord_noise
                    tour = gravity_guided_tsp(noisy_coords, noisy_distances)
                else:
                    tour = gravity_guided_tsp(coords, noisy_distances)
                strategy_name = "gravity"
                
            elif strategy < 16:
                start_node = np.random.randint(0, n)
                tour = nearest_neighbor(coords, noisy_distances, start=start_node)
                strategy_name = "nn"
                
            elif strategy < 20:
                n_starts = np.random.choice([2, 3, 5])
                tour = multi_start_solver(coords, noisy_distances, n_starts=n_starts)
                strategy_name = f"multistart_{n_starts}"
                
            elif strategy < 24:
                tour = lin_kernighan_lite(coords, noisy_distances, max_iterations=100)
                strategy_name = "lk_noisy"
                
            else:
                tour = np.random.permutation(n)
                strategy_name = "random"
            
            # Mutaciones
            n_mutations = np.random.randint(5, 15)
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
                    i = np.random.randint(0, n)
                    j = np.random.randint(0, n)
                    node = tour[i]
                    tour = np.delete(tour, i)
                    tour = np.insert(tour, j, node)
            
            # Mejora local básica
            if np.random.random() > 0.3:
                tour, _ = two_opt_improvement(tour, distances)
            
            # VALIDACIÓN GEOMÉTRICA
            q_score, q_details = quality_score(tour, coords, distances)
            
            # Filtro 1: Rechazar si tiene cruces
            if q_details['crossings'] > 0:
                # Intentar arreglar
                tour = remove_crossings(tour, coords)
                q_score, q_details = quality_score(tour, coords, distances)
                
                if q_details['crossings'] > 0:
                    rejected_crossings += 1
                    continue  # Todavía tiene cruces, descartar
            
            # Filtro 2: Rechazar si calidad geométrica muy mala
            if q_score > 1000:  # Umbral ajustable
                rejected_quality += 1
                continue
            
            # Calcular costo REAL
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            
            # Hash
            tour_hash = hashlib.md5(tour.tobytes()).hexdigest()
            
            if tour_hash not in unique_tours:
                # Combinar costo con quality score
                combined_score = cost + q_score * 10  # Ajustar peso
                solutions.append((cost, combined_score, tour, strategy_name, q_details))
                unique_tours.add(tour_hash)
            
            # Progress
            if iteration % 100 == 0 and solutions:
                best = min(solutions, key=lambda x: x[0])[0]
                avg_quality = np.mean([s[4]['local_ratio'] for s in solutions])
                print(f"      → {iteration} iter, {len(solutions)} válidas, mejor: {best:.2f}, local: {avg_quality:.1%}")
        
        print(f"   ✅ {len(solutions)} soluciones geométricamente válidas")
        print(f"   ❌ Rechazadas: {rejected_crossings} (cruces), {rejected_quality} (calidad)")
        
        if len(solutions) == 0:
            print("   ⚠️ Generando solución fallback")
            tour = nearest_neighbor(coords, distances, start=0)
            tour = remove_crossings(tour, coords)
            cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            solutions.append((cost, cost, tour, "fallback", {}))
        
        # FASE 2: REFINAMIENTO GEOMÉTRICO (40% tiempo)
        print(f"   Fase 2: Refinamiento con validación...")
        
        # Ordenar por combined_score (costo + geometría)
        solutions.sort(key=lambda x: x[1])
        top_solutions = solutions[:40]
        
        improved = []
        for i, (cost, combined, tour, name, q_details) in enumerate(top_solutions):
            if time.time() - start_time > time_budget * 0.95:
                break
            
            # LK potente
            if np.random.random() > 0.3:
                tour_lk = lin_kernighan_lite(coords, distances, max_iterations=500)
            else:
                tour_temp = three_opt_improvement(tour, distances, max_iter=10)
                tour_lk = lin_kernighan_lite(coords, distances, max_iterations=300)
            
            # Eliminar cruces si tiene
            tour_lk = remove_crossings(tour_lk, coords)
            
            cost_lk = sum(distances[tour_lk[i]][tour_lk[(i+1)%n]] for i in range(n))
            q_score_lk, q_details_lk = quality_score(tour_lk, coords, distances)
            
            improved.append((cost_lk, cost_lk + q_score_lk * 10, tour_lk, f"lk_{name}", q_details_lk))
            
            if (i + 1) % 10 == 0:
                best = min(improved, key=lambda x: x[0])[0]
                print(f"      → {i+1}/{len(top_solutions)} refinados, mejor: {best:.2f}")
        
        # Combinar todas
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])  # Ordenar por costo real
        
        best_cost, _, best_tour, best_name, best_q = all_solutions[0]
        
        total_time = time.time() - start_time
        
        print(f"   ✅ FINAL: {best_cost:.2f} en {total_time:.2f}s")
        print(f"   🏆 Ganador: {best_name}")
        print(f"   📐 Calidad geométrica:")
        print(f"      Cruces: {best_q.get('crossings', 0)}")
        print(f"      Aristas locales: {best_q.get('local_ratio', 0):.1%}")
        print(f"      Giros bruscos: {best_q.get('sharp_turns', 0)}")
        print(f"      Balance (CV): {best_q.get('cv', 0):.3f}")
        
        metadata = {
            'strategies_used': ['quantum_v3_geometric'],
            'total_solutions': len(all_solutions),
            'unique_solutions': len(unique_tours),
            'rejected_crossings': rejected_crossings,
            'rejected_quality': rejected_quality,
            'best_strategy': best_name,
            'geometric_quality': best_q,
            'total_time': total_time
        }
        
        return best_tour.tolist(), best_cost, metadata


def quantum_v3_solve(coords, distances, time_budget=10.0):
    """Función conveniente."""
    solver = QuantumV3Solver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
