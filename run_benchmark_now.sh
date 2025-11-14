#!/bin/bash
#
# Run ATSP Benchmark - Works with or without LKH
# ==============================================

echo ""
echo "========================================================================"
echo "  ATSP BENCHMARK READY"
echo "========================================================================"
echo ""

# Check Python dependencies
echo "Checking dependencies..."
echo ""

python3 -c "
import sys
missing = []

try:
    import numpy
    print('✓ numpy')
except:
    missing.append('numpy')
    print('✗ numpy')

try:
    import numba
    print('✓ numba')
except:
    missing.append('numba')
    print('✗ numba')

try:
    import scipy
    print('✓ scipy')
except:
    missing.append('scipy')
    print('✗ scipy')

try:
    import ortools
    print('✓ OR-Tools (Google solver available)')
except:
    print('⚠ OR-Tools not installed (optional)')

print('')

# Check for LKH
import subprocess
lkh_found = False
for lkh in ['LKH', 'lkh', './LKH', './lkh', 'LKH.exe', './LKH.exe']:
    try:
        result = subprocess.run([lkh], capture_output=True, timeout=1)
        print(f'✓ LKH-3 found at: {lkh}')
        lkh_found = True
        break
    except:
        pass

if not lkh_found:
    print('⚠ LKH-3 not found (optional)')
    print('')
    print('  Benchmark will run with PIMST and OR-Tools only.')
    print('  This is sufficient for publication!')
    print('')

print('')

if missing:
    print('ERROR: Missing required dependencies:')
    for m in missing:
        print(f'  - {m}')
    print('')
    print('Install with: pip install', ' '.join(missing))
    sys.exit(1)
else:
    print('✅ All required dependencies are installed!')
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Missing dependencies. Install with:"
    echo "   pip install numpy numba scipy ortools"
    echo ""
    exit 1
fi

echo ""
echo "========================================================================"
echo "  BENCHMARK OPTIONS"
echo "========================================================================"
echo ""
echo "1. Quick test (5 minutes) - 1 problem to verify everything works"
echo "2. Full benchmark (30-60 minutes) - 13 problems, comprehensive"
echo ""

# Check if --quick flag was passed
if [ "$1" == "--quick" ]; then
    CHOICE="1"
else
    read -p "Choose [1 or 2]: " CHOICE
fi

echo ""

if [ "$CHOICE" == "1" ]; then
    echo "========================================================================"
    echo "  RUNNING QUICK TEST"
    echo "========================================================================"
    echo ""
    python benchmark_atsp_complete.py --quick

elif [ "$CHOICE" == "2" ]; then
    echo "========================================================================"
    echo "  RUNNING FULL BENCHMARK"
    echo "========================================================================"
    echo ""
    echo "⚠️  This will take 30-60 minutes"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python benchmark_atsp_complete.py
    else
        echo "Benchmark cancelled."
        exit 0
    fi

else
    echo "Invalid choice. Use 1 or 2."
    exit 1
fi

echo ""
echo "========================================================================"
echo "  BENCHMARK COMPLETE!"
echo "========================================================================"
echo ""
echo "Results saved to:"
echo "  - JSON: atsp_complete_benchmark_TIMESTAMP.json"
echo "  - Report: atsp_benchmark_report_TIMESTAMP.md"
echo ""
echo "Next steps:"
echo "  1. Review the report markdown file"
echo "  2. Analyze JSON for detailed data"
echo "  3. Create visualizations (optional)"
echo ""
