#!/bin/bash
# System-wide installation (requires sudo)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Installing Apt-Ex Update Checker (system-wide)..."

# Check for sudo
if [ "$EUID" -ne 0 ]; then
    echo "This script requires sudo privileges"
    exec sudo bash "$0" "$@"
fi

# Create system directories
mkdir -p /usr/lib/systemd/user
mkdir -p /usr/lib/systemd/user-preset
mkdir -p /usr/share/apt-ex-package-manager

# Copy daemon script
cp "$PROJECT_DIR/src/update_daemon.py" /usr/share/apt-ex-package-manager/
chmod +x /usr/share/apt-ex-package-manager/update_daemon.py

# Copy service file (update ExecStart path)
sed 's|%h/.local/share|/usr/share|g' "$PROJECT_DIR/systemd/apt-ex-update-checker.service" > /usr/lib/systemd/user/apt-ex-update-checker.service

# Copy preset file
cp "$PROJECT_DIR/systemd/90-apt-ex.preset" /usr/lib/systemd/user-preset/

# Reload systemd for current user (if running as sudo)
if [ -n "$SUDO_USER" ]; then
    sudo -u "$SUDO_USER" systemctl --user daemon-reload 2>/dev/null || true
    sudo -u "$SUDO_USER" systemctl --user preset apt-ex-update-checker.service 2>/dev/null || true
    sudo -u "$SUDO_USER" systemctl --user start apt-ex-update-checker.service 2>/dev/null || true
fi

echo "✓ Daemon installed system-wide and enabled for all users"
echo "  Current user status: systemctl --user status apt-ex-update-checker"
echo "  Note: New users will have it enabled automatically on first login"
