"""
Test Suite for PIMST Base Algorithms
=====================================

Tests for v14.x, v17.x and other core algorithms.
"""

import pytest
import numpy as np
import time


class TestAlgorithmPerformance:
    """Performance tests for different algorithm versions."""
    
    def test_nearest_neighbor_basic(self):
        """Test basic nearest neighbor heuristic."""
        from pimst.algorithms import nearest_neighbor
        
        distances = np.array([
            [0, 2, 9, 10],
            [1, 0, 6, 4],
            [15, 7, 0, 8],
            [6, 3, 12, 0]
        ])
        
        tour, cost = nearest_neighbor(distances)
        
        assert len(tour) == 4
        assert len(set(tour)) == 4  # All unique
        assert cost > 0
    
    def test_2opt_improvement(self):
        """Test 2-opt local search."""
        from pimst.algorithms import two_opt_improve
        
        # Create simple instance
        n = 10
        distances = np.random.rand(n, n)
        np.fill_diagonal(distances, 0)
        
        # Start with random tour
        tour = list(range(n))
        initial_cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        
        improved_tour, improved_cost = two_opt_improve(distances, tour)
        
        # Should improve or stay same
        assert improved_cost <= initial_cost
    
    def test_3opt_improvement(self):
        """Test 3-opt local search."""
        from pimst.algorithms import three_opt_improve
        
        n = 15
        distances = np.random.rand(n, n)
        np.fill_diagonal(distances, 0)
        
        # Start with NN tour
        from pimst.algorithms import nearest_neighbor
        tour, initial_cost = nearest_neighbor(distances)
        
        improved_tour, improved_cost = three_opt_improve(distances, tour)
        
        # 3-opt should improve or match 2-opt
        assert improved_cost <= initial_cost


class TestGravityAlgorithms:
    """Test gravity-based algorithms."""
    
    def test_gravity_solver(self):
        """Test gravity-based TSP solver."""
        from pimst.gravity import gravity_solver
        
        # Create instance with coordinates
        n = 20
        coords = np.random.rand(n, 2) * 100
        
        distances = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                distances[i][j] = np.linalg.norm(coords[i] - coords[j])
        
        tour, cost = gravity_solver(distances, coords)
        
        assert len(tour) == n
        assert cost > 0
    
    def test_gravity_forces(self):
        """Test gravity force calculations."""
        from pimst.gravity import calculate_forces
        
        coords = np.array([
            [0, 0],
            [1, 0],
            [0, 1]
        ])
        
        forces = calculate_forces(coords)
        
        assert forces.shape == (3, 2)
        assert np.all(np.isfinite(forces))


class TestVersionComparison:
    """Compare different algorithm versions."""
    
    def test_v14_vs_v17(self):
        """Compare v14.x and v17.x performance."""
        from pimst.algorithms import v14_solver, v17_solver
        
        n = 30
        distances = np.random.rand(n, n)
        np.fill_diagonal(distances, 0)
        
        # Test v14
        tour_v14, cost_v14 = v14_solver(distances)
        
        # Test v17
        tour_v17, cost_v17 = v17_solver(distances)
        
        # Both should be valid
        assert len(tour_v14) == n
        assert len(tour_v17) == n
        
        # v17 should be competitive
        ratio = cost_v17 / cost_v14
        assert ratio < 1.2, f"v17 is {ratio:.2f}x worse than v14"
    
    def test_version_speed(self):
        """Test speed of different versions."""
        from pimst.algorithms import fast_heuristic, v14_solver
        
        n = 50
        distances = np.random.rand(n, n)
        np.fill_diagonal(distances, 0)
        
        # Fast heuristic should be faster
        start = time.time()
        tour_fast, cost_fast = fast_heuristic(distances)
        time_fast = time.time() - start
        
        start = time.time()
        tour_v14, cost_v14 = v14_solver(distances)
        time_v14 = time.time() - start
        
        # Fast should be at least 2x faster
        assert time_fast < time_v14 / 2, \
            f"Fast: {time_fast:.3f}s, v14: {time_v14:.3f}s"


class TestCandidateLists:
    """Test candidate list functionality."""
    
    def test_candidate_list_creation(self):
        """Test creating candidate lists."""
        from pimst.utils import create_candidate_lists
        
        distances = np.random.rand(20, 20)
        np.fill_diagonal(distances, 0)
        
        candidates = create_candidate_lists(distances, k=5)
        
        assert len(candidates) == 20
        assert all(len(c) == 5 for c in candidates)
    
    def test_candidate_list_quality(self):
        """Test that candidate lists contain nearest neighbors."""
        from pimst.utils import create_candidate_lists
        
        n = 15
        distances = np.random.rand(n, n)
        np.fill_diagonal(distances, 0)
        
        k = 5
        candidates = create_candidate_lists(distances, k=k)
        
        # Check that candidates are actually nearest
        for i in range(n):
            sorted_indices = np.argsort(distances[i])
            sorted_indices = sorted_indices[sorted_indices != i][:k]
            
            # Should match (order might differ)
            assert set(candidates[i]) == set(sorted_indices)


