# Contributing to Apt-Ex Package Manager

## Welcome

This is a personal side project, but contributions are welcome! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

## Before You Start

### Check Implementation Status
Read [STATUS.md](STATUS.md) to understand:
- What's currently implemented (✅)
- What's in progress (🔄)
- What's planned (📋)
- What's just an idea (💡)

### Understand the Architecture
- **Current**: Monolithic APT controller
- **Planned**: Plugin-based multi-backend system
- See [DEVELOPMENT.md](DEVELOPMENT.md) for current architecture

## How to Contribute

### Reporting Issues
- Check existing issues first
- Provide clear description
- Include steps to reproduce
- Mention your OS and Python version

### Suggesting Features
- Check [STATUS.md](STATUS.md) - it might already be planned
- Open an issue to discuss before implementing
- Consider if it fits the project goals

### Submitting Code

#### 1. Setup Development Environment
```bash
git clone <repository-url>
cd apt-qt6-manager
pip install -r requirements.txt
```

#### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

#### 3. Make Your Changes
- Follow code style guidelines (see below)
- Test on Ubuntu/Debian with APT
- Update documentation if needed

#### 4. Test Your Changes
```bash
# Run application
python src/main.py

# Test your specific changes
# Verify existing features still work
```

#### 5. Commit Your Changes
```bash
git add .
git commit -m "Brief description of changes"
```

#### 6. Submit Pull Request
- Describe what you changed and why
- Reference any related issues
- Mention if you used AI assistance

## Code Style

### Python Standards
- **PEP 8**: Follow Python style guide
- **Type Hints**: Required for all functions
- **Docstrings**: Required for public methods
- **Naming**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_SNAKE_CASE` for constants

### Example
```python
def search_packages(self, query: str) -> List[Package]:
    """Search for packages matching query.
    
    Args:
        query: Search term
        
    Returns:
        List of matching Package objects
    """
    pass
```

### Qt6 Patterns
- Use `PyQt6` (not PyQt5)
- Load UI files with `uic.loadUi()`
- Connect signals in `setup_ui()` method
- Follow existing patterns in codebase

### Database Access
- Use model classes (don't write raw SQL in views/controllers)
- Use LMDB cache via `cache_manager`
- Follow existing caching patterns

## What to Work On

### Good First Issues
- UI improvements
- Bug fixes in existing features
- Documentation improvements
- Code cleanup and refactoring

### Needs Discussion First
- Plugin architecture implementation
- New backend support (Flatpak, AppImage)
- Major architectural changes
- Breaking changes to existing features

### Not Ready Yet
- Features requiring plugin system (wait for architecture)
- Multi-backend features (APT only currently)

## Testing Requirements

### Minimum Testing
- Run application: `python src/main.py`
- Test your specific changes
- Verify existing features work
- Test on KDE Plasma 6 if possible

### Test Environment
- Ubuntu 22.04+ or Debian-based system
- Python 3.8+
- Active APT repositories

## Documentation

### When to Update Docs
- Adding new features → Update [FEATURES.md](features/FEATURES.md)
- Completing planned features → Update [STATUS.md](STATUS.md)
- Changing architecture → Update [DEVELOPMENT.md](DEVELOPMENT.md)
- Adding UI patterns → Update [DESIGN_GUIDELINES.md](features/DESIGN_GUIDELINES.md)

### Documentation Style
- Clear and concise
- Include code examples
- Update cross-references
- Keep STATUS.md accurate

## Using AI Assistance

AI tools (Amazon Q, GitHub Copilot, ChatGPT) are welcome! See [AI_ASSISTED_DEVELOPMENT.md](developer/AI_ASSISTED_DEVELOPMENT.md) for guidelines.

### Best Practices
- Review AI-generated code carefully
- Test before submitting
- Understand what the code does
- Mention AI usage in PR description

### Common AI Mistakes
- Implementing plugin system (not ready yet)
- Using SQLite instead of LMDB
- Using PyQt5 instead of PyQt6
- Assuming Flatpak/AppImage support exists

## Pull Request Guidelines

### PR Description Should Include
- What changed and why
- Related issue numbers
- Testing performed
- Screenshots (for UI changes)
- AI assistance used (if any)

### Example PR Description
```markdown
## Changes
- Added package count to category buttons
- Improved category loading performance

## Testing
- Tested on Ubuntu 22.04 with KDE Plasma 6
- Verified all categories load correctly
- Checked cache behavior

## AI Assistance
- Used GitHub Copilot for boilerplate code
- Manually reviewed and tested all changes
```

## Code Review Process

As a personal project, review may take time. Be patient!

### What I Look For
- Code quality and style
- Compatibility with existing code
- Testing performed
- Documentation updates
- No breaking changes (unless discussed)

## Questions?

- Check [STATUS.md](STATUS.md) for implementation status
- Read [DEVELOPMENT.md](DEVELOPMENT.md) for architecture
- See [AI_ASSISTED_DEVELOPMENT.md](developer/AI_ASSISTED_DEVELOPMENT.md) for AI help
- Open an issue for discussion

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Apt-Ex Package Manager!
