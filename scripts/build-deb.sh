#!/bin/bash
# Automated Debian package builder for Apt-Ex Package Manager

set -e

echo "=== Apt-Ex Package Manager - Debian Package Builder ==="
echo

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: Could not find project root directory"
    exit 1
fi

# Create build directory and copy packaging files
echo "Preparing build directory..."
mkdir -p .tmp/debian
cp -r packaging/debian/* .tmp/debian/

# Create symlink for dpkg-buildpackage (it expects debian/)
rm -f debian
ln -s .tmp/debian debian

# Check for required tools
echo "Checking build dependencies..."
if ! command -v dpkg-buildpackage &> /dev/null; then
    echo "Missing dpkg-buildpackage"
    echo "Install with: sudo apt install dpkg-dev"
    exit 1
fi

# Update debian/changelog from version.py
echo "Updating debian/changelog..."
./scripts/update-version.sh "Automated build"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf .tmp/debian
mkdir -p .tmp/debian
cp -r packaging/debian/* .tmp/debian/
rm -f ../*.deb ../*.build ../*.buildinfo ../*.changes

# Build the package
echo "Building Debian package..."
dpkg-buildpackage -us -uc -b

echo
echo "=== Build Complete ==="

# Create builds directory and move artifacts
mkdir -p builds
mv ../*.deb ../*.build ../*.buildinfo ../*.changes builds/ 2>/dev/null || true

echo "Package created in builds/ directory:"
ls -lh builds/*.deb
echo
echo "Install with: sudo dpkg -i builds/apt-ex-package-manager_*.deb"
echo "Or: sudo apt install builds/apt-ex-package-manager_*.deb"
echo

# Cleanup
rm -f debian
