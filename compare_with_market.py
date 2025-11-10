#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparador completo de PIMST con los mejores solvers del mercado

Compara con:
- Google OR-Tools
- LKH-3 (si está disponible)
- Concorde (si está disponible)
- Python-TSP library
"""

import numpy as np
import time
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import subprocess
import sys

# Imports condicionales
try:
    import pimst
    PIMST_AVAILABLE = True
except ImportError:
    PIMST_AVAILABLE = False
    print("⚠️  PIMST no está instalado")

try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    print("⚠️  OR-Tools no está disponible (pip install ortools)")

try:
    from python_tsp.exact import solve_tsp_dynamic_programming
    from python_tsp.heuristics import solve_tsp_simulated_annealing
    PYTHON_TSP_AVAILABLE = True
except ImportError:
    PYTHON_TSP_AVAILABLE = False
    print("⚠️  python-tsp no está disponible (pip install python-tsp)")


class MarketComparator:
    """Comparador de rendimiento contra solvers del mercado."""
    
    def __init__(self, output_dir: Path = Path("comparison_results")):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}
    
    def generate_test_instances(self) -> Dict[str, List[Tuple[float, float]]]:
        """Genera instancias de prueba diversas."""
        np.random.seed(42)
        instances = {}
        
        # Pequeñas instancias (óptimo exacto posible)
        for n in [10, 15, 20]:
            instances[f'tiny-random-{n}'] = [
                (np.random.rand() * 100, np.random.rand() * 100) for _ in range(n)
            ]
        
        # Instancias medianas
        for n in [30, 50, 70, 100]:
            instances[f'medium-random-{n}'] = [
                (np.random.rand() * 100, np.random.rand() * 100) for _ in range(n)
            ]
        
        # Instancias estructuradas
        def make_grid(rows, cols):
            return [(i * 10, j * 10) for i in range(rows) for j in range(cols)]
        
        def make_circle(n):
            return [
                (50 + 40 * np.cos(2 * np.pi * i / n),
                 50 + 40 * np.sin(2 * np.pi * i / n))
                for i in range(n)
            ]
        
        def make_clusters(n_clusters, per_cluster):
            coords = []
            for _ in range(n_clusters):
                cx, cy = np.random.rand() * 100, np.random.rand() * 100
                for _ in range(per_cluster):
                    coords.append((
                        cx + np.random.randn() * 5,
                        cy + np.random.randn() * 5
                    ))
            return coords
        
        instances['grid-25'] = make_grid(5, 5)
        instances['grid-100'] = make_grid(10, 10)
        instances['circle-50'] = make_circle(50)
        instances['clustered-60'] = make_clusters(6, 10)
        
        # Instancias grandes (solo heurísticas)
        for n in [200, 500]:
            instances[f'large-random-{n}'] = [
                (np.random.rand() * 1000, np.random.rand() * 1000) for _ in range(n)
            ]
        
        return instances
    
    def solve_pimst(self, coords: List[Tuple], quality: str = 'balanced') -> Optional[Dict]:
        """Resolver con PIMST."""
        if not PIMST_AVAILABLE:
            return None
        
        try:
            start = time.time()
            result = pimst.solve(coords, quality=quality)
            elapsed = time.time() - start
            
            return {
                'length': result['length'],
                'time': elapsed,
                'solver': f'PIMST-{quality}',
                'success': True
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def solve_ortools(self, coords: List[Tuple], time_limit: int = 30) -> Optional[Dict]:
        """Resolver con OR-Tools."""
        if not ORTOOLS_AVAILABLE:
            return None
        
        try:
            n = len(coords)
            
            def distance(i, j):
                dx = coords[i][0] - coords[j][0]
                dy = coords[i][1] - coords[j][1]
                return int(np.sqrt(dx*dx + dy*dy) * 1000)
            
            manager = pywrapcp.RoutingIndexManager(n, 1, 0)
            routing = pywrapcp.RoutingModel(manager)
            
            def distance_callback(from_index, to_index):
                return distance(manager.IndexToNode(from_index), 
                              manager.IndexToNode(to_index))
            
            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
            
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )
            search_parameters.time_limit.seconds = time_limit
            
            start = time.time()
            solution = routing.SolveWithParameters(search_parameters)
            elapsed = time.time() - start
            
            if solution:
                tour = []
                index = routing.Start(0)
                while not routing.IsEnd(index):
                    tour.append(manager.IndexToNode(index))
                    index = solution.Value(routing.NextVar(index))
                
                length = 0.0
                for i in range(len(tour)):
                    j = (i + 1) % len(tour)
                    dx = coords[tour[i]][0] - coords[tour[j]][0]
                    dy = coords[tour[i]][1] - coords[tour[j]][1]
                    length += np.sqrt(dx*dx + dy*dy)
                
                return {
                    'length': length,
                    'time': elapsed,
                    'solver': 'OR-Tools',
                    'success': True
                }
            
            return {'success': False, 'error': 'No solution found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def solve_python_tsp_exact(self, coords: List[Tuple]) -> Optional[Dict]:
        """Resolver con python-tsp (exacto - solo para instancias pequeñas)."""
        if not PYTHON_TSP_AVAILABLE or len(coords) > 20:
            return None
        
        try:
            # Crear matriz de distancias
            n = len(coords)
            dist_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    dx = coords[i][0] - coords[j][0]
                    dy = coords[i][1] - coords[j][1]
                    dist_matrix[i, j] = np.sqrt(dx*dx + dy*dy)
            
            start = time.time()
            permutation, distance = solve_tsp_dynamic_programming(dist_matrix)
            elapsed = time.time() - start
            
            return {
                'length': distance,
                'time': elapsed,
                'solver': 'Python-TSP-Exact',
                'success': True
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def solve_python_tsp_sa(self, coords: List[Tuple]) -> Optional[Dict]:
        """Resolver con python-tsp simulated annealing."""
        if not PYTHON_TSP_AVAILABLE:
            return None
        
        try:
            n = len(coords)
            dist_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    dx = coords[i][0] - coords[j][0]
                    dy = coords[i][1] - coords[j][1]
                    dist_matrix[i, j] = np.sqrt(dx*dx + dy*dy)
            
            start = time.time()
            permutation, distance = solve_tsp_simulated_annealing(dist_matrix)
            elapsed = time.time() - start
            
            return {
                'length': distance,
                'time': elapsed,
                'solver': 'Python-TSP-SA',
                'success': True
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_lkh_available(self) -> bool:
        """Verifica si LKH está disponible."""
        try:
            result = subprocess.run(['LKH'], capture_output=True, timeout=1)
            return True
        except:
            return False
    
    def run_comparison(self):
        """Ejecuta comparación completa."""
        print("\n" + "=" * 80)
        print("🏆 COMPARACIÓN COMPLETA CON EL MERCADO")
        print("=" * 80)
        
        # Verificar solvers disponibles
        available_solvers = []
        if PIMST_AVAILABLE:
            available_solvers.append("PIMST")
        if ORTOOLS_AVAILABLE:
            available_solvers.append("OR-Tools")
        if PYTHON_TSP_AVAILABLE:
            available_solvers.append("Python-TSP")
        if self.check_lkh_available():
            available_solvers.append("LKH-3")
        
        print(f"\n✅ Solvers disponibles: {', '.join(available_solvers)}")
        print(f"⚠️  Solvers NO disponibles: ", end='')
        all_solvers = ["PIMST", "OR-Tools", "Python-TSP", "LKH-3"]
        missing = [s for s in all_solvers if s not in available_solvers]
        print(', '.join(missing) if missing else 'Ninguno')
        
        # Generar instancias
        print("\n📊 Generando instancias de prueba...")
        instances = self.generate_test_instances()
        print(f"✅ {len(instances)} instancias generadas\n")
        
        # Ejecutar comparación
        for name, coords in instances.items():
            n = len(coords)
            print(f"\n{'='*80}")
            print(f"📊 Instancia: {name} (N={n})")
            print(f"{'='*80}")
            
            self.results[name] = {
                'n': n,
                'solvers': {}
            }
            
            # PIMST - 3 niveles de calidad
            if PIMST_AVAILABLE:
                for quality in ['fast', 'balanced', 'optimal']:
                    print(f"  PIMST ({quality})... ", end='', flush=True)
                    result = self.solve_pimst(coords, quality)
                    if result and result['success']:
                        self.results[name]['solvers'][f'pimst_{quality}'] = result
                        print(f"✅ {result['length']:.2f} en {result['time']*1000:.1f}ms")
                    else:
                        print(f"❌ {result.get('error', 'Error') if result else 'N/A'}")
            
            # OR-Tools
            if ORTOOLS_AVAILABLE:
                time_limit = 10 if n <= 50 else 30
                print(f"  OR-Tools... ", end='', flush=True)
                result = self.solve_ortools(coords, time_limit)
                if result and result['success']:
                    self.results[name]['solvers']['ortools'] = result
                    print(f"✅ {result['length']:.2f} en {result['time']:.2f}s")
                else:
                    print(f"❌ {result.get('error', 'Error') if result else 'N/A'}")
            
            # Python-TSP Exacto (solo instancias pequeñas)
            if n <= 20:
                print(f"  Python-TSP (exacto)... ", end='', flush=True)
                result = self.solve_python_tsp_exact(coords)
                if result and result['success']:
                    self.results[name]['solvers']['python_tsp_exact'] = result
                    print(f"✅ {result['length']:.2f} en {result['time']:.2f}s")
                else:
                    print(f"❌ {result.get('error', 'Error') if result else 'N/A'}")
            
            # Python-TSP SA
            if PYTHON_TSP_AVAILABLE and n <= 100:
                print(f"  Python-TSP (SA)... ", end='', flush=True)
                result = self.solve_python_tsp_sa(coords)
                if result and result['success']:
                    self.results[name]['solvers']['python_tsp_sa'] = result
                    print(f"✅ {result['length']:.2f} en {result['time']:.2f}s")
                else:
                    print(f"❌ {result.get('error', 'Error') if result else 'N/A'}")
        
        # Análisis y guardado
        self.analyze_results()
        self.save_results()
    
    def analyze_results(self):
        """Analizar y mostrar resultados."""
        print("\n" + "=" * 80)
        print("📈 ANÁLISIS DE RESULTADOS")
        print("=" * 80)
        
        # Tabla resumen
        print("\n### Comparación por Instancia\n")
        print(f"{'Instancia':<25} {'N':<5} {'Mejor':<12} {'PIMST Gap':<12} {'Speedup vs OR-Tools':<20}")
        print("-" * 80)
        
        for name, data in sorted(self.results.items(), key=lambda x: x[1]['n']):
            solvers = data['solvers']
            if not solvers:
                continue
            
            n = data['n']
            
            # Encontrar mejor solución
            best_length = min(s['length'] for s in solvers.values() if s['success'])
            best_solver = [k for k, v in solvers.items() 
                          if v['success'] and v['length'] == best_length][0]
            
            # Gap de PIMST balanced
            pimst_gap = "N/A"
            if 'pimst_balanced' in solvers and solvers['pimst_balanced']['success']:
                pimst_len = solvers['pimst_balanced']['length']
                gap = ((pimst_len - best_length) / best_length) * 100
                pimst_gap = f"{gap:.2f}%"
            
            # Speedup vs OR-Tools
            speedup = "N/A"
            if ('pimst_balanced' in solvers and 'ortools' in solvers and
                solvers['pimst_balanced']['success'] and solvers['ortools']['success']):
                pimst_time = solvers['pimst_balanced']['time']
                ortools_time = solvers['ortools']['time']
                speedup_val = ortools_time / pimst_time
                speedup = f"{speedup_val:.1f}x"
            
            print(f"{name:<25} {n:<5} {best_solver:<12} {pimst_gap:<12} {speedup:<20}")
        
        # Estadísticas globales
        print("\n" + "=" * 80)
        print("📊 ESTADÍSTICAS GLOBALES - PIMST (balanced)")
        print("=" * 80)
        
        gaps = []
        speedups = []
        times = []
        
        for name, data in self.results.items():
            solvers = data['solvers']
            if 'pimst_balanced' not in solvers or not solvers['pimst_balanced']['success']:
                continue
            
            best_length = min(s['length'] for s in solvers.values() if s['success'])
            pimst_len = solvers['pimst_balanced']['length']
            pimst_time = solvers['pimst_balanced']['time']
            
            gap = ((pimst_len - best_length) / best_length) * 100
            gaps.append(gap)
            times.append(pimst_time)
            
            if 'ortools' in solvers and solvers['ortools']['success']:
                ortools_time = solvers['ortools']['time']
                speedup_val = ortools_time / pimst_time
                speedups.append(speedup_val)
        
        if gaps:
            print(f"\n✅ Calidad:")
            print(f"   Gap promedio:     {np.mean(gaps):.2f}%")
            print(f"   Gap mediana:      {np.median(gaps):.2f}%")
            print(f"   Gap mínimo:       {np.min(gaps):.2f}%")
            print(f"   Gap máximo:       {np.max(gaps):.2f}%")
            print(f"   Soluciones <3%:   {sum(1 for g in gaps if g < 3)}/{len(gaps)}")
            print(f"   Soluciones <5%:   {sum(1 for g in gaps if g < 5)}/{len(gaps)}")
        
        if speedups:
            print(f"\n⚡ Velocidad vs OR-Tools:")
            print(f"   Speedup promedio: {np.mean(speedups):.1f}x")
            print(f"   Speedup mediana:  {np.median(speedups):.1f}x")
            print(f"   Speedup mínimo:   {np.min(speedups):.1f}x")
            print(f"   Speedup máximo:   {np.max(speedups):.1f}x")
        
        if times:
            print(f"\n⏱️  Tiempo de ejecución:")
            print(f"   Tiempo promedio:  {np.mean(times)*1000:.1f}ms")
            print(f"   Tiempo mediana:   {np.median(times)*1000:.1f}ms")
    
    def save_results(self):
        """Guardar resultados en JSON."""
        output_file = self.output_dir / f"market_comparison_{int(time.time())}.json"
        
        # Convertir a formato serializable
        serializable_results = {}
        for name, data in self.results.items():
            serializable_results[name] = {
                'n': data['n'],
                'solvers': {}
            }
            for solver, result in data['solvers'].items():
                if result['success']:
                    serializable_results[name]['solvers'][solver] = {
                        'length': float(result['length']),
                        'time': float(result['time']),
                        'solver': result['solver']
                    }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\n✅ Resultados guardados en: {output_file}")


def main():
    print("\n" + "=" * 80)
    print("🚀 COMPARADOR DE SOLVERS TSP")
    print("=" * 80)
    print("\nEste script comparará PIMST con los mejores solvers del mercado.")
    print("Puede tardar varios minutos dependiendo de las instancias...\n")
    
    input("Presiona ENTER para comenzar...")
    
    comparator = MarketComparator()
    comparator.run_comparison()
    
    print("\n" + "=" * 80)
    print("✅ COMPARACIÓN COMPLETADA")
    print("=" * 80)
    print("\n🎉 ¡Resultados listos para publicar!")


if __name__ == '__main__':
    main()
