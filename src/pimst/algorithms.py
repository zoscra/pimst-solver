"""
Standard TSP algorithms: Nearest Neighbor, Lin-Kernighan, Multi-Start.
"""

import numpy as np
from numba import njit

from .utils import calculate_tour_length, create_candidate_lists
from .gravity import gravity_guided_tsp


@njit
def nearest_neighbor(coords: np.ndarray, dist_matrix: np.ndarray, start: int = 0) -> np.ndarray:
    """
    Classic Nearest Neighbor heuristic.
    
    Args:
        coords: Array of (x, y) coordinates
        dist_matrix: Distance matrix
        start: Starting city
        
    Returns:
        Tour as array of city indices
    """
    n = len(coords)
    tour = np.zeros(n, dtype=np.int32)
    visited = np.zeros(n, dtype=np.bool_)
    
    current = start
    tour[0] = current
    visited[current] = True
    
    for i in range(1, n):
        best_next = -1
        best_dist = np.inf
        
        for j in range(n):
            if not visited[j]:
                if dist_matrix[current, j] < best_dist:
                    best_dist = dist_matrix[current, j]
                    best_next = j
        
        tour[i] = best_next
        visited[best_next] = True
        current = best_next
    
    return tour


@njit
def two_opt_swap(tour: np.ndarray, i: int, j: int) -> np.ndarray:
    """
    Perform a 2-opt swap: reverse tour[i:j+1].
    
    Args:
        tour: Current tour
        i, j: Indices to reverse between (inclusive)
        
    Returns:
        New tour with segment reversed
    """
    new_tour = tour.copy()
    new_tour[i:j+1] = tour[i:j+1][::-1]
    return new_tour


@njit
def two_opt_improvement(tour: np.ndarray, dist_matrix: np.ndarray) -> tuple:
    """
    Try to improve tour with 2-opt moves.
    
    Returns:
        (improved_tour, improvement_found)
    """
    n = len(tour)
    improved = False
    best_tour = tour.copy()
    best_length = calculate_tour_length(tour, dist_matrix)
    
    for i in range(n - 1):
        for j in range(i + 2, n):
            new_tour = two_opt_swap(tour, i, j)
            new_length = calculate_tour_length(new_tour, dist_matrix)
            
            if new_length < best_length:
                best_tour = new_tour
                best_length = new_length
                improved = True
    
    return best_tour, improved


@njit
def three_opt_improvement(tour: np.ndarray, dist_matrix: np.ndarray, max_iter: int = 3) -> np.ndarray:
    """
    Simple 3-opt local search (limited iterations for speed).
    
    Args:
        tour: Initial tour
        dist_matrix: Distance matrix
        max_iter: Maximum iterations
        
    Returns:
        Improved tour
    """
    current_tour = tour.copy()
    
    for _ in range(max_iter):
        improved = False
        current_length = calculate_tour_length(current_tour, dist_matrix)
        
        # Try 2-opt moves
        new_tour, imp = two_opt_improvement(current_tour, dist_matrix)
        if imp:
            current_tour = new_tour
            improved = True
        
        if not improved:
            break
    
    return current_tour


def lin_kernighan_lite(
    coords: np.ndarray,
    dist_matrix: np.ndarray,
    max_iterations: int = 100
) -> np.ndarray:
    """
    Lin-Kernighan Lite: simplified version for speed.
    
    Uses:
    - Gravity-guided initialization
    - 2-opt and limited 3-opt
    - Candidate lists for efficiency
    
    Args:
        coords: Array of (x, y) coordinates
        dist_matrix: Distance matrix
        max_iterations: Maximum local search iterations
        
    Returns:
        Improved tour
    """
    # Start with gravity-guided tour
    tour = gravity_guided_tsp(coords, dist_matrix)
    
    # Create candidate lists for efficiency
    n = len(coords)
    k = min(20, n - 1)
    
    # Iterative improvement
    for iteration in range(max_iterations):
        # 2-opt improvement
        new_tour, improved = two_opt_improvement(tour, dist_matrix)
        
        if improved:
            tour = new_tour
        else:
            # Try 3-opt if 2-opt found no improvement
            tour = three_opt_improvement(tour, dist_matrix, max_iter=2)
            break  # Exit if no improvement
    
    return tour


