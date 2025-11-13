"""
Christofides Algorithm - Implementación completa
"""
import numpy as np
import networkx as nx
from scipy.sparse.csgraph import minimum_spanning_tree

def christofides_complete(coords: np.ndarray, distances: np.ndarray) -> np.ndarray:
    """
    Christofides algorithm con NetworkX.
    Garantiza <= 1.5x óptimo.
    """
    n = len(coords)
    
    # 1. MST
    mst = minimum_spanning_tree(distances)
    
    # 2. Crear grafo NetworkX
    G_mst = nx.Graph()
    mst_array = mst.toarray()
    for i in range(n):
        for j in range(i+1, n):
            if mst_array[i][j] > 0:
                G_mst.add_edge(i, j, weight=mst_array[i][j])
    
    # 3. Encontrar vértices de grado impar
    odd_vertices = [v for v in G_mst.nodes() if G_mst.degree(v) % 2 == 1]
    
    # 4. Matching mínimo en vértices impares
    if len(odd_vertices) > 0:
        G_odd = nx.Graph()
        for i in range(len(odd_vertices)):
            for j in range(i+1, len(odd_vertices)):
                v1, v2 = odd_vertices[i], odd_vertices[j]
                G_odd.add_edge(v1, v2, weight=-distances[v1][v2])
        
        matching = nx.max_weight_matching(G_odd, maxcardinality=True)
        
        # Agregar matching al MST
        for u, v in matching:
            G_mst.add_edge(u, v, weight=distances[u][v])
    
    # 5. Eulerian circuit
    eulerian = list(nx.eulerian_circuit(G_mst, source=0))
    
    # 6. Convertir a Hamiltonian
    visited = set()
    tour = []
    for u, v in eulerian:
        if u not in visited:
            tour.append(u)
            visited.add(u)
    
    return np.array(tour)
