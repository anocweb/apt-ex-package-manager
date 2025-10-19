# Plugin Architecture Migration Guide

> **Audience**: Developers updating views to use the new plugin architecture
> **Status**: Active - Use this guide when refactoring views

## Overview

This guide helps you migrate existing code from the old monolithic APT controller to the new plugin-based architecture. The migration is designed to be gradual and non-breaking.

## Key Changes

### Before: Direct Controller Access
```python
# Old way - direct access to apt_controller
results = self.package_manager.apt_controller.search_packages(query)
installed = self.package_manager.apt_controller.get_installed_packages()
```

### After: Unified PackageManager API
```python
# New way - unified API with optional backend parameter
results = self.package_manager.search_packages(query)
installed = self.package_manager.get_installed_packages()

# Or specify backend explicitly
results = self.package_manager.search_packages(query, backend='apt')
```

## Migration Steps

### Step 1: Identify Direct Controller Access

Search your view files for patterns like:
- `self.package_manager.apt_controller.`
- Direct imports of `APTController`

### Step 2: Replace with Unified API

**Pattern 1: Search Operations**
```python
# Before
results = self.package_manager.apt_controller.search_packages(query)

# After
results = self.package_manager.search_packages(query)
# Or for multi-backend search:
results = self.package_manager.search_packages(query)  # Searches all backends
```

**Pattern 2: Install/Remove Operations**
```python
# Before
success = self.package_manager.apt_controller.install_package(name)

# After
success = self.package_manager.install_package(name)
# Or specify backend:
success = self.package_manager.install_package(name, backend='apt')
```

**Pattern 3: List Operations**
```python
# Before
packages = self.package_manager.apt_controller.get_installed_packages()

# After
packages = self.package_manager.get_installed_packages()
# Or from specific backend:
packages = self.package_manager.get_installed_packages(backend='apt')
```

### Step 3: Add Backend Selection (Optional)

If you want users to choose backends:

```python
# Get available backends
backends = self.package_manager.get_available_backends()

# Create UI selector
for backend_id in backends:
    backend = self.package_manager.get_backend(backend_id)
    # Add to dropdown: backend.display_name

# Use selected backend
results = self.package_manager.search_packages(query, backend=selected_backend)
```

### Step 4: Show Backend Badges

Display which backend a package comes from:

```python
for package in results:
    # package.backend contains 'apt', 'flatpak', etc.
    display_text = f"{package.name} [{package.backend.upper()}]"
```

### Step 5: Handle Capabilities

Check if backend supports an operation:

```python
backend = self.package_manager.get_backend('flatpak')
if backend and 'categories' in backend.get_capabilities():
    # Show category browser
    categories = backend.get_categories()
else:
    # Hide category browser
    pass
```

## Common Patterns

### Pattern: Search with Backend Filter

```python
def search_packages(self, query, backend_filter=None):
    """Search with optional backend filter"""
    if backend_filter:
        # Search specific backend
        return self.package_manager.search_packages(query, backend=backend_filter)
    else:
        # Search all backends
        return self.package_manager.search_packages(query)
```

### Pattern: Multi-Backend Display

```python
def display_search_results(self, query):
    """Display results grouped by backend"""
    results = self.package_manager.search_packages(query)
    
    # Group by backend
    by_backend = {}
    for pkg in results:
        if pkg.backend not in by_backend:
            by_backend[pkg.backend] = []
        by_backend[pkg.backend].append(pkg)
    
    # Display grouped results
    for backend_id, packages in by_backend.items():
        backend = self.package_manager.get_backend(backend_id)
        self.add_section(backend.display_name, packages)
```

### Pattern: Capability-Based UI

```python
def setup_ui(self):
    """Setup UI based on available backends and capabilities"""
    backends = self.package_manager.get_available_backends()
    
    for backend_id in backends:
        backend = self.package_manager.get_backend(backend_id)
        caps = backend.get_capabilities()
        
        # Show/hide UI elements based on capabilities
        if 'categories' in caps:
            self.show_category_browser()
        
        if 'list_updates' in caps:
            self.show_updates_tab()
        
        if 'repositories' in caps:
            self.show_repository_manager()
```

