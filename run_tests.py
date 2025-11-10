#!/usr/bin/env python3
"""
PIMST Test Runner
=================

Convenient script to run tests with different configurations.

Usage:
    python run_tests.py                  # Run all tests
    python run_tests.py --fast           # Skip slow tests
    python run_tests.py --unit           # Run only unit tests
    python run_tests.py --integration    # Run only integration tests
    python run_tests.py --coverage       # Run with coverage report
    python run_tests.py --verbose        # Verbose output
"""

import sys
import subprocess
import argparse


def run_tests(args):
    """Run pytest with specified configuration."""
    
    # Base pytest command
    cmd = ['pytest']
    
    # Add test selection
    if args.unit:
        cmd.extend(['-m', 'unit'])
    elif args.integration:
        cmd.extend(['-m', 'integration'])
    elif args.sino:
        cmd.append('tests/test_sino_system.py')
    elif args.algorithms:
        cmd.append('tests/test_algorithms.py')
    elif args.file:
        cmd.append(args.file)
    else:
        cmd.append('tests/')
    
    # Add options
    if args.fast:
        cmd.append('--fast')
    
    if args.coverage:
        cmd.extend(['--cov=src/pimst', '--cov-report=html', '--cov-report=term'])
    
    if args.verbose:
        cmd.append('-vv')
    else:
        cmd.append('-v')
    
    if args.failed_first:
        cmd.append('--failed-first')
    
    if args.exitfirst:
        cmd.append('-x')
    
    if args.pdb:
        cmd.append('--pdb')
    
    if args.markers:
        # List available markers
        cmd = ['pytest', '--markers']
    
    # Print command
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    
    # Execute
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description='Run PIMST tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      # Run all tests
  %(prog)s --fast               # Skip slow tests
  %(prog)s --unit               # Run unit tests only
  %(prog)s --integration        # Run integration tests only
  %(prog)s --sino               # Run SiNo system tests only
  %(prog)s --algorithms         # Run algorithm tests only
  %(prog)s --coverage           # Run with coverage report
  %(prog)s --file tests/test_sino_system.py  # Run specific file
  %(prog)s -x                   # Stop on first failure
  %(prog)s --pdb                # Drop into debugger on failure
        """
    )
    
    # Test selection
    selection = parser.add_argument_group('Test Selection')
    selection.add_argument('--unit', action='store_true',
                          help='Run only unit tests')
    selection.add_argument('--integration', action='store_true',
                          help='Run only integration tests')
    selection.add_argument('--sino', action='store_true',
                          help='Run only SiNo system tests')
    selection.add_argument('--algorithms', action='store_true',
                          help='Run only algorithm tests')
    selection.add_argument('--file', type=str,
                          help='Run specific test file')
    
    # Test options
    options = parser.add_argument_group('Options')
    options.add_argument('--fast', action='store_true',
                        help='Skip slow tests')
    options.add_argument('--coverage', action='store_true',
                        help='Generate coverage report')
    options.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    options.add_argument('--failed-first', action='store_true',
                        help='Run failed tests first')
    options.add_argument('-x', '--exitfirst', action='store_true',
                        help='Exit on first failure')
    options.add_argument('--pdb', action='store_true',
                        help='Drop into debugger on failure')
    options.add_argument('--markers', action='store_true',
                        help='List available test markers')
    
    args = parser.parse_args()
    
    # Run tests
    return run_tests(args)


if __name__ == '__main__':
    sys.exit(main())
