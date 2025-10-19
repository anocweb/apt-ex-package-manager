# Installation Guide

## Installation Methods

### Method 1: System Installation (Recommended)

Install to system directories for all users:

```bash
# Install dependencies
pip install -r requirements.txt

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

### Method 2: Development Mode

Run directly from source without installation:

```bash
# Install dependencies
pip install -r requirements.txt

# Run from source
make dev
# Or directly
python src/main.py
```

**Plugin loading in dev mode:**
- Loads from: `src/controllers/plugins/`

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

## Post-Installation

After installation, the application can be launched:

- From application menu: Search for "Apt-Ex Package Manager"
- From terminal: `apt-ex`
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
