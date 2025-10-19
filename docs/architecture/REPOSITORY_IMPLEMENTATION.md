# Repository Implementation Guide

## Overview
This document outlines the implementation approach for retrieving and managing package repositories across different package systems in Apt-Ex Package Manager.

## APT Repository Implementation

### Method: Python APT Library
Use the `python3-apt` library for robust APT repository management.

### Implementation Details

#### Getting Repository Sources
```python
import apt

def get_apt_sources():
    """Retrieve all APT repository sources"""
    try:
        cache = apt.Cache()
        sources = []
        
        # Get source list
        source_list = apt.SourcesList()
        
        for source in source_list:
            if not source.disabled:
                sources.append({
                    'uri': source.uri,
                    'dist': source.dist,
                    'comps': source.comps,
                    'type': source.type,  # 'deb' or 'deb-src'
                    'comment': source.comment,
                    'file': source.file
                })
        
        return sources
    except Exception as e:
        # Fallback to parsing files directly
        return parse_sources_files()
```

#### Repository Status Detection
```python
def get_repository_status(source):
    """Determine if repository is enabled/disabled"""
    return not source.disabled

def is_default_repository(source):
    """Check if repository is a default Ubuntu repository"""
    default_patterns = [
        'archive.ubuntu.com',
        'security.ubuntu.com',
        'ports.ubuntu.com'
    ]
    return any(pattern in source.uri for pattern in default_patterns)
```

### Error Handling
- Graceful fallback to file parsing if APT library fails
- Handle permission issues for system repositories
- Validate repository accessibility

## Flatpak Repository Implementation

### Method: Command-line Interface
Use `flatpak remotes` command to distinguish user vs system repositories.

### Implementation Details

#### Getting User Repositories
```python
import subprocess
import json

def get_flatpak_user_remotes():
    """Get user-level Flatpak remotes"""
    try:
        result = subprocess.run([
            'flatpak', 'remotes', '--user', '--show-details'
        ], capture_output=True, text=True, check=True)
        
        return parse_flatpak_remotes(result.stdout, scope='user')
    except subprocess.CalledProcessError:
        return []

def get_flatpak_system_remotes():
    """Get system-level Flatpak remotes"""
    try:
        result = subprocess.run([
            'flatpak', 'remotes', '--system', '--show-details'
        ], capture_output=True, text=True, check=True)
        
        return parse_flatpak_remotes(result.stdout, scope='system')
    except subprocess.CalledProcessError:
        return []
```

#### Parsing Remote Details
```python
def parse_flatpak_remotes(output, scope):
    """Parse flatpak remotes output"""
    remotes = []
    current_remote = {}
    
    for line in output.strip().split('\n'):
        if line and not line.startswith(' '):
            # New remote name
            if current_remote:
                remotes.append(current_remote)
            current_remote = {
                'name': line.strip(),
                'scope': scope,
                'enabled': True
            }
        elif line.startswith(' '):
            # Remote details
            key_value = line.strip().split(': ', 1)
            if len(key_value) == 2:
                key, value = key_value
                current_remote[key.lower().replace(' ', '_')] = value
    
    if current_remote:
        remotes.append(current_remote)
    
    return remotes
```

#### Combined Repository List
```python
def get_all_flatpak_remotes():
    """Get all Flatpak remotes (user + system)"""
    user_remotes = get_flatpak_user_remotes()
    system_remotes = get_flatpak_system_remotes()
    
    return {
        'user': user_remotes,
        'system': system_remotes,
        'all': user_remotes + system_remotes
    }
```

### Repository Management Operations

#### Enable/Disable Repositories
```python
def toggle_flatpak_remote(name, scope, enable=True):
    """Enable or disable a Flatpak remote"""
    action = 'modify' if enable else 'modify'
    flag = '--enable' if enable else '--disable'
    scope_flag = f'--{scope}'
    
    try:
        subprocess.run([
            'flatpak', 'remote-modify', scope_flag, flag, name
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
```

#### Add New Repository
```python
def add_flatpak_remote(name, url, scope='user'):
    """Add a new Flatpak remote"""
    scope_flag = f'--{scope}'
    
    try:
        subprocess.run([
            'flatpak', 'remote-add', scope_flag, name, url
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
```

## Error Handling Strategy

### APT Error Handling
- **Permission Issues**: Detect and prompt for elevated privileges
- **Cache Lock**: Handle APT lock file conflicts
- **Network Issues**: Graceful handling of unreachable repositories
- **Malformed Sources**: Skip invalid entries with logging

### Flatpak Error Handling
- **Command Not Found**: Check if Flatpak is installed
- **Permission Denied**: Handle system repository access issues
- **Network Timeout**: Handle remote repository connectivity
- **Invalid Remotes**: Skip malformed remote configurations

## Integration Points

### Controller Integration
```python
class RepositoryController:
    def __init__(self):
        self.apt_sources = []
        self.flatpak_remotes = {}
        self.last_refresh = None
    
    def refresh_all_sources(self):
        """Refresh all repository sources"""
        self.apt_sources = get_apt_sources()
        self.flatpak_remotes = get_all_flatpak_remotes()
        self.last_refresh = datetime.now()
    
    def get_unified_source_list(self):
        """Return unified list for UI display"""
        sources = []
        
        # Add APT sources
        for source in self.apt_sources:
            sources.append({
                'type': 'apt',
                'name': f"{source['uri']} - {source['dist']}",
                'enabled': not source.get('disabled', False),
                'scope': 'system',
                'source': source
            })
        
        # Add Flatpak sources
        for remote in self.flatpak_remotes['all']:
            sources.append({
                'type': 'flatpak',
                'name': f"{remote['name']} - {remote.get('url', 'Unknown')}",
                'enabled': remote.get('enabled', True),
                'scope': remote['scope'],
                'source': remote
            })
        
        return sources
```

## Performance Considerations

### Caching Strategy
- Cache repository lists for 5-10 minutes
- Refresh on user request or after repository changes
- Background refresh to avoid UI blocking

### Threading
- Use QThread for repository operations
- Emit signals for UI updates
- Handle cancellation for long-running operations

### Resource Management
- Close APT cache properly
- Limit concurrent subprocess calls
- Handle memory usage for large repository lists

## Security Considerations

### APT Security
- Validate repository signatures
- Check for secure (HTTPS) repositories
- Warn about unsigned repositories

### Flatpak Security
- Verify remote authenticity
- Check GPG signatures when available
- Validate remote URLs before adding

## Testing Strategy

### Unit Tests
- Mock subprocess calls for Flatpak operations
- Test APT library integration with sample data
- Validate error handling scenarios

### Integration Tests
- Test with real system repositories
- Verify user vs system scope handling
- Test repository enable/disable operations

## Future Enhancements

### Planned Features
- Repository health checking
- Automatic repository updates
- Repository recommendation system
- Backup/restore repository configurations