"""
Geometric Hotspots Analyzer
============================

Identifica puntos críticos donde cambiar decisiones produce 
soluciones muy diferentes.

Inspirado en SINO: análisis geométrico de la estructura del problema.
"""

import numpy as np
import time
from typing import List, Tuple, Set


class HotspotAnalyzer:
    """
    Analiza geometría para encontrar puntos críticos.
    """
    
    def identify_hotspots(
        self, 
        coords: np.ndarray, 
        distances: np.ndarray,
        n_hotspots: int = 5
    ) -> List[int]:
        """
        Identifica hotspots: nodos donde las decisiones importan más.
        
        Hotspot = nodo con:
        1. Alta centralidad (muchos caminos lo cruzan)
        2. Múltiples opciones cercanas (decisiones ambiguas)
        3. Posición estratégica (esquinas, centros)
        """
        n = len(coords)
        hotspot_scores = np.zeros(n)
        
        # Factor 1: Centralidad (cercanía a muchos otros nodos)
        centrality = self._compute_centrality(coords, distances)
        
        # Factor 2: Ambigüedad (cuántos vecinos "igual de buenos")
        ambiguity = self._compute_ambiguity(distances)
        
        # Factor 3: Posición estratégica (extremos del espacio)
        strategic = self._compute_strategic_position(coords)
        
        # Combinar scores
        hotspot_scores = 0.4 * centrality + 0.4 * ambiguity + 0.2 * strategic
        
        # Top-k hotspots
        hotspot_indices = np.argsort(hotspot_scores)[-n_hotspots:][::-1]
        
        return hotspot_indices.tolist()
    
    def _compute_centrality(
        self, 
        coords: np.ndarray, 
        distances: np.ndarray
    ) -> np.ndarray:
        """
        Centralidad: promedio de distancias a otros nodos.
        Nodos centrales tienen distancia promedio baja.
        """
        n = len(coords)
        centrality = np.zeros(n)
        
        for i in range(n):
            # Distancia promedio a todos los demás
            avg_dist = np.mean([distances[i][j] for j in range(n) if j != i])
            # Invertir: menor distancia = mayor centralidad
            centrality[i] = 1.0 / (1.0 + avg_dist)
        
        # Normalizar
        centrality = (centrality - centrality.min()) / (centrality.max() - centrality.min() + 1e-10)
        
        return centrality
    
    def _compute_ambiguity(self, distances: np.ndarray) -> np.ndarray:
        """
        Ambigüedad: cuántos vecinos están a distancia similar.
        
        Si un nodo tiene 5 vecinos casi equidistantes, es ambiguo
        (cualquier decisión parece buena).
        """
        n = len(distances)
        ambiguity = np.zeros(n)
        
        for i in range(n):
            # Distancias a otros nodos (ordenadas)
            dists = sorted([distances[i][j] for j in range(n) if j != i])
            
            # Contar cuántos están dentro del 20% del más cercano
            min_dist = dists[0]
            threshold = min_dist * 1.2
            
            similar_neighbors = sum(1 for d in dists if d <= threshold)
            
            # Más vecinos similares = más ambigüedad
            ambiguity[i] = similar_neighbors / n
        
        # Normalizar
        ambiguity = (ambiguity - ambiguity.min()) / (ambiguity.max() - ambiguity.min() + 1e-10)
        
        return ambiguity
    
    def _compute_strategic_position(self, coords: np.ndarray) -> np.ndarray:
        """
        Posición estratégica: esquinas, bordes del convex hull.
        """
        n = len(coords)
        strategic = np.zeros(n)
        
        # Calcular centroide
        centroid = np.mean(coords, axis=0)
        
        # Distancia al centroide
        for i in range(n):
            dist_to_center = np.linalg.norm(coords[i] - centroid)
            strategic[i] = dist_to_center
        
        # Normalizar
        strategic = (strategic - strategic.min()) / (strategic.max() - strategic.min() + 1e-10)
        
        return strategic
    
    def generate_hotspot_biased_starts(
        self,
        hotspots: List[int],
        n_variants: int = 10
    ) -> List[Tuple[int, Set[int]]]:
        """
        Genera variantes de inicio basadas en hotspots.
        
        Returns:
            Lista de (start_node, forbidden_edges) para forzar diversidad
        """
        variants = []
        
        # Variante 1: Empezar desde cada hotspot
        for hotspot in hotspots:
            variants.append((hotspot, set()))
        
        # Variante 2: Empezar desde hotspot, prohibir conexión a otro hotspot
        for i, h1 in enumerate(hotspots):
            for h2 in hotspots[i+1:]:
                if len(variants) >= n_variants:
                    break
                # Prohibir arista entre h1 y h2
                variants.append((h1, {(h1, h2), (h2, h1)}))
        
        return variants[:n_variants]


