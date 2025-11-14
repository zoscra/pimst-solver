#!/bin/bash
#
# LKH-3 Installation Script for Windows (Git Bash / MinGW)
# =========================================================

echo ""
echo "========================================================================"
echo "  LKH-3 INSTALLATION FOR WINDOWS"
echo "========================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "atsp_solver.py" ]; then
    echo "❌ Error: Please run this script from pimst-solver directory"
    exit 1
fi

# Check for required tools
echo "Checking for required tools..."

if ! command -v make &> /dev/null; then
    echo "❌ 'make' not found. Please install MinGW or MSYS2."
    echo ""
    echo "Install options:"
    echo "1. MinGW: https://sourceforge.net/projects/mingw/"
    echo "2. MSYS2: https://www.msys2.org/"
    exit 1
fi

if ! command -v gcc &> /dev/null; then
    echo "❌ 'gcc' not found. Please install MinGW or MSYS2."
    exit 1
fi

echo "✓ make found: $(which make)"
echo "✓ gcc found: $(which gcc)"
echo ""

# Download LKH-3
echo "========================================================================"
echo "  DOWNLOADING LKH-3"
echo "========================================================================"
echo ""

LKH_VERSION="3.0.9"
LKH_URL="http://akira.ruc.dk/~keld/research/LKH-3/LKH-${LKH_VERSION}.tgz"
LKH_DIR="LKH-${LKH_VERSION}"

if [ -f "LKH.exe" ] || [ -f "LKH" ]; then
    echo "✓ LKH already exists in this directory"
    read -p "Reinstall? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

echo "Downloading from: $LKH_URL"

if command -v wget &> /dev/null; then
    wget -O "LKH-${LKH_VERSION}.tgz" "$LKH_URL" 2>&1 | grep -E '(HTTP|saved|error)' || true
elif command -v curl &> /dev/null; then
    curl -L -o "LKH-${LKH_VERSION}.tgz" "$LKH_URL"
else
    echo "❌ Neither wget nor curl found. Please download manually:"
    echo "   $LKH_URL"
    exit 1
fi

if [ ! -f "LKH-${LKH_VERSION}.tgz" ]; then
    echo "❌ Download failed. Please download manually:"
    echo "   URL: $LKH_URL"
    echo "   Save as: LKH-${LKH_VERSION}.tgz"
    exit 1
fi

echo "✓ Download complete"
echo ""

# Extract
echo "========================================================================"
echo "  EXTRACTING LKH-3"
echo "========================================================================"
echo ""

if [ -d "$LKH_DIR" ]; then
    echo "Removing old LKH directory..."
    rm -rf "$LKH_DIR"
fi

tar -xzf "LKH-${LKH_VERSION}.tgz"

if [ ! -d "$LKH_DIR" ]; then
    echo "❌ Extraction failed"
    exit 1
fi

echo "✓ Extracted to $LKH_DIR"
echo ""

# Compile
echo "========================================================================"
echo "  COMPILING LKH-3"
echo "========================================================================"
echo ""

cd "$LKH_DIR"

echo "Running make..."
make clean 2>/dev/null || true
make

if [ ! -f "LKH" ] && [ ! -f "LKH.exe" ]; then
    echo ""
    echo "❌ Compilation failed"
    echo ""
    echo "Possible issues:"
    echo "1. Missing compiler (install MinGW)"
    echo "2. Path issues (check MSYS2/MinGW setup)"
    echo ""
    echo "Try manual compilation:"
    echo "  cd $LKH_DIR"
    echo "  make"
    exit 1
fi

echo "✓ Compilation successful"
echo ""

# Copy to project directory
echo "========================================================================"
echo "  INSTALLING LKH-3"
echo "========================================================================"
echo ""

cd ..

if [ -f "$LKH_DIR/LKH" ]; then
    cp "$LKH_DIR/LKH" ./LKH
    chmod +x ./LKH
    echo "✓ Copied LKH to project directory"
elif [ -f "$LKH_DIR/LKH.exe" ]; then
    cp "$LKH_DIR/LKH.exe" ./LKH.exe
    chmod +x ./LKH.exe
    echo "✓ Copied LKH.exe to project directory"
fi

# Test
echo ""
echo "Testing LKH installation..."

if [ -f "./LKH" ]; then
    ./LKH 2>&1 | head -5 || echo "✓ LKH executable found"
    LKH_CMD="./LKH"
elif [ -f "./LKH.exe" ]; then
    ./LKH.exe 2>&1 | head -5 || echo "✓ LKH.exe executable found"
    LKH_CMD="./LKH.exe"
else
    echo "❌ LKH executable not found"
    exit 1
fi

echo ""
echo "========================================================================"
echo "  ✓ INSTALLATION COMPLETE"
echo "========================================================================"
echo ""
echo "LKH-3 installed at: $LKH_CMD"
echo ""
echo "Next steps:"
echo ""
echo "1. Test LKH:"
echo "   $LKH_CMD"
echo ""
echo "2. Run quick benchmark with LKH:"
echo "   python benchmark_atsp_complete.py --quick"
echo ""
echo "3. Run full benchmark:"
echo "   python benchmark_atsp_complete.py"
echo ""
echo "Expected results with LKH:"
echo "  - LKH-3: gap ~1-3%, time ~60-120s"
echo "  - PIMST-Quantum: gap ~20%, time ~20s (3-6x faster!)"
echo ""
echo "========================================================================"
echo ""

# Cleanup option
read -p "Clean up source files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleaning up..."
    rm -rf "$LKH_DIR"
    rm -f "LKH-${LKH_VERSION}.tgz"
    echo "✓ Cleanup complete"
fi

echo ""
echo "Installation finished!"
echo ""
