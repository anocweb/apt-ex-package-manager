#!/bin/bash
# Update debian/changelog with version from src/version.py

set -e

# Change to project root directory
cd "$(dirname "$0")/.."

# Extract version from src/version.py
VERSION=$(grep "^__version__ = " src/version.py | cut -d "'" -f 2)

if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from src/version.py"
    exit 1
fi

# Get message from argument or use default
MESSAGE="${1:-Version $VERSION release}"

# Get current date in RFC 2822 format
DATE=$(date -R)

# Create new changelog entry
cat > packaging/debian/changelog.new << EOF
apt-ex-package-manager ($VERSION-1) unstable; urgency=medium

  * $MESSAGE

 -- Apt-Ex Team <maintainer@example.com>  $DATE

EOF

# Append old changelog if it exists
if [ -f packaging/debian/changelog ]; then
    cat packaging/debian/changelog >> packaging/debian/changelog.new
fi

# Replace old changelog
mv packaging/debian/changelog.new packaging/debian/changelog

echo "Updated packaging/debian/changelog to version $VERSION-1"
