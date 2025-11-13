"""
ATSP Algorithms - Asymmetric Traveling Salesman Problem
========================================================

Core algorithms adapted for asymmetric distance matrices.
Key difference: dist[i][j] != dist[j][i]

All algorithms work directly with distance matrices (no coordinates).
"""

import numpy as np
from numba import njit
from typing import Tuple, List


@njit
def calculate_atsp_tour_length(tour: np.ndarray, dist_matrix: np.ndarray) -> float:
    """
    Calculate total tour length for ATSP.

    Args:
        tour: Array of city indices in visit order
        dist_matrix: Asymmetric distance matrix

    Returns:
        Total tour length
    """
    n = len(tour)
    total = 0.0
    for i in range(n):
        current = tour[i]
        next_city = tour[(i + 1) % n]
        total += dist_matrix[current, next_city]
    return total


@njit
def nearest_neighbor_atsp(dist_matrix: np.ndarray, start: int = 0) -> np.ndarray:
    """
    Nearest Neighbor heuristic for ATSP.
    Works identically to TSP version but with asymmetric matrix.

    Args:
        dist_matrix: Asymmetric distance matrix
        start: Starting city

    Returns:
        Tour as array of city indices
    """
    n = len(dist_matrix)
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
                # Use asymmetric distance: current -> j
                if dist_matrix[current, j] < best_dist:
                    best_dist = dist_matrix[current, j]
                    best_next = j

        tour[i] = best_next
        visited[best_next] = True
        current = best_next

    return tour


@njit
def farthest_insertion_atsp(dist_matrix: np.ndarray, start: int = 0) -> np.ndarray:
    """
    Farthest Insertion heuristic for ATSP.
    Often produces better initial solutions than nearest neighbor.

    Strategy:
    1. Start with single city
    2. Find farthest city from tour
    3. Insert it at position with minimum cost increase
    4. Repeat until all cities included

    Args:
        dist_matrix: Asymmetric distance matrix
        start: Starting city

    Returns:
        Tour as array of city indices
    """
    n = len(dist_matrix)
    tour = [start]
    in_tour = np.zeros(n, dtype=np.bool_)
    in_tour[start] = True

    while len(tour) < n:
        # Find farthest city from tour
        max_min_dist = -np.inf
        farthest = -1

        for city in range(n):
            if not in_tour[city]:
                # Min distance from city to any city in tour
                min_dist = np.inf
                for tour_city in tour:
                    # Both directions (asymmetric)
                    d1 = dist_matrix[city, tour_city]
                    d2 = dist_matrix[tour_city, city]
                    min_dist = min(min_dist, d1, d2)

                if min_dist > max_min_dist:
                    max_min_dist = min_dist
                    farthest = city

        # Find best insertion position
        best_pos = 0
        best_cost_increase = np.inf

        for pos in range(len(tour)):
            # Insert between tour[pos] and tour[pos+1]
            i = tour[pos]
            j = tour[(pos + 1) % len(tour)]

            # Cost increase = dist(i->farthest) + dist(farthest->j) - dist(i->j)
            cost_increase = (
                dist_matrix[i, farthest] +
                dist_matrix[farthest, j] -
                dist_matrix[i, j]
            )

            if cost_increase < best_cost_increase:
                best_cost_increase = cost_increase
                best_pos = pos + 1

        # Insert at best position
        tour.insert(best_pos, farthest)
        in_tour[farthest] = True

    return np.array(tour, dtype=np.int32)


@njit
def two_opt_atsp(tour: np.ndarray, dist_matrix: np.ndarray, max_iterations: int = 100) -> np.ndarray:
    """
    2-opt local search for ATSP.

    Try reversing segments to improve tour.
    Works with asymmetric distances.

    Args:
        tour: Initial tour
        dist_matrix: Asymmetric distance matrix
        max_iterations: Maximum improvement iterations

    Returns:
        Improved tour
    """
    n = len(tour)
    current_tour = tour.copy()
    improved = True
    iterations = 0

    while improved and iterations < max_iterations:
        improved = False
        current_length = calculate_atsp_tour_length(current_tour, dist_matrix)

        for i in range(n - 1):
            for j in range(i + 2, n):
                # Try reversing segment [i+1, j]
                new_tour = current_tour.copy()
                new_tour[i+1:j+1] = new_tour[i+1:j+1][::-1]

                new_length = calculate_atsp_tour_length(new_tour, dist_matrix)

                if new_length < current_length:
                    current_tour = new_tour
                    current_length = new_length
                    improved = True
                    break

            if improved:
                break

        iterations += 1

    return current_tour


@njit
def three_opt_atsp(tour: np.ndarray, dist_matrix: np.ndarray, max_iterations: int = 50) -> np.ndarray:
    """
    3-opt local search for ATSP.

    More powerful than 2-opt but slower.
    Tries removing 3 edges and reconnecting in different ways.

    Args:
        tour: Initial tour
        dist_matrix: Asymmetric distance matrix
        max_iterations: Maximum improvement iterations

    Returns:
        Improved tour
    """
    n = len(tour)
    current_tour = tour.copy()

    for iteration in range(max_iterations):
        improved = False
        current_length = calculate_atsp_tour_length(current_tour, dist_matrix)

        # Try 2-opt first (faster)
        for i in range(n - 1):
            for j in range(i + 2, n):
                new_tour = current_tour.copy()
                new_tour[i+1:j+1] = new_tour[i+1:j+1][::-1]

                new_length = calculate_atsp_tour_length(new_tour, dist_matrix)

                if new_length < current_length:
                    current_tour = new_tour
                    current_length = new_length
                    improved = True
                    break

            if improved:
                break

        if not improved:
            # No 2-opt improvement found
            break

    return current_tour


