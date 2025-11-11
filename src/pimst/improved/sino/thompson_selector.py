"""
Thompson Sampling Selector - Adaptive Algorithm Selection
==========================================================

Uses Thompson Sampling (Bayesian bandits) to learn which algorithm
works best for different problem characteristics.
"""

import numpy as np
from typing import Tuple, List, Dict, Callable, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class AlgorithmStats:
    """Statistics for one algorithm."""
    name: str
    successes: int = 1  # Start with 1/1 (optimistic initialization)
    failures: int = 1
    
    def sample(self) -> float:
        """Sample from Beta distribution."""
        return np.random.beta(self.successes, self.failures)
    
    def update(self, is_success: bool):
        """Update based on result."""
        if is_success:
            self.successes += 1
        else:
            self.failures += 1
    
    def win_rate(self) -> float:
        """Current estimated win rate."""
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.5


@dataclass
class ProblemFeatures:
    """Geometric and structural features of a TSP instance."""
    n: int
    density: float
    cluster_coefficient: float
    diameter: float
    avg_edge_weight: float
    std_edge_weight: float
    coord_range: float
    is_circle: bool
    is_clustered: bool
    
    def to_key(self) -> str:
        """Convert to string key for lookup."""
        # Bucket size into categories
        size_cat = 'small' if self.n < 50 else 'medium' if self.n < 100 else 'large'
        
        # Categorize structure
        if self.is_circle:
            structure = 'circle'
        elif self.is_clustered:
            structure = 'clustered'
        else:
            structure = 'random'
        
        return f"{size_cat}_{structure}"


