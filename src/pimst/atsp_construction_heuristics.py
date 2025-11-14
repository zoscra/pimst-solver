"""
Advanced Construction Heuristics for ATSP
==========================================

Implements high-quality initial solution construction methods:

1. Farthest Insertion: Builds tour by inserting farthest city
2. Cheapest Insertion: Inserts city with minimum cost increase
3. Savings Algorithm (ATSP adaptation): Based on savings criterion
4. Nearest Addition: Adds nearest unvisited city to tour

These provide better starting points than simple Nearest Neighbor,
leading to better final solutions.

Expected improvement: -2 to -3 percentage points in gap.

Author: PIMST Project
Date: 2025-11-14
"""

import numpy as np
from numba import njit


@njit
def farthest_insertion_atsp(dist_matrix, start_city=None):
    """
    Farthest Insertion heuristic for ATSP.

    Builds a tour by repeatedly inserting the city that is farthest
    from the current partial tour, at the position that minimizes
    the cost increase.

    This generally produces better tours than Nearest Neighbor.

    Parameters
    ----------
    dist_matrix : ndarray
        Asymmetric distance matrix (n x n)
    start_city : int, optional
        Starting city (if None, chooses city with largest total distance)

    Returns
    -------
    tour : ndarray
        Tour as array of city indices
    cost : float
        Total tour cost
    """
    n = len(dist_matrix)

    # Choose starting city if not provided
    if start_city is None:
        # Start with city that has maximum sum of distances
        sums = np.zeros(n)
        for i in range(n):
            sums[i] = np.sum(dist_matrix[i, :])
        start_city = np.argmax(sums)

    # Initialize with a 2-city partial tour
    # Find farthest city from start_city
    farthest = -1
    max_dist = -1.0
    for i in range(n):
        if i != start_city:
            d = dist_matrix[start_city, i]
            if d > max_dist:
                max_dist = d
                farthest = i

    partial_tour = [start_city, farthest]
    in_tour = np.zeros(n, dtype=np.bool_)
    in_tour[start_city] = True
    in_tour[farthest] = True

    # Add remaining cities one by one
    while len(partial_tour) < n:
        # Find farthest city from partial tour
        farthest_city = -1
        max_min_dist = -1.0

        for i in range(n):
            if not in_tour[i]:
                # Find minimum distance from city i to any city in tour
                min_dist = np.inf
                for j in partial_tour:
                    d = min(dist_matrix[i, j], dist_matrix[j, i])
                    if d < min_dist:
                        min_dist = d

                if min_dist > max_min_dist:
                    max_min_dist = min_dist
                    farthest_city = i

        # Insert farthest_city at position that minimizes cost increase
        best_pos = 0
        best_increase = np.inf

        for pos in range(len(partial_tour)):
            # Cost of inserting farthest_city between partial_tour[pos] and partial_tour[pos+1]
            prev_city = partial_tour[pos]
            next_city = partial_tour[(pos + 1) % len(partial_tour)]

            old_cost = dist_matrix[prev_city, next_city]
            new_cost = dist_matrix[prev_city, farthest_city] + dist_matrix[farthest_city, next_city]
            increase = new_cost - old_cost

            if increase < best_increase:
                best_increase = increase
                best_pos = pos + 1

        # Insert at best position
        partial_tour.insert(best_pos, farthest_city)
        in_tour[farthest_city] = True

    # Convert to numpy array
    tour = np.array(partial_tour, dtype=np.int32)

    # Calculate total cost
    cost = 0.0
    for i in range(n):
        cost += dist_matrix[tour[i], tour[(i + 1) % n]]

    return tour, cost