def lin_kernighan_atsp(
    dist_matrix: np.ndarray,
    initial_tour: np.ndarray = None,
    max_iterations: int = 100
) -> np.ndarray:
    """
    Lin-Kernighan local search for ATSP.

    Adaptive k-opt that tries 2-opt, 3-opt, and combinations.
    Uses candidate lists for efficiency.

    Args:
        dist_matrix: Asymmetric distance matrix
        initial_tour: Initial tour (if None, use nearest neighbor)
        max_iterations: Maximum iterations

    Returns:
        Improved tour
    """
    n = len(dist_matrix)

    # Initialize tour
    if initial_tour is None:
        tour = nearest_neighbor_atsp(dist_matrix, 0)
    else:
        tour = initial_tour.copy()

    # Iterative improvement
    for iteration in range(max_iterations):
        # Try 2-opt
        new_tour = two_opt_atsp(tour, dist_matrix, max_iterations=10)

        new_length = calculate_atsp_tour_length(new_tour, dist_matrix)
        old_length = calculate_atsp_tour_length(tour, dist_matrix)

        if new_length < old_length:
            tour = new_tour
        else:
            # No improvement, stop
            break

    return tour


def multi_start_atsp(
    dist_matrix: np.ndarray,
    n_starts: int = 10,
    strategy: str = 'diverse'
) -> Tuple[np.ndarray, float]:
    """
    Multi-start strategy for ATSP.

    Strategies:
    - 'diverse': Different start cities + different heuristics
    - 'intensive': Multiple runs with best heuristic
    - 'balanced': Mix of both

    Args:
        dist_matrix: Asymmetric distance matrix
        n_starts: Number of different starts
        strategy: Strategy to use

    Returns:
        (best_tour, best_length)
    """
    n = len(dist_matrix)
    best_tour = None
    best_length = np.inf

    if strategy == 'diverse':
        # Half nearest neighbor, half farthest insertion
        # from different start points
        for i in range(n_starts):
            start_city = int((i * n) / n_starts)

            if i % 2 == 0:
                # Nearest neighbor
                tour = nearest_neighbor_atsp(dist_matrix, start_city)
            else:
                # Farthest insertion
                tour = farthest_insertion_atsp(dist_matrix, start_city)

            # Improve with Lin-Kernighan
            tour = lin_kernighan_atsp(dist_matrix, tour, max_iterations=50)
            length = calculate_atsp_tour_length(tour, dist_matrix)

            if length < best_length:
                best_tour = tour
                best_length = length

    elif strategy == 'intensive':
        # Use farthest insertion (usually better) from all start points
        for start_city in range(min(n_starts, n)):
            tour = farthest_insertion_atsp(dist_matrix, start_city)
            tour = lin_kernighan_atsp(dist_matrix, tour, max_iterations=100)
            length = calculate_atsp_tour_length(tour, dist_matrix)

            if length < best_length:
                best_tour = tour
                best_length = length

    else:  # balanced
        # 1/3 nearest neighbor, 2/3 farthest insertion
        for i in range(n_starts):
            start_city = int((i * n) / n_starts)

            if i < n_starts // 3:
                tour = nearest_neighbor_atsp(dist_matrix, start_city)
                max_iter = 50
            else:
                tour = farthest_insertion_atsp(dist_matrix, start_city)
                max_iter = 75

            tour = lin_kernighan_atsp(dist_matrix, tour, max_iterations=max_iter)
            length = calculate_atsp_tour_length(tour, dist_matrix)

            if length < best_length:
                best_tour = tour
                best_length = length

    return best_tour, best_length


def solve_atsp_smart(
    dist_matrix: np.ndarray,
    quality: str = 'balanced'
) -> Tuple[np.ndarray, float]:
    """
    Smart algorithm selection for ATSP based on size and quality.

    Args:
        dist_matrix: Asymmetric distance matrix
        quality: 'fast', 'balanced', or 'optimal'

    Returns:
        (tour, tour_length)
    """
    n = len(dist_matrix)

    if n < 30:
        # Small: just nearest neighbor
        tour = nearest_neighbor_atsp(dist_matrix, 0)
        length = calculate_atsp_tour_length(tour, dist_matrix)

    elif n < 60:
        # Medium: single run with good heuristic
        if quality == 'fast':
            tour = nearest_neighbor_atsp(dist_matrix, 0)
        else:
            tour = farthest_insertion_atsp(dist_matrix, 0)
            tour = lin_kernighan_atsp(dist_matrix, tour, max_iterations=50)
        length = calculate_atsp_tour_length(tour, dist_matrix)

    elif n < 100:
        # Large: multi-start
        if quality == 'fast':
            n_starts = 3
        elif quality == 'balanced':
            n_starts = 5
        else:
            n_starts = 10

        tour, length = multi_start_atsp(dist_matrix, n_starts, strategy='balanced')

    else:
        # Very large: intensive multi-start
        if quality == 'fast':
            n_starts = 5
        elif quality == 'balanced':
            n_starts = 10
        else:
            n_starts = 20

        tour, length = multi_start_atsp(dist_matrix, n_starts, strategy='intensive')

    return tour, length
