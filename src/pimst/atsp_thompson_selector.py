"""
Thompson Sampling Selector - ATSP Version
==========================================

Uses Thompson Sampling (Bayesian bandits) to learn which algorithm
works best for different ATSP problem characteristics.

Adaptado para ATSP: Sin coordenadas geométricas, usa características
de la matriz de distancias para clasificar problemas.
"""

import numpy as np
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
import json
from pathlib import Path
from .atsp_algorithms import (
    nearest_neighbor_atsp,
    farthest_insertion_atsp,
    lin_kernighan_atsp,
    multi_start_atsp,
    calculate_atsp_tour_length
)


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
class ATSPProblemFeatures:
    """Structural features of an ATSP instance."""
    n: int
    asymmetry_ratio: float  # How asymmetric is the matrix
    density: float
    diameter: float
    avg_edge_weight: float
    std_edge_weight: float
    triangle_inequality_violations: float

    def to_key(self) -> str:
        """Convert to string key for lookup."""
        # Bucket size
        size_cat = 'small' if self.n < 50 else 'medium' if self.n < 100 else 'large'

        # Categorize asymmetry
        if self.asymmetry_ratio < 0.1:
            asym_cat = 'nearly_symmetric'
        elif self.asymmetry_ratio < 0.3:
            asym_cat = 'moderately_asymmetric'
        else:
            asym_cat = 'highly_asymmetric'

        return f"{size_cat}_{asym_cat}"


