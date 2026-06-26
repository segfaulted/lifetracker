import os
import sys
import webbrowser
from datetime import datetime, timedelta, timezone

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFrame, QGraphicsDropShadowEffect, QComboBox,
    QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QMouseEvent, QPen
from PyQt6.QtCore import Qt, QSize, QSettings, QPoint, QTimer, QThread, pyqtSignal, QUrl
from PyQt6.QtWebSockets import QWebSocket

from app.api_client import LifeTrackerApiClient
from app.widgets import SwitchButton
from app.styles import STYLESHEET

def format_duration(total_seconds: int) -> str:
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Custom Title Bar for frameless window
class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(36)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 8, 0)
        self.layout.setSpacing(8)
        
        # Logo/Icon
        self.logo_label = QLabel("⏱️")
        self.logo_label.setStyleSheet("font-size: 14px;")
        
        # Title text
        self.title_label = QLabel("Life Tracker Client")
        self.title_label.setObjectName("TitleLabel")
        
        # Window buttons
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(4)
        
        self.min_btn = QPushButton("−")
        self.min_btn.setObjectName("MinButton")
        self.min_btn.setToolTip("Minimize to system tray")
        self.min_btn.clicked.connect(self.parent().hide)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setToolTip("Close application")
        self.close_btn.clicked.connect(self.parent().hide)
        
        self.buttons_layout.addWidget(self.min_btn)
        self.buttons_layout.addWidget(self.close_btn)
        
        self.layout.addWidget(self.logo_label)
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addLayout(self.buttons_layout)
        
        self.drag_position = QPoint()
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            if window and window.windowHandle():
                window.windowHandle().startSystemMove()
            else:
                self.drag_position = event.globalPosition().toPoint() - self.parent().pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        window = self.window()
        if not (window and window.windowHandle()):
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.parent().move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()

