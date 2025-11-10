"""
Pytest Configuration and Shared Fixtures
=========================================

Shared test fixtures and configuration for PIMST tests.
"""

import pytest
import numpy as np
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ============================================================================
# Distance Matrix Fixtures
# ============================================================================

@pytest.fixture
def tiny_distances():
    """Minimal 3-node distance matrix."""
    return np.array([
        [0, 1, 2],
        [1, 0, 3],
        [2, 3, 0]
    ], dtype=float)


@pytest.fixture
def small_distances():
    """Small 10-node random distance matrix."""
    np.random.seed(42)
    d = np.random.rand(10, 10) * 100
    d = (d + d.T) / 2  # Make symmetric
    np.fill_diagonal(d, 0)
    return d


@pytest.fixture
def medium_distances():
    """Medium 50-node random distance matrix."""
    np.random.seed(42)
    d = np.random.rand(50, 50) * 100
    d = (d + d.T) / 2
    np.fill_diagonal(d, 0)
    return d


@pytest.fixture
def large_distances():
    """Large 100-node random distance matrix."""
    np.random.seed(42)
    d = np.random.rand(100, 100) * 100
    d = (d + d.T) / 2
    np.fill_diagonal(d, 0)
    return d


# ============================================================================
# Coordinate Fixtures
# ============================================================================

@pytest.fixture
def circle_coords_small():
    """Small circle with 20 points."""
    n = 20
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    return np.column_stack([
        np.cos(angles),
        np.sin(angles)
    ])


@pytest.fixture
def circle_coords_medium():
    """Medium circle with 50 points."""
    n = 50
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    return np.column_stack([
        np.cos(angles),
        np.sin(angles)
    ])


@pytest.fixture
def random_coords():
    """Random 2D coordinates."""
    np.random.seed(42)
    return np.random.rand(30, 2) * 100


@pytest.fixture
def grid_coords():
    """Grid coordinates 5x5."""
    x = np.repeat(np.arange(5), 5)
    y = np.tile(np.arange(5), 5)
    return np.column_stack([x, y])


# ============================================================================
# Helper Functions
# ============================================================================

def coords_to_distances(coords):
    """Convert coordinates to distance matrix."""
    n = len(coords)
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = np.linalg.norm(coords[i] - coords[j])
    return distances


@pytest.fixture
def coords_to_dist():
    """Fixture that returns the conversion function."""
    return coords_to_distances


# ============================================================================
# TSP Instance Fixtures
# ============================================================================

@pytest.fixture
def tsp_instances():
    """Collection of different TSP instances for testing."""
    np.random.seed(42)
    
    instances = {
        'tiny': np.array([[0, 1, 2], [1, 0, 3], [2, 3, 0]], dtype=float),
        
        'small_random': lambda: (lambda d: (d + d.T) / 2)(np.random.rand(10, 10) * 100),
        
        'medium_random': lambda: (lambda d: (d + d.T) / 2)(np.random.rand(50, 50) * 100),
        
        'circle_20': coords_to_distances(
            np.column_stack([
                np.cos(np.linspace(0, 2*np.pi, 20, endpoint=False)),
                np.sin(np.linspace(0, 2*np.pi, 20, endpoint=False))
            ])
        ),
    }
    
    return instances


# ============================================================================
# Performance Testing
# ============================================================================

@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests."""
    import time
    
    class PerformanceTracker:
        def __init__(self):
            self.times = []
            self.costs = []
        
        def time_execution(self, func, *args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            self.times.append(elapsed)
            return result, elapsed
        
        def record_cost(self, cost):
            self.costs.append(cost)
        
        def get_stats(self):
            return {
                'mean_time': np.mean(self.times) if self.times else 0,
                'max_time': np.max(self.times) if self.times else 0,
                'min_cost': np.min(self.costs) if self.costs else 0,
                'mean_cost': np.mean(self.costs) if self.costs else 0,
            }
    
    return PerformanceTracker()


# ============================================================================
# Markers
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance benchmarks"
    )


# ============================================================================
# Test Session Info
# ============================================================================

def pytest_report_header(config):
    """Add custom header to test report."""
    return [
        "PIMST Solver Test Suite",
        f"Python: {sys.version.split()[0]}",
        f"NumPy: {np.__version__}",
        "=" * 60
    ]


# ============================================================================
# Cleanup
# ============================================================================

@pytest.fixture(autouse=True)
def reset_random_seed():
    """Reset random seed before each test."""
    np.random.seed(42)
    yield
    # Cleanup if needed


# ============================================================================
# Skip Conditions
# ============================================================================

@pytest.fixture
def skip_if_slow(request):
    """Skip test if running in fast mode."""
    if request.config.getoption("--fast", default=False):
        pytest.skip("Skipped in fast mode")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--fast",
        action="store_true",
        default=False,
        help="Skip slow tests"
    )
    parser.addoption(
        "--integration-only",
        action="store_true",
        default=False,
        help="Run only integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on options."""
    if config.getoption("--fast"):
        skip_slow = pytest.mark.skip(reason="--fast option enabled")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
    
    if config.getoption("--integration-only"):
        skip_unit = pytest.mark.skip(reason="--integration-only option enabled")
        for item in items:
            if "integration" not in item.keywords:
                item.add_marker(skip_unit)
