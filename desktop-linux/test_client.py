import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from app.window_tasks import MainWindow
from app.api_client import LifeTrackerApiClient

def run_integration_test():
    print("[Test] Initializing QApplication...")
    app = QApplication(sys.argv)
    
    print("[Test] Checking backend server connectivity...")
    client = LifeTrackerApiClient("http://127.0.0.1:8000")
    if not client.check_connection():
        print("[FAIL] Backend server is not running on port 8000.")
        sys.exit(1)
    print("[OK] Backend server is reachable.")

    print("[Test] Creating MainWindow...")
    window = MainWindow()
    
    attempts = 0
    max_attempts = 15  # Wait up to 3 seconds
    
    def check_projects_loaded():
        nonlocal attempts
        attempts += 1
        
        project_count = window.project_dropdown.count()
        print(f"[Test] Attempt {attempts} (projects): Dropdown count is {project_count}")
        
        if project_count > 1:
            print("[OK] Projects successfully loaded from backend!")
            # Select the first project in dropdown
            window.project_dropdown.setCurrentIndex(1)
            QTimer.singleShot(500, check_tasks_or_create)
        elif attempts >= max_attempts:
            print("[FAIL] Timeout waiting for projects to load.")
            app.quit()
            sys.exit(1)
        else:
            QTimer.singleShot(200, check_projects_loaded)

    def check_tasks_or_create():
        # Check if tasks are populated
        task_rows = 0
        for i in range(window.scroll_content_layout.count()):
            widget = window.scroll_content_layout.itemAt(i).widget()
            if widget and widget.objectName() == "TaskRow":
                task_rows += 1
                
        print(f"[Test] Tasks count in GUI: {task_rows}")
        if task_rows > 0:
            print("[OK] Tasks successfully found in GUI!")
            print("[SUCCESS] All integration tests passed successfully!")
            app.quit()
            sys.exit(0)
        else:
            print("[Test] No tasks found. Creating a test task programmatically...")
            window.task_input.setText("Automated Test Task")
            # Programmatically trigger task creation button click
            window.add_task_btn.click()
            # Wait and check again
            QTimer.singleShot(500, verify_task_created)

    verify_attempts = 0
    max_verify_attempts = 15

    def verify_task_created():
        nonlocal verify_attempts
        verify_attempts += 1
        
        task_rows = 0
        for i in range(window.scroll_content_layout.count()):
            widget = window.scroll_content_layout.itemAt(i).widget()
            if widget and widget.objectName() == "TaskRow":
                task_rows += 1
                
        print(f"[Test] Verify attempt {verify_attempts}: Tasks count is {task_rows}")
        if task_rows > 0:
            print("[OK] Task created and rendered in GUI successfully!")
            print("[SUCCESS] All integration tests passed successfully!")
            app.quit()
            sys.exit(0)
        elif verify_attempts >= max_verify_attempts:
            print("[FAIL] Timeout waiting for created task to render in GUI.")
            app.quit()
            sys.exit(1)
        else:
            QTimer.singleShot(200, verify_task_created)

    # Start the test cascade
    QTimer.singleShot(200, check_projects_loaded)
    
    # Run event loop
    app.exec()

if __name__ == "__main__":
    run_integration_test()
