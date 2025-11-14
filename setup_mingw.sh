#!/bin/bash
#
# MinGW Setup Script for LKH-3 Compilation
# =========================================

echo ""
echo "========================================================================"
echo "  MINGW SETUP FOR LKH-3"
echo "========================================================================"
echo ""

# Define paths
MINGW_ZIP="mingw-w64-v11.0.0.zip"
MINGW_DIR="mingw-w64"

# Check if zip file exists
if [ ! -f "$MINGW_ZIP" ]; then
    echo "❌ Error: $MINGW_ZIP not found in current directory"
    echo ""
    echo "Please make sure you're in the directory containing the zip file"
    echo "or move the zip file to: $(pwd)"
    echo ""
    exit 1
fi

echo "✓ Found $MINGW_ZIP"
echo ""

# Extract MinGW
echo "========================================================================"
echo "  EXTRACTING MINGW"
echo "========================================================================"
echo ""

if [ -d "$MINGW_DIR" ]; then
    echo "⚠  MinGW directory already exists"
    read -p "Remove and re-extract? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old directory..."
        rm -rf "$MINGW_DIR"
    else
        echo "Using existing directory"
    fi
fi

if [ ! -d "$MINGW_DIR" ]; then
    echo "Extracting $MINGW_ZIP..."
    unzip -q "$MINGW_ZIP" -d .

    # MinGW might extract to different directory names
    # Try to find it
    if [ ! -d "$MINGW_DIR" ]; then
        # Look for common variations
        for dir in mingw64 mingw-w64-* MinGW*; do
            if [ -d "$dir" ]; then
                echo "Found extracted directory: $dir"
                if [ "$dir" != "$MINGW_DIR" ]; then
                    mv "$dir" "$MINGW_DIR"
                fi
                break
            fi
        done
    fi
fi

if [ ! -d "$MINGW_DIR" ]; then
    echo "❌ Error: Failed to extract MinGW"
    echo "Please extract manually and ensure directory is named: $MINGW_DIR"
    exit 1
fi

echo "✓ MinGW extracted to: $(pwd)/$MINGW_DIR"
echo ""

# Find the bin directory
BIN_DIR=""
if [ -d "$MINGW_DIR/bin" ]; then
    BIN_DIR="$MINGW_DIR/bin"
elif [ -d "$MINGW_DIR/mingw64/bin" ]; then
    BIN_DIR="$MINGW_DIR/mingw64/bin"
elif [ -d "$MINGW_DIR/mingw32/bin" ]; then
    BIN_DIR="$MINGW_DIR/mingw32/bin"
else
    echo "❌ Error: Could not find bin directory in MinGW"
    echo "Contents of $MINGW_DIR:"
    ls -la "$MINGW_DIR"
    exit 1
fi

echo "✓ Found bin directory: $BIN_DIR"
echo ""

# Check for gcc and make
if [ -f "$BIN_DIR/gcc.exe" ] || [ -f "$BIN_DIR/gcc" ]; then
    echo "✓ gcc found in $BIN_DIR"
else
    echo "❌ Warning: gcc not found in $BIN_DIR"
fi

if [ -f "$BIN_DIR/make.exe" ] || [ -f "$BIN_DIR/make" ] || [ -f "$BIN_DIR/mingw32-make.exe" ]; then
    echo "✓ make found in $BIN_DIR"
else
    echo "❌ Warning: make not found in $BIN_DIR"
fi

echo ""

# Add to PATH for current session
echo "========================================================================"
echo "  CONFIGURING PATH"
echo "========================================================================"
echo ""

FULL_BIN_PATH="$(cd "$(pwd)/$BIN_DIR" && pwd)"
echo "Adding to PATH: $FULL_BIN_PATH"
export PATH="$FULL_BIN_PATH:$PATH"

echo ""
echo "✓ PATH updated for current session"
echo ""

# Test gcc and make
echo "========================================================================"
echo "  TESTING TOOLS"
echo "========================================================================"
echo ""

if command -v gcc &> /dev/null; then
    echo "✓ gcc is now available:"
    gcc --version | head -1
else
    echo "❌ gcc still not found"
    echo "PATH: $PATH"
fi

echo ""

# Check for make or mingw32-make
if command -v make &> /dev/null; then
    echo "✓ make is now available:"
    make --version | head -1
elif command -v mingw32-make &> /dev/null; then
    echo "✓ mingw32-make is available:"
    mingw32-make --version | head -1
    echo ""
    echo "Note: You may need to use 'mingw32-make' instead of 'make'"
    # Create a make wrapper
    if [ -f "$BIN_DIR/mingw32-make.exe" ] && [ ! -f "$BIN_DIR/make.exe" ]; then
        echo "Creating make.exe wrapper..."
        cp "$BIN_DIR/mingw32-make.exe" "$BIN_DIR/make.exe"
        echo "✓ Created make.exe"
    fi
else
    echo "❌ make still not found"
fi

echo ""
echo "========================================================================"
echo "  SETUP COMPLETE"
echo "========================================================================"
echo ""
echo "MinGW is now configured for this terminal session."
echo ""
echo "IMPORTANT: To make this permanent, add the following to your PATH:"
echo "  $FULL_BIN_PATH"
echo ""
echo "Next steps:"
echo ""
echo "1. Test the tools:"
echo "   gcc --version"
echo "   make --version"
echo ""
echo "2. Run LKH installation:"
echo "   ./install_lkh.sh"
echo ""
echo "========================================================================"
echo ""
