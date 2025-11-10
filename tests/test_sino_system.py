"""
Test Suite for SiNo System
===========================

Comprehensive tests for the SiNo decision-making system.
"""

import pytest
import numpy as np
from pimst.improved.sino import (
    SiNoSolver,
    SmartSelector,
    solve_tsp,
    smart_solve,
    DecisionType,
    SolverConfig
)


class TestSiNoBasics:
    """Basic functionality tests."""
    
    def test_simple_solve(self):
        """Test basic solving capability."""
        distances = np.array([
            [0, 1, 2],
            [1, 0, 3],
            [2, 3, 0]
        ])
        
        result = solve_tsp(distances)
        assert len(result.tour) == 3
        assert result.cost > 0
        assert result.decision in [DecisionType.SI, DecisionType.SINO, DecisionType.NO]
    
    def test_solver_initialization(self):
        """Test solver can be initialized."""
        solver = SiNoSolver()
        assert solver is not None
        assert solver.config is not None
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = SolverConfig(
            si_threshold=0.85,
            no_threshold=0.15
        )
        solver = SiNoSolver(config)
        assert solver.config.si_threshold == 0.85


class TestDecisionTypes:
    """Test different decision paths."""
    
    def test_small_instance_decision(self):
        """Small instances should get fast decision."""
        distances = np.random.rand(5, 5)
        np.fill_diagonal(distances, 0)
        
        result = solve_tsp(distances)
        # Small instances likely NO (fast path)
        assert result.decision in [DecisionType.NO, DecisionType.SINO]
    
    def test_large_instance_decision(self):
        """Large instances may need comprehensive solving."""
        distances = np.random.rand(100, 100)
        np.fill_diagonal(distances, 0)
        
        result = solve_tsp(distances)
        assert result.decision in [DecisionType.SI, DecisionType.SINO]
    
    def test_decision_consistency(self):
        """Same instance should give consistent decisions."""
        distances = np.random.rand(20, 20)
        np.fill_diagonal(distances, 0)
        
        result1 = solve_tsp(distances)
        result2 = solve_tsp(distances)
        
        # Decisions should be similar (allowing for randomness)
        assert result1.decision == result2.decision


class TestSmartSelector:
    """Test the smart selector integration."""
    
    def test_selector_basic(self):
        """Test selector basic functionality."""
        selector = SmartSelector()
        distances = np.random.rand(30, 30)
        np.fill_diagonal(distances, 0)
        
        tour, cost, metadata = selector.select_and_solve(distances)
        
        assert len(tour) == 30
        assert cost > 0
        assert 'decision' in metadata
    
    def test_circle_detection(self):
        """Test circle graph fast path."""
        # Create perfect circle
        n = 50
        angles = np.linspace(0, 2*np.pi, n, endpoint=False)
        coordinates = np.column_stack([
            np.cos(angles),
            np.sin(angles)
        ])
        
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distances[i][j] = np.linalg.norm(coordinates[i] - coordinates[j])
        
        selector = SmartSelector()
        tour, cost, metadata = selector.select_and_solve(
            distances, 
            coordinates, 
            graph_type='circle'
        )
        
        assert metadata['decision'] == 'FAST_PATH'
        assert metadata['graph_type'] == 'circle'
    
    def test_selector_statistics(self):
        """Test selector statistics tracking."""
        selector = SmartSelector()
        
        # Solve multiple instances
        for _ in range(5):
            distances = np.random.rand(20, 20)
            np.fill_diagonal(distances, 0)
            selector.select_and_solve(distances)
        
        stats = selector.get_stats()
        assert stats['total_calls'] == 5
        assert 'fast_path' in stats


class TestBatchProcessing:
    """Test batch solving capabilities."""
    
    def test_batch_solve(self):
        """Test solving multiple instances."""
        solver = SiNoSolver()
        
        instances = [
            np.random.rand(10, 10),
            np.random.rand(15, 15),
            np.random.rand(20, 20)
        ]
        
        for inst in instances:
            np.fill_diagonal(inst, 0)
        
        results = solver.batch_solve(instances)
        
        assert len(results) == 3
        assert all(r.cost > 0 for r in results)
    
    def test_batch_consistency(self):
        """Test batch results are consistent."""
        solver = SiNoSolver()
        
        # Same instance multiple times
        distances = np.random.rand(15, 15)
        np.fill_diagonal(distances, 0)
        instances = [distances.copy() for _ in range(3)]
        
        results = solver.batch_solve(instances)
        
        # All should make same decision
        decisions = [r.decision for r in results]
        assert len(set(decisions)) == 1


