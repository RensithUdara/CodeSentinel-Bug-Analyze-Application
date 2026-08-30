"""
Reusable card widgets for the dashboard.
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.ui.theme import COLORS, CARD_TITLE_STYLE, META_LABEL_STYLE


CARD_STYLE = f"""
QFrame#card {{
    background-color: {COLORS['surface']};
    border-radius: 8px;
    border: 1px solid {COLORS['border']};
}}
QFrame#card:hover {{
    border-color: {COLORS['border_hover']};
    background-color: {COLORS['surface_hover']};
}}
"""


def _shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(18)
    shadow.setColor(QColor(0, 0, 0, 80))
    shadow.setOffset(0, 5)
    return shadow


class MetricCard(QFrame):
    def __init__(self, title: str, value, subtitle: str = "", color: str = None, icon: str = ""):
        super().__init__()
        color = color or COLORS["primary"]
        self.setObjectName("card")
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(CARD_STYLE)
        self.setGraphicsEffect(_shadow())

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(18, 18, 18, 18)

        header_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setFixedSize(34, 24)
            icon_label.setStyleSheet(
                f"background-color: #202820; color: {color}; border-radius: 6px; "
                "font-size: 11px; font-weight: 800;"
            )
            header_layout.addWidget(icon_label)
        title_label = QLabel(title)
        title_label.setStyleSheet(CARD_TITLE_STYLE)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"color: {color}; font-size: 31px; font-weight: 750;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(value_label)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(META_LABEL_STYLE)
            layout.addWidget(sub)


class ProgressCard(QFrame):
    def __init__(self, title: str, value: int, max_value: int = 100, color: str = None):
        super().__init__()
        color = color or COLORS["primary"]
        self.setObjectName("card")
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(CARD_STYLE)
        self.setGraphicsEffect(_shadow())

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(CARD_TITLE_STYLE)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.value_label = QLabel(f"{value}/{max_value}")
        self.value_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 700;")
        header_layout.addWidget(self.value_label)
        layout.addLayout(header_layout)

        self.progress = QProgressBar()
        self.progress.setRange(0, max_value)
        self.progress.setValue(value)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #252921;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color}, stop:1 {COLORS['accent']});
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.progress)


class IssueSummaryCard(QFrame):
    def __init__(self, critical: int, high: int, medium: int, low: int):
        super().__init__()
        self.setObjectName("card")
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(CARD_STYLE)
        self.setGraphicsEffect(_shadow())

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        title = QLabel("Findings Mix")
        title.setStyleSheet(CARD_TITLE_STYLE)
        layout.addWidget(title)

        for name, count, color in [
            ("Critical", critical, COLORS["critical"]),
            ("High", high, COLORS["high"]),
            ("Medium", medium, COLORS["medium"]),
            ("Low", low, COLORS["low"]),
        ]:
            row = QHBoxLayout()
            dot = QLabel("|")
            dot.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 900;")
            row.addWidget(dot)
            label = QLabel(name)
            label.setStyleSheet(f"color: {COLORS['text']}; font-size: 13px;")
            row.addWidget(label)
            row.addStretch()
            count_label = QLabel(str(count))
            count_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 700;")
            row.addWidget(count_label)
            layout.addLayout(row)
