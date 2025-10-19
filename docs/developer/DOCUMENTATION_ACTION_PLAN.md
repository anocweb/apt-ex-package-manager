# Documentation Action Plan

## Current State (Based on Maintainer Input)

- **Database**: SQLite → LMDB migration in progress (SQLite removal tonight)
- **Backends**: APT only (Flatpak/AppImage planned)
- **Plugin Architecture**: Planned, requires refactor
- **Project Type**: Fun side project (no formal roadmap)
- **Documentation Audience**: 
  - `docs/` = Human developers/users
  - `.amazonq/rules/` = AI assistants only

---

## Immediate Actions (Tonight/This Week)

### 1. Database Documentation Cleanup
**After SQLite removal:**
- [x] Delete or archive `docs/DATABASE_ARCHITECTURE.md`
- [x] Rename `docs/LMDB_ARCHITECTURE.md` → `docs/DATABASE_ARCHITECTURE.md`
- [x] Update `CACHING_SYSTEM.md` to reference LMDB only
- [x] Update `.amazonq/rules/memory-bank/tech.md` to mention LMDB

### 2. Add Implementation Status Headers
**COMPLETED** - Added status headers to:
- [x] `docs/architecture/PLUGIN_ARCHITECTURE.md`
- [x] `docs/features/FEATURES.md`
- [x] `docs/architecture/DATA_STRUCTURES.md`

### 3. Update README.md
```markdown
## Current Features
- APT package browsing and management
- Category-based navigation
- Package search
- Installation/removal operations

## Planned Features
- Multi-backend plugin architecture
- Flatpak support
- AppImage support
```

---

## Short-term Improvements (Next Few Weeks)

### 4. Clarify Documentation Purpose
Add headers to key files:

**docs/PLUGIN_ARCHITECTURE.md:**
```markdown
# Plugin Architecture (Design Specification)

> This document describes the planned plugin system architecture.
> It serves as a design specification for future implementation.
```

**docs/PLUGIN_EXAMPLE.md:**
```markdown
# Plugin Implementation Example (Reference)

> This is a reference implementation for the planned plugin system.
> Not currently implemented in codebase.
```

### 5. Create Simple Status Tracker
**docs/STATUS.md:**
```markdown
# Implementation Status

## Current (Working)
- APT package listing, search, install, remove
- Category browsing (APT sections)
- LMDB caching
- Qt6 UI with KDE Plasma 6 styling

## In Progress
- LMDB migration (replacing SQLite)

## Planned (Design Phase)
- Plugin architecture
- Flatpak backend
- AppImage backend
- Multi-backend search

## Future Ideas
- Package ratings/reviews
- Repository management UI
- Update scheduling
```

### 6. Simplify Amazon Q Rules
Update `.amazonq/rules/plugin-development.md`:
```markdown
# Plugin Development Rules

> **Status**: PLANNED - Design specification only
> **See**: docs/PLUGIN_ARCHITECTURE.md for complete specification

## Current Implementation
- APT controller is monolithic (src/controllers/apt_controller.py)
- No plugin system exists yet

## When Plugin System is Implemented
[Keep existing rules but add note they're for future use]
```

---

## Documentation Maintenance Strategy

### What to Keep Updated
1. **docs/STATUS.md** - Update as features are completed
2. **README.md** - Keep current features accurate
3. **Implementation status headers** - Update when starting/completing features

### What Can Wait
- Comprehensive API documentation (until plugin system is stable)
- Detailed testing guides (until test suite is established)
- Deployment documentation (until ready for distribution)

### Amazon Q Rules Maintenance
- Keep synchronized with docs/ when making major changes
- Focus on coding patterns and current implementation
- Mark planned features clearly as "FUTURE"

---

## Recommended New Documents (Minimal Set)

### 1. docs/STATUS.md (see above)
Quick reference for what's working vs. planned

### 2. docs/DEVELOPMENT.md
```markdown
# Development Guide

## Setup
```bash
pip install -r requirements.txt
python src/main.py
```

## Project Structure
- `src/controllers/` - Business logic (APT operations)
- `src/views/` - Qt6 UI components
- `src/models/` - Data structures
- `src/cache/` - LMDB caching layer

## Current Architecture
[Brief overview of current implementation]

## Planned Architecture
See docs/PLUGIN_ARCHITECTURE.md for future plugin system design.
```

