import os
import sys
import webbrowser
from datetime import date, datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFrame, QGraphicsDropShadowEffect, QApplication,
    QScrollArea
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QMouseEvent
from PyQt6.QtCore import Qt, QSize, QSettings, QPoint, QTimer, QThread, pyqtSignal

from app.api_client import LifeTrackerApiClient as MedTrackerClient
from app.widgets import SwitchButton
from app.styles import STYLESHEET

# Custom Title Bar for frameless window
class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(36)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 8, 0)
        self.layout.setSpacing(8)
        
        # Icon / Emoji Logo
        self.logo_label = QLabel("🩺")
        self.logo_label.setStyleSheet("font-size: 14px;")
        
        # Title text
        self.title_label = QLabel("MedTracker Client")
        self.title_label.setObjectName("TitleLabel")
        
        # Window buttons layout
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(4)
        
        # Minimize (Hide to Tray) button
        self.min_btn = QPushButton("−")
        self.min_btn.setObjectName("MinButton")
        self.min_btn.setToolTip("Minimize to system tray")
        self.min_btn.clicked.connect(self.parent().hide)
        
        # Close button
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
        
        # Drag window state
        self.drag_position = QPoint()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

# Background thread to execute API tasks cleanly
class ApiWorker(QThread):
    finished = pyqtSignal(bool, object)

    def __init__(self, action: str, client: MedTrackerClient, *args):
        super().__init__()
        self.action = action
        self.client = client
        self.args = args

    def run(self):
        try:
            method = getattr(self.client, self.action)
            res = method(*self.args)
            if res is not None and res is not False:
                self.finished.emit(True, res)
            else:
                self.finished.emit(False, res)
        except Exception:
            self.finished.emit(False, None)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize Settings and Client
        self.settings = QSettings("MedTracker", "TrayClient")
        server_url = self.settings.value("server_url", "http://127.0.0.1:8000")
        self.client = MedTrackerClient(server_url)
        
        self.is_connected = False
        self.active_workers = []
        
        # Window attributes
        self.setObjectName("CentralWidget")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setStyleSheet(STYLESHEET)
        
        # Size boundaries (now larger to accommodate checklist + meals)
        self.setFixedWidth(350)
        self.setMinimumHeight(520)
        self.setMaximumHeight(520)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 1, 1, 1)  # Outline border space
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
        self.set_indicator_color("#ef4444")  # Start red (offline)
        
        self.status_text = QLabel("Checking connection...")
        self.status_text.setObjectName("ConnectionStatusLabel")
        self.status_text.setStyleSheet("color: #94a3b8;")
        
        self.header_layout.addWidget(self.status_indicator)
        self.header_layout.addWidget(self.status_text)
        self.header_layout.addStretch()
        
        # Refresh Button
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setObjectName("SettingsToggleButton")
        self.refresh_btn.setToolTip("Refresh Checklist")
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
        
        url_label = QLabel("MEDTRACKER SERVER URL")
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
        
        # 4. Section: Daily Checklist
        checklist_header = QLabel("Daily Checklist")
        checklist_header.setObjectName("SectionHeaderLabel")
        self.content_layout.addWidget(checklist_header)

        self.card_frame = QFrame()
        self.card_frame.setObjectName("CardFrame")
        
        # Add drop shadow to Checklist Card
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 3)
        self.card_frame.setGraphicsEffect(shadow)
        
        self.card_layout = QVBoxLayout(self.card_frame)
        self.card_layout.setContentsMargins(14, 10, 14, 10)
        self.card_layout.setSpacing(8)
        
        # Build Checklist rows
        self.checklist_items = {
            "morning_meds": {"label": "Morning Meds", "desc": "💊 Fasting pills & vitamins"},
            "morning_inject": {"label": "Morning Inject", "desc": "💉 Morning injection log"},
            "evening_meds": {"label": "Evening Meds", "desc": "🌙 Nightly dosage"}
        }
        
        self.ui_rows = {}
        for key, info in self.checklist_items.items():
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 4, 0, 4)
            row_layout.setSpacing(10)
            
            # Left Text block
            text_block = QWidget()
            text_layout = QVBoxLayout(text_block)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(2)
            
            item_lbl = QLabel(info["label"])
            item_lbl.setObjectName("ItemLabel")
            
            time_lbl = QLabel(info["desc"])
            time_lbl.setObjectName("TimeLabel")
            
            text_layout.addWidget(item_lbl)
            text_layout.addWidget(time_lbl)
            row_layout.addWidget(text_block)
            row_layout.addStretch()
            
            # Custom Switch
            switch = SwitchButton()
            switch.setEnabled(False)  # Disabled until connected
            switch.clicked.connect(lambda checked, k=key: self.on_switch_toggled(k))
            row_layout.addWidget(switch)
            
            self.ui_rows[key] = {
                "label": item_lbl,
                "time": time_lbl,
                "switch": switch,
                "desc_template": info["desc"]
            }
            self.card_layout.addWidget(row_widget)
            
        self.content_layout.addWidget(self.card_frame)
        
        # 5. Section: Mealtime Injections
        meals_header = QLabel("Mealtime Injections")
        meals_header.setObjectName("SectionHeaderLabel")
        self.content_layout.addWidget(meals_header)
        
        self.meals_card = QFrame()
        self.meals_card.setObjectName("CardFrame")
        
        meals_shadow = QGraphicsDropShadowEffect(self)
        meals_shadow.setBlurRadius(12)
        meals_shadow.setColor(QColor(0, 0, 0, 50))
        meals_shadow.setOffset(0, 3)
        self.meals_card.setGraphicsEffect(meals_shadow)
        
        self.meals_card_layout = QVBoxLayout(self.meals_card)
        self.meals_card_layout.setContentsMargins(12, 10, 12, 10)
        self.meals_card_layout.setSpacing(8)
        
        # Quick log buttons layout
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(6)
        
        quick_tags = [
            ("Breakfast", "🍳 Breakfast"),
            ("Lunch", "🥗 Lunch"),
            ("Dinner", "🍲 Dinner"),
            ("Snack", "🍎 Snack")
        ]
        for tag, label in quick_tags:
            btn = QPushButton(label)
            btn.setObjectName("QuickLogButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=tag: self.log_meal_injection(t))
            quick_layout.addWidget(btn)
            
        self.meals_card_layout.addLayout(quick_layout)
        
        # Custom note layout
        custom_log_layout = QHBoxLayout()
        custom_log_layout.setSpacing(6)
        
        self.meal_input = QLineEdit()
        self.meal_input.setObjectName("MealInput")
        self.meal_input.setPlaceholderText("Enter custom meal note...")
        self.meal_input.returnPressed.connect(self.log_custom_meal)
        
        add_meal_btn = QPushButton("+")
        add_meal_btn.setObjectName("AddMealButton")
        add_meal_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_meal_btn.setToolTip("Log custom meal injection")
        add_meal_btn.clicked.connect(self.log_custom_meal)
        
        custom_log_layout.addWidget(self.meal_input)
        custom_log_layout.addWidget(add_meal_btn)
        self.meals_card_layout.addLayout(custom_log_layout)
        
        # Scrolling area for logged meal list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(105)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(0, 0, 4, 0)
        self.scroll_content_layout.setSpacing(6)
        
        self.scroll_area.setWidget(self.scroll_content)
        self.meals_card_layout.addWidget(self.scroll_area)
        
        self.content_layout.addWidget(self.meals_card)
        
        # 6. Dashboard Link Button
        self.dashboard_btn = QPushButton("Open Web Dashboard ↗")
        self.dashboard_btn.setObjectName("DashboardButton")
        self.dashboard_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dashboard_btn.clicked.connect(self.open_dashboard)
        self.content_layout.addWidget(self.dashboard_btn)
        
        self.main_layout.addWidget(self.content_widget)
        
        # Restore position
        self.restore_geometry()
        
        # Auto-update status every 10 seconds
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.refresh_data)
        self.poll_timer.start(10000)
        
        # Initial refresh
        self.refresh_data()

    def set_indicator_color(self, hex_color):
        self.status_indicator.setStyleSheet(f"background-color: {hex_color}; border-radius: 4px;")

    def moveEvent(self, event):
        super().moveEvent(event)
        self.settings.setValue("pos", self.pos())

    def restore_geometry(self):
        pos = self.settings.value("pos")
        if pos:
            screen_geom = QApplication.primaryScreen().geometry()
            pt = pos
            if screen_geom.contains(pt):
                self.move(pt)
                return
        
        # Center window
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def run_worker(self, worker):
        self.active_workers.append(worker)
        worker.finished.connect(lambda: self.active_workers.remove(worker))
        worker.start()

    # Refresh current checklist and meal logs
    def refresh_data(self):
        worker = ApiWorker("get_status", self.client, date.today().isoformat())
        worker.finished.connect(self.on_data_received)
        self.run_worker(worker)

    def on_data_received(self, success, data):
        self.is_connected = success
        if success and isinstance(data, dict):
            self.set_indicator_color("#10b981")  # Green
            self.status_text.setText("Connected to server")
            self.status_text.setStyleSheet("color: #10b981;")
            
            checklist_data = data.get("checklist", {})
            self.update_checklist_ui(checklist_data)
            
            meal_injections = data.get("meal_injections", [])
            self.update_meals_ui(meal_injections)
        else:
            self.set_indicator_color("#ef4444")  # Red
            self.status_text.setText("Server offline")
            self.status_text.setStyleSheet("color: #ef4444;")
            
            # Disable switches if offline
            for row in self.ui_rows.values():
                row["switch"].setEnabled(False)
            
            self.clear_layout(self.scroll_content_layout)
            empty_lbl = QLabel("Check server connection")
            empty_lbl.setStyleSheet("color: #ef4444; font-size: 11px;")
            self.scroll_content_layout.addWidget(empty_lbl)

    def update_checklist_ui(self, checklist_data):
        for key, row in self.ui_rows.items():
            taken = checklist_data.get(key, False) if checklist_data else False
            taken_at = checklist_data.get(f"{key}_taken_at") if checklist_data else None
            
            row["switch"].blockSignals(True)
            row["switch"].setChecked(taken)
            row["switch"].setEnabled(True)
            row["switch"].blockSignals(False)
            
            if taken and taken_at:
                time_str = parse_to_local_time_str(taken_at)
                if time_str:
                    row["time"].setText(f"✓ Taken at {time_str}")
                    row["time"].setStyleSheet("color: #10b981; font-weight: 500;")
                else:
                    row["time"].setText("✓ Completed")
                    row["time"].setStyleSheet("color: #10b981; font-weight: 500;")
            else:
                row["time"].setText(row["desc_template"])
                row["time"].setStyleSheet("color: #94a3b8;")

    def update_meals_ui(self, meal_injections):
        self.clear_layout(self.scroll_content_layout)
        
        if not meal_injections:
            empty_lbl = QLabel("No injections logged today")
            empty_lbl.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic; padding: 4px;")
            self.scroll_content_layout.addWidget(empty_lbl)
            self.scroll_content_layout.addStretch()
            return
            
        for meal in meal_injections:
            row_frame = QFrame()
            row_frame.setObjectName("MealItemRow")
            
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(8, 6, 8, 6)
            row_layout.setSpacing(6)
            
            # Syringe symbol
            icon_lbl = QLabel("💉")
            icon_lbl.setStyleSheet("font-size: 11px;")
            
            note_txt = meal.get("note") or "Injection"
            note_lbl = QLabel(note_txt)
            note_lbl.setObjectName("MealNoteLabel")
            
            time_str = ""
            ts = meal.get("timestamp")
            if ts:
                time_str = parse_to_local_time_str(ts)
            time_lbl = QLabel(time_str)
            time_lbl.setObjectName("MealTimeLabel")
            
            delete_btn = QPushButton("×")
            delete_btn.setObjectName("DeleteMealButton")
            delete_btn.setToolTip("Delete Log")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Wire up delete functionality
            meal_id = meal.get("id")
            delete_btn.clicked.connect(lambda checked, m_id=meal_id: self.delete_meal_injection(m_id))
            
            row_layout.addWidget(icon_lbl)
            row_layout.addWidget(note_lbl)
            row_layout.addStretch()
            row_layout.addWidget(time_lbl)
            row_layout.addWidget(delete_btn)
            
            self.scroll_content_layout.addWidget(row_frame)
            
        self.scroll_content_layout.addStretch()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # Checklist switch toggling
    def on_switch_toggled(self, key):
        row = self.ui_rows[key]
        row["switch"].setEnabled(False)
        
        worker = ApiWorker("toggle_item", self.client, date.today().isoformat(), key)
        worker.finished.connect(lambda success, data, k=key: self.on_toggle_finished(success, data, k))
        self.run_worker(worker)

    def on_toggle_finished(self, success, data, key):
        row = self.ui_rows[key]
        row["switch"].setEnabled(True)
        if success:
            self.update_checklist_ui(data)
        else:
            self.refresh_data()

    # Log Meal Injection
    def log_meal_injection(self, note):
        if not self.is_connected:
            return
        worker = ApiWorker("add_meal_injection", self.client, date.today().isoformat(), note)
        worker.finished.connect(self.on_meal_logged)
        self.run_worker(worker)

    def log_custom_meal(self):
        note = self.meal_input.text().strip()
        if not note or not self.is_connected:
            return
        self.meal_input.clear()
        self.log_meal_injection(note)

    def on_meal_logged(self, success, data):
        if success:
            self.refresh_data()

    # Delete Meal Injection
    def delete_meal_injection(self, meal_id):
        if not self.is_connected or meal_id is None:
            return
        worker = ApiWorker("delete_meal_injection", self.client, meal_id)
        worker.finished.connect(self.on_meal_deleted)
        self.run_worker(worker)

    def on_meal_deleted(self, success, data):
        if success:
            self.refresh_data()

    # Settings toggle
    def toggle_settings(self):
        visible = self.settings_frame.isVisible()
        self.settings_frame.setVisible(not visible)
        
        target_height = 605 if not visible else 520
        self.setMinimumHeight(target_height)
        self.setMaximumHeight(target_height)

    def save_settings(self):
        new_url = self.url_input.text().strip()
        if new_url:
            self.settings.setValue("server_url", new_url)
            self.client.base_url = new_url.rstrip('/')
            self.toggle_settings()
            self.status_text.setText("Connecting...")
            self.status_text.setStyleSheet("color: #94a3b8;")
            self.refresh_data()

    def open_dashboard(self):
        webbrowser.open(self.client.base_url + "/")

    def toggle_window(self):
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

# Programmatic high-res tray icon
def create_tray_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw background pill/shield
    painter.setBrush(QBrush(QColor("#a855f7")))  # Purple Accent
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 16, 16)
    
    # Draw checkmark path
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#ffffff")))
    
    from PyQt6.QtGui import QPainterPath
    path = QPainterPath()
    path.moveTo(18, 30)
    path.lineTo(28, 41)
    path.lineTo(47, 20)
    path.lineTo(43, 16)
    path.lineTo(28, 33)
    path.lineTo(22, 26)
    path.closeSubpath()
    painter.drawPath(path)
    
    painter.end()
    return QIcon(pixmap)

# Converts timezone-aware ISO-8601 datetime strings to local timezone and formats them
def parse_to_local_time_str(ts_str: str) -> str:
    if not ts_str:
        return ""
    try:
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is not None:
            # Timezone-aware: convert to system local timezone
            dt = dt.astimezone()
        return dt.strftime("%I:%M %p").lstrip('0')
    except Exception:
        # Fallback to naive parsing if fromisoformat fails on offset formatting
        try:
            clean_ts = ts_str.split(".")[0]
            dt = datetime.fromisoformat(clean_ts)
            return dt.strftime("%I:%M %p").lstrip('0')
        except Exception:
            return ""
