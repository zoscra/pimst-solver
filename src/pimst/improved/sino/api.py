"""
SiNo System - Main API
======================
"""

from typing import List, Tuple, Optional, Dict
import numpy as np
from .types import DecisionType, SiNoResult, SolverConfig
from .decision import DecisionEngine
from .explorer import ExplorationEngine
from .confidence import ConfidenceAnalyzer


class SiNoSolver:
    """Main API for the SiNo system using PIMST's best algorithms."""
    
    def __init__(self, config: Optional[SolverConfig] = None):
        self.config = config or SolverConfig()
        self.decision_engine = DecisionEngine(self.config)
        self.exploration_engine = ExplorationEngine(self.config)
        self.confidence_analyzer = ConfidenceAnalyzer()
        
    def solve(
        self, 
        distances: np.ndarray,
        coordinates: Optional[np.ndarray] = None
    ) -> SiNoResult:
        """Solve TSP using the SiNo system with PIMST algorithms."""
        n = len(distances)
        
        if coordinates is None:
            coordinates = self._derive_coordinates(distances)
        
        confidence = self.confidence_analyzer.analyze(distances, coordinates)
        decision = self.decision_engine.decide(confidence, n)
        
        if decision == DecisionType.SI:
            tour, cost = self._solve_with_quality(coordinates, distances, 'optimal')
        elif decision == DecisionType.SINO:
            tour, cost = self._solve_with_quality(coordinates, distances, 'balanced')
        else:
            tour, cost = self._solve_with_quality(coordinates, distances, 'fast')
        
        return SiNoResult(
            tour=tour,
            cost=cost,
            decision=decision,
            confidence=confidence,
            n_nodes=n
        )
    
    def _derive_coordinates(self, distances: np.ndarray) -> np.ndarray:
        """Derive approximate coordinates from distance matrix."""
        try:
            from sklearn.manifold import MDS
            mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
            coords = mds.fit_transform(distances)
            return coords
        except:
            n = len(distances)
            np.random.seed(42)
            return np.random.rand(n, 2) * 100
    
    def _solve_with_quality(self, coords: np.ndarray, dist_matrix: np.ndarray, quality: str) -> Tuple[List[int], float]:
        """Solve using solve_tsp_smart with specified quality."""
        from pimst.algorithms import solve_tsp_smart
        tour = solve_tsp_smart(coords, dist_matrix, quality=quality)
        cost = sum(dist_matrix[tour[i]][tour[(i+1) % len(tour)]] for i in range(len(tour)))
        return tour.tolist(), cost
    
    def batch_solve(self, instances: List[np.ndarray]) -> List[SiNoResult]:
        return [self.solve(dist) for dist in instances]
    
    def get_statistics(self) -> Dict:
        return self.decision_engine.get_stats()


def solve_tsp(distances: np.ndarray, config: Optional[SolverConfig] = None) -> SiNoResult:
    """Convenience function to solve a single TSP instance."""
    solver = SiNoSolver(config)
    return solver.solve(distances)
