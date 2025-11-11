"""
Cluster-First-Route-Second Solver
"""

import numpy as np
from typing import List, Tuple


def calculate_cost(tour: List[int], dist_matrix: np.ndarray) -> float:
    """Calcular costo de un tour."""
    n = len(tour)
    return sum(dist_matrix[tour[i]][tour[(i+1)%n]] for i in range(n))


def cluster_first_route_second(coords: np.ndarray, dist_matrix: np.ndarray) -> Tuple[List[int], float]:
    """
    Divide en clusters, resuelve cada uno, y une con 2-opt.
    """
    from pimst.algorithms import gravity_guided_tsp, two_opt_improvement
    
    n = len(coords)
    
    # Para problemas pequeños, usar directamente
    if n < 40:
        tour = gravity_guided_tsp(coords, dist_matrix)
        tour_improved, _ = two_opt_improvement(tour, dist_matrix)  # _ es booleano!
        cost = calculate_cost(tour_improved.tolist(), dist_matrix)
        return tour_improved.tolist(), cost
    
    # Detectar clusters con KMeans
    try:
        from sklearn.cluster import KMeans
        n_clusters = min(4, max(2, n // 15))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(coords)
    except Exception:
        # Fallback: sin clustering
        tour = gravity_guided_tsp(coords, dist_matrix)
        tour_improved, _ = two_opt_improvement(tour, dist_matrix)
        cost = calculate_cost(tour_improved.tolist(), dist_matrix)
        return tour_improved.tolist(), cost
    
    # Resolver cada cluster
    cluster_tours = []
    for cluster_id in range(n_clusters):
        mask = labels == cluster_id
        indices = np.where(mask)[0]
        
        if len(indices) < 2:
            cluster_tours.append(indices.tolist())
            continue
        
        # Resolver cluster
        cluster_coords = coords[indices]
        cluster_dist = dist_matrix[np.ix_(indices, indices)]
        
        # Usar gravity para cada cluster (rápido)
        local_tour = gravity_guided_tsp(cluster_coords, cluster_dist)
        
        # Mapear a índices globales
        global_tour = [indices[i] for i in local_tour]
        cluster_tours.append(global_tour)
    
    # Unir clusters
    tour = []
    for cluster_tour in cluster_tours:
        tour.extend(cluster_tour)
    
    # Mejorar con 2-opt global
    tour_array = np.array(tour, dtype=int)
    tour_improved, _ = two_opt_improvement(tour_array, dist_matrix)  # _ es booleano
    
    # SIEMPRE calcular costo manualmente
    final_cost = calculate_cost(tour_improved.tolist(), dist_matrix)
    
    # Verificar validez
    if len(set(tour_improved)) != n:
        # Fallback
        tour = gravity_guided_tsp(coords, dist_matrix)
        tour_improved, _ = two_opt_improvement(tour, dist_matrix)
        final_cost = calculate_cost(tour_improved.tolist(), dist_matrix)
    
    return tour_improved.tolist(), final_cost