class TestUtilities:
    """Test utility functions."""
    
    def test_tour_cost_calculation(self):
        """Test tour cost calculation."""
        from pimst.utils import calculate_tour_cost
        
        distances = np.array([
            [0, 1, 2],
            [1, 0, 3],
            [2, 3, 0]
        ])
        
        tour = [0, 1, 2]
        cost = calculate_tour_cost(distances, tour)
        
        # 0->1: 1, 1->2: 3, 2->0: 2
        assert cost == 6
    
    def test_tour_validation(self):
        """Test tour validation."""
        from pimst.utils import is_valid_tour
        
        # Valid tour
        assert is_valid_tour([0, 1, 2, 3], n=4)
        
        # Invalid tours
        assert not is_valid_tour([0, 1, 2], n=4)  # Missing node
        assert not is_valid_tour([0, 1, 1, 2], n=3)  # Duplicate
        assert not is_valid_tour([0, 1, 5], n=3)  # Out of range
    
    def test_distance_matrix_validation(self):
        """Test distance matrix validation."""
        from pimst.utils import is_valid_distance_matrix
        
        # Valid symmetric matrix
        d1 = np.array([[0, 1, 2], [1, 0, 3], [2, 3, 0]])
        assert is_valid_distance_matrix(d1)
        
        # Invalid: not square
        d2 = np.array([[0, 1], [1, 0], [2, 3]])
        assert not is_valid_distance_matrix(d2)
        
        # Invalid: negative distances
        d3 = np.array([[0, -1, 2], [-1, 0, 3], [2, 3, 0]])
        assert not is_valid_distance_matrix(d3)


class TestRandomInstances:
    """Test with random instances."""
    
    @pytest.mark.parametrize("n", [10, 20, 50, 100])
    def test_different_sizes(self, n):
        """Test algorithm works for different problem sizes."""
        from pimst.algorithms import v14_solver
        
        distances = np.random.rand(n, n)
        np.fill_diagonal(distances, 0)
        
        tour, cost = v14_solver(distances)
        
        assert len(tour) == n
        assert cost > 0
    
    @pytest.mark.parametrize("seed", range(5))
    def test_different_random_seeds(self, seed):
        """Test with different random seeds."""
        from pimst.algorithms import v14_solver
        
        np.random.seed(seed)
        distances = np.random.rand(30, 30)
        np.fill_diagonal(distances, 0)
        
        tour, cost = v14_solver(distances)
        
        assert len(tour) == 30
        assert cost > 0


class TestEdgeCases:
    """Test edge cases and corner cases."""
    
    def test_minimal_instance(self):
        """Test with minimal 3-node instance."""
        from pimst.algorithms import v14_solver
        
        distances = np.array([
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ])
        
        tour, cost = v14_solver(distances)
        
        assert len(tour) == 3
        assert cost == 3.0
    
    def test_degenerate_instance(self):
        """Test with all equal distances."""
        from pimst.algorithms import v14_solver
        
        n = 10
        distances = np.ones((n, n))
        np.fill_diagonal(distances, 0)
        
        tour, cost = v14_solver(distances)
        
        assert len(tour) == n
        assert cost == n  # Each edge costs 1
    
    def test_sparse_distances(self):
        """Test with sparse distance matrix (many zeros)."""
        from pimst.algorithms import v14_solver
        
        n = 10
        distances = np.zeros((n, n))
        
        # Only add some edges
        for i in range(n-1):
            distances[i][i+1] = 1
            distances[i+1][i] = 1
        distances[0][n-1] = 1
        distances[n-1][0] = 1
        
        tour, cost = v14_solver(distances)
        
        assert len(tour) == n


# Pytest fixtures
@pytest.fixture
def small_symmetric_matrix():
    """Small symmetric distance matrix."""
    d = np.random.rand(10, 10)
    d = (d + d.T) / 2
    np.fill_diagonal(d, 0)
    return d


@pytest.fixture
def medium_symmetric_matrix():
    """Medium symmetric distance matrix."""
    d = np.random.rand(50, 50)
    d = (d + d.T) / 2
    np.fill_diagonal(d, 0)
    return d


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
