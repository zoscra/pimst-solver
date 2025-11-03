"""
Gravity-Guided TSP - Novel physics-inspired initialization heuristic.

This module implements the core innovation: treating cities as gravitational
masses where isolated nodes have higher mass and attract tour construction.
"""

import numpy as np
from numba import njit

from .utils import calculate_tour_length, create_candidate_lists


@njit
def calculate_gravity_masses(coords: np.ndarray, dist_matrix: np.ndarray) -> np.ndarray:
    """
    Calculate gravitational mass for each city based on isolation.
    
    Cities that are:
    - Far from center → Higher mass
    - Poorly connected (few nearby neighbors) → Higher mass
    
    This ensures isolated cities are prioritized in tour construction.
    
    Args:
        coords: Array of (x, y) coordinates
        dist_matrix: Distance matrix
        
    Returns:
        Array of masses for each city
    """
    n = len(coords)
    
    # Calculate center of mass
    center_x = np.mean(coords[:, 0])
    center_y = np.mean(coords[:, 1])
    
    masses = np.zeros(n, dtype=np.float64)
    
    for i in range(n):
        # Distance to center (normalized)
        dx = coords[i, 0] - center_x
        dy = coords[i, 1] - center_y
        dist_to_center = np.sqrt(dx * dx + dy * dy)
        
        # Average distance to k nearest neighbors (connectivity)
        k = min(5, n - 1)
        nearest_dists = np.sort(dist_matrix[i])[1:k+1]  # Exclude self
        avg_neighbor_dist = np.mean(nearest_dists)
        
        # Degree (number of close neighbors) - normalized
        threshold = np.median(dist_matrix[i])
        degree = np.sum(dist_matrix[i] < threshold) - 1  # Exclude self
        degree_normalized = degree / (n - 1)
        
        # Mass formula: isolated + far from center = high mass
        # Well-connected + near center = low mass
        mass = (dist_to_center + avg_neighbor_dist) * (1.0 - degree_normalized + 0.1)
        masses[i] = mass
    
    # Normalize masses to [1, 10] range for numerical stability
    min_mass = np.min(masses)
    max_mass = np.max(masses)
    if max_mass > min_mass:
        masses = 1.0 + 9.0 * (masses - min_mass) / (max_mass - min_mass)
    else:
        masses = np.ones(n, dtype=np.float64) * 5.0
    
    return masses


@njit
def gravity_weighted_distances(
    dist_matrix: np.ndarray,
    masses: np.ndarray,
    epsilon: float = 1e-6
) -> np.ndarray:
    """
    Calculate gravity-weighted distances using F = G * m1 * m2 / r²
    
    High-mass cities attract more strongly (shorter effective distance).
    
    Args:
        dist_matrix: Original distance matrix
        masses: Gravitational mass for each city
        epsilon: Small value to avoid division by zero
        
    Returns:
        Gravity-weighted distance matrix
    """
    n = len(dist_matrix)
    weighted = np.zeros((n, n), dtype=np.float64)
    
    for i in range(n):
        for j in range(n):
            if i == j:
                weighted[i, j] = 0.0
            else:
                # Gravitational attraction: higher mass = stronger attraction
                # = shorter effective distance for tour construction
                gravity_factor = masses[i] * masses[j]
                weighted[i, j] = dist_matrix[i, j] / (gravity_factor + epsilon)
    
    return weighted


@njit
def nearest_neighbor_gravity(
    coords: np.ndarray,
    weighted_dist: np.ndarray,
    start_node: int = 0
) -> np.ndarray:
    """
    Nearest neighbor using gravity-weighted distances.
    
    Args:
        coords: City coordinates
        weighted_dist: Gravity-weighted distance matrix
        start_node: Starting city
        
    Returns:
        Tour as array of city indices
    """
    n = len(coords)
    tour = np.zeros(n, dtype=np.int32)
    visited = np.zeros(n, dtype=np.bool_)
    
    current = start_node
    tour[0] = current
    visited[current] = True
    
    for i in range(1, n):
        best_next = -1
        best_dist = np.inf
        
        for j in range(n):
            if not visited[j]:
                if weighted_dist[current, j] < best_dist:
                    best_dist = weighted_dist[current, j]
                    best_next = j
        
        tour[i] = best_next
        visited[best_next] = True
        current = best_next
    
    return tour


def gravity_guided_tsp(
    coords: np.ndarray,
    dist_matrix: np.ndarray,
    start_node: int = 0
) -> np.ndarray:
    """
    Main gravity-guided TSP solver.
    
    This is the novel contribution: uses gravitational physics to guide
    tour construction, naturally prioritizing isolated cities.
    
    Args:
        coords: Array of (x, y) coordinates
        dist_matrix: Euclidean distance matrix
        start_node: Starting city (default: 0)
        
    Returns:
        Tour as array of city indices
        
    Example:
        >>> coords = np.array([(0,0), (1,5), (5,2), (8,3)])
        >>> dist_matrix = create_distance_matrix(coords)
        >>> tour = gravity_guided_tsp(coords, dist_matrix)
        >>> print(tour)
    """
    # Calculate gravitational masses
    masses = calculate_gravity_masses(coords, dist_matrix)
    
    # Create gravity-weighted distance matrix
    weighted_dist = gravity_weighted_distances(dist_matrix, masses)
    
    # Construct tour using weighted distances
    tour = nearest_neighbor_gravity(coords, weighted_dist, start_node)
    
    return tour


def gravity_multi_start(
    coords: np.ndarray,
    dist_matrix: np.ndarray,
    n_starts: int = 3
) -> np.ndarray:
    """
    Multi-start gravity-guided TSP.
    
    Tries multiple starting nodes and returns best tour.
    
    Args:
        coords: Array of (x, y) coordinates
        dist_matrix: Distance matrix
        n_starts: Number of different starts to try
        
    Returns:
        Best tour found
    """
    n = len(coords)
    best_tour = None
    best_length = np.inf
    
    # Calculate masses once
    masses = calculate_gravity_masses(coords, dist_matrix)
    weighted_dist = gravity_weighted_distances(dist_matrix, masses)
    
    # Try different starting nodes
    start_nodes = np.linspace(0, n-1, n_starts, dtype=np.int32)
    
    for start in start_nodes:
        tour = nearest_neighbor_gravity(coords, weighted_dist, start)
        length = calculate_tour_length(tour, dist_matrix)
        
        if length < best_length:
            best_length = length
            best_tour = tour
    
    return best_tour
