"""
Benchmark Justo: SiNo vs OR-Tools con múltiples time limits
"""

import numpy as np
import time
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from pimst.improved.sino import smart_solve

def test_circle(n=50):
    """Test en círculo perfecto."""
    print(f"\n{'='*70}")
    print(f"  CÍRCULO PERFECTO - {n} nodos")
    print(f"{'='*70}")
    
    # Crear círculo
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    coords = np.column_stack([np.cos(angles), np.sin(angles)])
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = np.linalg.norm(coords[i] - coords[j])
    
    # SiNo
    print("\n🔵 SiNo:")
    start = time.time()
    tour_sino, cost_sino = smart_solve(distances, coords)
    time_sino = time.time() - start
    print(f"   Costo: {cost_sino:.6f}")
    print(f"   Tiempo: {time_sino*1000:.2f}ms")
    
    # OR-Tools con diferentes time limits
    for tl in [1, 5, 10]:
        print(f"\n🟢 OR-Tools (time_limit={tl}s):")
        
        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distances[from_node][to_node] * 10000)
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = tl
        
        start = time.time()
        solution = routing.SolveWithParameters(search_parameters)
        time_or = time.time() - start
        
        if solution:
            tour = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                tour.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            
            cost_or = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
            
            print(f"   Costo: {cost_or:.6f}")
            print(f"   Tiempo: {time_or*1000:.2f}ms")
            
            gap = ((cost_sino - cost_or) / cost_or) * 100
            speedup = time_or / time_sino
            
            print(f"   Gap: {gap:+.2f}%")
            print(f"   Speedup de SiNo: {speedup:.2f}x")

def test_random(n=50):
    """Test aleatorio."""
    print(f"\n{'='*70}")
    print(f"  ALEATORIO - {n} nodos")
    print(f"{'='*70}")
    
    np.random.seed(42)
    coords = np.random.rand(n, 2) * 100
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distances[i][j] = np.linalg.norm(coords[i] - coords[j])
    
    # SiNo
    print("\n🔵 SiNo:")
    start = time.time()
    tour_sino, cost_sino = smart_solve(distances, coords)
    time_sino = time.time() - start
    print(f"   Costo: {cost_sino:.2f}")
    print(f"   Tiempo: {time_sino*1000:.1f}ms")
    
    # OR-Tools con time limit razonable
    print(f"\n🟢 OR-Tools (time_limit=5s):")
    
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distances[from_node][to_node] * 10000)
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 5
    
    start = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    time_or = time.time() - start
    
    if solution:
        tour = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            tour.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        
        cost_or = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        
        print(f"   Costo: {cost_or:.2f}")
        print(f"   Tiempo: {time_or*1000:.1f}ms")
        
        gap = ((cost_sino - cost_or) / cost_or) * 100
        speedup = time_or / time_sino
        
        print(f"\n📊 Comparación:")
        print(f"   Gap: {gap:+.2f}%")
        print(f"   Speedup: {speedup:.2f}x")

if __name__ == '__main__':
    test_circle(50)
    test_random(50)
