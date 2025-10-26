"""Worker thread for package install/remove operations"""
from PyQt6.QtCore import QThread, pyqtSignal
import subprocess
import os
import pty
import select
import pyte


class PackageOperationWorker(QThread):
    """Worker thread for package operations with real-time output"""
    
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)
    output_line = pyqtSignal(str)
    command_started = pyqtSignal(str)
    
    def __init__(self, backend, operation, package_name, logging_service=None, terminal_width=120):
        super().__init__()
        self.backend = backend
        self.operation = operation
        self.package_name = package_name
        self.logging_service = logging_service
        self.logger = logging_service.get_logger('operations') if logging_service else None
        self.output_buffer = []
        
        # Pyte terminal emulation with dynamic width
        self.screen = pyte.Screen(terminal_width, 100)
        self.stream = pyte.Stream(self.screen)
        self.last_display = ""
    
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
            
            # Run command with PTY for interactive support
            master_fd, slave_fd = pty.openpty()
            
            process = subprocess.Popen(
                cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                close_fds=True
            )
            
            os.close(slave_fd)
            
            # Read output from PTY with Pyte terminal emulation
            while True:
                try:
                    ready, _, _ = select.select([master_fd], [], [], 0.1)
                    if ready:
                        data = os.read(master_fd, 1024).decode('utf-8', errors='replace')
                        if data:
                            # Feed data to Pyte terminal emulator
                            self.stream.feed(data)
                            
                            # Get current display and emit full screen
                            current_display = '\n'.join(line.rstrip() for line in self.screen.display).rstrip()
                            if current_display != self.last_display:
                                self.output_line.emit(current_display)
                                self.last_display = current_display
                    
                    # Check if process finished
                    if process.poll() is not None:
                        # Read any remaining data
                        try:
                            while True:
                                data = os.read(master_fd, 1024).decode('utf-8', errors='replace')
                                if not data:
                                    break
                                self.stream.feed(data)
                        except:
                            pass
                        break
                except OSError as e:
                    # Errno 5 (I/O error) is expected when PTY closes
                    if e.errno != 5 and self.logger:
                        self.logger.error(f"PTY read error: {e}")
                    break
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"PTY read error: {e}")
                    break
            
            os.close(master_fd)
            process.wait()
            result = process.returncode == 0
            
            # Get final clean output from terminal
            final_output = '\n'.join(line.rstrip() for line in self.screen.display).rstrip()
            
            # Log result with output
            if self.logger:
                if result:
                    self.logger.info(f"Command completed successfully", data=final_output)
                else:
                    self.logger.error(f"Command failed with exit code {process.returncode}", data=final_output)
            
            self.finished.emit(result, self.package_name)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Operation failed: {e}")
            self.error.emit(str(e))
