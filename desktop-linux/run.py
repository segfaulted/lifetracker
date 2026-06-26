import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction

from app.window_tasks import MainWindow as MainWindowTasks
from app.window_meds import MainWindow as MainWindowMeds
from app.window_tasks import create_tray_icon
from app.ipc import IPCManager

def main():
    # 1. Parse command line arguments
    toggle_tasks = "--toggle-tasks" in sys.argv
    toggle_meds = "--toggle-meds" in sys.argv
    toggle_generic = "--toggle" in sys.argv
    
    if toggle_tasks:
        success = IPCManager.send_toggle_command("tasks")
        if success:
            print("[CLI] Toggle Tasks signal sent successfully to running instance.")
            sys.exit(0)
    elif toggle_meds:
        success = IPCManager.send_toggle_command("meds")
        if success:
            print("[CLI] Toggle Meds signal sent successfully to running instance.")
            sys.exit(0)
    elif toggle_generic:
        success = IPCManager.send_toggle_command("tasks")
        if success:
            print("[CLI] Toggle Tasks (generic) signal sent successfully to running instance.")
            sys.exit(0)

    # 2. Start the main application
    app = QApplication(sys.argv)
    
    # Crucial for system tray applications: don't quit when window is hidden
    app.setQuitOnLastWindowClosed(False)
    
    # 3. Check for single instance / start IPC Server
    ipc_manager = IPCManager()
    if not ipc_manager.start_server():
        print("[System] Another instance of Tracker Client is already running. Exiting.")
        sys.exit(1)
        
    # 4. Create Main GUI Windows
    window_tasks = MainWindowTasks()
    window_meds = MainWindowMeds()
    
    # Connect IPC signal to toggle window visibility
    def handle_ipc_toggle(target: str):
        if target == "tasks":
            window_tasks.toggle_window()
        elif target == "meds":
            window_meds.toggle_window()
            
    ipc_manager.toggle_requested.connect(handle_ipc_toggle)
    
    # 5. Initialize System Tray Icon
    tray_icon = QSystemTrayIcon(create_tray_icon(), app)
    tray_icon.setToolTip("Tracker Client")
    
    # Create tray menu
    tray_menu = QMenu()
    
    toggle_tasks_action = QAction("Toggle Tasks Window", app)
    toggle_tasks_action.triggered.connect(window_tasks.toggle_window)
    tray_menu.addAction(toggle_tasks_action)
    
    toggle_meds_action = QAction("Toggle Medication Window", app)
    toggle_meds_action.triggered.connect(window_meds.toggle_window)
    tray_menu.addAction(toggle_meds_action)
    
    dashboard_action = QAction("Open Tasks Dashboard", app)
    dashboard_action.triggered.connect(window_tasks.open_dashboard)
    tray_menu.addAction(dashboard_action)
    
    tray_menu.addSeparator()
    
    exit_action = QAction("Exit All", app)
    exit_action.triggered.connect(app.quit)
    tray_menu.addAction(exit_action)
    
    tray_icon.setContextMenu(tray_menu)
    
    # Single click or double click on tray icon toggles the tasks window by default
    def on_tray_activated(reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            window_tasks.toggle_window()
            
    tray_icon.activated.connect(on_tray_activated)
    tray_icon.show()
    
    # Show the windows on startup based on which toggle option was requested
    if toggle_meds:
        window_meds.show()
        window_meds.raise_()
        window_meds.activateWindow()
    else:
        window_tasks.show()
        window_tasks.raise_()
        window_tasks.activateWindow()
    
    print("[System] Unified Tracker Client started successfully.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