class ThompsonSamplingATSP:
    """
    Adaptive algorithm selector for ATSP using Thompson Sampling.

    Learns which algorithm works best for different ATSP problem types.
    """

    def __init__(self, cache_file: Optional[Path] = None):
        self.cache_file = cache_file or Path.home() / '.pimst_thompson_atsp_cache.json'

        # Available algorithms
        self.algorithms = {
            'nearest_neighbor': self._solve_nearest_neighbor,
            'farthest_insertion': self._solve_farthest_insertion,
            'lin_kernighan': self._solve_lin_kernighan,
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

    def extract_features(self, distances: np.ndarray) -> ATSPProblemFeatures:
        """
        Extract structural features from ATSP distance matrix.

        Args:
            distances: Asymmetric distance matrix

        Returns:
            ATSPProblemFeatures object
        """
        n = len(distances)

        # Asymmetry ratio: avg |d[i,j] - d[j,i]| / avg d[i,j]
        asymmetry_sum = 0.0
        total_sum = 0.0
        count = 0

        for i in range(n):
            for j in range(i+1, n):
                if distances[i,j] > 0 or distances[j,i] > 0:
                    asymmetry_sum += abs(distances[i,j] - distances[j,i])
                    total_sum += (distances[i,j] + distances[j,i]) / 2
                    count += 1

        asymmetry_ratio = asymmetry_sum / total_sum if total_sum > 0 else 0

        # Density
        density = np.count_nonzero(distances) / (n * n)

        # Diameter
        diameter = np.max(distances)

        # Edge statistics
        mask = distances > 0
        avg_edge = np.mean(distances[mask]) if mask.any() else 0
        std_edge = np.std(distances[mask]) if mask.any() else 0

        # Triangle inequality violations
        # Count how many triplets violate d[i,k] > d[i,j] + d[j,k]
        violations = 0
        samples = min(1000, n * n)  # Sample to avoid O(n³)

        for _ in range(samples):
            i, j, k = np.random.choice(n, 3, replace=False)
            if distances[i,k] > distances[i,j] + distances[j,k] + 1e-6:
                violations += 1

        violation_rate = violations / samples if samples > 0 else 0

        return ATSPProblemFeatures(
            n=n,
            asymmetry_ratio=asymmetry_ratio,
            density=density,
            diameter=diameter,
            avg_edge_weight=avg_edge,
            std_edge_weight=std_edge,
            triangle_inequality_violations=violation_rate
        )

    def select_algorithm(self, features: ATSPProblemFeatures) -> str:
        """
        Select algorithm using Thompson Sampling.

        Args:
            features: Problem features

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
        distances: np.ndarray,
        time_budget: float = 10.0,
        verbose: bool = False
    ) -> Tuple[np.ndarray, float, Dict]:
        """
        Solve ATSP using Thompson Sampling and learn from result.

        Args:
            distances: Asymmetric distance matrix
            time_budget: Time budget (not strictly enforced)
            verbose: Print progress

        Returns:
            (tour, cost, metadata)
        """
        import time

        features = self.extract_features(distances)
        problem_key = features.to_key()

        # Select algorithm
        selected_algo = self.select_algorithm(features)

        if verbose:
            print(f"  🎲 Thompson Sampling selected: {selected_algo}")
            print(f"  📊 Problem type: {problem_key}\n")

        # Execute
        start = time.time()
        tour, cost = self.algorithms[selected_algo](distances)
        elapsed = time.time() - start

        # Also try one alternative for comparison (exploration)
        if np.random.random() < 0.1:  # 10% exploration
            alternatives = [name for name in self.algorithms.keys() if name != selected_algo]
            if alternatives:
                alt_algo = np.random.choice(alternatives)
                alt_tour, alt_cost = self.algorithms[alt_algo](distances)

                # Update both
                is_success = cost <= alt_cost
                self.stats[problem_key][selected_algo].update(is_success)
                self.stats[problem_key][alt_algo].update(not is_success)

                # Use better solution
                if alt_cost < cost:
                    tour, cost = alt_tour, alt_cost
                    selected_algo = alt_algo
        else:
            # Assume success (no ground truth available)
            self.stats[problem_key][selected_algo].update(True)

        # Record history
        self.history.append({
            'problem_key': problem_key,
            'algorithm': selected_algo,
            'cost': cost,
            'time': elapsed,
            'n': features.n,
            'asymmetry': features.asymmetry_ratio
        })

        # Save cache periodically
        if len(self.history) % 10 == 0:
            self._save_cache()

        metadata = {
            'algorithm': selected_algo,
            'problem_type': problem_key,
            'time': elapsed,
            'asymmetry_ratio': features.asymmetry_ratio
        }

        return tour, cost, metadata

    # Algorithm implementations
    def _solve_nearest_neighbor(self, distances: np.ndarray) -> Tuple[np.ndarray, float]:
        tour = nearest_neighbor_atsp(distances, 0)
        cost = calculate_atsp_tour_length(tour, distances)
        return tour, cost

    def _solve_farthest_insertion(self, distances: np.ndarray) -> Tuple[np.ndarray, float]:
        tour = farthest_insertion_atsp(distances, 0)
        tour = lin_kernighan_atsp(distances, tour, max_iterations=20)
        cost = calculate_atsp_tour_length(tour, distances)
        return tour, cost

    def _solve_lin_kernighan(self, distances: np.ndarray) -> Tuple[np.ndarray, float]:
        tour = farthest_insertion_atsp(distances, 0)
        tour = lin_kernighan_atsp(distances, tour, max_iterations=50)
        cost = calculate_atsp_tour_length(tour, distances)
        return tour, cost

    def _solve_multi_start_3(self, distances: np.ndarray) -> Tuple[np.ndarray, float]:
        return multi_start_atsp(distances, n_starts=3, strategy='balanced')

    def _solve_multi_start_5(self, distances: np.ndarray) -> Tuple[np.ndarray, float]:
        return multi_start_atsp(distances, n_starts=5, strategy='balanced')

    def _solve_multi_start_10(self, distances: np.ndarray) -> Tuple[np.ndarray, float]:
        return multi_start_atsp(distances, n_starts=10, strategy='intensive')

    def print_stats(self):
        """Print learned statistics."""
        print("\n" + "="*70)
        print("  THOMPSON SAMPLING ATSP STATISTICS")
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


# Función de conveniencia
def solve_atsp_thompson(
    distances: np.ndarray,
    time_budget: float = 10.0,
    verbose: bool = True
) -> Tuple[np.ndarray, float, Dict]:
    """
    Resolver ATSP usando Thompson Sampling.

    Args:
        distances: Asymmetric distance matrix
        time_budget: Time budget (informative)
        verbose: Print progress

    Returns:
        (tour, cost, metadata)
    """
    selector = ThompsonSamplingATSP()
    return selector.solve_and_learn(distances, time_budget, verbose)
