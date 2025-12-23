#!/bin/bash
# Automated Debian package builder for Apt-Ex Package Manager

set -e

echo "=== Apt-Ex Package Manager - Debian Package Builder ==="
echo

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: Must be run from project root directory"
    exit 1
fi

# Check for required tools
echo "Checking build dependencies..."
if ! command -v dpkg-buildpackage &> /dev/null; then
    echo "Missing dpkg-buildpackage"
    echo "Install with: sudo apt install dpkg-dev"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf debian/apt-ex-package-manager debian/.debhelper debian/files debian/*.substvars debian/*.log
rm -f ../*.deb ../*.build ../*.buildinfo ../*.changes

# Build the package
echo "Building Debian package..."
dpkg-buildpackage -us -uc -b

echo
echo "=== Build Complete ==="
echo "Package created in parent directory:"
ls -lh ../*.deb
echo
echo "Install with: sudo dpkg -i ../apt-ex-package-manager_*.deb"
echo "Or: sudo apt install ../apt-ex-package-manager_*.deb"
