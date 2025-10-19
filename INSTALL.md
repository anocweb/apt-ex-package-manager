# Installation Guide

## Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: Linux (KDE Plasma 6 recommended)
- **Optional**: python3-apt (for APT backend on Debian/Ubuntu systems)

## Installation Methods

### Method 1: Development Mode (Recommended for Testing)

Run directly from source without installation:

```bash
# Clone repository
git clone https://github.com/anocweb/apt-ex-package-manager.git
cd apt-ex-package-manager

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install system packages (optional, backend-specific)
# For APT backend (Debian/Ubuntu only)
sudo apt install python3-apt

# Run from source
python src/main.py
```

### Method 2: System Installation

Install to system directories for all users:

```bash
# Install dependencies
pip install -r requirements.txt

# Install system packages
sudo apt install python3-apt  # Debian/Ubuntu only

# Install application
sudo make install

# Or with custom prefix
sudo make install PREFIX=/usr/local
```

**Installed locations:**
- Application: `/usr/bin/apt-ex`
- Plugins: `/usr/share/apt-ex-package-manager/plugins/`
- UI files: `/usr/share/apt-ex-package-manager/ui/`
- Icons: `/usr/share/apt-ex-package-manager/icons/`
- Desktop file: `/usr/share/applications/apt-ex-package-manager.desktop`

### Method 3: User Installation

Install for current user only:

```bash
pip install --user .
```

## Plugin Discovery Order

The application searches for plugins in this order:

1. **User plugins**: `~/.config/apt-ex-package-manager/plugins/` (highest priority)
2. **System plugins**: `/usr/share/apt-ex-package-manager/plugins/`
3. **Development plugins**: `src/controllers/plugins/` (when running from source)

Plugins found in earlier paths override those in later paths.

## Uninstallation

```bash
sudo make uninstall
```

## Building Packages

### Debian/Ubuntu Package

```bash
# Install build dependencies
sudo apt install debhelper dh-python python3-all

# Build package
dpkg-buildpackage -us -uc

# Install
sudo dpkg -i ../apt-ex-package-manager_*.deb
```

### RPM Package (Fedora/RHEL)

```bash
# Install build dependencies
sudo dnf install rpm-build python3-devel

# Build package
rpmbuild -ba apt-ex-package-manager.spec

# Install
sudo rpm -i ~/rpmbuild/RPMS/noarch/apt-ex-package-manager-*.rpm
```

## Backend-Specific Setup

### APT Backend (Debian/Ubuntu)

**Required**: python3-apt must be installed system-wide

```bash
sudo apt install python3-apt
```

Note: python-apt cannot be installed via pip. It must be installed as a system package.

**Virtual Environment Workaround**:

If using a virtual environment, you need to allow access to system packages:

```bash
# Create venv with system packages
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

Or create a symlink:

```bash
# After creating venv
ln -s /usr/lib/python3/dist-packages/apt* .venv/lib/python3.*/site-packages/
```

### Flatpak Backend (When Implemented)

```bash
# Debian/Ubuntu
sudo apt install flatpak

# Fedora
sudo dnf install flatpak
```

## Post-Installation

After installation, the application can be launched:

- From application menu: Search for "Apt-Ex Package Manager"
- From terminal: `apt-ex` (if system installed) or `python src/main.py` (dev mode)
- From desktop file: Click the desktop icon

## Verifying Installation

Check that plugins are loaded:

```bash
apt-ex --list-backends
```

Expected output:
```
Available backends:
  - apt: APT Packages
  - flatpak: Flatpak Packages (if flatpak installed)
  - appimage: AppImage Packages (if appimage support installed)
```

## Troubleshooting

### Plugins not loading

Check plugin directories exist:
```bash
ls -la /usr/share/apt-ex-package-manager/plugins/
```

Check application logs:
```bash
tail -f ~/.cache/apt-ex-package-manager/app.log
```

### Permission issues

Ensure plugins have correct permissions:
```bash
sudo chmod 644 /usr/share/apt-ex-package-manager/plugins/*.py
```

### Missing dependencies

Install all Python dependencies:
```bash
pip install -r requirements.txt
```

### python-apt not found in virtual environment

Either:
1. Use `--system-site-packages` when creating venv
2. Create symlink to system python-apt
3. Run without virtual environment (not recommended)

### APT backend not available

Check if python3-apt is installed:
```bash
python3 -c "import apt; print('APT available')"
```

If not, install:
```bash
sudo apt install python3-apt
```