# Background thread to execute API tasks cleanly
class ApiWorker(QThread):
    finished = pyqtSignal(bool, str, object)

    def __init__(self, action: str, client: LifeTrackerApiClient, *args):
        super().__init__()
        self.action = action
        self.client = client
        self.args = args

    def run(self):
        try:
            method = getattr(self.client, self.action)
            res = method(*self.args)
            if res is not None and res is not False:
                self.finished.emit(True, self.action, res)
            elif self.action == "get_active_timer" and res is None:
                self.finished.emit(True, self.action, None)
            else:
                self.finished.emit(False, self.action, res)
        except Exception as e:
            self.finished.emit(False, self.action, str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize Settings and Client
        self.settings = QSettings("LifeTracker", "TrayClient")
        server_url = self.settings.value("server_url", "http://127.0.0.1:8000")
        self.client = LifeTrackerApiClient(server_url)
        
        self.is_connected = False
        self.projects_list = []
        self.active_project_id = None
        self.active_workers = []
        
        # Timer tracking state
        self.is_tracking = False
        self.is_timer_running = False
        self.elapsed_seconds = 0
        self.tracking_start_time = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_tick)
        
        # Window attributes
        self.setObjectName("CentralWidget")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setStyleSheet(STYLESHEET)
        
        self.setFixedWidth(350)
        self.setMinimumHeight(540)
        self.setMaximumHeight(540)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 1, 1, 1)
        self.main_layout.setSpacing(0)
        
        # 1. Custom Title Bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # 2. Content area
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("ContentArea")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 12, 16, 16)
        self.content_layout.setSpacing(10)
        
        # Sub-header: Connection & Refresh / Settings actions
        self.header_layout = QHBoxLayout()
        
        # Indicator Dot & Status Text
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(8, 8)
        self.set_indicator_color("#ef4444")  # Start red
        
        self.status_text = QLabel("Checking connection...")
        self.status_text.setObjectName("ConnectionStatusLabel")
        self.status_text.setStyleSheet("color: #71717a;")
        
        self.header_layout.addWidget(self.status_indicator)
        self.header_layout.addWidget(self.status_text)
        self.header_layout.addStretch()
        
        # Refresh Button
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setObjectName("SettingsToggleButton")
        self.refresh_btn.setToolTip("Refresh Data")
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.header_layout.addWidget(self.refresh_btn)
        
        # Settings Toggle Button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setObjectName("SettingsToggleButton")
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self.toggle_settings)
        self.header_layout.addWidget(self.settings_btn)
        
        self.content_layout.addLayout(self.header_layout)
        
        # 3. Settings Drawer (Collapsible)
        self.settings_frame = QFrame()
        self.settings_frame.setObjectName("SettingsFrame")
        self.settings_frame.setVisible(False)
        
        settings_layout = QVBoxLayout(self.settings_frame)
        settings_layout.setContentsMargins(12, 12, 12, 12)
        settings_layout.setSpacing(8)
        
        url_label = QLabel("LIFETRACKER SERVER URL")
        url_label.setObjectName("SettingsLabel")
        
        self.url_input = QLineEdit()
        self.url_input.setObjectName("UrlInput")
        self.url_input.setText(server_url)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("SettingsSaveButton")
        save_btn.clicked.connect(self.save_settings)
        
        settings_layout.addWidget(url_label)
        settings_layout.addWidget(self.url_input)
        settings_layout.addWidget(save_btn)
        
        self.content_layout.addWidget(self.settings_frame)

        # 4. Project Selector Dropdown
        self.project_dropdown = QComboBox()
        self.project_dropdown.addItem("Select Project...")
        self.project_dropdown.currentIndexChanged.connect(self.on_project_changed)
        self.content_layout.addWidget(self.project_dropdown)
        
        # 5. Section: Time Tracker
        self.timer_frame = QFrame()
        self.timer_frame.setObjectName("CardFrame")
        
        shadow1 = QGraphicsDropShadowEffect(self)
        shadow1.setBlurRadius(10)
        shadow1.setColor(QColor(0, 0, 0, 40))
        shadow1.setOffset(0, 2)
        self.timer_frame.setGraphicsEffect(shadow1)
        
        self.timer_layout = QVBoxLayout(self.timer_frame)
        self.timer_layout.setContentsMargins(14, 12, 14, 12)
        self.timer_layout.setSpacing(8)
        
        # Large Clock Label
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setObjectName("TimerLabel")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_layout.addWidget(self.clock_label)
        
        # Controls Row
        self.timer_controls_widget = QWidget()
        self.timer_controls_layout = QHBoxLayout(self.timer_controls_widget)
        self.timer_controls_layout.setContentsMargins(0, 0, 0, 0)
        self.timer_controls_layout.setSpacing(8)
        
        self.start_btn = QPushButton("Start Tracking")
        self.start_btn.setObjectName("TimerStartButton")
        self.start_btn.clicked.connect(self.start_timer)
        self.timer_controls_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setObjectName("TimerPauseButton")
        self.pause_btn.setVisible(False)
        self.pause_btn.clicked.connect(self.pause_timer)
        self.timer_controls_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("TimerStopButton")
        self.stop_btn.setVisible(False)
        self.stop_btn.clicked.connect(self.stop_timer)
        self.timer_controls_layout.addWidget(self.stop_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("TimerCancelButton")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_timer)
        self.timer_controls_layout.addWidget(self.cancel_btn)
        
        self.timer_layout.addWidget(self.timer_controls_widget)
        
        # Save Time Log Form (Hidden by default)
        self.save_log_widget = QWidget()
        self.save_log_layout = QVBoxLayout(self.save_log_widget)
        self.save_log_layout.setContentsMargins(0, 0, 0, 0)
        self.save_log_layout.setSpacing(6)
        
        self.save_log_desc = QLineEdit()
        self.save_log_desc.setObjectName("Input")
        self.save_log_desc.setPlaceholderText("Enter what you accomplished...")
        self.save_log_layout.addWidget(self.save_log_desc)
        
        save_log_btns_layout = QHBoxLayout()
        save_log_btns_layout.setSpacing(6)
        
        self.confirm_save_btn = QPushButton("Save Log")
        self.confirm_save_btn.setObjectName("ActionButton")
        self.confirm_save_btn.clicked.connect(self.submit_time_log)
        
        self.discard_save_btn = QPushButton("Discard")
        self.discard_save_btn.setObjectName("TimerCancelButton")
        self.discard_save_btn.clicked.connect(self.discard_time_log)
        
        save_log_btns_layout.addWidget(self.discard_save_btn)
        save_log_btns_layout.addWidget(self.confirm_save_btn)
        
        self.save_log_layout.addLayout(save_log_btns_layout)
        self.save_log_widget.setVisible(False)
        self.timer_layout.addWidget(self.save_log_widget)
        
        self.content_layout.addWidget(self.timer_frame)
        
        # 6. Section: Tasks Checklist
        self.checklist_frame = QFrame()
        self.checklist_frame.setObjectName("CardFrame")
        
        shadow2 = QGraphicsDropShadowEffect(self)
        shadow2.setBlurRadius(10)
        shadow2.setColor(QColor(0, 0, 0, 40))
        shadow2.setOffset(0, 2)
        self.checklist_frame.setGraphicsEffect(shadow2)
        
        self.checklist_layout = QVBoxLayout(self.checklist_frame)
        self.checklist_layout.setContentsMargins(14, 10, 14, 10)
        self.checklist_layout.setSpacing(8)
        
        # Scroll Area for Task List
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 4px; background: transparent; } QScrollBar::handle:vertical { background: #272730; border-radius: 2px; }")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_content_layout.setSpacing(6)
        self.scroll_content_layout.addStretch() # Push everything to top
        self.scroll_area.setWidget(self.scroll_content)
        
        self.checklist_layout.addWidget(self.scroll_area)
        
        # Quick Task Creation Form (at the bottom of checklist card)
        self.add_task_widget = QWidget()
        self.add_task_layout = QHBoxLayout(self.add_task_widget)
        self.add_task_layout.setContentsMargins(0, 4, 0, 0)
        self.add_task_layout.setSpacing(6)
        
        self.task_input = QLineEdit()
        self.task_input.setObjectName("Input")
        self.task_input.setPlaceholderText("Add a new task...")
        self.task_input.returnPressed.connect(self.create_new_task)
        
        self.add_task_btn = QPushButton("Add")
        self.add_task_btn.setObjectName("ActionButton")
        self.add_task_btn.clicked.connect(self.create_new_task)
        
        self.add_task_layout.addWidget(self.task_input)
        self.add_task_layout.addWidget(self.add_task_btn)
        self.checklist_layout.addWidget(self.add_task_widget)
        
        self.content_layout.addWidget(self.checklist_frame)
        
        # 7. Action: Dashboard Button
        self.dashboard_btn = QPushButton("🔗 Open Web Dashboard")
        self.dashboard_btn.setObjectName("DashboardButton")
        self.dashboard_btn.clicked.connect(self.open_dashboard)
        self.content_layout.addWidget(self.dashboard_btn)
        
        self.main_layout.addWidget(self.content_widget)
        
        # Load Window geometry (restore previous dragged position)
        self.restore_geometry()
        
        # Initial Connectivity check & database load
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.check_connection_background)
        self.refresh_timer.start(5000) # Every 5 seconds
        
        self.check_connection_background()
        
        # Real-time WebSocket Live Sync Setup
        self.websocket = QWebSocket()
        self.websocket.textMessageReceived.connect(self.on_websocket_message)
        self.websocket.disconnected.connect(self.on_websocket_disconnected)
        self.connect_websocket()

    def set_indicator_color(self, color_hex):
        self.status_indicator.setStyleSheet(
            f"background-color: {color_hex}; border-radius: 4px;"
        )

    def set_ui_enabled(self, enabled: bool):
        self.project_dropdown.setEnabled(enabled)
        self.task_input.setEnabled(enabled)
        self.add_task_btn.setEnabled(enabled)
        self.start_btn.setEnabled(enabled and self.active_project_id is not None)
        # Enable switches if active
        for i in range(self.scroll_content_layout.count()):
            widget = self.scroll_content_layout.itemAt(i).widget()
            if widget and widget.objectName() == "TaskRow":
                switch = widget.findChild(SwitchButton)
                if switch:
                    switch.setEnabled(enabled)
                del_btn = widget.findChild(QPushButton, "DeleteTaskButton")
                if del_btn:
                    del_btn.setEnabled(enabled)

    # Window Actions
    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            self.refresh_data()

    def open_dashboard(self):
        webbrowser.open(self.client.base_url.replace('/api', '') or "http://localhost:5173")

    def toggle_settings(self):
        self.settings_frame.setVisible(not self.settings_frame.isVisible())

    def save_settings(self):
        url = self.url_input.text().strip()
        if url:
            self.settings.setValue("server_url", url)
            self.client.base_url = url.rstrip('/')
            self.toggle_settings()
            
            # Reconnect WebSocket
            self.websocket.close()
            self.connect_websocket()
            
            self.refresh_data()

    def restore_geometry(self):
        pos = self.settings.value("window_pos", QPoint(200, 200))
        # Ensure position is inside screen bounds (basic validation)
        self.move(pos)

    def closeEvent(self, event):
        # Save position on close
        self.settings.setValue("window_pos", self.pos())
        super().closeEvent(event)

    def hideEvent(self, event):
        # Save position on hide (tray resident workflow)
        self.settings.setValue("window_pos", self.pos())
        super().hideEvent(event)

    # WebSocket connection management
    def connect_websocket(self):
        base_url = self.client.base_url
        if base_url.startswith("https://"):
            ws_url = base_url.replace("https://", "wss://") + "/api/ws"
        elif base_url.startswith("http://"):
            ws_url = base_url.replace("http://", "ws://") + "/api/ws"
        else:
            ws_url = "ws://localhost:8000/api/ws"
            
        print(f"[WebSocket] Connecting to {ws_url}...")
        self.websocket.open(QUrl(ws_url))

    def on_websocket_message(self, message):
        if message == "refresh":
            print("[WebSocket] LiveSync: Refresh signal received from server")
            self.refresh_data()

    def on_websocket_disconnected(self):
        # Retry connection after 3 seconds
        QTimer.singleShot(3000, self.connect_websocket)

    # API Workers Manager
    def start_worker(self, action: str, *args):
        worker = ApiWorker(action, self.client, *args)
        worker.finished.connect(self.on_worker_finished)
        self.active_workers.append(worker)
        worker.start()

    def on_worker_finished(self, success: bool, action: str, result):
        # Clean up finished workers
        self.active_workers = [w for w in self.active_workers if not w.isFinished()]
        
        if not success:
            print(f"[API Error] Action '{action}' failed: {result}")
            if action == "check_connection":
                self.is_connected = False
                self.set_indicator_color("#ef4444")
                self.status_text.setText("Connection Lost")
                self.set_ui_enabled(False)
            return

        if action == "check_connection":
            if not self.is_connected: # Transition to online
                self.is_connected = True
                self.set_indicator_color("#10b981")
                self.status_text.setText("Connected")
                self.load_projects()
        
        elif action == "get_projects":
            self.projects_list = result
            # Populate dropdown
            current_project_id = self.active_project_id
            
            self.project_dropdown.blockSignals(True)
            self.project_dropdown.clear()
            self.project_dropdown.addItem("Select Project...")
            
            select_idx = 0
            for idx, p in enumerate(self.projects_list):
                self.project_dropdown.addItem(p["name"], p["id"])
                if p["id"] == current_project_id:
                    select_idx = idx + 1 # offset due to "Select Project..."
            
            self.project_dropdown.setCurrentIndex(select_idx)
            self.project_dropdown.blockSignals(False)
            
            # If no project selected but we have projects, auto-select first
            if current_project_id is None and len(self.projects_list) > 0:
                self.project_dropdown.setCurrentIndex(1)
            elif current_project_id is not None:
                self.load_tasks(current_project_id)
                
            self.set_ui_enabled(True)

        elif action == "get_tasks":
            self.populate_tasks(result)

        elif action == "create_task":
            self.task_input.clear()
            if self.active_project_id:
                self.load_tasks(self.active_project_id)

        elif action == "update_task":
            # Refresh checklist to make sure we reflect DB state
            if self.active_project_id:
                self.load_tasks(self.active_project_id)

        elif action == "delete_task":
            if self.active_project_id:
                self.load_tasks(self.active_project_id)

        elif action == "start_active_timer":
            self.timer_controls_widget.setVisible(True)
            self.save_log_widget.setVisible(False)
            
            if result:
                try:
                    start_str = result["start_time"].replace('Z', '+00:00')
                    start_dt = datetime.fromisoformat(start_str)
                    server_str = result["server_time"].replace('Z', '+00:00')
                    server_dt = datetime.fromisoformat(server_str)
                    
                    if result.get("is_paused", False):
                        elapsed = result.get("accumulated_seconds", 0)
                    else:
                        elapsed = result.get("accumulated_seconds", 0) + int((server_dt - start_dt).total_seconds())
                except Exception as e:
                    print(f"[Timer] Error parsing start_active_timer result: {e}")
                    elapsed = 0
                self.elapsed_seconds = elapsed if elapsed >= 0 else 0
            else:
                self.elapsed_seconds = 0

            self.clock_label.setText(format_duration(self.elapsed_seconds))
            self.is_tracking = True
            
            is_paused = result.get("is_paused", False) if result else False
            if not is_paused:
                self.is_timer_running = True
                self.timer.start(1000)
                self.start_btn.setVisible(False)
                self.pause_btn.setVisible(True)
            else:
                self.is_timer_running = False
                self.timer.stop()
                self.start_btn.setText("Resume Tracking")
                self.start_btn.setVisible(True)
                self.pause_btn.setVisible(False)
                
            self.stop_btn.setVisible(True)
            self.cancel_btn.setVisible(True)

        elif action == "pause_active_timer":
            print("[Timer] Active timer pause completed.")
            self.is_timer_running = False
            self.timer.stop()
            self.start_btn.setText("Resume Tracking")
            self.start_btn.setVisible(True)
            self.pause_btn.setVisible(False)
            self.stop_btn.setVisible(True)
            self.cancel_btn.setVisible(True)

        elif action in ("stop_active_timer", "discard_active_timer"):
            print("[Timer] Active timer stop/discard completed.")
            self.save_log_widget.setVisible(False)
            self.timer_controls_widget.setVisible(True)
            self.clock_label.setText("00:00:00")
            self.elapsed_seconds = 0
            self.is_tracking = False
            self.is_timer_running = False
            self.timer.stop()
            
            # Reset buttons
            self.start_btn.setText("Start Tracking")
            self.start_btn.setVisible(True)
            self.pause_btn.setVisible(False)
            self.stop_btn.setVisible(False)
            self.cancel_btn.setVisible(False)
            self.start_btn.setEnabled(True)
            
            if self.active_project_id:
                self.load_tasks(self.active_project_id)

        elif action == "get_active_timer":
            if result:  # A timer is running on the server
                project_id = result["project_id"]
                try:
                    start_str = result["start_time"].replace('Z', '+00:00')
                    start_dt = datetime.fromisoformat(start_str)
                    
                    server_str = result["server_time"].replace('Z', '+00:00')
                    server_dt = datetime.fromisoformat(server_str)
                    
                    if result.get("is_paused", False):
                        elapsed = result.get("accumulated_seconds", 0)
                    else:
                        elapsed = result.get("accumulated_seconds", 0) + int((server_dt - start_dt).total_seconds())
                except Exception as e:
                    print(f"[Timer] Error parsing datetime: {e}")
                    elapsed = 0
                
                self.elapsed_seconds = elapsed if elapsed >= 0 else 0
                self.clock_label.setText(format_duration(self.elapsed_seconds))
                
                self.is_tracking = True
                is_paused = result.get("is_paused", False)
                if not is_paused:
                    if not self.is_timer_running:
                        self.is_timer_running = True
                        self.timer.start(1000)
                    self.start_btn.setVisible(False)
                    self.pause_btn.setVisible(True)
                else:
                    if self.is_timer_running:
                        self.is_timer_running = False
                        self.timer.stop()
                    self.start_btn.setText("Resume Tracking")
                    self.start_btn.setVisible(True)
                    self.pause_btn.setVisible(False)
                    
                self.stop_btn.setVisible(True)
                self.cancel_btn.setVisible(True)
                
                # Sync project selector dropdown
                if self.active_project_id != project_id:
                    for i in range(1, self.project_dropdown.count()):
                        if self.project_dropdown.itemData(i) == project_id:
                            self.project_dropdown.blockSignals(True)
                            self.project_dropdown.setCurrentIndex(i)
                            self.active_project_id = project_id
                            self.project_dropdown.blockSignals(False)
                            self.load_tasks(project_id)
                            break
            else:  # No timer is running on server
                if self.is_tracking:
                    self.is_tracking = False
                    self.is_timer_running = False
                    self.timer.stop()
                    self.elapsed_seconds = 0
                    self.clock_label.setText("00:00:00")
                    
                    self.start_btn.setText("Start Tracking")
                    self.start_btn.setVisible(True)
                    self.pause_btn.setVisible(False)
                    self.stop_btn.setVisible(False)
                    self.cancel_btn.setVisible(False)
                    self.start_btn.setEnabled(True)
                    
                    if self.active_project_id:
                        self.load_tasks(self.active_project_id)

    # Timer Tick Event
    def on_timer_tick(self):
        self.elapsed_seconds += 1
        self.clock_label.setText(format_duration(self.elapsed_seconds))

    # Timer Action Handlers
    def start_timer(self):
        if self.active_project_id is None:
            return
        self.save_log_desc.clear()
        self.start_worker("start_active_timer", self.active_project_id)

    def pause_timer(self):
        self.start_worker("pause_active_timer")

    def stop_timer(self):
        self.pause_timer()
        self.timer_controls_widget.setVisible(False)
        self.save_log_widget.setVisible(True)
        self.save_log_desc.setFocus()

    def cancel_timer(self):
        if confirm_dialog(self, "Discard tracked time?", "Are you sure you want to discard this tracked time?"):
            self.save_log_desc.clear()
            self.start_worker("discard_active_timer")

    def submit_time_log(self):
        desc = self.save_log_desc.text().strip()
        if not desc:
            return
        self.save_log_desc.clear()
        self.start_worker("stop_active_timer", desc)

    def discard_time_log(self):
        self.save_log_desc.clear()
        self.start_worker("discard_active_timer")

    # API Trigger Handlers
    def check_connection_background(self):
        self.start_worker("check_connection")
        if self.is_connected:
            self.start_worker("get_active_timer")

    def load_projects(self):
        self.start_worker("get_projects")

    def load_tasks(self, project_id: int):
        self.start_worker("get_tasks", project_id)

    def refresh_data(self):
        self.check_connection_background()
        if self.is_connected:
            self.load_projects()

    def on_project_changed(self, index):
        if index <= 0:
            self.active_project_id = None
            self.clear_tasks_layout()
            self.scroll_content_layout.addStretch()
            self.start_btn.setEnabled(False)
            return
        
        proj_id = self.project_dropdown.currentData()
        self.active_project_id = proj_id
        
        # Enable tracking button if project is selected
        self.start_btn.setEnabled(True)
        
        # Load tasks
        self.load_tasks(proj_id)

    def create_new_task(self):
        if self.active_project_id is None:
            return
        title = self.task_input.text().strip()
        if not title:
            return
        self.start_worker("create_task", self.active_project_id, title)

    def on_task_toggled(self, task_id: int, checked: bool):
        self.start_worker("update_task", task_id, {"is_completed": checked})

    def delete_task_click(self, task_id: int, title: str):
        if confirm_dialog(self, "Delete Task", f"Are you sure you want to delete task '{title}'?"):
            self.start_worker("delete_task", task_id)

    # Layout Helpers
    def clear_tasks_layout(self):
        # Remove items from task scroll layout
        while self.scroll_content_layout.count():
            item = self.scroll_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def populate_tasks(self, tasks):
        self.clear_tasks_layout()
        
        if not tasks:
            no_tasks_lbl = QLabel("No tasks listed. Add one below!")
            no_tasks_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_tasks_lbl.setStyleSheet("color: #71717a; font-size: 11px; padding: 20px;")
            self.scroll_content_layout.addWidget(no_tasks_lbl)
            self.scroll_content_layout.addStretch()
            return
            
        # Sort tasks (uncompleted first, then by priority High -> Medium -> Low)
        sorted_tasks = sorted(tasks, key=lambda t: (
            t["is_completed"],
            0 if t["priority"] == "High" else 1 if t["priority"] == "Medium" else 2,
            t["id"]
        ))
        
        for task in sorted_tasks:
            task_row = QFrame()
            task_row.setObjectName("TaskRow")
            task_row.setMinimumHeight(48)
            
            row_layout = QHBoxLayout(task_row)
            row_layout.setContentsMargins(10, 4, 8, 4)
            row_layout.setSpacing(8)
            
            # Left Text block
            text_block = QWidget()
            text_block.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            text_layout = QVBoxLayout(text_block)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(2)
            
            item_lbl = QLabel(task["title"])
            item_lbl.setObjectName("ItemLabelCompleted" if task["is_completed"] else "ItemLabel")
            item_lbl.setWordWrap(True)
            
            # Sub row with priority
            sub_row = QWidget()
            sub_layout = QHBoxLayout(sub_row)
            sub_layout.setContentsMargins(0, 0, 0, 0)
            sub_layout.setSpacing(6)
            
            priority_tag = QLabel(task["priority"])
            priority_tag.setObjectName("PriorityTag")
            if task["priority"] == "High":
                priority_tag.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #f87171;")
            elif task["priority"] == "Medium":
                priority_tag.setStyleSheet("background-color: rgba(245, 158, 11, 0.15); color: #fbbf24;")
            else:
                priority_tag.setStyleSheet("background-color: rgba(59, 130, 246, 0.15); color: #60a5fa;")
            
            sub_layout.addWidget(priority_tag)
            
            if task["due_date"]:
                # Parse and show due date
                due_dt = datetime.strptime(task["due_date"], "%Y-%m-%d")
                due_str = due_dt.strftime("%b %d")
                due_lbl = QLabel(f"📅 {due_str}")
                due_lbl.setStyleSheet("color: #71717a; font-size: 9px;")
                sub_layout.addWidget(due_lbl)
            
            sub_layout.addStretch()
            
            text_layout.addWidget(item_lbl)
            text_layout.addWidget(sub_row)
            
            row_layout.addWidget(text_block)
            
            # Toggle Switch Checkbox
            switch = SwitchButton()
            switch.setEnabled(self.is_connected)
            switch.setChecked(task["is_completed"])
            
            # Hook toggled signal
            switch.toggled.connect(
                lambda checked, tid=task["id"]: self.on_task_toggled(tid, checked)
            )
            row_layout.addWidget(switch)
            
            # Delete button (visible on hover would be ideal, but standard button is fine for desktop client)
            del_btn = QPushButton("🗑️")
            del_btn.setObjectName("DeleteTaskButton")
            del_btn.setToolTip("Delete Task")
            del_btn.clicked.connect(
                lambda checked, tid=task["id"], title=task["title"]: self.delete_task_click(tid, title)
            )
            row_layout.addWidget(del_btn)
            
            self.scroll_content_layout.addWidget(task_row)
            
        self.scroll_content_layout.addStretch()


