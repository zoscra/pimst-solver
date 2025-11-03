"""
Utility functions for PIMST.
"""

import numpy as np
from numba import njit


@njit
def calculate_tour_length(tour: np.ndarray, dist_matrix: np.ndarray) -> float:
    """Calculate total length of a tour."""
    n = len(tour)
    length = 0.0
    for i in range(n):
        length += dist_matrix[tour[i], tour[(i + 1) % n]]
    return length


@njit
def create_distance_matrix(coords: np.ndarray) -> np.ndarray:
    """Create Euclidean distance matrix from coordinates."""
    n = len(coords)
    dist_matrix = np.zeros((n, n), dtype=np.float64)
    
    for i in range(n):
        for j in range(i + 1, n):
            dx = coords[i, 0] - coords[j, 0]
            dy = coords[i, 1] - coords[j, 1]
            dist = np.sqrt(dx * dx + dy * dy)
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    
    return dist_matrix


@njit
def create_candidate_lists(dist_matrix: np.ndarray, k: int = 20) -> np.ndarray:
    """
    Create candidate lists for each city (k nearest neighbors).
    
    Args:
        dist_matrix: Distance matrix
        k: Number of nearest neighbors to keep
        
    Returns:
        Array of shape (n, k) with k nearest neighbors for each city
    """
    n = len(dist_matrix)
    k = min(k, n - 1)
    candidates = np.zeros((n, k), dtype=np.int32)
    
    for i in range(n):
        # Sort cities by distance
        distances = dist_matrix[i].copy()
        distances[i] = np.inf  # Exclude self
        sorted_indices = np.argsort(distances)
        candidates[i] = sorted_indices[:k]
    
    return candidates


def validate_tour(tour: np.ndarray, n: int) -> bool:
    """Validate that tour is a valid permutation of cities."""
    if len(tour) != n:
        return False
    if len(set(tour)) != n:
        return False
    if not all(0 <= city < n for city in tour):
        return False
    return True


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 0.001:
        return f"{seconds*1000000:.1f}μs"
    elif seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