@njit
def cheapest_insertion_atsp(dist_matrix, start_city=None):
    """
    Cheapest Insertion heuristic for ATSP.

    Builds tour by repeatedly inserting the city that results in
    the smallest cost increase.

    Parameters
    ----------
    dist_matrix : ndarray
        Asymmetric distance matrix
    start_city : int, optional
        Starting city

    Returns
    -------
    tour : ndarray
        Tour as array of city indices
    cost : float
        Total tour cost
    """
    n = len(dist_matrix)

    if start_city is None:
        start_city = 0

    # Initialize with triangle (3 cities)
    # Find two nearest cities to start_city
    distances = []
    for i in range(n):
        if i != start_city:
            distances.append((i, dist_matrix[start_city, i]))

    distances.sort(key=lambda x: x[1])
    city1 = distances[0][0]
    city2 = distances[1][0]

    partial_tour = [start_city, city1, city2]
    in_tour = np.zeros(n, dtype=np.bool_)
    in_tour[start_city] = True
    in_tour[city1] = True
    in_tour[city2] = True

    # Add remaining cities
    while len(partial_tour) < n:
        best_city = -1
        best_pos = -1
        best_increase = np.inf

        # Try inserting each unvisited city
        for city in range(n):
            if in_tour[city]:
                continue

            # Try all insertion positions
            for pos in range(len(partial_tour)):
                prev_city = partial_tour[pos]
                next_city = partial_tour[(pos + 1) % len(partial_tour)]

                old_cost = dist_matrix[prev_city, next_city]
                new_cost = dist_matrix[prev_city, city] + dist_matrix[city, next_city]
                increase = new_cost - old_cost

                if increase < best_increase:
                    best_increase = increase
                    best_city = city
                    best_pos = pos + 1

        # Insert best city at best position
        partial_tour.insert(best_pos, best_city)
        in_tour[best_city] = True

    tour = np.array(partial_tour, dtype=np.int32)

    cost = 0.0
    for i in range(n):
        cost += dist_matrix[tour[i], tour[(i + 1) % n]]

    return tour, cost


@njit
def nearest_addition_atsp(dist_matrix, start_city=None):
    """
    Nearest Addition heuristic for ATSP.

    Starts with a partial tour and repeatedly adds the nearest
    unvisited city to the tour.

    Parameters
    ----------
    dist_matrix : ndarray
        Asymmetric distance matrix
    start_city : int, optional
        Starting city

    Returns
    -------
    tour : ndarray
        Tour as array of city indices
    cost : float
        Total tour cost
    """
    n = len(dist_matrix)

    if start_city is None:
        start_city = 0

    # Start with single city
    partial_tour = [start_city]
    in_tour = np.zeros(n, dtype=np.bool_)
    in_tour[start_city] = True

    # Add cities one by one
    while len(partial_tour) < n:
        # Find nearest city to any city in tour
        nearest_city = -1
        min_dist = np.inf

        for city in range(n):
            if in_tour[city]:
                continue

            for tour_city in partial_tour:
                d = dist_matrix[tour_city, city]
                if d < min_dist:
                    min_dist = d
                    nearest_city = city

        # Find best insertion position for nearest_city
        best_pos = 0
        best_increase = np.inf

        for pos in range(len(partial_tour)):
            prev_city = partial_tour[pos]
            next_city = partial_tour[(pos + 1) % len(partial_tour)]

            old_cost = dist_matrix[prev_city, next_city]
            new_cost = dist_matrix[prev_city, nearest_city] + dist_matrix[nearest_city, next_city]
            increase = new_cost - old_cost

            if increase < best_increase:
                best_increase = increase
                best_pos = pos + 1

        partial_tour.insert(best_pos, nearest_city)
        in_tour[nearest_city] = True

    tour = np.array(partial_tour, dtype=np.int32)

    cost = 0.0
    for i in range(n):
        cost += dist_matrix[tour[i], tour[(i + 1) % n]]

    return tour, cost


