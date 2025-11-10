"""
SiNo System - Checkpoint Manager
=================================

Manages checkpoints for backtracking in the SiNo decision system.

A checkpoint represents a SINO decision point where the algorithm
can return if the chosen path leads to a dead end.

Key features:
- Stack-based checkpoint management
- Tracks alternative decisions not yet explored
- Supports nested backtracking (checkpoint chains)
- Memory-efficient (only stores essential state)
"""

from typing import List, Set, Optional, Tuple
from dataclasses import dataclass, field
from .decision import Decision, CheckpointData


@dataclass
class CheckpointState:
    """
    Complete state at a checkpoint.
    
    Extends CheckpointData with tracking information.
    
    Attributes:
        checkpoint_id: Unique identifier for this checkpoint
        decision: The SINO decision that created this checkpoint
        data: Checkpoint data (tour state, available nodes, alternatives)
        times_visited: How many times we've returned to this checkpoint
        exhausted: True if all alternatives have been tried
    """
    checkpoint_id: int
    decision: Decision
    data: CheckpointData
    times_visited: int = 0
    exhausted: bool = False
    
    def mark_visited(self):
        """Mark that we've returned to this checkpoint."""
        self.times_visited += 1
    
    def is_exhausted(self) -> bool:
        """Check if all alternatives have been tried."""
        return not self.data.alternatives or self.exhausted
    
    def get_next_alternative(self) -> Optional[Decision]:
        """
        Get the next untried alternative.
        
        Returns:
            Next Decision to try, or None if exhausted
        """
        if self.data.alternatives:
            return self.data.alternatives.pop(0)
        return None


