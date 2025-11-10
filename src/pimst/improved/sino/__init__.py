"""
SiNo (Selective Intelligent No-brainer Optimizer) System
=========================================================

A sophisticated decision-making system for TSP that determines
whether to use comprehensive, exploratory, or fast solving approaches.

Quick Start:
    >>> from pimst.improved.sino import SiNoSolver, smart_solve
    >>> import numpy as np
    >>> 
    >>> # Simple usage
    >>> distances = np.random.rand(50, 50)
    >>> tour, cost = smart_solve(distances)
    >>> 
    >>> # Full control
    >>> solver = SiNoSolver()
    >>> result = solver.solve(distances)
    >>> print(f"Decision: {result.decision}, Cost: {result.cost}")
"""

# Import everything from the modules
from .types import *
from .decision import *
from .explorer import *
from .confidence import *
from .checkpoint import *
from .api import SiNoSolver, solve_tsp
from .selector import SmartSelector, smart_solve

__all__ = [
    # High-level API (most important)
    'SiNoSolver',
    'solve_tsp',
    'SmartSelector',
    'smart_solve',
    
    # All exports from submodules
    'DecisionType',
    'SiNoResult',
    'SolverConfig',
    'DecisionEngine',
    'ExplorationEngine',
    'ConfidenceAnalyzer',
    'CheckpointManager',
]

__version__ = '1.0.0'
__author__ = 'Jose Manuel Reguera'
