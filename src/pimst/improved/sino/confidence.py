"""
SiNo System - Confidence Calculator
====================================

Core module for calculating confidence in decision moves.

The confidence calculation combines 4 factors:
1. Graph type patterns (40%) - Structural expectations
2. Distance metrics (30%) - Geometric proximity
3. Tour context (20%) - Current state awareness
4. Local structure (10%) - Neighborhood analysis

Confidence ranges:
- [0.80, 1.00] → SI (High confidence, execute)
- [0.20, 0.80] → SINO (Moderate, checkpoint)
- [0.00, 0.20] → NO (Low confidence, discard)
"""

import numpy as np
from typing import List, Tuple, Set, Optional
from scipy.spatial import distance_matrix
from .types import (
    GraphType,
    SiNoConfig,
    DEFAULT_CONFIG,
    get_decision_type,
    CIRCLE_CONFIDENCE_RULES,
    GRID_CONFIDENCE_RULES,
    CLUSTERED_CONFIDENCE_RULES,
    RANDOM_CONFIDENCE_RULES,
    DIAGONAL_CONFIDENCE_RULES,
)
from .decision import Decision, TourContext


class ConfidenceCalculator:
    """
    Calculates confidence scores for move decisions.
    
    The calculator uses 4 weighted factors to determine confidence:
    - Graph type patterns (40%)
    - Distance metrics (30%)
    - Tour context (20%)
    - Local structure (10%)
    
    Attributes:
        points: Numpy array of city coordinates
        dist_matrix: Precomputed distance matrix
        config: Configuration parameters
        graph_type: Type of graph being solved
    
    Example:
        >>> calc = ConfidenceCalculator(points, GraphType.RANDOM)
        >>> confidence = calc.calculate(current=0, candidate=5, context)
        >>> print(f"Confidence: {confidence:.2f}")
    """
    
    def __init__(
        self,
        points: np.ndarray,
        graph_type: GraphType,
        config: SiNoConfig = DEFAULT_CONFIG
    ):
        """
        Initialize confidence calculator.
        
        Args:
            points: Array of city coordinates (N x 2)
            graph_type: Type of graph structure
            config: Configuration parameters
        """
        self.points = points
        self.N = len(points)
        self.graph_type = graph_type
        self.config = config
        
        # Precompute distance matrix
        self.dist_matrix = distance_matrix(points, points)
        
        # Cache for repeated calculations
        self._distance_cache = {}
        self._structure_cache = {}
    
    def calculate(
        self,
        current: int,
        candidate: int,
        context: TourContext
    ) -> float:
        """
        Calculate confidence for moving from current to candidate.
        
        Args:
            current: Current node
            candidate: Candidate next node
            context: Current tour context
        
        Returns:
            Confidence score [0.0, 1.0]
        """
        # Factor 1: Graph type patterns (40%)
        graph_confidence = self._calculate_graph_type_confidence(
            current, candidate, context
        )
        
        # Factor 2: Distance metrics (30%)
        distance_confidence = self._calculate_distance_confidence(
            current, candidate, context.available
        )
        
        # Factor 3: Tour context (20%)
        tour_confidence = self._calculate_tour_context_confidence(
            current, candidate, context
        )
        
        # Factor 4: Local structure (10%)
        structure_confidence = self._calculate_local_structure_confidence(
            current, candidate, context
        )
        
        # Weighted combination
        total_confidence = (
            self.config.GRAPH_TYPE_WEIGHT * graph_confidence +
            self.config.DISTANCE_WEIGHT * distance_confidence +
            self.config.TOUR_CONTEXT_WEIGHT * tour_confidence +
            self.config.LOCAL_STRUCTURE_WEIGHT * structure_confidence
        )
        
        return np.clip(total_confidence, 0.0, 1.0)
    
    def _calculate_graph_type_confidence(
        self,
        current: int,
        candidate: int,
        context: TourContext
    ) -> float:
        """
        Calculate confidence based on graph type patterns.
        
        Different graph types have different structural patterns:
        - Circle: Adjacent nodes high confidence
        - Grid: Orthogonal moves preferred
        - Clustered: Intra-cluster moves high
        - Random: Distance-based only
        - Diagonal: Line-following high
        
        Args:
            current: Current node
            candidate: Candidate node
            context: Tour context
        
        Returns:
            Confidence [0.0, 1.0]
        """
        if self.graph_type == GraphType.CIRCLE:
            return self._confidence_circle(current, candidate)
        elif self.graph_type == GraphType.GRID:
            return self._confidence_grid(current, candidate)
        elif self.graph_type == GraphType.CLUSTERED:
            return self._confidence_clustered(current, candidate, context)
        elif self.graph_type == GraphType.DIAGONAL:
            return self._confidence_diagonal(current, candidate)
        else:  # RANDOM
            return self._confidence_random(current, candidate, context)
    
    def _confidence_circle(self, current: int, candidate: int) -> float:
        """Confidence for circle graphs - adjacent nodes high."""
        # Check if nodes are adjacent in sorted order
        dist = self.dist_matrix[current, candidate]
        
        # Find all distances from current
        all_distances = sorted([
            self.dist_matrix[current, i] 
            for i in range(self.N) if i != current
        ])
        
        if len(all_distances) < 2:
            return 0.60
        
        # Is it the closest or second closest?
        if dist == all_distances[0]:
            return CIRCLE_CONFIDENCE_RULES['adjacent']  # 0.95
        elif dist == all_distances[1]:
            return CIRCLE_CONFIDENCE_RULES['near_adjacent']  # 0.65
        else:
            return CIRCLE_CONFIDENCE_RULES['far']  # 0.15
    
    def _confidence_grid(self, current: int, candidate: int) -> float:
        """Confidence for grid graphs - orthogonal moves preferred."""
        curr_pos = self.points[current]
        cand_pos = self.points[candidate]
        
        # Check if move is orthogonal (aligned in x or y)
        dx = abs(cand_pos[0] - curr_pos[0])
        dy = abs(cand_pos[1] - curr_pos[1])
        
        # Orthogonal move (one coordinate same)
        if dx < 1e-6 or dy < 1e-6:
            dist = self.dist_matrix[current, candidate]
            # Check if it's a near orthogonal move
            median_dist = np.median(self.dist_matrix[current])
            if dist < median_dist:
                return GRID_CONFIDENCE_RULES['orthogonal']  # 0.90
            else:
                return GRID_CONFIDENCE_RULES['diagonal_near']  # 0.55
        
        # Diagonal move - depends on distance
        dist = self.dist_matrix[current, candidate]
        median_dist = np.median(self.dist_matrix[current])
        
        if dist < median_dist * 1.5:
            return GRID_CONFIDENCE_RULES['diagonal_near']  # 0.55
        elif dist < median_dist * 2.5:
            return GRID_CONFIDENCE_RULES['diagonal_far']  # 0.40
        else:
            return GRID_CONFIDENCE_RULES['jump']  # 0.10
    
    def _confidence_clustered(
        self,
        current: int,
        candidate: int,
        context: TourContext
    ) -> float:
        """Confidence for clustered graphs - intra-cluster high."""
        # Simplified cluster detection: use distance threshold
        dist = self.dist_matrix[current, candidate]
        
        # Get distances from current to all nodes
        distances = self.dist_matrix[current]
        available_distances = [distances[i] for i in context.available]
        
        if not available_distances:
            return 0.50
        
        median_dist = np.median(available_distances)
        
        # Same cluster: distance < median
        if dist < median_dist * 0.7:
            return CLUSTERED_CONFIDENCE_RULES['same_cluster']  # 0.85
        # Adjacent cluster: distance near median
        elif dist < median_dist * 1.5:
            return CLUSTERED_CONFIDENCE_RULES['adjacent_cluster']  # 0.50
        # Far cluster
        else:
            return CLUSTERED_CONFIDENCE_RULES['far_cluster']  # 0.25
    
    def _confidence_diagonal(self, current: int, candidate: int) -> float:
        """Confidence for diagonal graphs - line-following high."""
        # Check if candidate continues the line pattern
        if len(self.points) < 3:
            return 0.60
        
        # Simple heuristic: is candidate the nearest node?
        distances = sorted([
            (i, self.dist_matrix[current, i])
            for i in range(self.N) if i != current
        ], key=lambda x: x[1])
        
        if len(distances) < 2:
            return 0.60
        
        if distances[0][0] == candidate:
            return DIAGONAL_CONFIDENCE_RULES['next_in_line']  # 0.95
        elif distances[1][0] == candidate:
            return DIAGONAL_CONFIDENCE_RULES['skip_one']  # 0.50
        else:
            return DIAGONAL_CONFIDENCE_RULES['skip_many']  # 0.15
    
    def _confidence_random(
        self,
        current: int,
        candidate: int,
        context: TourContext
    ) -> float:
        """Confidence for random graphs - distance-based only."""
        dist = self.dist_matrix[current, candidate]
        
        # Get distances to available nodes
        available_distances = sorted([
            self.dist_matrix[current, i] 
            for i in context.available
        ])
        
        if not available_distances:
            return 0.50
        
        # Classify by distance percentile
        if dist == available_distances[0]:
            return RANDOM_CONFIDENCE_RULES['nearest']  # 0.60
        elif dist < np.percentile(available_distances, 33):
            return RANDOM_CONFIDENCE_RULES['near']  # 0.45
        elif dist < np.percentile(available_distances, 66):
            return RANDOM_CONFIDENCE_RULES['medium']  # 0.30
        else:
            return RANDOM_CONFIDENCE_RULES['far']  # 0.15
    
    def _calculate_distance_confidence(
        self,
        current: int,
        candidate: int,
        available: Set[int]
    ) -> float:
        """
        Calculate confidence based on relative distance.
        
        Closer nodes generally have higher confidence.
        
        Args:
            current: Current node
            candidate: Candidate node
            available: Available nodes
        
        Returns:
            Confidence [0.0, 1.0]
        """
        dist = self.dist_matrix[current, candidate]
        
        # Get distances to all available nodes
        available_distances = [
            self.dist_matrix[current, i] for i in available
        ]
        
        if not available_distances:
            return 0.50
        
        min_dist = min(available_distances)
        max_dist = max(available_distances)
        
        # Normalize distance to [0, 1] (inverted - closer is better)
        if max_dist > min_dist:
            normalized = 1.0 - (dist - min_dist) / (max_dist - min_dist)
        else:
            normalized = 1.0
        
        return normalized
    
    def _calculate_tour_context_confidence(
        self,
        current: int,
        candidate: int,
        context: TourContext
    ) -> float:
        """
        Calculate confidence based on tour context.
        
        Considers:
        - Tour completion progress
        - Avoiding creating crossings
        - Maintaining reasonable tour length
        
        Args:
            current: Current node
            candidate: Candidate node
            context: Tour context
        
        Returns:
            Confidence [0.0, 1.0]
        """
        confidence = 0.60  # Base confidence
        
        # Factor 1: Progress bonus (later in tour = more conservative)
        if context.progress > 0.8:
            # Near end of tour - prefer completing efficiently
            dist = self.dist_matrix[current, candidate]
            available_distances = [
                self.dist_matrix[current, i] for i in context.available
            ]
            if available_distances:
                median_dist = np.median(available_distances)
                if dist < median_dist:
                    confidence += 0.20
                else:
                    confidence -= 0.10
        
        # Factor 2: Avoid backtracking
        if len(context.tour) >= 2:
            prev_node = context.tour[-2]
            # Penalize if going back to previous node's neighbor
            dist_prev_to_cand = self.dist_matrix[prev_node, candidate]
            dist_curr_to_cand = self.dist_matrix[current, candidate]
            
            if dist_prev_to_cand < dist_curr_to_cand * 0.5:
                confidence -= 0.15  # Likely backtracking
        
        return np.clip(confidence, 0.0, 1.0)
    
    def _calculate_local_structure_confidence(
        self,
        current: int,
        candidate: int,
        context: TourContext
    ) -> float:
        """
        Calculate confidence based on local neighborhood structure.
        
        Analyzes the local connectivity pattern around the candidate.
        
        Args:
            current: Current node
            candidate: Candidate node
            context: Tour context
        
        Returns:
            Confidence [0.0, 1.0]
        """
        # Check how many nearby nodes are available near candidate
        # More available neighbors = better for future moves
        
        dist_to_candidate = self.dist_matrix[current, candidate]
        
        # Find available nodes near the candidate
        nearby_count = 0
        for node in context.available:
            if node == candidate:
                continue
            dist_from_candidate = self.dist_matrix[candidate, node]
            if dist_from_candidate < dist_to_candidate * 1.5:
                nearby_count += 1
        
        # Normalize by remaining nodes
        if context.remaining_nodes > 1:
            nearby_ratio = nearby_count / (context.remaining_nodes - 1)
        else:
            nearby_ratio = 0.5
        
        # More nearby options = higher confidence
        return 0.4 + 0.6 * nearby_ratio
    
    def evaluate_all_options(
        self,
        current: int,
        available: Set[int],
        context: TourContext
    ) -> List[Decision]:
        """
        Evaluate all available moves and create Decision objects.
        
        Args:
            current: Current node
            available: Set of available nodes
            context: Tour context
        
        Returns:
            List of Decision objects sorted by confidence (descending)
        
        Example:
            >>> decisions = calc.evaluate_all_options(0, {1,2,3}, context)
            >>> for d in decisions:
            ...     print(f"Node {d.node}: {d.confidence:.2f} ({d.type.value})")
        """
        decisions = []
        
        for candidate in available:
            # Calculate confidence
            confidence = self.calculate(current, candidate, context)
            
            # Determine decision type
            decision_type = get_decision_type(confidence, self.config)
            
            # Create reason string
            reason = self._create_reason(
                current, candidate, confidence, context
            )
            
            # Get cost (distance)
            cost = self.dist_matrix[current, candidate]
            
            # Create Decision
            decision = Decision(
                node=candidate,
                confidence=confidence,
                type=decision_type,
                reason=reason,
                cost=cost
            )
            
            decisions.append(decision)
        
        # Sort by confidence (descending)
        decisions.sort(key=lambda d: d.confidence, reverse=True)
        
        return decisions
    
    def _create_reason(
        self,
        current: int,
        candidate: int,
        confidence: float,
        context: TourContext
    ) -> str:
        """Create human-readable reason for confidence level."""
        dist = self.dist_matrix[current, candidate]
        
        reasons = []
        
        # Graph type reason
        if self.graph_type == GraphType.CIRCLE and confidence > 0.85:
            reasons.append("adjacent in circle")
        elif self.graph_type == GraphType.GRID and confidence > 0.85:
            reasons.append("orthogonal move in grid")
        elif self.graph_type == GraphType.CLUSTERED and confidence > 0.80:
            reasons.append("same cluster")
        elif self.graph_type == GraphType.DIAGONAL and confidence > 0.90:
            reasons.append("continues line")
        
        # Distance reason
        available_distances = [
            self.dist_matrix[current, i] for i in context.available
        ]
        if available_distances:
            if dist == min(available_distances):
                reasons.append("nearest available")
            elif dist < np.median(available_distances):
                reasons.append("close distance")
        
        # Default
        if not reasons:
            reasons.append(f"{self.graph_type.value} graph")
        
        return ", ".join(reasons)