class CheckpointManager:
    """
    Manages checkpoints for backtracking.
    
    The manager maintains a stack of checkpoints and provides
    methods to save, restore, and navigate through them.
    
    Attributes:
        checkpoints: Stack of checkpoint states
        max_checkpoints: Maximum number of checkpoints to keep
        current_depth: Current exploration depth
    
    Example:
        >>> manager = CheckpointManager(max_checkpoints=10)
        >>> manager.save_checkpoint(decision, tour, available, alternatives)
        >>> # ... explore path ...
        >>> if dead_end:
        ...     tour, available = manager.backtrack()
    """
    
    def __init__(self, max_checkpoints: int = 50):
        """
        Initialize checkpoint manager.
        
        Args:
            max_checkpoints: Maximum number of checkpoints to store
        """
        self.checkpoints: List[CheckpointState] = []
        self.max_checkpoints = max_checkpoints
        self.current_depth = 0
        self._checkpoint_counter = 0
    
    def save_checkpoint(
        self,
        decision: Decision,
        tour_state: List[int],
        available: Set[int],
        alternatives: List[Decision],
        parent_checkpoint: Optional[int] = None
    ) -> int:
        """
        Save a checkpoint at a SINO decision.
        
        Args:
            decision: The SINO decision being made
            tour_state: Current tour
            available: Available nodes
            alternatives: Other SINO options to try if this fails
            parent_checkpoint: ID of parent checkpoint (for nesting)
        
        Returns:
            Checkpoint ID
        
        Raises:
            ValueError: If max checkpoints exceeded
        """
        if len(self.checkpoints) >= self.max_checkpoints:
            # Remove oldest checkpoint to make room
            self._remove_oldest_checkpoint()
        
        # Create checkpoint data
        checkpoint_data = CheckpointData(
            tour_state=tour_state.copy(),
            available=available.copy(),
            alternatives=alternatives.copy(),
            parent_checkpoint=parent_checkpoint,
            depth=self.current_depth
        )
        
        # Create checkpoint state
        checkpoint_id = self._checkpoint_counter
        self._checkpoint_counter += 1
        
        checkpoint_state = CheckpointState(
            checkpoint_id=checkpoint_id,
            decision=decision,
            data=checkpoint_data,
            times_visited=0,
            exhausted=False
        )
        
        self.checkpoints.append(checkpoint_state)
        self.current_depth += 1
        
        return checkpoint_id
    
    def backtrack(self) -> Optional[Tuple[List[int], Set[int], Decision]]:
        """
        Backtrack to the most recent checkpoint with alternatives.
        
        Searches backwards through checkpoints to find one with
        unexplored alternatives.
        
        Returns:
            Tuple of (tour_state, available, next_decision) if successful
            None if no checkpoints with alternatives exist
        
        Example:
            >>> result = manager.backtrack()
            >>> if result:
            ...     tour, available, next_decision = result
            ...     print(f"Backtracked to node {next_decision.node}")
        """
        # Search backwards for checkpoint with alternatives
        while self.checkpoints:
            checkpoint = self.checkpoints[-1]
            
            # Mark as visited
            checkpoint.mark_visited()
            
            # Check if this checkpoint has alternatives
            if not checkpoint.is_exhausted():
                next_alternative = checkpoint.get_next_alternative()
                
                if next_alternative:
                    # Found alternative - restore state
                    tour = checkpoint.data.tour_state.copy()
                    available = checkpoint.data.available.copy()
                    
                    # Update depth
                    self.current_depth = checkpoint.data.depth + 1
                    
                    return tour, available, next_alternative
            
            # This checkpoint is exhausted, remove it
            checkpoint.exhausted = True
            self.checkpoints.pop()
            self.current_depth = max(0, self.current_depth - 1)
        
        # No checkpoints with alternatives
        return None
    
    def has_checkpoints(self) -> bool:
        """Check if any checkpoints exist."""
        return len(self.checkpoints) > 0
    
    def get_depth(self) -> int:
        """Get current exploration depth."""
        return self.current_depth
    
    def get_checkpoint_count(self) -> int:
        """Get number of active checkpoints."""
        return len(self.checkpoints)
    
    def clear(self):
        """Clear all checkpoints."""
        self.checkpoints.clear()
        self.current_depth = 0
    
    def _remove_oldest_checkpoint(self):
        """Remove the oldest checkpoint to free memory."""
        if self.checkpoints:
            self.checkpoints.pop(0)
    
    def get_statistics(self) -> dict:
        """
        Get statistics about checkpoint usage.
        
        Returns:
            Dictionary with checkpoint statistics
        """
        if not self.checkpoints:
            return {
                "total_checkpoints": 0,
                "current_depth": 0,
                "max_visits": 0,
                "avg_visits": 0,
                "exhausted_count": 0,
            }
        
        visits = [cp.times_visited for cp in self.checkpoints]
        exhausted = sum(1 for cp in self.checkpoints if cp.exhausted)
        
        return {
            "total_checkpoints": len(self.checkpoints),
            "current_depth": self.current_depth,
            "max_visits": max(visits) if visits else 0,
            "avg_visits": sum(visits) / len(visits) if visits else 0,
            "exhausted_count": exhausted,
        }
    
    def debug_print(self):
        """Print checkpoint stack for debugging."""
        print("\n" + "=" * 60)
        print("Checkpoint Stack:")
        print("=" * 60)
        
        if not self.checkpoints:
            print("  (empty)")
        else:
            for i, cp in enumerate(self.checkpoints):
                print(f"\n  [{i}] Checkpoint {cp.checkpoint_id}:")
                print(f"      Node: {cp.decision.node}")
                print(f"      Depth: {cp.data.depth}")
                print(f"      Visited: {cp.times_visited} times")
                print(f"      Alternatives left: {len(cp.data.alternatives)}")
                print(f"      Exhausted: {cp.exhausted}")
        
        print("\n" + "=" * 60)
        print(f"Current depth: {self.current_depth}")
        print("=" * 60 + "\n")


