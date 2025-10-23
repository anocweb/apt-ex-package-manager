"""Dependency checking utilities"""
import shutil
import subprocess
import importlib
import re
from typing import Dict, List, Any, Optional
from utils.version_checker import VersionChecker

class DependencyChecker:
    @staticmethod
    def check_system_command(command: str) -> bool:
        """Check if system command exists"""
        return shutil.which(command) is not None
    
    @staticmethod
    def get_command_version(version_command: List[str]) -> Optional[str]:
        """Get version from command output"""
        try:
            result = subprocess.run(version_command, capture_output=True, text=True, timeout=5)
            output = result.stdout + result.stderr
            
            # Extract version number
            match = re.search(r'(\d+\.[\d.]+)', output)
            return match.group(1) if match else None
        except:
            return None
    
    @staticmethod
    def check_python_module(module_name: str) -> bool:
        """Check if Python module is importable"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_module_version(module_name: str) -> Optional[str]:
        """Get Python module version"""
        try:
            module = importlib.import_module(module_name)
            return getattr(module, '__version__', None)
        except:
            return None
    
    @staticmethod
    def check_system_dependency(dep: Dict[str, Any]) -> Dict[str, Any]:
        """Check single system dependency with version"""
        result = {
            'name': dep.get('name', ''),
            'command': dep.get('command', ''),
            'required_version': dep.get('min_version', ''),
            'installed_version': None,
            'satisfied': False
        }
        
        # Check if command exists
        if not DependencyChecker.check_system_command(dep['command']):
            return result
        
        # Get version if specified
        if 'version_command' in dep:
            version = DependencyChecker.get_command_version(dep['version_command'])
            result['installed_version'] = version
            
            # Check version constraint
            if dep.get('min_version') and version:
                result['satisfied'] = VersionChecker.check_constraint(version, f">={dep['min_version']}")
            else:
                result['satisfied'] = True
        else:
            result['satisfied'] = True
        
        return result
    
    @staticmethod
    def check_python_dependency(spec: str) -> Dict[str, Any]:
        """Check single Python dependency with version"""
        package, constraint = VersionChecker.parse_pip_spec(spec)
        
        result = {
            'package': package,
            'required_version': constraint or '',
            'installed_version': None,
            'satisfied': False
        }
        
        # Check if module exists
        if not DependencyChecker.check_python_module(package):
            return result
        
        # Get version
        version = DependencyChecker.get_module_version(package)
        result['installed_version'] = version
        
        # Check version constraint
        if constraint and version:
            result['satisfied'] = VersionChecker.check_constraint(version, constraint)
        else:
            result['satisfied'] = True
        
        return result
    
    @staticmethod
    def check_plugin_dependencies(plugin) -> Dict[str, Any]:
        """Check all dependencies for a plugin"""
        system_deps = []
        python_deps = []
        missing = []
        
        # Check system dependencies
        for dep in plugin.get_system_dependencies():
            status = DependencyChecker.check_system_dependency(dep)
            system_deps.append(status)
            if not status['satisfied']:
                missing.append(f"{status['name']} (command: {status['command']})")
        
        # Check Python dependencies
        for spec in plugin.get_python_dependencies():
            status = DependencyChecker.check_python_dependency(spec)
            python_deps.append(status)
            if not status['satisfied']:
                missing.append(f"Python: {status['package']}")
        
        all_satisfied = all(d['satisfied'] for d in system_deps + python_deps)
        
        return {
            'system': system_deps,
            'python': python_deps,
            'all_satisfied': all_satisfied,
            'missing': missing
        }
