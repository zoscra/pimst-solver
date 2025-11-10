"""
SiNo System - Main API
======================

Simple, production-ready API for the SiNo selective solver system.
"""

from typing import List, Tuple, Optional, Dict
import numpy as np
from .types import DecisionType, SiNoResult, SolverConfig
from .decision import DecisionEngine
from .explorer import ExplorationEngine
from .confidence import ConfidenceAnalyzer


class SiNoSolver:
    """
    Main API for the SiNo (Selective Intelligent Solver) system.
    
    This solver uses a probabilistic decision engine to determine:
    - SI (Yes): Use comprehensive solver
    - SINO (Maybe): Use exploration with checkpoints
    - NO (No): Use fast heuristic
    
    Example:
        >>> from pimst.improved.sino import SiNoSolver
        >>> solver = SiNoSolver()
        >>> distances = np.array([[0, 1, 2], [1, 0, 3], [2, 3, 0]])
        >>> result = solver.solve(distances)
        >>> print(f"Tour: {result.tour}, Cost: {result.cost}")
    """
    
    def __init__(self, config: Optional[SolverConfig] = None):
        """
        Initialize the SiNo solver.
        
        Args:
            config: Optional configuration. If None, uses defaults.
        """
        self.config = config or SolverConfig()
        self.decision_engine = DecisionEngine(self.config)
        self.exploration_engine = ExplorationEngine(self.config)
        self.confidence_analyzer = ConfidenceAnalyzer()
        
    def solve(
        self, 
        distances: np.ndarray,
        coordinates: Optional[np.ndarray] = None
    ) -> SiNoResult:
        """
        Solve TSP using the SiNo system.
        
        Args:
            distances: Distance matrix (n x n)
            coordinates: Optional coordinates for visualization
            
        Returns:
            SiNoResult with tour, cost, and decision metadata
        """
        n = len(distances)
        
        # Step 1: Analyze confidence
        confidence = self.confidence_analyzer.analyze(distances, coordinates)
        
        # Step 2: Make decision
        decision = self.decision_engine.decide(confidence, n)
        
        # Step 3: Execute based on decision
        if decision == DecisionType.SI:
            tour, cost = self._solve_comprehensive(distances)
        elif decision == DecisionType.SINO:
            tour, cost = self._solve_with_exploration(distances, confidence)
        else:  # DecisionType.NO
            tour, cost = self._solve_fast(distances)
        
        return SiNoResult(
            tour=tour,
            cost=cost,
            decision=decision,
            confidence=confidence,
            n_nodes=n
        )
    
    def _solve_comprehensive(
        self, 
        distances: np.ndarray
    ) -> Tuple[List[int], float]:
        """
        Use comprehensive solver (for high-value instances).
        
        This is where you'd integrate your best algorithm (v14.4, LKH, etc.)
        """
        from pimst.algorithms import comprehensive_solver
        return comprehensive_solver(distances)
    
    def _solve_with_exploration(
        self, 
        distances: np.ndarray,
        confidence: float
    ) -> Tuple[List[int], float]:
        """
        Use exploration with checkpoints (for uncertain cases).
        """
        return self.exploration_engine.explore(distances, confidence)
    
    def _solve_fast(
        self, 
        distances: np.ndarray
    ) -> Tuple[List[int], float]:
        """
        Use fast heuristic (for easy instances).
        """
        from pimst.algorithms import fast_heuristic
        return fast_heuristic(distances)
    
    def batch_solve(
        self, 
        instances: List[np.ndarray]
    ) -> List[SiNoResult]:
        """
        Solve multiple TSP instances.
        
        Args:
            instances: List of distance matrices
            
        Returns:
            List of SiNoResult objects
        """
        return [self.solve(dist) for dist in instances]
    
    def get_statistics(self) -> Dict:
        """
        Get solver statistics.
        
        Returns:
            Dictionary with decision counts and performance metrics
        """
        return self.decision_engine.get_stats()


def solve_tsp(
    distances: np.ndarray,
    config: Optional[SolverConfig] = None
) -> SiNoResult:
    """
    Convenience function to solve a single TSP instance.
    
    Args:
        distances: Distance matrix
        config: Optional solver configuration
        
    Returns:
        SiNoResult with tour and metadata
        
    Example:
        >>> distances = np.array([[0, 1, 2], [1, 0, 3], [2, 3, 0]])
        >>> result = solve_tsp(distances)
        >>> print(result.tour)
    """
    solver = SiNoSolver(config)
    return solver.solve(distances)
