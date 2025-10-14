# Coding Standards for Apt-Ex Package Manager

> **Note**: Detailed development patterns and conventions are documented in the Memory Bank (guidelines.md). This file covers project-specific standards.

## Error Handling
- Provide user-friendly error messages
- Log technical errors for debugging
- Handle APT command failures gracefully
- Show progress and status feedback

## Security
- Validate all user inputs
- Use secure privilege escalation methods
- Verify package signatures when possible
- Sanitize command-line arguments

## Performance
- Cache package lists efficiently
- Use threading for long-running operations
- Implement incremental search results
- Minimize system resource usage

## Dependencies
- List all dependencies in requirements.txt
- Use Qt6 for GUI framework
- Minimize external dependencies
- Document any system requirements

## Documentation Synchronization
- When updating docs/FEATURES.md or docs/DESIGN_GUIDELINES.md, reflect changes in corresponding Amazon Q rules
- Keep .amazonq/rules/ files aligned with project documentation
- Update rules when project standards or guidelines change