def multi_start_solver(
    coords: np.ndarray,
    dist_matrix: np.ndarray,
    n_starts: int = 10
) -> np.ndarray:
    """
    Multi-start strategy: try multiple initializations and return best.
    
    Strategies:
    1. Nearest neighbor from node 0
    2. Nearest neighbor from center node
    3. Nearest neighbor from corner nodes
    4-10. Gravity-guided from different start nodes
    
    Args:
        coords: Array of (x, y) coordinates
        dist_matrix: Distance matrix
        n_starts: Number of different starts (default: 10)
        
    Returns:
        Best tour found across all starts
    """
    n = len(coords)
    best_tour = None
    best_length = np.inf
    
    # Find center node (closest to centroid)
    center_x = np.mean(coords[:, 0])
    center_y = np.mean(coords[:, 1])
    center_node = 0
    min_dist = np.inf
    for i in range(n):
        dist = np.sqrt((coords[i, 0] - center_x)**2 + (coords[i, 1] - center_y)**2)
        if dist < min_dist:
            min_dist = dist
            center_node = i
    
    # Strategy 1: NN from node 0
    if n_starts >= 1:
        tour = nearest_neighbor(coords, dist_matrix, 0)
        tour = lin_kernighan_lite(coords, dist_matrix)
        length = calculate_tour_length(tour, dist_matrix)
        if length < best_length:
            best_tour = tour
            best_length = length
    
    # Strategy 2: NN from center
    if n_starts >= 2:
        tour = nearest_neighbor(coords, dist_matrix, center_node)
        tour = lin_kernighan_lite(coords, dist_matrix)
        length = calculate_tour_length(tour, dist_matrix)
        if length < best_length:
            best_tour = tour
            best_length = length
    
    # Strategy 3+: Gravity-guided from different nodes
    for i in range(2, n_starts):
        start_node = int((i - 2) * n / (n_starts - 2))
        tour = gravity_guided_tsp(coords, dist_matrix, start_node)
        tour = lin_kernighan_lite(coords, dist_matrix)
        length = calculate_tour_length(tour, dist_matrix)
        
        if length < best_length:
            best_tour = tour
            best_length = length
    
    return best_tour


def solve_tsp_smart(
    coords: np.ndarray,
    dist_matrix: np.ndarray,
    quality: str = 'balanced'
) -> np.ndarray:
    """
    Smart algorithm selection based on instance size and quality setting.
    
    Args:
        coords: Array of (x, y) coordinates
        dist_matrix: Distance matrix
        quality: 'fast', 'balanced', or 'optimal'
        
    Returns:
        Tour as array of city indices
    """
    n = len(coords)
    
    if n < 30:
        # Small instances: just nearest neighbor
        return nearest_neighbor(coords, dist_matrix)
    
    elif n < 60:
        # Medium instances
        if quality == 'fast':
            return gravity_guided_tsp(coords, dist_matrix)
        else:
            return lin_kernighan_lite(coords, dist_matrix)
    
    elif n < 85:
        # Large instances
        if quality == 'fast':
            return lin_kernighan_lite(coords, dist_matrix)
        else:
            # Multi-start with 3 runs for balanced
            return multi_start_solver(coords, dist_matrix, n_starts=3)
    
    else:
        # Very large instances: always multi-start
        if quality == 'fast':
            n_starts = 3
        elif quality == 'balanced':
            n_starts = 5
        else:  # optimal
            n_starts = 10
        
        return multi_start_solver(coords, dist_matrix, n_starts=n_starts)
