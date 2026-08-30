"""
Small UI building blocks used to match the CodeSentinel dashboard design.
"""
import os
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QGraphicsDropShadowEffect, QProgressBar
)

from app.ui.widgets.icons import make_pixmap
from app.ui.theme import (
    APP_NAME, APP_TAGLINE, APP_VERSION, COLORS, EYEBROW_STYLE,
    PAGE_TITLE_STYLE, SUBTITLE_STYLE, SECTION_TITLE_STYLE, LABEL_STYLE,
    META_LABEL_STYLE, panel_style, severity_color
)


def add_shadow(widget: QWidget, blur: int = 24, y: int = 10):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(0, 0, 0, 95))
    shadow.setOffset(0, y)
    widget.setGraphicsEffect(shadow)


def clear_layout(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if item.widget():
            item.widget().setParent(None)
        elif item.layout():
            clear_layout(item.layout())


def project_name_from_path(path: str = "") -> str:
    if not path:
        return "No project scanned"
    return os.path.basename(os.path.normpath(path)) or path


def compact_path(path: str = "", line=None, keep_parts: int = 4) -> str:
    if not path:
        base = "Unknown"
    else:
        normalized = path.replace("\\", "/")
        parts = [part for part in normalized.split("/") if part]
        base = "/".join(parts[-keep_parts:]) if len(parts) > keep_parts else normalized
    return f"{base}:{line}" if line not in (None, "") else base


def format_timestamp(value) -> str:
    if not value:
        return "No scan yet"
    if isinstance(value, datetime):
        return value.strftime("%b %d, %Y  %I:%M %p")
    return str(value)[:16]


class AppLogo(QFrame):
    def __init__(self, compact: bool = False):
        super().__init__()
        size = 44 if compact else 52
        self.setFixedSize(size, size)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #12583d, stop:1 #0d2c33);
                border: 1px solid #145d46;
                border-radius: 8px;
            }}
            QLabel {{
                color: {COLORS['primary']};
                background: transparent;
                border: none;
                font-size: {24 if compact else 28}px;
                font-weight: 900;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 1)
        mark = QLabel()
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setPixmap(make_pixmap("code", COLORS["primary"], 30 if compact else 36))
        layout.addWidget(mark)


class PageHeader(QWidget):
    def __init__(self, eyebrow: str, title: str, subtitle: str, icon: str = ""):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        if icon:
            icon_box = QFrame()
            icon_box.setFixedSize(58, 58)
            icon_box.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #104935, stop:1 #0b2333);
                    border: 1px solid {COLORS['border']};
                    border-radius: 10px;
                }}
                QLabel {{
                    color: {COLORS['primary']};
                    background: transparent;
                    border: none;
                    font-size: 24px;
                    font-weight: 850;
                }}
            """)
            icon_layout = QVBoxLayout(icon_box)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setPixmap(make_pixmap(icon, COLORS["primary"], 30))
            icon_layout.addWidget(icon_label)
            layout.addWidget(icon_box)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        eyebrow_label = QLabel(eyebrow.upper())
        eyebrow_label.setStyleSheet(EYEBROW_STYLE)
        title_label = QLabel(title)
        title_label.setStyleSheet(PAGE_TITLE_STYLE)
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(SUBTITLE_STYLE)
        text_layout.addWidget(eyebrow_label)
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        layout.addLayout(text_layout)
        layout.addStretch()


class InfoChip(QFrame):
    def __init__(self, title: str, value: str, icon: str = ""):
        super().__init__()
        self.setMinimumHeight(68)
        self.setStyleSheet(panel_style())
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(14)

        if icon:
            icon_box = QLabel()
            icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_box.setFixedSize(38, 38)
            icon_box.setStyleSheet(f"""
                background-color: #102438;
                color: {COLORS['muted']};
                border-radius: 8px;
                font-size: 18px;
                font-weight: 800;
            """)
            icon_box.setPixmap(make_pixmap(icon, COLORS["muted"], 22))
            layout.addWidget(icon_box)

        text = QVBoxLayout()
        text.setSpacing(3)
        title_label = QLabel(title)
        title_label.setStyleSheet(META_LABEL_STYLE)
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; font-weight: 650;")
        text.addWidget(title_label)
        text.addWidget(value_label)
        layout.addLayout(text)


class StatCard(QFrame):
    def __init__(self, title: str, value: str, color: str, icon: str = "", suffix: str = "/ 100"):
        super().__init__()
        self.setMinimumHeight(104)
        self.setStyleSheet(panel_style(8, hover=True))
        add_shadow(self, 18, 5)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(18)

        icon_box = QLabel()
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setFixedSize(54, 54)
        icon_box.setStyleSheet(f"""
            background-color: rgba(45, 242, 157, 0.12);
            color: {color};
            border-radius: 10px;
            font-size: 20px;
            font-weight: 900;
        """)
        icon_box.setPixmap(make_pixmap(icon or "info", color, 28))
        layout.addWidget(icon_box)

        text = QVBoxLayout()
        text.setSpacing(8)
        label = QLabel(title)
        label.setStyleSheet(LABEL_STYLE)
        row = QHBoxLayout()
        score = QLabel(value)
        score.setStyleSheet(f"color: {color}; font-size: 31px; font-weight: 850;")
        score.setMinimumWidth(64)
        suffix_label = QLabel(suffix)
        suffix_label.setStyleSheet(META_LABEL_STYLE)
        row.addWidget(score)
        row.addWidget(suffix_label)
        row.addStretch()
        text.addWidget(label)
        text.addLayout(row)
        layout.addLayout(text)


class SectionPanel(QFrame):
    def __init__(self, title: str = "", icon: str = ""):
        super().__init__()
        self.setStyleSheet(panel_style())
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 16, 18, 16)
        self.layout.setSpacing(14)
        if title:
            row = QHBoxLayout()
            if icon:
                icon_label = QLabel()
                icon_label.setPixmap(make_pixmap(icon, COLORS["primary"], 22))
                icon_label.setStyleSheet(f"color: {COLORS['primary']}; font-size: 20px; font-weight: 900;")
                row.addWidget(icon_label)
            label = QLabel(title)
            label.setStyleSheet(SECTION_TITLE_STYLE)
            row.addWidget(label)
            row.addStretch()
            self.layout.addLayout(row)


class SeverityBadge(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        color = severity_color(text)
        bg = {
            "Critical": "rgba(255, 79, 117, 0.22)",
            "High": "rgba(255, 145, 77, 0.22)",
            "Medium": "rgba(255, 218, 87, 0.22)",
            "Low": "rgba(70, 230, 154, 0.18)",
        }.get(text, "rgba(119, 144, 173, 0.18)")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(92, 28)
        self.setStyleSheet(f"""
            color: {color};
            background-color: {bg};
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 8px;
            padding: 0px;
            font-weight: 800;
        """)


class ScorePill(QLabel):
    def __init__(self, text: str, color: str):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(72)
        self.setStyleSheet(f"""
            color: {color};
            background-color: rgba(255, 255, 255, 0.06);
            border-radius: 8px;
            padding: 6px 14px;
            font-weight: 800;
        """)


class BigProgressCard(QFrame):
    def __init__(self, score: int):
        super().__init__()
        self.setStyleSheet(panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        row = QHBoxLayout()
        title = QLabel("Overall Grade")
        title.setStyleSheet(SECTION_TITLE_STYLE)
        value = QLabel(f"{score} / 100")
        value.setStyleSheet(f"color: {COLORS['primary']}; font-size: 22px; font-weight: 850;")
        row.addWidget(title)
        row.addStretch()
        row.addWidget(value)
        layout.addLayout(row)

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(max(0, min(100, score)))
        progress.setTextVisible(False)
        progress.setFixedHeight(16)
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 8px;
                background-color: #18283a;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
                border-radius: 8px;
            }}
        """)
        layout.addWidget(progress)

        note = QLabel("Good code quality. Keep it up!")
        note.setStyleSheet(LABEL_STYLE)
        layout.addWidget(note)


class ProductFooter(QLabel):
    def __init__(self):
        super().__init__(f"{APP_NAME} v{APP_VERSION}\nBetter Code. Stronger Projects.")
        self.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px; padding: 10px 18px;")
