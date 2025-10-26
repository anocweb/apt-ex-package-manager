"""Worker thread for package install/remove operations"""
from PyQt6.QtCore import QThread, pyqtSignal
import subprocess


class PackageOperationWorker(QThread):
    """Worker thread for package operations with real-time output"""
    
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)
    output_line = pyqtSignal(str)
    command_started = pyqtSignal(str)
    
    def __init__(self, backend, operation, package_name, logging_service=None):
        super().__init__()
        self.backend = backend
        self.operation = operation
        self.package_name = package_name
        self.logging_service = logging_service
        self.logger = logging_service.get_logger('operations') if logging_service else None
        self.output_buffer = []
    
    def run(self):
        try:
            # Build command
            if self.operation == 'install':
                cmd = ['pkexec', 'apt-get', 'install', '-y', self.package_name]
            elif self.operation == 'remove':
                cmd = ['pkexec', 'apt-get', 'remove', '-y', self.package_name]
            elif self.operation == 'update':
                cmd = ['pkexec', 'apt-get', 'install', '--only-upgrade', '-y', self.package_name]
            elif self.operation == 'update_all':
                cmd = ['pkexec', 'apt-get', 'upgrade', '-y']
            else:
                self.error.emit(f"Unknown operation: {self.operation}")
                return
            
            cmd_str = ' '.join(cmd)
            self.command_started.emit(cmd_str)
            
            # Log command
            if self.logger:
                self.logger.info(f"Executing: {cmd_str}")
            
            # Run command with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Read output line by line
            for line in process.stdout:
                line_stripped = line.rstrip()
                self.output_line.emit(line_stripped)
                self.output_buffer.append(line_stripped)
            
            process.wait()
            result = process.returncode == 0
            
            # Log result with output
            if self.logger:
                output_text = '\n'.join(self.output_buffer)
                if result:
                    self.logger.info(f"Command completed successfully", data=output_text)
                else:
                    self.logger.error(f"Command failed with exit code {process.returncode}", data=output_text)
            
            self.finished.emit(result, self.package_name)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Operation failed: {e}")
            self.error.emit(str(e))
