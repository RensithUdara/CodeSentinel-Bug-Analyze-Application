"""
Global stylesheets for the application.
"""

from app.ui.theme import COLORS

DARK_STYLESHEET = f"""
QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

QPushButton {{
    background-color: {COLORS['surface_soft']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 16px;
    color: {COLORS['text']};
    font-weight: 650;
}}
QPushButton:hover {{
    background-color: #0e2638;
    border-color: {COLORS['border_hover']};
}}
QPushButton:pressed {{
    background-color: #0a2a20;
}}
QPushButton:disabled {{
    background-color: {COLORS['input']};
    color: {COLORS['subtle']};
    border-color: {COLORS['border']};
}}
QPushButton#primaryButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['primary_text']};
    border: none;
    font-weight: 800;
}}

QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['input']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLORS['text']};
    selection-background-color: #146244;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['primary']};
}}
QComboBox::drop-down {{
    border: none;
    width: 30px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['input']};
    border: 1px solid {COLORS['border']};
    selection-background-color: #146244;
}}

QCheckBox {{
    color: {COLORS['text']};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid {COLORS['border_hover']};
    background-color: {COLORS['input']};
}}
QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QTableWidget {{
    background-color: transparent;
    alternate-background-color: rgba(255, 255, 255, 0.025);
    gridline-color: {COLORS['border']};
    border: none;
    border-radius: 8px;
    selection-background-color: #10533d;
    selection-color: {COLORS['text']};
}}
QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.035);
}}
QTableWidget::item:selected {{
    background-color: #10533d;
}}
QTableWidget::item:hover {{
    background-color: #0e2638;
}}
QHeaderView::section {{
    background-color: #0d2132;
    color: {COLORS['muted']};
    padding: 12px;
    border: none;
    font-weight: 800;
    font-size: 12px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: #526273;
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['primary']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background: #526273;
    min-width: 30px;
    border-radius: 5px;
}}

QProgressBar {{
    border: none;
    border-radius: 7px;
    background-color: #16283a;
    text-align: center;
    color: {COLORS['text']};
    height: 20px;
    font-weight: 700;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
    border-radius: 7px;
}}

QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['surface_soft']};
    border-radius: 8px;
}}
QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['muted']};
    padding: 10px 20px;
    margin-right: 2px;
    font-weight: 650;
}}
QTabBar::tab:selected {{
    color: {COLORS['primary']};
    border-bottom: 2px solid {COLORS['primary']};
}}

QToolTip {{
    background-color: {COLORS['surface']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 10px;
}}

QStatusBar {{
    background-color: {COLORS['bg']};
    color: {COLORS['muted']};
    border-top: 1px solid {COLORS['border']};
}}
"""

SIDEBAR_STYLE = f"""
QFrame {{
    background-color: {COLORS['sidebar']};
    border-right: 1px solid {COLORS['border']};
}}
QPushButton {{
    text-align: left;
    padding: 12px 14px;
    border-radius: 8px;
    font-size: 14px;
    color: {COLORS['muted']};
    background-color: transparent;
    border: none;
    margin: 3px 10px;
}}
QPushButton:hover {{
    background-color: #0e2638;
    color: {COLORS['text']};
}}
QPushButton:checked {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0d6a4a, stop:1 #0f513f);
    color: {COLORS['primary']};
    font-weight: 800;
}}
"""

SCROLL_AREA_STYLE = """
QScrollArea {
    border: none;
    background: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
"""