class ThompsonSamplingSelector:
    """
    Adaptive algorithm selector using Thompson Sampling.
    
    Learns which algorithm works best for different problem types
    by maintaining Beta distributions for each algorithm's success rate.
    """
    
    def __init__(self, cache_file: Optional[Path] = None):
        self.cache_file = cache_file or Path.home() / '.pimst_thompson_cache.json'
        
        # Available algorithms
        self.algorithms = {
            'gravity': self._solve_gravity,
            'lin_kernighan': self._solve_lk,
            'multi_start_3': self._solve_multi_start_3,
            'multi_start_5': self._solve_multi_start_5,
            'multi_start_10': self._solve_multi_start_10,
        }
        
        # Statistics per (problem_type, algorithm)
        self.stats: Dict[str, Dict[str, AlgorithmStats]] = {}
        
        # Load cache
        self._load_cache()
        
        # Performance tracking
        self.history = []
    
    def _load_cache(self):
        """Load learned statistics from cache."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                
                for problem_key, algos in data.items():
                    self.stats[problem_key] = {}
                    for algo_name, stats in algos.items():
                        self.stats[problem_key][algo_name] = AlgorithmStats(
                            name=algo_name,
                            successes=stats['successes'],
                            failures=stats['failures']
                        )
            except:
                pass  # Start fresh if cache corrupted
    
    def _save_cache(self):
        """Save learned statistics to cache."""
        data = {}
        for problem_key, algos in self.stats.items():
            data[problem_key] = {}
            for algo_name, stats in algos.items():
                data[problem_key][algo_name] = {
                    'successes': stats.successes,
                    'failures': stats.failures,
                    'win_rate': stats.win_rate()
                }
        
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass  # Fail silently if can't save
    
    def extract_features(self, coords: np.ndarray, distances: np.ndarray) -> ProblemFeatures:
        """Extract geometric features from problem."""
        n = len(coords)
        
        # Density
        density = np.count_nonzero(distances) / (n * n)
        
        # Cluster coefficient (simplified)
        from scipy.spatial.distance import pdist
        all_dists = pdist(coords)
        cluster_coeff = np.std(all_dists) / (np.mean(all_dists) + 1e-10)
        
        # Diameter
        diameter = np.max(distances)
        
        # Edge statistics
        mask = distances > 0
        avg_edge = np.mean(distances[mask]) if mask.any() else 0
        std_edge = np.std(distances[mask]) if mask.any() else 0
        
        # Coordinate range
        coord_range = np.ptp(coords)
        
        # Detect circle
        center = coords.mean(axis=0)
        dists_from_center = np.linalg.norm(coords - center, axis=1)
        std_ratio = dists_from_center.std() / (dists_from_center.mean() + 1e-10)
        is_circle = std_ratio < 0.15
        
        # Detect clusters
        is_clustered = cluster_coeff > 0.5
        
        return ProblemFeatures(
            n=n,
            density=density,
            cluster_coefficient=cluster_coeff,
            diameter=diameter,
            avg_edge_weight=avg_edge,
            std_edge_weight=std_edge,
            coord_range=coord_range,
            is_circle=is_circle,
            is_clustered=is_clustered
        )
    
    def select_algorithm(self, features: ProblemFeatures) -> str:
        """
        Select algorithm using Thompson Sampling.
        
        Returns:
            Algorithm name
        """
        problem_key = features.to_key()
        
        # Initialize stats for this problem type if needed
        if problem_key not in self.stats:
            self.stats[problem_key] = {
                name: AlgorithmStats(name=name)
                for name in self.algorithms.keys()
            }
        
        # Thompson Sampling: sample from each algorithm's Beta distribution
        samples = {
            name: stats.sample()
            for name, stats in self.stats[problem_key].items()
        }
        
        # Select algorithm with highest sample
        selected = max(samples.items(), key=lambda x: x[1])[0]
        
        return selected
    
    def solve_and_learn(
        self,
        coords: np.ndarray,
        distances: np.ndarray,
        time_budget: float = 10.0
    ) -> Tuple[List[int], float]:
        """
        Solve TSP using Thompson Sampling and learn from result.
        
        Returns:
            (tour, cost)
        """
        import time
        
        features = self.extract_features(coords, distances)
        problem_key = features.to_key()
        
        # Fast path for circles
        if features.is_circle:
            return self._solve_circle_optimal(coords, distances)
        
        # Select algorithm
        selected_algo = self.select_algorithm(features)
        
        # Execute
        start = time.time()
        tour, cost = self.algorithms[selected_algo](coords, distances)
        elapsed = time.time() - start
        
        # Also try one alternative for comparison (exploration)
        if np.random.random() < 0.1:  # 10% exploration
            alternatives = [name for name in self.algorithms.keys() if name != selected_algo]
            if alternatives:
                alt_algo = np.random.choice(alternatives)
                alt_tour, alt_cost = self.algorithms[alt_algo](coords, distances)
                
                # Update both
                is_success = cost <= alt_cost
                self.stats[problem_key][selected_algo].update(is_success)
                self.stats[problem_key][alt_algo].update(not is_success)
                
                # Use better solution
                if alt_cost < cost:
                    tour, cost = alt_tour, alt_cost
                    selected_algo = alt_algo
        else:
            # Assume success (we don't have ground truth)
            # In practice, could compare to a baseline
            self.stats[problem_key][selected_algo].update(True)
        
        # Record history
        self.history.append({
            'problem_key': problem_key,
            'algorithm': selected_algo,
            'cost': cost,
            'time': elapsed,
            'n': features.n
        })
        
        # Save cache periodically
        if len(self.history) % 10 == 0:
            self._save_cache()
        
        return tour, cost
    
    def _solve_circle_optimal(self, coords: np.ndarray, distances: np.ndarray) -> Tuple[List[int], float]:
        """Optimal solution for circles."""
        n = len(coords)
        center = coords.mean(axis=0)
        angles = np.arctan2(coords[:, 1] - center[1], coords[:, 0] - center[0])
        tour = list(np.argsort(angles))
        cost = sum(distances[tour[i]][tour[(i+1)%n]] for i in range(n))
        return tour, cost
    
    def _solve_gravity(self, coords: np.ndarray, distances: np.ndarray) -> Tuple[List[int], float]:
        """Solve using gravity."""
        from pimst.algorithms import gravity_guided_tsp
        tour = gravity_guided_tsp(coords, distances)
        cost = sum(distances[tour[i]][tour[(i+1)%len(tour)]] for i in range(len(tour)))
        return tour.tolist(), cost
    
    def _solve_lk(self, coords: np.ndarray, distances: np.ndarray) -> Tuple[List[int], float]:
        """Solve using Lin-Kernighan."""
        from pimst.algorithms import lin_kernighan_lite
        tour = lin_kernighan_lite(coords, distances)
        cost = sum(distances[tour[i]][tour[(i+1)%len(tour)]] for i in range(len(tour)))
        return tour.tolist(), cost
    
    def _solve_multi_start_3(self, coords: np.ndarray, distances: np.ndarray) -> Tuple[List[int], float]:
        """Solve using multi-start with 3 starts."""
        from pimst.algorithms import multi_start_solver
        tour = multi_start_solver(coords, distances, n_starts=3)
        cost = sum(distances[tour[i]][tour[(i+1)%len(tour)]] for i in range(len(tour)))
        return tour.tolist(), cost
    
    def _solve_multi_start_5(self, coords: np.ndarray, distances: np.ndarray) -> Tuple[List[int], float]:
        """Solve using multi-start with 5 starts."""
        from pimst.algorithms import multi_start_solver
        tour = multi_start_solver(coords, distances, n_starts=5)
        cost = sum(distances[tour[i]][tour[(i+1)%len(tour)]] for i in range(len(tour)))
        return tour.tolist(), cost
    
    def _solve_multi_start_10(self, coords: np.ndarray, distances: np.ndarray) -> Tuple[List[int], float]:
        """Solve using multi-start with 10 starts."""
        from pimst.algorithms import multi_start_solver
        tour = multi_start_solver(coords, distances, n_starts=10)
        cost = sum(distances[tour[i]][tour[(i+1)%len(tour)]] for i in range(len(tour)))
        return tour.tolist(), cost
    
    def print_stats(self):
        """Print learned statistics."""
        print("\n" + "="*70)
        print("  THOMPSON SAMPLING STATISTICS")
        print("="*70)
        
        for problem_key in sorted(self.stats.keys()):
            print(f"\n📊 {problem_key}:")
            algos = self.stats[problem_key]
            
            # Sort by win rate
            sorted_algos = sorted(
                algos.items(),
                key=lambda x: x[1].win_rate(),
                reverse=True
            )
            
            for name, stats in sorted_algos:
                win_rate = stats.win_rate()
                total = stats.successes + stats.failures
                print(f"   {name:<20} Win: {win_rate:.1%}  ({stats.successes}/{total})")
