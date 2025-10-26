"""
Example: Integrating Operation Status UI into MainView

This example shows how to integrate the OperationStatusBar and OperationPanel
into the main window to track package operations.
"""

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from widgets.operation_panel import OperationPanel, OperationStatusBar
from workers.package_operation_worker import PackageOperationWorker


class MainViewWithOperationStatus(QMainWindow):
    """Example main view with operation status UI"""
    
    def __init__(self):
        super().__init__()
        self.setup_operation_ui()
    
    def setup_operation_ui(self):
        """Setup operation status UI components"""
        # Get or create central widget
        if not self.centralWidget():
            central = QWidget()
            self.setCentralWidget(central)
        
        central = self.centralWidget()
        
        # Create operation panel (overlay)
        self.operation_panel = OperationPanel(central)
        self.operation_panel.collapsed.connect(self.on_panel_collapsed)
        
        # Create operation status bar
        self.operation_status_bar = OperationStatusBar(central)
        self.operation_status_bar.expand_requested.connect(self.on_expand_requested)
        
        # Position status bar at bottom
        self.position_status_bar()
    
    def position_status_bar(self):
        """Position status bar at bottom of window"""
        if self.centralWidget():
            width = self.centralWidget().width()
            height = self.centralWidget().height()
            self.operation_status_bar.setGeometry(
                0, 
                height - self.operation_status_bar.height(),
                width,
                self.operation_status_bar.height()
            )
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        self.position_status_bar()
        if self.operation_panel.is_expanded:
            self.operation_panel.update_position()
    
    def install_package(self, package_name: str, backend):
        """Install a package with operation tracking"""
        # Create worker
        self.worker = PackageOperationWorker(backend, 'install', package_name)
        
        # Connect signals
        self.worker.command_started.connect(self.on_command_started)
        self.worker.output_line.connect(self.on_output_line)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.error.connect(self.on_operation_error)
        
        # Start operation UI
        self.operation_status_bar.start_operation("Installing", package_name)
        self.operation_panel.set_operation("Installing", package_name, "")
        
        # Start worker
        self.worker.start()
    
    def remove_package(self, package_name: str, backend):
        """Remove a package with operation tracking"""
        # Create worker
        self.worker = PackageOperationWorker(backend, 'remove', package_name)
        
        # Connect signals
        self.worker.command_started.connect(self.on_command_started)
        self.worker.output_line.connect(self.on_output_line)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.error.connect(self.on_operation_error)
        
        # Start operation UI
        self.operation_status_bar.start_operation("Removing", package_name)
        self.operation_panel.set_operation("Removing", package_name, "")
        
        # Start worker
        self.worker.start()
    
    def on_command_started(self, command: str):
        """Handle command started signal"""
        # Update panel with actual command
        if hasattr(self, 'worker'):
            operation = self.worker.operation.capitalize()
            package = self.worker.package_name
            self.operation_panel.set_operation(operation, package, command)
    
    def on_output_line(self, line: str):
        """Handle output line from worker"""
        self.operation_panel.append_output(line)
    
    def on_operation_finished(self, success: bool, package_name: str):
        """Handle operation completion"""
        # Update UI
        self.operation_panel.set_complete(success)
        
        if success:
            message = f"Successfully installed {package_name}"
        else:
            message = f"Failed to install {package_name}"
        
        self.operation_status_bar.set_complete(success, message)
        
        # Cleanup worker
        if hasattr(self, 'worker'):
            self.worker.deleteLater()
            delattr(self, 'worker')
    
    def on_operation_error(self, error_msg: str):
        """Handle operation error"""
        self.operation_panel.append_output(f"\nError: {error_msg}")
        self.operation_panel.set_complete(False)
        self.operation_status_bar.set_complete(False, error_msg)
        
        # Cleanup worker
        if hasattr(self, 'worker'):
            self.worker.deleteLater()
            delattr(self, 'worker')
    
    def on_expand_requested(self):
        """Handle expand button clicked"""
        self.operation_panel.expand_panel()
    
    def on_panel_collapsed(self):
        """Handle panel collapsed"""
        # Panel is now hidden, status bar still visible
        pass


# Example usage in existing code:

def integrate_into_existing_main_view():
    """
    To integrate into existing MainView:
    
    1. Add to __init__:
        self.setup_operation_ui()
    
    2. Add method:
        def setup_operation_ui(self):
            self.operation_panel = OperationPanel(self.centralWidget())
            self.operation_panel.collapsed.connect(self.on_panel_collapsed)
            
            self.operation_status_bar = OperationStatusBar(self.centralWidget())
            self.operation_status_bar.expand_requested.connect(
                self.operation_panel.expand_panel
            )
    
    3. Update resizeEvent:
        def resizeEvent(self, event):
            super().resizeEvent(event)
            # ... existing code ...
            self.position_status_bar()
            if self.operation_panel.is_expanded:
                self.operation_panel.update_position()
    
    4. Replace existing install/remove calls:
        # Old:
        self.package_manager.install_package(package_name, backend)
        
        # New:
        self.install_package(package_name, backend)
    
    5. Connect worker signals in install_package/remove_package methods
    """
    pass
