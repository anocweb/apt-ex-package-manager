# Debian Package Build Guide

## Overview
This guide explains how to build and install the Debian package for Apt-Ex Package Manager.

## Prerequisites

Install build dependencies:
```bash
sudo apt install devscripts debhelper dh-python python3-all python3-setuptools
```

## Quick Build

### Using the build script:
```bash
./build-deb.sh
```

### Using Make:
```bash
make deb
```

### Manual build:
```bash
dpkg-buildpackage -us -uc -b
```

## Installation

After building, install the package:
```bash
sudo apt install ../apt-ex-package-manager_*.deb
```

Or with Make:
```bash
make install
```

## Package Structure

The Debian package includes:
- **Binary**: `/usr/bin/apt-ex`
- **Python modules**: `/usr/lib/python3/dist-packages/`
- **UI files**: `/usr/share/apt-ex-package-manager/ui/`
- **Icons**: `/usr/share/apt-ex-package-manager/icons/`
- **Desktop entry**: `/usr/share/applications/apt-ex-package-manager.desktop`
- **Systemd service**: `/usr/lib/systemd/system/apt-ex-update-checker.service`

## Debian Files

### debian/control
Package metadata, dependencies, and description.

### debian/rules
Build instructions using dh and pybuild.

### debian/changelog
Version history and release notes.

### debian/install
Additional files to install (UI files, plugins).

### debian/postinst
Post-installation script (enables systemd service).

### debian/prerm
Pre-removal script (stops systemd service).

## Cleaning

Remove build artifacts:
```bash
make clean
```

## Uninstallation

```bash
sudo apt remove apt-ex-package-manager
```

Or with Make:
```bash
make uninstall
```

## Troubleshooting

### Missing build dependencies
If build fails with missing dependencies:
```bash
sudo apt build-dep .
```

### Permission errors
Ensure scripts are executable:
```bash
chmod +x build-deb.sh debian/rules debian/postinst debian/prerm
```

### Clean build
For a completely clean build:
```bash
make clean
./build-deb.sh
```

## Version Updates

To release a new version:

1. Update version in `setup.py`
2. Update `debian/changelog`:
   ```bash
   dch -v 0.2.0-1 "New release"
   ```
3. Build package:
   ```bash
   make deb
   ```
