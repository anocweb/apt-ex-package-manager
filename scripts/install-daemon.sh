#!/bin/bash
# Per-user installation (no sudo required)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Installing Apt-Ex Update Checker (current user only)..."

# Create user systemd directory
mkdir -p ~/.config/systemd/user

# Create daemon directory
mkdir -p ~/.local/share/apt-ex-package-manager

# Copy daemon script
cp "$PROJECT_DIR/src/update_daemon.py" ~/.local/share/apt-ex-package-manager/
chmod +x ~/.local/share/apt-ex-package-manager/update_daemon.py

# Copy service file
cp "$PROJECT_DIR/systemd/apt-ex-update-checker.service" ~/.config/systemd/user/

# Reload and enable
systemctl --user daemon-reload
systemctl --user enable apt-ex-update-checker.service
systemctl --user start apt-ex-update-checker.service

echo "✓ Daemon installed and started for current user"
echo "  Status: systemctl --user status apt-ex-update-checker"
