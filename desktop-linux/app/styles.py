# Sleek Dark Modern QSS stylesheet for Life Tracker Client

STYLESHEET = """
/* Main Window */
QWidget#CentralWidget {
    background-color: #09090b;
    border: 1px solid #1f1f23;
    border-radius: 16px;
}

/* Custom Title Bar */
QWidget#TitleBar {
    background-color: #121217;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
    border-bottom: 1px solid #1c1c24;
}

QLabel#TitleLabel {
    color: #f4f4f5;
    font-size: 13px;
    font-weight: bold;
    font-family: "Inter", "Segoe UI", "Ubuntu", sans-serif;
}

QPushButton#CloseButton {
    background-color: transparent;
    color: #71717a;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
}

QPushButton#CloseButton:hover {
    background-color: #ef4444;
    color: white;
}

QPushButton#MinButton {
    background-color: transparent;
    color: #71717a;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
}

QPushButton#MinButton:hover {
    background-color: #272730;
    color: white;
}

/* Main Content Area */
QWidget#ContentArea {
    background-color: transparent;
}

/* Container Cards */
QFrame#CardFrame {
    background-color: #121217;
    border: 1px solid #1f1f2a;
    border-radius: 12px;
}

/* Header Connection Status */
QLabel#ConnectionStatusLabel {
    font-size: 11px;
    font-weight: 500;
    font-family: "Inter", "Segoe UI", sans-serif;
}

/* Project Selector Dropdown */
QComboBox {
    background-color: #121217;
    border: 1px solid #1f1f2a;
    border-radius: 8px;
    color: #f4f4f5;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    font-family: "Inter", "Segoe UI", sans-serif;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #6366f1;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #121217;
    border: 1px solid #1f1f2a;
    border-radius: 8px;
    color: #f4f4f5;
    selection-background-color: #6366f1;
    selection-color: white;
    outline: none;
    padding: 4px;
}

/* Checklist Labels */
QLabel#ItemLabel {
    color: #f4f4f5;
    font-size: 12px;
    font-weight: 500;
    font-family: "Inter", "Segoe UI", sans-serif;
}

QLabel#ItemLabelCompleted {
    color: #71717a;
    font-size: 12px;
    font-weight: 500;
    font-family: "Inter", "Segoe UI", sans-serif;
    text-decoration: line-through;
}

QLabel#PriorityTag {
    font-size: 8px;
    font-weight: bold;
    border-radius: 3px;
    padding: 2px 4px;
    text-transform: uppercase;
}

/* Timer styles */
QLabel#TimerLabel {
    font-family: "Cascadia Code", "Courier New", monospace;
    font-size: 32px;
    font-weight: bold;
    color: #f4f4f5;
}

/* Control Buttons */
QPushButton#TimerStartButton {
    background-color: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#TimerStartButton:hover {
    background-color: #4f46e5;
}

QPushButton#TimerPauseButton {
    background-color: #272730;
    color: #e4e4e7;
    border: 1px solid #3f3f46;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#TimerPauseButton:hover {
    background-color: #3f3f46;
}

QPushButton#TimerStopButton {
    background-color: rgba(239, 68, 68, 0.1);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#TimerStopButton:hover {
    background-color: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.5);
}

QPushButton#TimerCancelButton {
    background-color: transparent;
    color: #71717a;
    border: none;
    padding: 8px;
}

QPushButton#TimerCancelButton:hover {
    color: #e4e4e7;
}

/* Custom Text Input */
QLineEdit#Input {
    background-color: #09090b;
    border: 1px solid #1f1f2a;
    border-radius: 8px;
    color: #e2e8f0;
    padding: 6px 12px;
    font-size: 12px;
    font-family: "Inter", "Segoe UI", sans-serif;
}

QLineEdit#Input:focus {
    border-color: #6366f1;
}

QPushButton#ActionButton {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
    padding: 6px 14px;
}

QPushButton#ActionButton:hover {
    background-color: #4f46e5;
}

/* Settings Panel */
QFrame#SettingsFrame {
    background-color: #121217;
    border: 1px solid #1f1f2a;
    border-radius: 10px;
}

QLabel#SettingsLabel {
    color: #71717a;
    font-size: 10px;
    font-weight: bold;
}

QPushButton#SettingsSaveButton {
    background-color: #272730;
    color: #f4f4f5;
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#SettingsSaveButton:hover {
    background-color: #3f3f46;
}

/* Quick log list items */
QFrame#TaskRow {
    background-color: #121217;
    border: 1px solid #1f1f2a;
    border-radius: 8px;
}

QPushButton#DeleteTaskButton {
    background-color: transparent;
    color: #71717a;
    border: none;
    font-size: 13px;
    font-weight: bold;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
    border-radius: 4px;
}

QPushButton#DeleteTaskButton:hover {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

/* Dashboard Button */
QPushButton#DashboardButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #6366f1, stop:1 #8b5cf6);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
    font-family: "Inter", "Segoe UI", sans-serif;
    padding: 10px 16px;
}

QPushButton#DashboardButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #4f46e5, stop:1 #7c3aed);
}

QPushButton#SettingsToggleButton {
    background-color: transparent;
    border: 1px solid #1f1f2a;
    border-radius: 6px;
    color: #71717a;
    padding: 4px;
}

QPushButton#SettingsToggleButton:hover {
    background-color: #1f1f2a;
    color: #f4f4f5;
}

/* MedTracker styles */
QLabel#SectionHeaderLabel {
    color: #a855f7;
    font-size: 12px;
    font-weight: bold;
    font-family: "Inter", "Segoe UI", sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QPushButton#QuickLogButton {
    background-color: rgba(168, 85, 247, 0.15);
    color: #d8b4fe;
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    font-family: "Inter", "Segoe UI", sans-serif;
    padding: 6px 10px;
}

QPushButton#QuickLogButton:hover {
    background-color: rgba(168, 85, 247, 0.3);
    border-color: rgba(168, 85, 247, 0.6);
    color: #ffffff;
}

QPushButton#QuickLogButton:pressed {
    background-color: rgba(168, 85, 247, 0.4);
}

QLineEdit#MealInput {
    background-color: #09090b;
    border: 1px solid #1f1f2a;
    border-radius: 6px;
    color: #e2e8f0;
    padding: 6px 10px;
    font-size: 12px;
    font-family: "Inter", "Segoe UI", sans-serif;
}

QLineEdit#MealInput:focus {
    border-color: #a855f7;
}

QPushButton#AddMealButton {
    background-color: #a855f7;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    padding: 6px 12px;
}

QPushButton#AddMealButton:hover {
    background-color: #c084fc;
}

QFrame#MealItemRow {
    background-color: #121217;
    border: 1px solid #1f1f2a;
    border-radius: 6px;
}

QLabel#MealNoteLabel {
    color: #f4f4f5;
    font-size: 12px;
    font-weight: 500;
    font-family: "Inter", "Segoe UI", sans-serif;
}

QLabel#MealTimeLabel {
    color: #71717a;
    font-size: 11px;
    font-family: "Inter", "Segoe UI", sans-serif;
}

QPushButton#DeleteMealButton {
    background-color: transparent;
    color: #71717a;
    border: none;
    font-size: 14px;
    font-weight: bold;
    min-width: 20px;
    max-width: 20px;
    min-height: 20px;
    max-height: 20px;
    border-radius: 4px;
}

QPushButton#DeleteMealButton:hover {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}
"""
