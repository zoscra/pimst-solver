"""
Basic tests for PIMST solver.
"""

import pytest
import numpy as np
import pimst


def test_solve_basic():
    """Test basic solve functionality."""
    coords = [(0, 0), (1, 1), (2, 0), (1, -1)]
    result = pimst.solve(coords)
    
    assert 'tour' in result
    assert 'length' in result
    assert 'time' in result
    assert 'algorithm' in result
    
    assert len(result['tour']) == 4
    assert result['length'] > 0
    assert result['time'] >= 0


def test_solve_quality_levels():
    """Test different quality settings."""
    coords = [(0, 0), (1, 5), (5, 2), (8, 3), (3, 1), (7, 6)]
    
    for quality in ['fast', 'balanced', 'optimal']:
        result = pimst.solve(coords, quality=quality)
        assert len(result['tour']) == 6
        assert result['length'] > 0


def test_solve_with_details():
    """Test detailed solution output."""
    coords = [(0, 0), (1, 1), (2, 0), (1, -1)]
    result = pimst.solve_with_details(coords)
    
    assert 'gap_estimate' in result
    assert 'iterations' in result
    assert 'initial_length' in result
    assert 'improvement' in result


def test_gravity_guided():
    """Test gravity-guided initialization."""
    coords = np.array([(0, 0), (1, 5), (5, 2), (8, 3)], dtype=np.float64)
    dist_matrix = pimst.utils.create_distance_matrix(coords)
    
    tour = pimst.gravity_guided_tsp(coords, dist_matrix)
    
    assert len(tour) == 4
    assert len(set(tour)) == 4  # All cities visited once
    assert all(0 <= city < 4 for city in tour)


def test_nearest_neighbor():
    """Test nearest neighbor algorithm."""
    coords = np.array([(0, 0), (1, 1), (2, 0)], dtype=np.float64)
    dist_matrix = pimst.utils.create_distance_matrix(coords)
    
    tour = pimst.nearest_neighbor(coords, dist_matrix)
    
    assert len(tour) == 3
    assert len(set(tour)) == 3


def test_lin_kernighan_lite():
    """Test Lin-Kernighan Lite algorithm."""
    coords = np.array([(0, 0), (1, 1), (2, 0), (1, -1)], dtype=np.float64)
    dist_matrix = pimst.utils.create_distance_matrix(coords)
    
    tour = pimst.lin_kernighan_lite(coords, dist_matrix)
    
    assert len(tour) == 4
    assert len(set(tour)) == 4


def test_multi_start():
    """Test multi-start solver."""
    coords = np.array([
        (0, 0), (1, 5), (5, 2), (8, 3), 
        (3, 1), (7, 6), (2, 4)
    ], dtype=np.float64)
    dist_matrix = pimst.utils.create_distance_matrix(coords)
    
    tour = pimst.multi_start_solver(coords, dist_matrix, n_starts=3)
    
    assert len(tour) == 7
    assert len(set(tour)) == 7


def test_tour_validation():
    """Test tour validation."""
    n = 5
    valid_tour = np.array([0, 1, 2, 3, 4])
    invalid_tour_1 = np.array([0, 1, 2, 3])  # Wrong length
    invalid_tour_2 = np.array([0, 1, 1, 3, 4])  # Duplicate
    invalid_tour_3 = np.array([0, 1, 2, 3, 5])  # Invalid city
    
    assert pimst.utils.validate_tour(valid_tour, n) == True
    assert pimst.utils.validate_tour(invalid_tour_1, n) == False
    assert pimst.utils.validate_tour(invalid_tour_2, n) == False
    assert pimst.utils.validate_tour(invalid_tour_3, n) == False


def test_distance_matrix():
    """Test distance matrix creation."""
    coords = np.array([(0, 0), (1, 0), (0, 1)], dtype=np.float64)
    dist_matrix = pimst.utils.create_distance_matrix(coords)
    
    assert dist_matrix.shape == (3, 3)
    assert dist_matrix[0, 1] == pytest.approx(1.0)
    assert dist_matrix[0, 2] == pytest.approx(1.0)
    assert dist_matrix[1, 2] == pytest.approx(np.sqrt(2))
    
    # Symmetric
    assert np.allclose(dist_matrix, dist_matrix.T)
    
    # Zero diagonal
    assert np.all(np.diag(dist_matrix) == 0)


def test_performance_small():
    """Test performance on small instance."""
    import time
    
    coords = [(i, i) for i in range(20)]
    
    start = time.time()
    result = pimst.solve(coords, quality='fast')
    elapsed = time.time() - start
    
    assert elapsed < 0.1  # Should be very fast for n=20
    assert len(result['tour']) == 20


def test_performance_medium():
    """Test performance on medium instance."""
    import time
    
    np.random.seed(42)
    coords = [(np.random.random(), np.random.random()) for _ in range(50)]
    
    start = time.time()
    result = pimst.solve(coords, quality='balanced')
    elapsed = time.time() - start
    
    assert elapsed < 1.0  # Should be fast for n=50
    assert len(result['tour']) == 50


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
