"""
SiNo System - Smart Selector (OPTIMIZED)
"""

from typing import Tuple, List, Optional
import numpy as np
from .types import DecisionType, SolverConfig
from .decision import DecisionEngine
from .confidence import ConfidenceAnalyzer


class SmartSelector:
    """Smart algorithm selector using PIMST's best algorithms."""
    
    def __init__(self, config: Optional[SolverConfig] = None):
        self.config = config or SolverConfig()
        self.decision_engine = DecisionEngine(self.config)
        self.confidence_analyzer = ConfidenceAnalyzer()
        self.stats = {
            'fast_path': 0,
            'sino_path': 0,
            'comprehensive_path': 0,
            'total_calls': 0
        }
    
    def select_and_solve(
        self,
        distances: np.ndarray,
        coordinates: Optional[np.ndarray] = None,
        graph_type: Optional[str] = None
    ) -> Tuple[List[int], float, dict]:
        """Select best algorithm and solve TSP."""
        self.stats['total_calls'] += 1
        n = len(distances)
        
        if coordinates is None:
            coordinates = self._derive_coordinates(distances)
        
        if graph_type is None:
            graph_type = self._classify_graph(coordinates)
        
        # Fast path for circles
        if graph_type == 'circle' and n <= 100:
            tour, cost = self._solve_circle_fast(coordinates)
            self.stats['fast_path'] += 1
            return tour, cost, {
                'decision': 'FAST_PATH',
                'graph_type': graph_type,
                'reason': 'Circle graph detected'
            }
        
        confidence = self.confidence_analyzer.analyze(distances, coordinates)
        decision = self.decision_engine.decide(confidence, n)
        
        if decision == DecisionType.NO:
            tour, cost = self._solve_with_quality(coordinates, distances, 'fast', n)
            self.stats['fast_path'] += 1
            return tour, cost, {'decision': 'NO', 'confidence': confidence, 'graph_type': graph_type}
        elif decision == DecisionType.SINO:
            tour, cost = self._solve_with_quality(coordinates, distances, 'balanced', n)
            self.stats['sino_path'] += 1
            return tour, cost, {'decision': 'SINO', 'confidence': confidence, 'graph_type': graph_type}
        else:
            tour, cost = self._solve_with_quality(coordinates, distances, 'optimal', n)
            self.stats['comprehensive_path'] += 1
            return tour, cost, {'decision': 'SI', 'confidence': confidence, 'graph_type': graph_type}
    
    def _derive_coordinates(self, distances: np.ndarray) -> np.ndarray:
        """Derive coordinates from distance matrix."""
        try:
            from sklearn.manifold import MDS
            mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
            return mds.fit_transform(distances)
        except:
            n = len(distances)
            np.random.seed(42)
            return np.random.rand(n, 2) * 100
    
    def _classify_graph(self, coordinates: np.ndarray) -> str:
        """Classify graph type."""
        n = len(coordinates)
        if n < 10:
            return 'random'
        
        center = coordinates.mean(axis=0)
        distances_from_center = np.linalg.norm(coordinates - center, axis=1)
        std_ratio = distances_from_center.std() / (distances_from_center.mean() + 1e-10)
        
        if std_ratio < 0.15:
            return 'circle'
        
        from scipy.spatial.distance import pdist
        all_distances = pdist(coordinates)
        dist_std = all_distances.std() / (all_distances.mean() + 1e-10)
        
        if dist_std < 0.3:
            return 'uniform'
        
        return 'random'
    
    def _solve_circle_fast(self, coordinates: np.ndarray) -> Tuple[List[int], float]:
        """Ultra-fast circle solver."""
        n = len(coordinates)
        center = coordinates.mean(axis=0)
        angles = np.arctan2(coordinates[:, 1] - center[1], coordinates[:, 0] - center[0])
        tour = list(np.argsort(angles))
        
        cost = 0.0
        for i in range(n):
            p1 = coordinates[tour[i]]
            p2 = coordinates[tour[(i + 1) % n]]
            cost += np.linalg.norm(p2 - p1)
        
        return tour, cost
    
    def _solve_with_quality(self, coords: np.ndarray, dist_matrix: np.ndarray, quality: str, n: int) -> Tuple[List[int], float]:
        """Solve using appropriate strategy with INCREASED starts for large problems."""
        
        # CRÍTICO: Para n>=85, usar MUCHOS más starts
        if n >= 85:
            from pimst.algorithms import multi_start_solver
            
            # Ajustar n_starts según tamaño y quality
            if quality == 'fast':
                n_starts = max(5, 50 // (n // 100 + 1))  # 5-10 starts
            elif quality == 'balanced':
                n_starts = max(15, 100 // (n // 100 + 1))  # 15-20 starts
            else:  # optimal
                n_starts = max(25, 150 // (n // 100 + 1))  # 25-30 starts
            
            tour = multi_start_solver(coords, dist_matrix, n_starts=n_starts)
            cost = sum(dist_matrix[tour[i]][tour[(i+1)%len(tour)]] for i in range(len(tour)))
            return tour.tolist(), cost
        
        # Para problemas más pequeños, usar solve_tsp_smart normal
        from pimst.algorithms import solve_tsp_smart
        tour = solve_tsp_smart(coords, dist_matrix, quality=quality)
        cost = sum(dist_matrix[tour[i]][tour[(i+1)%len(tour)]] for i in range(len(tour)))
        return tour.tolist(), cost
    
    def get_stats(self) -> dict:
        total = self.stats['total_calls']
        if total == 0:
            return self.stats
        return {
            **self.stats,
            'fast_path_pct': 100 * self.stats['fast_path'] / total,
            'sino_path_pct': 100 * self.stats['sino_path'] / total,
            'comprehensive_path_pct': 100 * self.stats['comprehensive_path'] / total
        }


def smart_solve(
    distances: np.ndarray,
    coordinates: Optional[np.ndarray] = None,
    graph_type: Optional[str] = None
) -> Tuple[List[int], float]:
    """Solve TSP using smart selector with PIMST algorithms."""
    selector = SmartSelector()
    tour, cost, _ = selector.select_and_solve(distances, coordinates, graph_type)
    return tour, cost
