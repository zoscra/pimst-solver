"""
SiNo System - Explorer Engine
===============================

Main exploration engine with intelligent backtracking.

The explorer implements the core SiNo algorithm:
1. Evaluate all available moves
2. If SI exists → Execute immediately
3. If no SI → Use best SINO with checkpoint
4. If dead end → Backtrack to last checkpoint
5. Repeat until tour complete

Key features:
- Intelligent dead-end detection
- Limited backtracking (configurable)
- Tour quality estimation
- Efficient state management
"""

import numpy as np
from typing import List, Set, Tuple, Optional
from .types import DecisionType, GraphType, SiNoConfig, DEFAULT_CONFIG
from .decision import Decision, TourContext, filter_decisions_by_type, get_best_decision
from .confidence import ConfidenceCalculator
from .checkpoint import CheckpointManager, BacktrackHistory


class DeadEndDetector:
    """
    Detects when the algorithm is in a dead-end state.
    
    A dead end occurs when:
    - All remaining options have very low confidence (<0.20)
    - Estimated tour cost exceeds reasonable bounds
    - Stuck in a local region with no escape
    
    Attributes:
        config: Configuration parameters
        dist_matrix: Distance matrix for cost estimation
    """
    
    def __init__(self, dist_matrix: np.ndarray, config: SiNoConfig = DEFAULT_CONFIG):
        """
        Initialize dead-end detector.
        
        Args:
            dist_matrix: Precomputed distance matrix
            config: Configuration parameters
        """
        self.dist_matrix = dist_matrix
        self.config = config
        self.N = len(dist_matrix)
    
    def is_dead_end(
        self,
        decisions: List[Decision],
        tour: List[int],
        available: Set[int]
    ) -> Tuple[bool, str]:
        """
        Check if current state is a dead end.
        
        Args:
            decisions: List of available decisions
            tour: Current tour
            available: Available nodes
        
        Returns:
            Tuple of (is_dead_end, reason)
        """
        # Check 1: All decisions are NO (very low confidence)
        if decisions:
            max_confidence = max(d.confidence for d in decisions)
            if max_confidence < self.config.DEAD_END_THRESHOLD:
                return True, f"all_low_confidence (max={max_confidence:.2f})"
        
        # Check 2: Tour cost exceeds reasonable bounds
        if len(tour) >= 3:
            current_cost = self._calculate_tour_cost(tour)
            estimated_optimal = self._estimate_optimal_cost()
            
            if current_cost > estimated_optimal * self.config.DEAD_END_COST_RATIO:
                ratio = current_cost / estimated_optimal
                return True, f"excessive_cost (ratio={ratio:.2f})"
        
        # Check 3: No decisions available (should not happen, but safety)
        if not decisions and available:
            return True, "no_valid_decisions"
        
        # Not a dead end
        return False, ""
    
    def _calculate_tour_cost(self, tour: List[int]) -> float:
        """Calculate total cost of current tour."""
        cost = 0.0
        for i in range(len(tour) - 1):
            cost += self.dist_matrix[tour[i]][tour[i + 1]]
        return cost
    
    def _estimate_optimal_cost(self) -> float:
        """
        Estimate optimal tour cost using MST lower bound.
        
        Returns:
            Estimated optimal tour length
        """
        # Simple heuristic: sum of N smallest edges * 1.1
        all_edges = []
        for i in range(self.N):
            for j in range(i + 1, self.N):
                all_edges.append(self.dist_matrix[i][j])
        
        all_edges.sort()
        
        # MST uses N-1 edges, tour uses N edges
        if len(all_edges) >= self.N:
            mst_cost = sum(all_edges[:self.N - 1])
            # Tour is at least MST cost, typically 1.1-1.2x
            return mst_cost * 1.15
        else:
            return sum(all_edges) * 1.2