class BacktrackHistory:
    """
    Tracks backtracking history for analysis.
    
    Records each backtrack event for post-mortem analysis
    and algorithm tuning.
    
    Attributes:
        events: List of backtrack events
        total_backtracks: Total number of backtracks
    """
    
    def __init__(self):
        """Initialize backtrack history."""
        self.events: List[dict] = []
        self.total_backtracks = 0
    
    def record_backtrack(
        self,
        from_depth: int,
        to_depth: int,
        reason: str,
        checkpoint_id: int
    ):
        """
        Record a backtrack event.
        
        Args:
            from_depth: Depth where backtrack was triggered
            to_depth: Depth after backtracking
            reason: Reason for backtracking
            checkpoint_id: Checkpoint returned to
        """
        event = {
            "backtrack_num": self.total_backtracks + 1,
            "from_depth": from_depth,
            "to_depth": to_depth,
            "depth_change": from_depth - to_depth,
            "reason": reason,
            "checkpoint_id": checkpoint_id,
        }
        
        self.events.append(event)
        self.total_backtracks += 1
    
    def get_summary(self) -> dict:
        """
        Get summary statistics of backtracking.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.events:
            return {
                "total_backtracks": 0,
                "avg_depth_change": 0,
                "max_depth_change": 0,
            }
        
        depth_changes = [e["depth_change"] for e in self.events]
        
        return {
            "total_backtracks": self.total_backtracks,
            "avg_depth_change": sum(depth_changes) / len(depth_changes),
            "max_depth_change": max(depth_changes),
            "reasons": self._count_reasons(),
        }
    
    def _count_reasons(self) -> dict:
        """Count occurrences of each backtrack reason."""
        reasons = {}
        for event in self.events:
            reason = event["reason"]
            reasons[reason] = reasons.get(reason, 0) + 1
        return reasons
    
    def print_summary(self):
        """Print summary of backtracking history."""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("Backtrack History Summary")
        print("=" * 60)
        print(f"  Total backtracks: {summary['total_backtracks']}")
        
        if summary['total_backtracks'] > 0:
            print(f"  Avg depth change: {summary['avg_depth_change']:.1f}")
            print(f"  Max depth change: {summary['max_depth_change']}")
            
            print("\n  Reasons:")
            for reason, count in summary['reasons'].items():
                pct = 100 * count / summary['total_backtracks']
                print(f"    {reason}: {count} ({pct:.1f}%)")
        
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test checkpoint manager
    from .types import DecisionType
    
    print("=" * 60)
    print("Testing CheckpointManager")
    print("=" * 60)
    
    # Create manager
    manager = CheckpointManager(max_checkpoints=10)
    
    # Create test decisions
    decision1 = Decision(
        node=5,
        confidence=0.60,
        type=DecisionType.SINO,
        reason="Test decision 1",
        cost=10.0
    )
    
    decision2 = Decision(
        node=8,
        confidence=0.55,
        type=DecisionType.SINO,
        reason="Test decision 2",
        cost=12.0
    )
    
    alternative1 = Decision(
        node=7,
        confidence=0.50,
        type=DecisionType.SINO,
        reason="Alternative 1",
        cost=11.0
    )
    
    # Save checkpoints
    print("\n1. Saving checkpoint 1...")
    cp1 = manager.save_checkpoint(
        decision1,
        tour_state=[0, 1, 2],
        available={3, 4, 5, 6},
        alternatives=[alternative1]
    )
    print(f"   Checkpoint ID: {cp1}")
    print(f"   Depth: {manager.get_depth()}")
    
    print("\n2. Saving checkpoint 2...")
    cp2 = manager.save_checkpoint(
        decision2,
        tour_state=[0, 1, 2, 5],
        available={3, 4, 6, 8},
        alternatives=[],
        parent_checkpoint=cp1
    )
    print(f"   Checkpoint ID: {cp2}")
    print(f"   Depth: {manager.get_depth()}")
    
    # Debug print
    manager.debug_print()
    
    # Backtrack
    print("\n3. Backtracking...")
    result = manager.backtrack()
    if result:
        tour, available, next_decision = result
        print(f"   ✅ Backtracked successfully")
        print(f"   Restored tour: {tour}")
        print(f"   Next decision: {next_decision}")
    else:
        print("   ❌ No checkpoints with alternatives")
    
    # Statistics
    print("\n4. Statistics:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ CheckpointManager test complete")
    print("=" * 60)