@njit
def savings_algorithm_atsp(dist_matrix):
    """
    Savings Algorithm adapted for ATSP.

    Classical Clarke-Wright savings algorithm adapted for asymmetric distances.
    Builds tour by merging routes based on savings.

    Parameters
    ----------
    dist_matrix : ndarray
        Asymmetric distance matrix

    Returns
    -------
    tour : ndarray
        Tour as array of city indices
    cost : float
        Total tour cost
    """
    n = len(dist_matrix)

    # Use city 0 as depot initially
    depot = 0

    # Calculate savings for all pairs (i, j)
    savings = []
    for i in range(1, n):
        for j in range(i + 1, n):
            # Savings from connecting i and j instead of both to depot
            # s_ij = d(depot, i) + d(depot, j) - d(i, j)
            s = dist_matrix[depot, i] + dist_matrix[depot, j] - dist_matrix[i, j]
            savings.append((s, i, j))

    # Sort by descending savings
    savings.sort(reverse=True, key=lambda x: x[0])

    # Initialize routes (each city is its own route initially)
    routes = {}
    for i in range(1, n):
        routes[i] = [i]

    # Merge routes based on savings
    for s, i, j in savings:
        # Check if i and j are in different routes
        route_i = None
        route_j = None

        for key, route in routes.items():
            if i in route:
                route_i = key
            if j in route:
                route_j = key

        if route_i is not None and route_j is not None and route_i != route_j:
            # Merge routes
            merged = routes[route_i] + routes[route_j]
            routes[route_i] = merged
            del routes[route_j]

    # Flatten remaining routes into single tour
    tour = [depot]
    for key in routes:
        tour.extend(routes[key])

    tour = np.array(tour, dtype=np.int32)

    cost = 0.0
    for i in range(n):
        cost += dist_matrix[tour[i], tour[(i + 1) % n]]

    return tour, cost


def get_best_construction(dist_matrix, methods=None, time_limit=5.0):
    """
    Try multiple construction heuristics and return the best one.

    Parameters
    ----------
    dist_matrix : ndarray
        Asymmetric distance matrix
    methods : list, optional
        List of methods to try. Default: all methods
    time_limit : float
        Maximum time for all constructions

    Returns
    -------
    best_tour : ndarray
        Best tour found
    best_cost : float
        Cost of best tour
    method_name : str
        Name of method that produced best tour
    """
    import time

    if methods is None:
        methods = ['farthest_insertion', 'cheapest_insertion',
                  'nearest_addition', 'savings']

    start_time = time.time()
    best_tour = None
    best_cost = np.inf
    best_method = None

    construction_funcs = {
        'farthest_insertion': farthest_insertion_atsp,
        'cheapest_insertion': cheapest_insertion_atsp,
        'nearest_addition': nearest_addition_atsp,
        'savings': savings_algorithm_atsp,
    }

    for method in methods:
        if time.time() - start_time > time_limit:
            break

        if method in construction_funcs:
            try:
                tour, cost = construction_funcs[method](dist_matrix)

                if cost < best_cost:
                    best_cost = cost
                    best_tour = tour
                    best_method = method
            except:
                continue

    return best_tour, best_cost, best_method


if __name__ == '__main__':
    # Test construction heuristics
    print("Testing ATSP Construction Heuristics")
    print("=" * 60)

    n = 30
    np.random.seed(42)

    # Generate random ATSP
    dist_matrix = np.random.rand(n, n) * 100
    np.fill_diagonal(dist_matrix, 0)

    # Make asymmetric
    for i in range(n):
        for j in range(i + 1, n):
            if np.random.random() < 0.4:
                dist_matrix[i, j] *= np.random.uniform(1.5, 3.0)

    print(f"\nTesting on random ATSP with n={n}")
    print("\nResults:")

    # Test all methods
    methods = {
        'Farthest Insertion': farthest_insertion_atsp,
        'Cheapest Insertion': cheapest_insertion_atsp,
        'Nearest Addition': nearest_addition_atsp,
        'Savings Algorithm': savings_algorithm_atsp,
    }

    for name, func in methods.items():
        tour, cost = func(dist_matrix)
        print(f"  {name:20s}: Cost = {cost:8.2f}")

    # Test best construction
    print("\nBest Construction:")
    best_tour, best_cost, best_method = get_best_construction(dist_matrix)
    print(f"  Method: {best_method}")
    print(f"  Cost: {best_cost:.2f}")
