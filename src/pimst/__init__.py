"""
PIMST - Physics-Inspired Multi-Start TSP Solver

A novel heuristic for the Traveling Salesman Problem using gravity-guided
initialization and multi-start Lin-Kernighan local search.

Example:
    >>> import pimst
    >>> coords = [(0, 0), (1, 5), (5, 2), (8, 3)]
    >>> result = pimst.solve(coords)
    >>> print(f"Tour: {result['tour']}")
    >>> print(f"Length: {result['length']:.2f}")
"""

__version__ = "0.22.0"
__author__ = "[Your Name]"
__email__ = "hello@pimst.io"

from .solver import solve, solve_with_details
from .gravity import gravity_guided_tsp
from .algorithms import (
    nearest_neighbor,
    lin_kernighan_lite,
    multi_start_solver,
)

__all__ = [
    "solve",
    "solve_with_details",
    "gravity_guided_tsp",
    "nearest_neighbor",
    "lin_kernighan_lite",
    "multi_start_solver",
    "__version__",
]