class TestPerformance:
    """Performance benchmarks."""
    
    def test_solve_speed_small(self):
        """Test solving speed for small instances."""
        import time
        
        distances = np.random.rand(20, 20)
        np.fill_diagonal(distances, 0)
        
        start = time.time()
        result = solve_tsp(distances)
        elapsed = time.time() - start
        
        # Should be very fast
        assert elapsed < 1.0, f"Took {elapsed:.3f}s"
    
    def test_solve_speed_medium(self):
        """Test solving speed for medium instances."""
        import time
        
        distances = np.random.rand(50, 50)
        np.fill_diagonal(distances, 0)
        
        start = time.time()
        result = solve_tsp(distances)
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 5.0, f"Took {elapsed:.3f}s"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_minimal_instance(self):
        """Test minimal 3-node instance."""
        distances = np.array([
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ])
        
        result = solve_tsp(distances)
        assert len(result.tour) == 3
        assert result.cost == 3.0
    
    def test_asymmetric_distances(self):
        """Test with asymmetric distance matrix."""
        distances = np.array([
            [0, 1, 5],
            [2, 0, 3],
            [4, 6, 0]
        ])
        
        result = solve_tsp(distances)
        assert len(result.tour) == 3
        assert result.cost > 0
    
    def test_large_instance(self):
        """Test with large instance."""
        distances = np.random.rand(200, 200)
        np.fill_diagonal(distances, 0)
        
        result = solve_tsp(distances)
        assert len(result.tour) == 200
        assert result.cost > 0


class TestIntegration:
    """Integration tests with full system."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow."""
        # 1. Initialize
        solver = SiNoSolver()
        
        # 2. Create instance
        n = 30
        angles = np.random.rand(n) * 2 * np.pi
        coordinates = np.column_stack([
            np.cos(angles) * (1 + 0.2 * np.random.rand(n)),
            np.sin(angles) * (1 + 0.2 * np.random.rand(n))
        ])
        
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distances[i][j] = np.linalg.norm(coordinates[i] - coordinates[j])
        
        # 3. Solve
        result = solver.solve(distances, coordinates)
        
        # 4. Verify
        assert len(result.tour) == n
        assert result.cost > 0
        assert result.confidence >= 0 and result.confidence <= 1
        
        # 5. Get statistics
        stats = solver.get_statistics()
        assert stats is not None
    
    def test_smart_selector_integration(self):
        """Test smart selector with coordinates."""
        # Create different graph types
        test_cases = [
            ('circle', self._create_circle(20)),
            ('random', np.random.rand(20, 2)),
            ('uniform', self._create_grid(5))
        ]
        
        selector = SmartSelector()
        
        for graph_type, coords in test_cases:
            n = len(coords)
            distances = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    distances[i][j] = np.linalg.norm(coords[i] - coords[j])
            
            tour, cost, metadata = selector.select_and_solve(
                distances, 
                coords,
                graph_type=graph_type
            )
            
            assert len(tour) == n
            assert cost > 0
    
    @staticmethod
    def _create_circle(n):
        """Create circle coordinates."""
        angles = np.linspace(0, 2*np.pi, n, endpoint=False)
        return np.column_stack([np.cos(angles), np.sin(angles)])
    
    @staticmethod
    def _create_grid(side):
        """Create grid coordinates."""
        x = np.repeat(np.arange(side), side)
        y = np.tile(np.arange(side), side)
        return np.column_stack([x, y])


# Pytest configuration
@pytest.fixture
def small_distances():
    """Fixture for small distance matrix."""
    d = np.random.rand(10, 10)
    np.fill_diagonal(d, 0)
    return d


@pytest.fixture
def medium_distances():
    """Fixture for medium distance matrix."""
    d = np.random.rand(50, 50)
    np.fill_diagonal(d, 0)
    return d


@pytest.fixture
def circle_coordinates():
    """Fixture for circle coordinates."""
    n = 30
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    return np.column_stack([np.cos(angles), np.sin(angles)])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