### 3. docs/CONTRIBUTING.md (Simple Version)
```markdown
# Contributing

This is a personal side project, but contributions are welcome!

## Code Style
- Follow PEP 8
- Use type hints
- See .amazonq/rules/coding-standards.md

## Before Submitting
- Test with APT on Ubuntu/Debian
- Ensure UI works with KDE Plasma 6
- Update docs if adding features

## Note on Planned Features
See docs/STATUS.md for what's planned vs. implemented.
```

---

## Documentation Organization (Simplified)

### Keep Current Structure
```
docs/
├── STATUS.md                         # NEW - Implementation tracker
├── README.md                         # Update with current state
├── DEVELOPMENT.md                    # NEW - Quick dev guide
├── CONTRIBUTING.md                   # NEW - Simple contribution guide
│
├── FEATURES.md                       # Add status headers
├── DESIGN_GUIDELINES.md              # Keep as-is
├── CONTEXT_ACTIONS.md                # Keep as-is
├── APT_SECTION_MAPPING.md            # Keep as-is
│
├── DATABASE_ARCHITECTURE.md          # Replace with LMDB version
├── CACHING_SYSTEM.md                 # Update for LMDB
├── REPOSITORY_IMPLEMENTATION.md      # Keep as-is
│
├── PLUGIN_ARCHITECTURE.md            # Add "PLANNED" header
├── PLUGIN_EXAMPLE.md                 # Add "REFERENCE" header
└── DATA_STRUCTURES.md                # Add "SPECIFICATION" header
```

**Don't create** (until needed):
- Subdirectories (user-guide/, developer/, etc.)
- Comprehensive API docs
- Detailed testing guides
- FAQ (build organically)

---

## Amazon Q Rules Updates

### Update These Files:

**.amazonq/rules/memory-bank/tech.md:**
- Change SQLite → LMDB
- Note: APT only (Flatpak/AppImage planned)

**.amazonq/rules/memory-bank/structure.md:**
- Remove references to plugins/ directory (doesn't exist yet)
- Reflect current controller structure

**.amazonq/rules/plugin-development.md:**
- Add header: "PLANNED - Design specification"
- Note current implementation is monolithic

**.amazonq/rules/project-guidelines.md:**
- Update: "Primary Backend: APT (only current implementation)"
- Note: "Multi-backend support planned"

---

## Priority Checklist

### Tonight (After SQLite Removal)
- [x] Delete/archive DATABASE_ARCHITECTURE.md (SQLite version)
- [x] Rename LMDB_ARCHITECTURE.md → DATABASE_ARCHITECTURE.md
- [x] Update CACHING_SYSTEM.md references
- [x] Update .amazonq/rules/memory-bank/tech.md

### This Week
- [x] Add status headers to PLUGIN_ARCHITECTURE.md, FEATURES.md, DATA_STRUCTURES.md
- [ ] Create docs/STATUS.md
- [ ] Update README.md with current vs. planned features
- [ ] Update .amazonq/rules/plugin-development.md with "PLANNED" note

### Next Few Weeks (As Time Permits)
- [ ] Create docs/DEVELOPMENT.md
- [ ] Create docs/CONTRIBUTING.md
- [ ] Update .amazonq/rules/memory-bank/ files for current state
- [ ] Review and update cross-references

---

## Key Principles for Your Project

1. **Mark Planned Features Clearly** - Avoid confusion about what exists vs. what's designed
2. **Keep Docs Lightweight** - You're the sole maintainer, don't create maintenance burden
3. **Update as You Build** - When implementing plugins, update docs then
4. **Amazon Q Rules = Current State** - Help AI understand what's actually implemented
5. **docs/ = Design + Current** - Can include future designs, but mark them clearly

---

## Questions Resolved

✅ Database: LMDB (SQLite being removed)
✅ Plugin Architecture: Planned (design spec exists)
✅ Backends: APT only (others planned)
✅ Roadmap: Flexible (side project)
✅ Maintainer: You
✅ Doc Audience: docs/ = humans, .amazonq/rules/ = AI

---

*This action plan focuses on minimal, high-impact changes to clarify current vs. planned state.*
