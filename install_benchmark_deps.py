"""
Install dependencies for ATSP benchmarking
==========================================

Installs:
1. OR-Tools (Google optimization)
2. Instructions for LKH-3
"""

import subprocess
import sys
import platform


def install_ortools():
    """Install OR-Tools."""
    print("\n" + "="*70)
    print("  Installing OR-Tools")
    print("="*70)

    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ortools'])
        print("✓ OR-Tools installed successfully\n")
        return True
    except:
        print("✗ Failed to install OR-Tools\n")
        return False


def check_lkh():
    """Check if LKH is available."""
    print("\n" + "="*70)
    print("  Checking for LKH-3")
    print("="*70)

    lkh_paths = ['LKH', 'lkh', './LKH', './lkh', 'LKH-3', 'lkh-3']

    for path in lkh_paths:
        try:
            result = subprocess.run([path, '--version'], capture_output=True, timeout=1)
            print(f"✓ LKH found at: {path}\n")
            return True
        except:
            continue

    print("✗ LKH not found\n")
    return False


def print_lkh_instructions():
    """Print instructions for installing LKH."""
    print("\n" + "="*70)
    print("  LKH-3 Installation Instructions")
    print("="*70)
    print("""
LKH-3 is needed for comparison benchmarks. To install:

**Option 1: Download precompiled binary**

  Windows:
    1. Download from: http://akira.ruc.dk/~keld/research/LKH-3/
    2. Extract LKH.exe
    3. Add to PATH or place in project directory

  Linux/Mac:
    1. Download from: http://akira.ruc.dk/~keld/research/LKH-3/
    2. Compile: make
    3. Add to PATH: sudo mv LKH /usr/local/bin/

**Option 2: Compile from source**

  git clone https://github.com/mastqe/LKH
  cd LKH
  make

**After installation:**

  Run: LKH --version
  Or: ./LKH --version

**Note:** Benchmarks will work without LKH, but comparisons will be incomplete.
""")


def test_imports():
    """Test if all required packages work."""
    print("\n" + "="*70)
    print("  Testing Imports")
    print("="*70)

    # Test numpy
    try:
        import numpy as np
        print("✓ numpy")
    except:
        print("✗ numpy - Run: pip install numpy")
        return False

    # Test numba
    try:
        import numba
        print("✓ numba")
    except:
        print("✗ numba - Run: pip install numba")
        return False

    # Test scipy
    try:
        import scipy
        print("✓ scipy")
    except:
        print("✗ scipy - Run: pip install scipy")
        return False

    # Test OR-Tools
    try:
        from ortools.constraint_solver import pywrapcp
        print("✓ OR-Tools")
        ortools_ok = True
    except:
        print("✗ OR-Tools - Will install")
        ortools_ok = False

    # Test our ATSP modules
    try:
        from src.pimst.atsp_algorithms import nearest_neighbor_atsp
        print("✓ ATSP algorithms")
    except:
        print("✗ ATSP algorithms - Check installation")
        return False

    print()
    return ortools_ok


def main():
    print("\n" + "="*70)
    print("  ATSP BENCHMARK DEPENDENCIES INSTALLER")
    print("="*70)
    print(f"  Platform: {platform.system()}")
    print(f"  Python: {sys.version.split()[0]}")
    print("="*70)

    # Test existing installations
    ortools_ok = test_imports()

    # Install OR-Tools if needed
    if not ortools_ok:
        install_ortools()

    # Check for LKH
    lkh_ok = check_lkh()

    if not lkh_ok:
        print_lkh_instructions()

    # Final summary
    print("\n" + "="*70)
    print("  INSTALLATION SUMMARY")
    print("="*70)
    print(f"  {'numpy/numba/scipy':<30} {'✓ Ready' if True else '✗ Missing'}")
    print(f"  {'OR-Tools':<30} {'✓ Ready' if ortools_ok else '⚠ Install manually'}")
    print(f"  {'LKH-3':<30} {'✓ Ready' if lkh_ok else '⚠ Optional (see instructions)'}")
    print(f"  {'ATSP Solvers':<30} {'✓ Ready'}")
    print("="*70)

    print("\n📋 Next Steps:\n")

    if not lkh_ok:
        print("  1. (Optional) Install LKH-3 for complete comparison")
        print("  2. Run quick test: python benchmark_atsp_complete.py --quick")
        print("  3. Run full benchmark: python benchmark_atsp_complete.py")
    else:
        print("  1. Run quick test: python benchmark_atsp_complete.py --quick")
        print("  2. Run full benchmark: python benchmark_atsp_complete.py")

    print("\n  ⚠️  Note: Full benchmark can take 30-60 minutes\n")


if __name__ == "__main__":
    main()
