"""
SiNo System - Decision Class
==============================

Represents a decision to move to a specific node with confidence information.

A Decision contains:
- Target node
- Confidence level (0.0 to 1.0)
- Decision type (SI/NO/SINO)
- Reason for the confidence
- Cost (distance)
- Optional checkpoint data for SINO decisions
"""

from dataclasses import dataclass, field
from typing import Optional, Set, List
from .types import DecisionType, GraphType


@dataclass
class CheckpointData:
    """
    Checkpoint information for backtracking.
    
    Stores the state at a SINO decision point, allowing
    the algorithm to return here if the chosen path fails.
    
    Attributes:
        tour_state: Current tour up to this point
        available: Set of nodes not yet visited
        alternatives: Other SINO decisions not yet tried
        parent_checkpoint: Index of previous checkpoint (for nested backtracking)
        depth: Exploration depth at this checkpoint
    """
    tour_state: List[int]
    available: Set[int]
    alternatives: List['Decision']
    parent_checkpoint: Optional[int] = None
    depth: int = 0


@dataclass
class Decision:
    """
    Represents a decision to move to a specific node.
    
    Attributes:
        node: Target node to visit
        confidence: Confidence level [0.0, 1.0]
        type: Decision type (SI/NO/SINO) based on confidence
        reason: Explanation for the confidence level
        cost: Distance/cost to reach this node
        checkpoint_data: Optional checkpoint for SINO decisions
    
    Example:
        >>> decision = Decision(
        ...     node=5,
        ...     confidence=0.85,
        ...     type=DecisionType.SI,
        ...     reason="Adjacent node in circle",
        ...     cost=12.5
        ... )
        >>> print(decision)
        Decision(node=5, conf=0.85, type=SI, cost=12.5)
    """
    node: int
    confidence: float
    type: DecisionType
    reason: str
    cost: float
    checkpoint_data: Optional[CheckpointData] = None
    
    def __post_init__(self):
        """Validate decision parameters."""
        assert 0.0 <= self.confidence <= 1.0, \
            f"Confidence must be in [0, 1], got {self.confidence}"
        assert self.cost >= 0, \
            f"Cost must be non-negative, got {self.cost}"
    
    def __repr__(self) -> str:
        """String representation of decision."""
        return (
            f"Decision(node={self.node}, "
            f"conf={self.confidence:.2f}, "
            f"type={self.type.value}, "
            f"cost={self.cost:.2f})"
        )
    
    def is_si(self) -> bool:
        """Check if this is a SI (high confidence) decision."""
        return self.type == DecisionType.SI
    
    def is_no(self) -> bool:
        """Check if this is a NO (low confidence) decision."""
        return self.type == DecisionType.NO
    
    def is_sino(self) -> bool:
        """Check if this is a SINO (moderate confidence) decision."""
        return self.type == DecisionType.SINO
    
    def create_checkpoint(
        self,
        tour_state: List[int],
        available: Set[int],
        alternatives: List['Decision'],
        parent_checkpoint: Optional[int] = None,
        depth: int = 0
    ) -> 'Decision':
        """
        Create a checkpoint for this SINO decision.
        
        Args:
            tour_state: Current tour
            available: Available nodes
            alternatives: Other SINO options
            parent_checkpoint: Previous checkpoint index
            depth: Current depth
        
        Returns:
            New Decision with checkpoint data
        """
        checkpoint = CheckpointData(
            tour_state=tour_state.copy(),
            available=available.copy(),
            alternatives=alternatives.copy(),
            parent_checkpoint=parent_checkpoint,
            depth=depth
        )
        
        return Decision(
            node=self.node,
            confidence=self.confidence,
            type=self.type,
            reason=self.reason,
            cost=self.cost,
            checkpoint_data=checkpoint
        )