# Standard utility dialog helpers
def confirm_dialog(parent, title, message):
    from PyQt6.QtWidgets import QMessageBox
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    box.setDefaultButton(QMessageBox.StandardButton.No)
    
    # Custom dark palette style sheet for dialog message box
    box.setStyleSheet("""
        QMessageBox { background-color: #09090b; color: #f4f4f5; font-family: "Inter", sans-serif; }
        QLabel { color: #f4f4f5; font-size: 12px; }
        QPushButton { background-color: #272730; color: #f4f4f5; border: none; border-radius: 6px; padding: 6px 14px; font-weight: bold; min-width: 70px; }
        QPushButton:hover { background-color: #3f3f46; }
    """)
    
    return box.exec() == QMessageBox.StandardButton.Yes

# Programmatic high-res tray icon (Clock Face)
def create_tray_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw background pill/rounded rect
    painter.setBrush(QBrush(QColor("#6366f1")))  # Indigo Accent
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 16, 16)
    
    # Draw clock face circle
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(QColor("#ffffff"), 4))
    painter.drawEllipse(16, 16, 32, 32)
    
    # Draw hands
    painter.setPen(QPen(QColor("#ffffff"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    painter.drawLine(32, 32, 32, 22) # Center to top hand
    painter.drawLine(32, 32, 40, 32) # Center to right hand
    
    painter.end()
    return QIcon(pixmap)