if __name__ == "__main__":
    # Test confidence calculator
    print("=" * 60)
    print("Testing ConfidenceCalculator")
    print("=" * 60)
    
    # Create simple test case
    points = np.array([
        [0, 0], [1, 0], [2, 0], [3, 0], [4, 0]  # Diagonal line
    ])
    
    context = TourContext(
        tour=[0],
        available={1, 2, 3, 4},
        graph_type=GraphType.DIAGONAL,
        total_nodes=5
    )
    
    calc = ConfidenceCalculator(points, GraphType.DIAGONAL)
    
    print("\nEvaluating moves from node 0:")
    decisions = calc.evaluate_all_options(0, context.available, context)
    
    for decision in decisions:
        print(f"  Node {decision.node}: "
              f"{decision.confidence:.2f} "
              f"({decision.type.value}) - "
              f"{decision.reason}")
    
    print("\n" + "=" * 60)
    print("✅ ConfidenceCalculator test complete")
    print("=" * 60)


# ============================================================================
# Confidence Analyzer for API
# ============================================================================

class ConfidenceAnalyzer:
    """Analyze problem to determine confidence."""
    
    def analyze(self, distances, coordinates=None):
        """Return confidence level (0-1)."""
        import numpy as np
        n = len(distances)
        
        # Base on size
        if n < 10:
            base = 0.3
        elif n < 50:
            base = 0.5
        else:
            base = 0.7
        
        # Check if circular
        if coordinates is not None:
            center = coordinates.mean(axis=0)
            dists = np.linalg.norm(coordinates - center, axis=1)
            std_ratio = dists.std() / (dists.mean() + 1e-10)
            
            if std_ratio < 0.15:
                return 0.95
        
        # Check uniformity
        non_zero = distances[distances > 0]
        if len(non_zero) > 0:
            cv = non_zero.std() / (non_zero.mean() + 1e-10)
            if cv < 0.3:
                base += 0.2
            elif cv > 1.0:
                base -= 0.1
        
        return max(0.0, min(1.0, base))
