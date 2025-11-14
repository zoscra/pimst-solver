#!/bin/bash
#
# Check Python Installation on Windows
# ====================================

echo ""
echo "========================================================================"
echo "  PYTHON DETECTION"
echo "========================================================================"
echo ""

# Try different Python commands
PYTHON_CMD=""

echo "Checking for Python..."
echo ""

# Try 'py' launcher (Windows)
if command -v py &> /dev/null; then
    echo "✓ Found 'py' launcher"
    py --version
    PYTHON_CMD="py"
elif command -v python &> /dev/null; then
    echo "✓ Found 'python'"
    python --version
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    echo "✓ Found 'python3'"
    python3 --version
    PYTHON_CMD="python3"
else
    echo "❌ Python not found in PATH"
    echo ""
    echo "Options:"
    echo ""
    echo "1. Install Python from Microsoft Store (Windows 10/11):"
    echo "   - Open Microsoft Store"
    echo "   - Search 'Python 3.11' or 'Python 3.12'"
    echo "   - Click 'Install'"
    echo ""
    echo "2. Install Python from python.org:"
    echo "   - Visit: https://www.python.org/downloads/"
    echo "   - Download 'Python 3.11' or newer"
    echo "   - Run installer"
    echo "   - ⚠️ IMPORTANT: Check 'Add Python to PATH'"
    echo ""
    echo "3. Use existing Python installation:"
    echo "   - Find where Python is installed (e.g., C:\\Python311)"
    echo "   - Add to PATH manually"
    echo ""
    exit 1
fi

echo ""
echo "========================================================================"
echo "  PYTHON FOUND: $PYTHON_CMD"
echo "========================================================================"
echo ""

# Export for other scripts
export PYTHON_CMD
echo "$PYTHON_CMD" > .python_cmd.tmp

echo "To run the benchmark, use:"
echo ""
echo "  $PYTHON_CMD benchmark_atsp_complete.py"
echo ""
echo "Or to install dependencies first:"
echo ""
echo "  $PYTHON_CMD -m pip install numpy numba scipy ortools"
echo ""
