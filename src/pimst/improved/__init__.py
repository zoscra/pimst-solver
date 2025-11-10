"""
PIMST Improved Algorithms
==========================

This package contains improved versions of PIMST algorithms,
building upon the foundation of v25.x versions.

Submodules:
    - sino: SiNo decision system (SI/NO/SINO with backtracking)

Future additions:
    - v25_ultimate: Maximum quality variant
    - v25_2_hotspots: 138x speedup with perfect classification
    - v25_7_hybrid: Thompson sampling + geometry
"""

__version__ = "0.1.0"

# Import SiNo system
from . import sino

__all__ = [
    "sino",
]