## Backward Compatibility

The old API still works during migration:

```python
# This still works (backward compatible)
results = self.package_manager.apt_controller.search_packages(query)

# But this is preferred (new API)
results = self.package_manager.search_packages(query, backend='apt')
```

**When to use old API:**
- During gradual migration
- When you need APT-specific methods not in base interface
- For temporary compatibility

**When to use new API:**
- For new code
- When refactoring existing code
- When you want multi-backend support

## Testing Your Migration

### Test 1: Verify Functionality
```python
# Test that operations still work
results = self.package_manager.search_packages("firefox")
assert len(results) > 0
assert all(hasattr(pkg, 'backend') for pkg in results)
```

### Test 2: Verify Backend Routing
```python
# Test backend-specific operations
apt_results = self.package_manager.search_packages("firefox", backend='apt')
assert all(pkg.backend == 'apt' for pkg in apt_results)
```

### Test 3: Verify Multi-Backend
```python
# Test multi-backend search
all_results = self.package_manager.search_packages("firefox")
backends = set(pkg.backend for pkg in all_results)
assert len(backends) >= 1  # At least one backend
```

## Example: Complete View Migration

**Before:**
```python
class PackageSearchView:
    def __init__(self, package_manager):
        self.package_manager = package_manager
    
    def search(self, query):
        # Direct APT controller access
        results = self.package_manager.apt_controller.search_packages(query)
        self.display_results(results)
    
    def install(self, package_name):
        # Direct APT controller access
        success = self.package_manager.apt_controller.install_package(package_name)
        if success:
            self.show_success()
```

**After:**
```python
class PackageSearchView:
    def __init__(self, package_manager):
        self.package_manager = package_manager
        self.selected_backend = None  # None = all backends
    
    def search(self, query):
        # Unified API with optional backend
        results = self.package_manager.search_packages(
            query, 
            backend=self.selected_backend
        )
        self.display_results(results)
    
    def install(self, package):
        # Use package's backend for installation
        success = self.package_manager.install_package(
            package.name,
            backend=package.backend
        )
        if success:
            self.show_success()
    
    def set_backend_filter(self, backend_id):
        """Allow user to filter by backend"""
        self.selected_backend = backend_id
    
    def display_results(self, results):
        """Display results with backend badges"""
        for package in results:
            badge = f"[{package.backend.upper()}]"
            self.add_item(f"{package.name} {badge}")
```

## Checklist

Use this checklist when migrating a view:

- [ ] Identified all `apt_controller` direct accesses
- [ ] Replaced with unified `PackageManager` API
- [ ] Added backend parameter where needed
- [ ] Updated Package display to show backend
- [ ] Added backend selection UI (if applicable)
- [ ] Checked capabilities before showing features
- [ ] Tested with APT backend
- [ ] Tested with multiple backends (if available)
- [ ] Removed unused APTController imports
- [ ] Updated docstrings and comments

## Common Issues

### Issue 1: Package object missing backend attribute
**Problem:** Old Package objects don't have backend attribute
**Solution:** Update Package model or ensure all plugins set backend

### Issue 2: Method not available in base interface
**Problem:** Calling APT-specific method through unified API
**Solution:** Either add to base interface or access backend directly

```python
# If method is APT-specific
apt_backend = self.package_manager.get_backend('apt')
if apt_backend:
    result = apt_backend.apt_specific_method()
```

### Issue 3: Backend not available
**Problem:** Trying to use backend that's not installed
**Solution:** Check availability first

```python
backend = self.package_manager.get_backend('flatpak')
if backend:
    results = backend.search_packages(query)
else:
    self.show_error("Flatpak not available")
```

## Getting Help

- See [Plugin Implementation Guide](../architecture/PLUGIN_IMPLEMENTATION.md)
- See [Plugin Architecture Design](../architecture/PLUGIN_ARCHITECTURE.md)
- Check [Base Controller API](../api/BASE_CONTROLLER.md) (TODO)

## Next Steps

After migrating your view:
1. Test thoroughly with APT backend
2. Test with multiple backends if available
3. Update documentation
4. Submit for code review
5. Update other views using same patterns