class HotspotGuidedSolver:
    """
    Solver que usa hotspots para guiar exploración.
    """
    
    def __init__(self):
        self.analyzer = HotspotAnalyzer()
    
    def solve(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float, dict]:
        """
        Resolver con guía de hotspots.
        """
        from pimst.algorithms import (
            nearest_neighbor,
            lin_kernighan_lite,
            two_opt_improvement
        )
        
        n = len(coords)
        start_time = time.time()
        
        print(f"   🎯 HOTSPOT-GUIDED MODE")
        
        # Fase 1: Identificar hotspots
        print(f"   Fase 1: Análisis geométrico...")
        hotspots = self.analyzer.identify_hotspots(coords, distances, n_hotspots=min(10, n//10))
        print(f"   → Hotspots identificados: {hotspots}")
        
        # Fase 2: Generar variantes guiadas por hotspots
        print(f"   Fase 2: Exploración guiada por hotspots...")
        
        variants = self.analyzer.generate_hotspot_biased_starts(hotspots, n_variants=50)
        
        solutions = []
        
        for i, (start_node, forbidden) in enumerate(variants):
            if time.time() - start_time > time_budget * 0.6:
                break
            
            # NN desde hotspot
            tour = nearest_neighbor(coords, distances, start=start_node)
            
            # Si hay aristas prohibidas, perturbar el tour
            if forbidden:
                tour = self._perturb_tour_avoiding(tour, forbidden)
            
            # Mejorar con 2-opt
            tour, _ = two_opt_improvement(tour, distances)
            
            cost = sum(distances[tour[j]][tour[(j+1)%n]] for j in range(n))
            solutions.append((cost, tour, f'hotspot_variant_{i}'))
        
        print(f"   → {len(solutions)} variantes generadas")
        
        # Fase 3: Mejora intensiva de las mejores
        print(f"   Fase 3: Mejora intensiva...")
        
        solutions.sort(key=lambda x: x[0])
        top_solutions = solutions[:10]
        
        improved = []
        for cost, tour, name in top_solutions:
            if time.time() - start_time > time_budget * 0.8:
                break
            
            tour_lk = lin_kernighan_lite(coords, distances, max_iterations=500)
            cost_lk = sum(distances[tour_lk[i]][tour_lk[(i+1)%n]] for i in range(n))
            
            improved.append((cost_lk, tour_lk, f'lk_from_{name}'))
        
        all_solutions = solutions + improved
        all_solutions.sort(key=lambda x: x[0])
        
        best_cost, best_tour, best_name = all_solutions[0]
        
        total_time = time.time() - start_time
        
        print(f"   ✅ FINAL: {best_cost:.2f} en {total_time:.2f}s")
        
        metadata = {
            'strategies_used': ['hotspot_guided'],
            'hotspots': hotspots,
            'total_solutions': len(all_solutions),
            'best_strategy': best_name,
            'total_time': total_time
        }
        
        return best_tour.tolist(), best_cost, metadata
    
    def _perturb_tour_avoiding(
        self, 
        tour: np.ndarray, 
        forbidden: Set[Tuple[int, int]]
    ) -> np.ndarray:
        """
        Perturbar tour para evitar aristas prohibidas.
        """
        tour = tour.copy()
        n = len(tour)
        
        # Encontrar y romper aristas prohibidas
        for i in range(n):
            v1, v2 = tour[i], tour[(i+1) % n]
            if (v1, v2) in forbidden or (v2, v1) in forbidden:
                # Reversar segmento para romper la arista
                j = (i + n//4) % n
                tour[i:j] = tour[i:j][::-1]
        
        return tour


def hotspot_solve(
    coords: np.ndarray,
    distances: np.ndarray,
    time_budget: float = 10.0
) -> Tuple[List[int], float]:
    """Función conveniente."""
    solver = HotspotGuidedSolver()
    tour, cost, _ = solver.solve(coords, distances, time_budget)
    return tour, cost