class SiNoExplorer:
    """
    Main exploration engine with backtracking.
    
    Implements the complete SiNo algorithm:
    - Confidence-based decision making
    - Checkpoint creation at SINO decisions
    - Intelligent backtracking
    - Dead-end detection
    
    Attributes:
        points: City coordinates
        graph_type: Type of graph
        config: Configuration parameters
        confidence_calc: Confidence calculator
        checkpoint_manager: Checkpoint manager
        backtrack_history: History of backtracks
    
    Example:
        >>> explorer = SiNoExplorer(points, GraphType.RANDOM)
        >>> tour, length, stats = explorer.explore()
        >>> print(f"Tour: {tour}, Length: {length:.2f}")
        >>> print(f"Backtracks: {stats['total_backtracks']}")
    """
    
    def __init__(
        self,
        points: np.ndarray,
        graph_type: GraphType,
        config: SiNoConfig = DEFAULT_CONFIG
    ):
        """
        Initialize SiNo explorer.
        
        Args:
            points: Array of city coordinates
            graph_type: Type of graph structure
            config: Configuration parameters
        """
        self.points = points
        self.N = len(points)
        self.graph_type = graph_type
        self.config = config
        
        # Initialize components
        self.confidence_calc = ConfidenceCalculator(points, graph_type, config)
        self.checkpoint_manager = CheckpointManager(max_checkpoints=50)
        self.backtrack_history = BacktrackHistory()
        self.dead_end_detector = DeadEndDetector(
            self.confidence_calc.dist_matrix, config
        )
        
        # Statistics
        self.stats = {
            "total_decisions": 0,
            "si_decisions": 0,
            "sino_decisions": 0,
            "no_decisions": 0,
            "total_backtracks": 0,
            "max_depth": 0,
        }
    
    def explore(self, start_node: int = 0) -> Tuple[List[int], float, dict]:
        """
        Explore and construct TSP tour using SiNo strategy.
        
        Args:
            start_node: Starting node for tour
        
        Returns:
            Tuple of (tour, tour_length, statistics)
        
        Example:
            >>> tour, length, stats = explorer.explore(start_node=0)
            >>> print(f"Found tour with length {length:.2f}")
            >>> print(f"Required {stats['total_backtracks']} backtracks")
        """
        # Initialize tour
        tour = [start_node]
        available = set(range(self.N)) - {start_node}
        
        # Main exploration loop
        while available:
            # Create context
            context = TourContext(
                tour=tour,
                available=available,
                graph_type=self.graph_type,
                total_nodes=self.N
            )
            
            # Evaluate all options
            decisions = self.confidence_calc.evaluate_all_options(
                tour[-1], available, context
            )
            
            # Check for dead end
            is_dead_end, reason = self.dead_end_detector.is_dead_end(
                decisions, tour, available
            )
            
            if is_dead_end:
                # Dead end detected - backtrack
                success = self._handle_dead_end(tour, available, reason)
                if not success:
                    # No more checkpoints - fail
                    break
                continue
            
            # Classify decisions by type
            si_decisions = filter_decisions_by_type(decisions, DecisionType.SI)
            sino_decisions = filter_decisions_by_type(decisions, DecisionType.SINO)
            
            # Decision strategy
            if si_decisions:
                # SI decision available - execute immediately
                chosen = get_best_decision(si_decisions)
                self._execute_decision(chosen, tour, available, save_checkpoint=False)
                self.stats["si_decisions"] += 1
            
            elif sino_decisions:
                # No SI - use SINO with checkpoint
                chosen = get_best_decision(sino_decisions)
                
                # Save checkpoint with alternatives
                other_sinos = [d for d in sino_decisions if d.node != chosen.node]
                self._save_checkpoint_for_decision(
                    chosen, tour, available, other_sinos
                )
                
                self._execute_decision(chosen, tour, available, save_checkpoint=False)
                self.stats["sino_decisions"] += 1
            
            else:
                # Only NO decisions - this shouldn't happen after dead-end check
                # But handle gracefully by backtracking
                success = self._handle_dead_end(
                    tour, available, "only_no_decisions"
                )
                if not success:
                    break
                continue
            
            self.stats["total_decisions"] += 1
            
            # Update max depth
            if self.checkpoint_manager.get_depth() > self.stats["max_depth"]:
                self.stats["max_depth"] = self.checkpoint_manager.get_depth()
            
            # Safety check: prevent infinite loops
            if len(tour) > self.N * 2:
                print("WARNING: Tour length exceeded N*2, breaking")
                break
        
        # Calculate final tour length
        tour_length = self._calculate_tour_length(tour)
        
        # Add final statistics
        self.stats["tour_length"] = len(tour)
        self.stats["tour_complete"] = len(tour) == self.N
        self.stats["final_checkpoints"] = self.checkpoint_manager.get_checkpoint_count()
        
        return tour, tour_length, self.stats
    
    def _execute_decision(
        self,
        decision: Decision,
        tour: List[int],
        available: Set[int],
        save_checkpoint: bool = False
    ):
        """
        Execute a decision by adding node to tour.
        
        Args:
            decision: Decision to execute
            tour: Current tour (modified in place)
            available: Available nodes (modified in place)
            save_checkpoint: Whether to save checkpoint (for SINO)
        """
        tour.append(decision.node)
        available.remove(decision.node)
    
    def _save_checkpoint_for_decision(
        self,
        decision: Decision,
        tour: List[int],
        available: Set[int],
        alternatives: List[Decision]
    ):
        """
        Save checkpoint for a SINO decision.
        
        Args:
            decision: The SINO decision being made
            tour: Current tour state
            available: Available nodes
            alternatives: Other SINO decisions to try if this fails
        """
        # Get parent checkpoint ID if exists
        parent_id = None
        if self.checkpoint_manager.has_checkpoints():
            parent_id = self.checkpoint_manager.checkpoints[-1].checkpoint_id
        
        # Save checkpoint
        self.checkpoint_manager.save_checkpoint(
            decision=decision,
            tour_state=tour,
            available=available,
            alternatives=alternatives,
            parent_checkpoint=parent_id
        )
    
    def _handle_dead_end(
        self,
        tour: List[int],
        available: Set[int],
        reason: str
    ) -> bool:
        """
        Handle dead-end situation by backtracking.
        
        Args:
            tour: Current tour (will be modified)
            available: Available nodes (will be modified)
            reason: Reason for dead end
        
        Returns:
            True if backtracked successfully, False if no checkpoints left
        """
        # Check backtrack limit
        if self.stats["total_backtracks"] >= self.config.MAX_BACKTRACKS:
            return False
        
        # Record current depth
        from_depth = self.checkpoint_manager.get_depth()
        
        # Attempt backtrack
        result = self.checkpoint_manager.backtrack()
        
        if result is None:
            # No checkpoints with alternatives
            return False
        
        # Unpack result
        restored_tour, restored_available, next_decision = result
        
        # Update state
        tour.clear()
        tour.extend(restored_tour)
        available.clear()
        available.update(restored_available)
        
        # Execute alternative decision
        self._execute_decision(next_decision, tour, available)
        
        # Record backtrack
        to_depth = self.checkpoint_manager.get_depth()
        self.backtrack_history.record_backtrack(
            from_depth=from_depth,
            to_depth=to_depth,
            reason=reason,
            checkpoint_id=next_decision.node  # Use node as identifier
        )
        
        self.stats["total_backtracks"] += 1
        
        return True
    
    def _calculate_tour_length(self, tour: List[int]) -> float:
        """
        Calculate total length of tour.
        
        Args:
            tour: List of nodes in tour
        
        Returns:
            Total tour length including return to start
        """
        if len(tour) < 2:
            return 0.0
        
        dist_matrix = self.confidence_calc.dist_matrix
        length = 0.0
        
        for i in range(len(tour)):
            next_i = (i + 1) % len(tour)
            length += dist_matrix[tour[i]][tour[next_i]]
        
        return length
    
    def get_statistics(self) -> dict:
        """
        Get detailed statistics about the exploration.
        
        Returns:
            Dictionary with exploration statistics
        """
        stats = self.stats.copy()
        
        # Add checkpoint statistics
        checkpoint_stats = self.checkpoint_manager.get_statistics()
        stats.update({
            f"checkpoint_{k}": v for k, v in checkpoint_stats.items()
        })
        
        # Add backtrack history
        backtrack_summary = self.backtrack_history.get_summary()
        stats.update({
            f"backtrack_{k}": v for k, v in backtrack_summary.items()
        })
        
        return stats
    
    def print_summary(self):
        """Print summary of exploration."""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("SiNo Explorer Summary")
        print("=" * 60)
        
        print(f"\nTour Construction:")
        print(f"  Total decisions: {stats['total_decisions']}")
        print(f"  SI decisions: {stats['si_decisions']} "
              f"({100*stats['si_decisions']/max(stats['total_decisions'],1):.1f}%)")
        print(f"  SINO decisions: {stats['sino_decisions']} "
              f"({100*stats['sino_decisions']/max(stats['total_decisions'],1):.1f}%)")
        
        print(f"\nBacktracking:")
        print(f"  Total backtracks: {stats['total_backtracks']}")
        print(f"  Max depth: {stats['max_depth']}")
        
        if stats['total_backtracks'] > 0:
            print(f"  Avg depth change: {stats.get('backtrack_avg_depth_change', 0):.1f}")
        
        print(f"\nFinal State:")
        print(f"  Tour length: {stats['tour_length']} nodes")
        print(f"  Complete: {'Yes' if stats['tour_complete'] else 'No'}")
        print(f"  Checkpoints remaining: {stats['final_checkpoints']}")
        
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test explorer
    print("=" * 60)
    print("Testing SiNoExplorer")
    print("=" * 60)
    
    # Create simple test case
    np.random.seed(42)
    points = np.random.rand(10, 2) * 100  # 10 random points
    
    # Test with random graph
    explorer = SiNoExplorer(points, GraphType.RANDOM)
    
    print("\nExploring random graph with 10 nodes...")
    tour, length, stats = explorer.explore(start_node=0)
    
    print(f"\nResults:")
    print(f"  Tour: {tour}")
    print(f"  Length: {length:.2f}")
    print(f"  Complete: {len(tour) == len(points)}")
    
    # Print summary
    explorer.print_summary()
    
    print("=" * 60)
    print("✅ SiNoExplorer test complete")
    print("=" * 60)


# ============================================================================
# Exploration Engine for API
# ============================================================================

class ExplorationEngine:
    """Exploration with checkpoints for SINO cases."""
    
    def __init__(self, config=None):
        from .types import SolverConfig
        self.config = config or SolverConfig()
    
    def explore(self, distances, confidence):
        """Explore with 2-opt improvement."""
        import numpy as np
        n = len(distances)
        
        # Nearest neighbor
        unvisited = set(range(1, n))
        tour = [0]
        current = 0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distances[current][x])
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        
        # 2-opt
        improved = True
        max_iter = int(50 * confidence)
        
        for _ in range(max(1, max_iter)):
            if not improved:
                break
            improved = False
            
            for i in range(n-1):
                for j in range(i+2, n):
                    new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
                    new_cost = sum(distances[new_tour[k]][new_tour[(k+1)%n]] for k in range(n))
                    
                    if new_cost < cost:
                        tour = new_tour
                        cost = new_cost
                        improved = True
                        break
                if improved:
                    break
        
        return tour, cost