@dataclass
class TourContext:
    """
    Context information about the current tour state.
    
    Used for calculating context-aware confidence.
    
    Attributes:
        tour: Current tour (list of node indices)
        available: Set of unvisited nodes
        graph_type: Type of graph being solved
        total_nodes: Total number of nodes in the problem
    """
    tour: List[int]
    available: Set[int]
    graph_type: GraphType
    total_nodes: int
    
    @property
    def current_node(self) -> int:
        """Get the current (last) node in the tour."""
        return self.tour[-1] if self.tour else 0
    
    @property
    def tour_length(self) -> int:
        """Get the current length of the tour."""
        return len(self.tour)
    
    @property
    def remaining_nodes(self) -> int:
        """Get the number of nodes left to visit."""
        return len(self.available)
    
    @property
    def progress(self) -> float:
        """Get tour completion progress [0.0, 1.0]."""
        return self.tour_length / self.total_nodes if self.total_nodes > 0 else 0.0
    
    def is_almost_complete(self, threshold: float = 0.9) -> bool:
        """Check if tour is almost complete."""
        return self.progress >= threshold


def filter_decisions_by_type(
    decisions: List[Decision],
    decision_type: DecisionType
) -> List[Decision]:
    """
    Filter decisions by type.
    
    Args:
        decisions: List of decisions
        decision_type: Type to filter for
    
    Returns:
        List of decisions matching the type
    
    Example:
        >>> decisions = [decision_si, decision_sino, decision_no]
        >>> si_only = filter_decisions_by_type(decisions, DecisionType.SI)
        >>> len(si_only)
        1
    """
    return [d for d in decisions if d.type == decision_type]


def get_best_decision(decisions: List[Decision]) -> Optional[Decision]:
    """
    Get the decision with highest confidence.
    
    Args:
        decisions: List of decisions
    
    Returns:
        Decision with highest confidence, or None if list is empty
    
    Example:
        >>> decisions = [
        ...     Decision(1, 0.85, DecisionType.SI, "test", 10.0),
        ...     Decision(2, 0.90, DecisionType.SI, "test", 12.0),
        ... ]
        >>> best = get_best_decision(decisions)
        >>> best.node
        2
    """
    if not decisions:
        return None
    return max(decisions, key=lambda d: d.confidence)


if __name__ == "__main__":
    # Test Decision creation
    from .types import DecisionType
    
    print("✅ Testing Decision class:")
    
    # Create a SI decision
    decision_si = Decision(
        node=5,
        confidence=0.85,
        type=DecisionType.SI,
        reason="Adjacent in circle",
        cost=12.5
    )
    print(f"\n   SI Decision: {decision_si}")
    print(f"   Is SI? {decision_si.is_si()}")
    
    # Create a SINO decision with checkpoint
    decision_sino = Decision(
        node=10,
        confidence=0.50,
        type=DecisionType.SINO,
        reason="Moderate distance in random graph",
        cost=25.3
    )
    decision_with_checkpoint = decision_sino.create_checkpoint(
        tour_state=[0, 1, 2],
        available={3, 4, 5, 10},
        alternatives=[],
        depth=3
    )
    print(f"\n   SINO Decision: {decision_with_checkpoint}")
    print(f"   Has checkpoint? {decision_with_checkpoint.checkpoint_data is not None}")
    
    # Test TourContext
    context = TourContext(
        tour=[0, 1, 2, 3],
        available={4, 5, 6, 7, 8, 9},
        graph_type=GraphType.RANDOM,
        total_nodes=10
    )
    print(f"\n   Tour Context:")
    print(f"   Current node: {context.current_node}")
    print(f"   Progress: {context.progress:.0%}")
    print(f"   Remaining: {context.remaining_nodes}")


# ============================================================================
# Decision Engine for API
# ============================================================================

class DecisionEngine:
    """Decision engine for making SI/SINO/NO decisions."""
    
    def __init__(self, config=None):
        from .types import SolverConfig
        self.config = config or SolverConfig()
        self.stats = {'SI': 0, 'SINO': 0, 'NO': 0}
    
    def decide(self, confidence: float, n: int):
        """Make decision based on confidence."""
        from .types import get_decision_type
        
        # Adjust for problem size
        if n > 100:
            confidence *= 0.9
        elif n < 20:
            confidence *= 1.1
        
        confidence = max(0.0, min(1.0, confidence))
        decision = get_decision_type(confidence, self.config)
        self.stats[decision.value.upper()] = self.stats.get(decision.value.upper(), 0) + 1
        return decision
    
    def get_stats(self):
        return self.stats.copy()
