# APT Plugin Documentation

## Overview
The APT plugin provides package management for Debian-based systems using the Advanced Package Tool (APT).

## Features
- Package search, install, remove
- Category browsing by APT sections
- Update detection and management
- LMDB caching for performance
- System-wide lock management

## Documentation

### [Locking Mechanism](locking.md)
APT lock management to prevent concurrent package operations and conflicts with other package managers.

## Plugin Details

**Backend ID**: `apt`  
**Display Name**: APT Packages  
**Location**: `src/controllers/plugins/apt_plugin.py`

## Capabilities
- `search` - Search packages
- `install` - Install packages
- `remove` - Remove packages
- `list_installed` - List installed packages
- `list_updates` - List available updates
- `categories` - Category browsing

## System Requirements
- Debian/Ubuntu-based Linux distribution
- `python3-apt` package installed
- Root privileges for install/remove operations

## Category Mapping
Maps APT sections to standard sidebar categories:
- **games** → games
- **graphics** → graphics
- **internet** → net, web, mail
- **multimedia** → sound, video
- **office** → editors, text, doc
- **development** → devel, libdevel, python, perl
- **system** → admin, base, kernel, shells
- **utilities** → utils, misc, otherosfs
- **education** → education, science
