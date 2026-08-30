"""
Main application window with sidebar navigation.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QSizePolicy, QFileDialog, QMessageBox,
    QToolButton
)
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon

from app.ui.dashboard import DashboardWidget
from app.ui.issues import IssuesWidget
from app.ui.files import FilesWidget
from app.ui.history import HistoryWidget
from app.ui.reports import ReportsWidget
from app.ui.settings import SettingsWidget
from app.ui.widgets.styles import DARK_STYLESHEET, SIDEBAR_STYLE
from app.ui.theme import APP_NAME, APP_TAGLINE, APP_VERSION, COLORS, PRIMARY_BUTTON_STYLE, LOGO_ASSET_PATH
from app.ui.widgets.kit import AppLogo, ProductFooter
from app.ui.widgets.icons import make_icon
from app.services.analysis_service import AnalysisService
from app.services.project_service import ProjectService


class TitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._drag_position = None
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #151922;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QLabel {{
                background: transparent;
                color: {COLORS['text']};
                font-size: 12px;
            }}
            QToolButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px;
            }}
            QToolButton:hover {{
                background-color: #243044;
            }}
            QToolButton#closeButton:hover {{
                background-color: #c42b45;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(8)

        icon = QLabel()
        logo_icon = QIcon(LOGO_ASSET_PATH)
        icon.setPixmap((logo_icon if not logo_icon.isNull() else make_icon("shield", COLORS["primary"], 18)).pixmap(18, 18))
        layout.addWidget(icon)

        title = QLabel(f"{APP_NAME} - {APP_TAGLINE}")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title)
        layout.addStretch()

        self.min_button = self._window_button("minimize")
        self.max_button = self._window_button("maximize")
        self.close_button = self._window_button("close")
        self.close_button.setObjectName("closeButton")

        self.min_button.clicked.connect(parent.showMinimized)
        self.max_button.clicked.connect(self._toggle_maximized)
        self.close_button.clicked.connect(parent.close)
        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)

    def _window_button(self, icon_name: str):
        button = QToolButton()
        button.setFixedSize(34, 28)
        button.setIcon(make_icon(icon_name, COLORS["text"], 18))
        button.setIconSize(QSize(14, 14))
        return button

    def _toggle_maximized(self):
        window = self.window()
        if window.isMaximized():
            window.showNormal()
            self.max_button.setIcon(make_icon("maximize", COLORS["text"], 18))
        else:
            window.showMaximized()
            self.max_button.setIcon(make_icon("restore", COLORS["text"], 18))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            if self.window().isMaximized():
                return
            self.window().move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximized()
            event.accept()


class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.analysis_service = AnalysisService(db_manager)
        self.project_service = ProjectService(db_manager)
        self.setWindowTitle(f"{APP_NAME} - {APP_TAGLINE}")
        logo_icon = QIcon(LOGO_ASSET_PATH)
        self.setWindowIcon(logo_icon if not logo_icon.isNull() else make_icon("shield", COLORS["primary"], 24))
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(1440, 920)
        self.setStyleSheet(DARK_STYLESHEET)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(TitleBar(self))

        app_body = QWidget()
        outer_layout.addWidget(app_body, 1)

        main_layout = QHBoxLayout(app_body)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        self.content_stack = QStackedWidget()
        self.content_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_stack.setStyleSheet(f"background-color: {COLORS['bg']};")

        self.dashboard_page = DashboardWidget(self.db)
        self.issues_page = IssuesWidget(self.db)
        self.files_page = FilesWidget(self.db)
        self.history_page = HistoryWidget(self.db)
        self.reports_page = ReportsWidget(self.db)
        self.settings_page = SettingsWidget(self.db)

        for page in [
            self.dashboard_page,
            self.issues_page,
            self.files_page,
            self.history_page,
            self.reports_page,
            self.settings_page,
        ]:
            self.content_stack.addWidget(page)

        main_layout.addWidget(self.content_stack)
        self.content_stack.setCurrentIndex(0)
        self.nav_buttons[0].setChecked(True)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(SIDEBAR_STYLE)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 30, 0, 18)

        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(18, 0, 18, 28)
        brand_row.setSpacing(12)
        brand_row.addWidget(AppLogo(compact=True))

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)
        logo = QLabel(APP_NAME)
        logo.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {COLORS['text']};")
        brand_layout.addWidget(logo)

        tagline = QLabel(APP_TAGLINE)
        tagline.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px;")
        brand_layout.addWidget(tagline)

        version = QLabel(f"v{APP_VERSION}")
        version.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px;")
        brand_layout.addWidget(version)
        brand_row.addLayout(brand_layout)
        layout.addLayout(brand_row)

        nav_items = [
            ("Dashboard", 0, "home"),
            ("Issues", 1, "issue"),
            ("Files", 2, "file"),
            ("History", 3, "history"),
            ("Reports", 4, "chart"),
            ("Settings", 5, "settings"),
        ]

        self.nav_buttons = []
        for label, index, icon in nav_items:
            btn = QPushButton(label)
            btn.setIcon(make_icon(icon, COLORS["muted"], 22))
            btn.setIconSize(QSize(20, 20))
            btn.setCheckable(True)
            btn.setMinimumHeight(46)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        analyze_btn = QPushButton("Scan Project")
        analyze_btn.setIcon(make_icon("play", COLORS["primary_text"], 22))
        analyze_btn.setIconSize(QSize(20, 20))
        analyze_btn.setObjectName("primaryButton")
        analyze_btn.setMinimumHeight(50)
        analyze_btn.setStyleSheet(
            PRIMARY_BUTTON_STYLE + "QPushButton { font-size: 14px; border-radius: 8px; margin: 8px 18px 10px 18px; }"
        )
        analyze_btn.clicked.connect(self.analyze_project)
        layout.addWidget(analyze_btn)

        layout.addWidget(ProductFooter())

        return sidebar

    def switch_page(self, index):
        for btn in self.nav_buttons:
            btn.setChecked(False)
        self.nav_buttons[index].setChecked(True)
        self.content_stack.setCurrentIndex(index)

    def analyze_project(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if not path:
            return
        try:
            self.analysis_service.analyze_project(path)
            QMessageBox.information(self, "Scan Complete", f"Project scan finished:\n{path}")
            self.dashboard_page.load_dashboard()
            self.issues_page.load_issues()
            self.files_page.load_files()
            self.history_page.load_history()
        except Exception as e:
            QMessageBox.critical(self, "Scan Failed", f"Analysis failed:\n{str(e)}")

    def closeEvent(self, event):
        event.accept()
