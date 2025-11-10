"""
SiNo System - Type Definitions
================================

Basic types and enumerations for the SiNo decision system.

This module defines:
- DecisionType: SI, NO, SINO
- GraphType: Circle, Grid, Clustered, Random, Diagonal
- Configuration parameters
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class DecisionType(Enum):
    """
    Type of decision based on confidence level.
    
    SI (YES): High confidence (>80%) - Execute immediately
    NO: Low confidence (<20%) - Discard option
    SINO (MAYBE): Moderate confidence (20-80%) - Create checkpoint
    """
    SI = "si"           # Execute with confidence
    NO = "no"           # Discard option
    SINO = "sino"       # Checkpoint for backtracking


class GraphType(Enum):
    """
    Classification of graph structure.
    
    Different graph types have different confidence patterns:
    - CIRCLE: Adjacent nodes have very high confidence
    - GRID: Orthogonal moves preferred
    - CLUSTERED: Intra-cluster moves high confidence
    - RANDOM: Distance-based confidence only
    - DIAGONAL: Line-following high confidence
    """
    CIRCLE = "circle"
    GRID = "grid"
    CLUSTERED = "clustered"
    RANDOM = "random"
    DIAGONAL = "diagonal"


@dataclass
class SiNoConfig:
    """
    Configuration parameters for SiNo system.
    
    Thresholds:
        - SI_THRESHOLD: Minimum confidence for SI decision (default: 0.80)
        - NO_THRESHOLD: Maximum confidence for NO decision (default: 0.20)
        - Between these values = SINO
    
    Backtracking limits:
        - MAX_BACKTRACKS: Maximum number of backtracks allowed (default: 5)
        - MAX_DEPTH: Maximum exploration depth (default: 100)
    
    Dead-end detection:
        - DEAD_END_THRESHOLD: All options below this = dead end (default: 0.20)
        - DEAD_END_COST_RATIO: Tour cost > optimal * ratio = dead end (default: 2.0)
    
    Confidence weights:
        - GRAPH_TYPE_WEIGHT: Weight for graph type factor (default: 0.40)
        - DISTANCE_WEIGHT: Weight for distance factor (default: 0.30)
        - TOUR_CONTEXT_WEIGHT: Weight for tour context (default: 0.20)
        - LOCAL_STRUCTURE_WEIGHT: Weight for local structure (default: 0.10)
    """
    
    # Thresholds for decision types
    SI_THRESHOLD: float = 0.80      # >80% = SI
    NO_THRESHOLD: float = 0.20      # <20% = NO
    # 20-80% = SINO
    
    # Backtracking limits
    MAX_BACKTRACKS: int = 5         # Maximum backtracks
    MAX_DEPTH: int = 100            # Maximum exploration depth
    
    # Dead-end detection
    DEAD_END_THRESHOLD: float = 0.20  # All options < this = dead end
    DEAD_END_COST_RATIO: float = 2.0  # Tour > 2x optimal estimate = dead end
    
    # Confidence calculation weights (must sum to 1.0)
    GRAPH_TYPE_WEIGHT: float = 0.40
    DISTANCE_WEIGHT: float = 0.30
    TOUR_CONTEXT_WEIGHT: float = 0.20
    LOCAL_STRUCTURE_WEIGHT: float = 0.10
    
    def __post_init__(self):
        """Validate configuration parameters."""
        # Check thresholds
        assert 0.0 <= self.NO_THRESHOLD < self.SI_THRESHOLD <= 1.0, \
            "Thresholds must satisfy: 0 <= NO < SI <= 1"
        
        # Check weights sum to 1.0
        total_weight = (
            self.GRAPH_TYPE_WEIGHT +
            self.DISTANCE_WEIGHT +
            self.TOUR_CONTEXT_WEIGHT +
            self.LOCAL_STRUCTURE_WEIGHT
        )
        assert abs(total_weight - 1.0) < 0.001, \
            f"Weights must sum to 1.0, got {total_weight}"
        
        # Check limits are positive
        assert self.MAX_BACKTRACKS > 0, "MAX_BACKTRACKS must be positive"
        assert self.MAX_DEPTH > 0, "MAX_DEPTH must be positive"


# Confidence rules for each graph type
# Format: {GraphType: {situation: confidence}}

CIRCLE_CONFIDENCE_RULES = {
    'adjacent': 0.95,        # Very high → SI
    'near_adjacent': 0.65,   # Moderate → SINO
    'far': 0.15,            # Low → NO
}

GRID_CONFIDENCE_RULES = {
    'orthogonal': 0.90,      # High → SI
    'diagonal_near': 0.55,   # Moderate → SINO
    'diagonal_far': 0.40,    # Moderate → SINO
    'jump': 0.10,            # Low → NO
}

CLUSTERED_CONFIDENCE_RULES = {
    'same_cluster': 0.85,    # High → SI
    'adjacent_cluster': 0.50, # Moderate → SINO
    'far_cluster': 0.25,     # Low-moderate → SINO/NO
}

RANDOM_CONFIDENCE_RULES = {
    'nearest': 0.60,         # Moderate-high → SINO/SI
    'near': 0.45,            # Moderate → SINO
    'medium': 0.30,          # Moderate-low → SINO
    'far': 0.15,             # Low → NO
}

DIAGONAL_CONFIDENCE_RULES = {
    'next_in_line': 0.95,    # Very high → SI
    'skip_one': 0.50,        # Moderate → SINO
    'skip_many': 0.15,       # Low → NO
}

# Default configuration instance
DEFAULT_CONFIG = SiNoConfig()


def get_decision_type(confidence: float, config: SiNoConfig = DEFAULT_CONFIG) -> DecisionType:
    """
    Classify confidence value into decision type.
    
    Args:
        confidence: Confidence value [0.0, 1.0]
        config: Configuration with thresholds
    
    Returns:
        DecisionType based on thresholds
    
    Example:
        >>> get_decision_type(0.85)  # > 0.80
        DecisionType.SI
        >>> get_decision_type(0.50)  # Between 0.20 and 0.80
        DecisionType.SINO
        >>> get_decision_type(0.15)  # < 0.20
        DecisionType.NO
    """
    if confidence >= config.SI_THRESHOLD:
        return DecisionType.SI
    elif confidence <= config.NO_THRESHOLD:
        return DecisionType.NO
    else:
        return DecisionType.SINO


if __name__ == "__main__":
    # Test configuration
    config = SiNoConfig()
    print("✅ SiNo Configuration:")
    print(f"   SI threshold: {config.SI_THRESHOLD}")
    print(f"   NO threshold: {config.NO_THRESHOLD}")
    print(f"   Max backtracks: {config.MAX_BACKTRACKS}")
    print(f"   Max depth: {config.MAX_DEPTH}")
    
    # Test decision classification
    print("\n✅ Decision Classification:")
    for conf in [0.95, 0.75, 0.50, 0.25, 0.05]:
        dtype = get_decision_type(conf)
        print(f"   Confidence {conf:.2f} → {dtype.value}")


# ============================================================================
# Additional Classes for API Compatibility
# ============================================================================

from typing import List, Dict, Any

@dataclass
class SiNoResult:
    """
    Result from SiNo solver.
    
    Attributes:
        tour: Solution tour (list of node indices)
        cost: Total tour cost
        decision: Type of decision made (SI/SINO/NO)
        confidence: Confidence level (0-1)
        n_nodes: Number of nodes in the problem
        metadata: Optional additional information
    """
    tour: List[int]
    cost: float
    decision: DecisionType
    confidence: float
    n_nodes: int
    metadata: Optional[Dict[str, Any]] = None


# Alias for backward compatibility
SolverConfig = SiNoConfig
