"""
Shared brand and visual tokens for the desktop UI.
"""

APP_NAME = "CodeSentinel"
APP_TAGLINE = "Code Quality Workbench"
APP_VERSION = "1.0.0"
APP_DATA_DIR = ".codesentinel"
DEFAULT_REPORT_BASENAME = "codesentinel_report"

COLORS = {
    "bg": "#06111b",
    "bg_alt": "#081724",
    "sidebar": "#07111b",
    "surface": "#0b1b29",
    "surface_hover": "#103223",
    "surface_soft": "#091622",
    "input": "#07131f",
    "border": "#183145",
    "border_hover": "#24516c",
    "text": "#f4f8ff",
    "muted": "#b5c9e6",
    "subtle": "#7790ad",
    "primary": "#2df29d",
    "primary_hover": "#52f6af",
    "primary_pressed": "#17c97d",
    "primary_text": "#02120c",
    "accent": "#ffd95a",
    "info": "#5fb8ff",
    "warning": "#ffe56b",
    "danger": "#ff637d",
    "critical": "#ff4f75",
    "high": "#ff914d",
    "medium": "#ffda57",
    "low": "#46e69a",
}

PAGE_TITLE_STYLE = f"font-size: 32px; font-weight: 800; color: {COLORS['text']};"
SECTION_TITLE_STYLE = f"font-size: 17px; font-weight: 650; color: {COLORS['text']};"
LABEL_STYLE = f"color: {COLORS['muted']}; font-size: 13px;"
META_LABEL_STYLE = f"color: {COLORS['subtle']}; font-size: 12px;"
CARD_TITLE_STYLE = f"color: {COLORS['muted']}; font-size: 12px; font-weight: 650;"
EYEBROW_STYLE = f"color: {COLORS['primary']}; font-size: 12px; font-weight: 800;"
SUBTITLE_STYLE = f"color: {COLORS['muted']}; font-size: 16px;"
PRIMARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['primary_text']};
    border: none;
    font-weight: 700;
    padding: 10px 14px;
}}
QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}
QPushButton:pressed {{
    background-color: {COLORS['primary_pressed']};
}}
"""


def panel_style(radius: int = 8, hover: bool = False) -> str:
    hover_rules = f"""
        QFrame:hover {{
            border-color: {COLORS['border_hover']};
        }}
    """ if hover else ""
    return f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0d2233, stop:1 {COLORS['surface_soft']});
            border-radius: {radius}px;
            border: 1px solid {COLORS['border']};
        }}
        {hover_rules}
    """


def severity_color(severity: str) -> str:
    return {
        "Critical": COLORS["critical"],
        "High": COLORS["high"],
        "Medium": COLORS["medium"],
        "Low": COLORS["low"],
    }.get(severity, COLORS["subtle"])
