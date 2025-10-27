"""
Daemon Manager - Install, control, and manage update daemon
"""

import os
import subprocess
from pathlib import Path
from typing import Tuple


class DaemonManager:
    """Manage update checker daemon installation and control"""
    
    SERVICE_NAME = 'apt-ex-update-checker.service'
    PRESET_NAME = '90-apt-ex.preset'
    
    @staticmethod
    def is_installed_system_wide() -> bool:
        """Check if daemon installed system-wide"""
        return Path('/usr/lib/systemd/user').joinpath(
            DaemonManager.SERVICE_NAME
        ).exists()
    
    @staticmethod
    def is_installed_user() -> bool:
        """Check if daemon installed for current user"""
        return Path.home().joinpath(
            '.config/systemd/user',
            DaemonManager.SERVICE_NAME
        ).exists()
    
    @staticmethod
    def is_installed() -> bool:
        """Check if daemon installed (either mode)"""
        return (DaemonManager.is_installed_system_wide() or 
                DaemonManager.is_installed_user())
    
    @staticmethod
    def get_installation_type() -> str:
        """Get installation type"""
        if DaemonManager.is_installed_system_wide():
            return "system-wide"
        elif DaemonManager.is_installed_user():
            return "user"
        return "not installed"
    
    @staticmethod
    def install_system_wide() -> Tuple[bool, str]:
        """Install daemon system-wide (requires sudo)"""
        script = Path(__file__).parent.parent.parent / 'scripts' / 'install-daemon-system.sh'
        
        if not script.exists():
            return False, f"Installation script not found: {script}"
        
        try:
            result = subprocess.run(
                ['bash', str(script)],
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr or str(e)
    
    @staticmethod
    def install_user() -> Tuple[bool, str]:
        """Install daemon for current user only"""
        script = Path(__file__).parent.parent.parent / 'scripts' / 'install-daemon.sh'
        
        if not script.exists():
            return False, f"Installation script not found: {script}"
        
        try:
            result = subprocess.run(
                ['bash', str(script)],
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr or str(e)
    
    @staticmethod
    def uninstall() -> Tuple[bool, str]:
        """Uninstall daemon (user or system-wide)"""
        messages = []
        
        try:
            # Stop and disable
            subprocess.run(
                ['systemctl', '--user', 'stop', DaemonManager.SERVICE_NAME],
                capture_output=True,
                check=False
            )
            messages.append("Daemon stopped")
            
            subprocess.run(
                ['systemctl', '--user', 'disable', DaemonManager.SERVICE_NAME],
                capture_output=True,
                check=False
            )
            messages.append("Daemon disabled")
            
            # Remove user service file
            user_service = Path.home().joinpath('.config/systemd/user', DaemonManager.SERVICE_NAME)
            if user_service.exists():
                user_service.unlink()
                messages.append("User service file removed")
            
            # Remove system-wide (requires sudo)
            if DaemonManager.is_installed_system_wide():
                result = subprocess.run(
                    ['sudo', 'rm', f'/usr/lib/systemd/user/{DaemonManager.SERVICE_NAME}'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    messages.append("System service file removed")
                
                result = subprocess.run(
                    ['sudo', 'rm', f'/usr/lib/systemd/user-preset/{DaemonManager.PRESET_NAME}'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    messages.append("Preset file removed")
            
            # Reload systemd
            subprocess.run(
                ['systemctl', '--user', 'daemon-reload'],
                capture_output=True,
                check=False
            )
            messages.append("Systemd reloaded")
            
            return True, "\n".join(messages)
        except Exception as e:
            return False, f"Uninstall failed: {str(e)}"
    
    @staticmethod
    def is_running() -> bool:
        """Check if daemon is currently running"""
        try:
            result = subprocess.run(
                ['systemctl', '--user', 'is-active', DaemonManager.SERVICE_NAME],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == 'active'
        except:
            return False
    
    @staticmethod
    def is_enabled() -> bool:
        """Check if daemon is enabled"""
        try:
            result = subprocess.run(
                ['systemctl', '--user', 'is-enabled', DaemonManager.SERVICE_NAME],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == 'enabled'
        except:
            return False
    
    @staticmethod
    def start() -> Tuple[bool, str]:
        """Start daemon"""
        try:
            result = subprocess.run(
                ['systemctl', '--user', 'start', DaemonManager.SERVICE_NAME],
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Daemon started successfully"
        except subprocess.CalledProcessError as e:
            return False, e.stderr or "Failed to start daemon"
    
    @staticmethod
    def stop() -> Tuple[bool, str]:
        """Stop daemon"""
        try:
            result = subprocess.run(
                ['systemctl', '--user', 'stop', DaemonManager.SERVICE_NAME],
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Daemon stopped successfully"
        except subprocess.CalledProcessError as e:
            return False, e.stderr or "Failed to stop daemon"
    
    @staticmethod
    def restart() -> Tuple[bool, str]:
        """Restart daemon"""
        try:
            result = subprocess.run(
                ['systemctl', '--user', 'restart', DaemonManager.SERVICE_NAME],
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Daemon restarted successfully"
        except subprocess.CalledProcessError as e:
            return False, e.stderr or "Failed to restart daemon"
    
    @staticmethod
    def get_status() -> dict:
        """Get daemon status information"""
        return {
            'installed': DaemonManager.is_installed(),
            'installation_type': DaemonManager.get_installation_type(),
            'running': DaemonManager.is_running(),
            'enabled': DaemonManager.is_enabled()
        }
