# AI-Assisted Development Guide

## Overview

This project welcomes AI-assisted development (Amazon Q, GitHub Copilot, ChatGPT, etc.). This guide helps you work effectively with AI tools while maintaining code quality and project consistency.

---

## Understanding the Documentation Split

### docs/ - Human Reference
- Complete specifications and design documents
- Implementation guides and examples
- Architecture decisions and rationale
- **Use these** when you need to understand the full context

### .amazonq/rules/ - AI Context
- Coding patterns and standards
- Quick reference summaries
- Project-specific conventions
- **AI tools read these automatically** to understand the project

---

## Before Using AI Assistance

### 1. Check Implementation Status
Always verify what's actually implemented vs. planned:

```bash
# Read this first
cat docs/STATUS.md
```

**Key distinctions:**
- ✅ **Implemented**: APT backend, LMDB caching, Qt6 UI
- 🔄 **In Progress**: LMDB migration
- 📋 **Planned**: Plugin architecture, Flatpak, AppImage

### 2. Understand Current Architecture
```
Current: Monolithic APT controller
Planned: Plugin-based multi-backend system
```

**Don't ask AI to:**
- "Add a new plugin" (plugin system doesn't exist yet)
- "Implement Flatpak support" (architecture not ready)
- "Use the BasePackageController" (doesn't exist yet)

**Do ask AI to:**
- "Improve APT package search"
- "Add caching for category counts"
- "Enhance UI responsiveness"

---

## Working with AI Tools

### Effective Prompts

❌ **Bad**: "Add Flatpak support"
- Plugin architecture doesn't exist yet

✅ **Good**: "Add a method to APTController to filter packages by installed status"
- Works with current architecture

❌ **Bad**: "Create a new backend plugin"
- Would create code that doesn't integrate

✅ **Good**: "Refactor APTController method X to improve performance"
- Improves existing code

### Context Awareness

**Always mention:**
- "This project currently only supports APT"
- "The plugin architecture is planned but not implemented"
- "We're using LMDB for caching, not SQLite"

**Example prompt:**
```
"In the current APT-only implementation, add a method to 
APTController to get packages by section. Use LMDB caching 
to store results. Follow the patterns in existing methods."
```

---

## AI-Generated Code Review Checklist

Before accepting AI-generated code, verify:

### 1. Architecture Alignment
- [ ] Uses existing APTController (not non-existent plugins)
- [ ] Integrates with LMDB cache (not SQLite)
- [ ] Follows Qt6 patterns (not Qt5)
- [ ] Uses existing models (Package, PackageSummary)

### 2. Code Standards
- [ ] Follows PEP 8
- [ ] Includes type hints
- [ ] Has docstrings for public methods
- [ ] Uses snake_case for functions/variables
- [ ] Uses PascalCase for classes

### 3. Project Patterns
- [ ] Database access through model classes (not direct SQL)
- [ ] UI updates via signals/slots
- [ ] Error handling returns empty lists (doesn't raise)
- [ ] Logging uses logging_service

### 4. Documentation
- [ ] Updates relevant docs/ files if adding features
- [ ] Adds comments for complex logic
- [ ] Updates STATUS.md if completing planned features

---

## Common AI Mistakes to Watch For

### 1. Implementing Planned Features
**AI might generate:**
```python
from controllers.base_controller import BasePackageController

class FlatpakPlugin(BasePackageController):
    ...
```

**Problem**: BasePackageController doesn't exist yet

**Fix**: Politely decline and explain current architecture

### 2. Using Wrong Database
**AI might generate:**
```python
import sqlite3
conn = sqlite3.connect('cache.db')
```

**Problem**: We use LMDB, not SQLite

**Fix**: Ask AI to use LMDB via existing cache classes

### 3. Direct Database Access
**AI might generate:**
```python
cursor.execute('SELECT * FROM package_cache WHERE ...')
```

**Problem**: Should use model classes

**Fix**: Use PackageCacheModel methods instead

### 4. Mixing Qt Versions
**AI might generate:**
```python
from PyQt5.QtWidgets import QWidget
```

**Problem**: We use Qt6, not Qt5

**Fix**: Change to `from PyQt6.QtWidgets import QWidget`

---

## Guiding AI to Current Implementation

### Provide Context in Prompts

**Template:**
```
Context: This project currently uses:
- APT backend only (no plugins yet)
- LMDB for caching
- Qt6 for UI
- Monolithic APTController in src/controllers/apt_controller.py

Task: [Your specific request]

Requirements:
- Follow existing patterns in APTController
- Use LMDB cache via cache_manager
- Include type hints and docstrings
```

### Reference Existing Code

**Good prompt:**
```
"Add a method similar to get_installed_packages() in APTController,
but for upgradable packages. Use the same caching pattern."
```

This helps AI understand:
- Where to add code
- What patterns to follow
- What the output should look like

---

## When AI Suggests Refactoring

AI might suggest implementing the plugin architecture. Evaluate:

### Consider If:
- [ ] You're ready to start the plugin migration
- [ ] You have time for a major refactor
- [ ] The suggestion aligns with docs/PLUGIN_ARCHITECTURE.md

### Decline If:
- [ ] You're in the middle of another feature
- [ ] The suggestion doesn't match the planned design
- [ ] It would break existing functionality

**Response template:**
```
"Thanks, but the plugin architecture is planned for later.
For now, let's improve the current APTController implementation.
Can you suggest improvements that work with the existing structure?"
```

---

## Updating Documentation with AI

### AI Can Help With:
- Writing docstrings
- Updating STATUS.md when features complete
- Adding code examples to docs
- Fixing typos and formatting

### AI Should NOT:
- Remove "PLANNED" status without your approval
- Mark features as complete that aren't
- Change architecture decisions
- Delete design specifications

### Prompt Template:
```
"Update docs/STATUS.md to mark [feature] as complete.
Keep the planned features section accurate - don't mark
anything else as done."
```

---

## Testing AI-Generated Code

### Minimum Testing
```bash
# 1. Syntax check
python -m py_compile src/controllers/apt_controller.py

# 2. Run the app
python src/main.py

# 3. Test the specific feature
# (manually verify it works)
```

### Ask AI for Tests
```
"Generate a simple test for this method that mocks
the APT cache and verifies the output format."
```

---

## Amazon Q Specific Tips

### Using @workspace
```
@workspace How do I add a new method to APTController?
```
Amazon Q will read .amazonq/rules/ automatically.

### Using @file
```
@file:src/controllers/apt_controller.py 
Add a method to get packages by section
```

### Clarifying Context
If Amazon Q suggests plugin code:
```
"Note: The plugin architecture in docs/ is planned but not
implemented. Please work with the current APTController."
```

---

## Contributing AI-Generated Code

### Before Submitting
1. **Review thoroughly** - Don't blindly accept AI output
2. **Test manually** - Verify it works with real APT packages
3. **Check docs** - Update if adding features
4. **Follow standards** - Run through checklist above

### In Pull Request Description
```markdown
## AI Assistance Used
- Tool: Amazon Q / GitHub Copilot / ChatGPT
- Scope: [Generated initial implementation / Helped with refactoring / etc.]
- Review: [Manually reviewed and tested / Modified AI output / etc.]
```

### Be Transparent
It's fine to use AI assistance! Just:
- Review the code yourself
- Test it works
- Understand what it does
- Take responsibility for the submission

---

## Best Practices Summary

### ✅ Do:
- Check STATUS.md before starting
- Provide context about current implementation
- Review AI-generated code carefully
- Test before committing
- Update docs when adding features
- Ask AI to follow existing patterns

### ❌ Don't:
- Assume AI knows what's implemented
- Accept code that uses non-existent features
- Skip testing AI-generated code
- Let AI mark planned features as complete
- Implement plugin system without planning
- Use AI-generated code you don't understand

---

## Getting Help

### If AI Generates Wrong Code
1. Check docs/STATUS.md for current state
2. Provide more context in your prompt
3. Reference existing code patterns
4. Ask AI to revise based on current architecture

### If Unsure About AI Suggestion
1. Read relevant docs/ files
2. Check if feature is planned vs. implemented
3. Look at existing code for patterns
4. Ask in project discussions (if applicable)

### If AI Suggests Major Changes
1. Review docs/PLUGIN_ARCHITECTURE.md
2. Consider if it's the right time
3. Discuss with maintainer (if contributing)
4. Start small, refactor incrementally

---

## Example Workflow

### Good AI-Assisted Development Flow

1. **Check status**
   ```bash
   cat docs/STATUS.md
   ```

2. **Provide context**
   ```
   "In APTController (current implementation), add method to
   filter packages by category. Use LMDB caching pattern from
   get_installed_packages()."
   ```

3. **Review generated code**
   - Check imports (Qt6, not Qt5)
   - Verify uses existing cache
   - Ensure follows patterns

4. **Test**
   ```bash
   python src/main.py
   # Test the new feature
   ```

5. **Update docs**
   - Add to STATUS.md if completing planned feature
   - Update relevant docs/ files

6. **Commit**
   ```bash
   git add .
   git commit -m "Add category filtering to APTController"
   ```

---

## Conclusion

AI assistance is a powerful tool for this project. The key is:
- **Understand** what's implemented vs. planned
- **Guide** AI with accurate context
- **Review** generated code carefully
- **Test** before committing
- **Document** changes appropriately

By following these guidelines, you'll get the benefits of AI assistance while maintaining code quality and project consistency.

---

*For questions about current implementation, see docs/STATUS.md*
*For coding standards, see .amazonq/rules/coding-standards.md*
*For architecture plans, see docs/PLUGIN_ARCHITECTURE.md*
*For plugin-specific documentation, see docs/plugins/*
