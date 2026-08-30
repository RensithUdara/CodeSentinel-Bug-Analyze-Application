"""
History view for comparing analysis runs.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QPushButton

from app.database.repository import Repository
from app.ui.theme import COLORS, LABEL_STYLE, PRIMARY_BUTTON_STYLE, panel_style
from app.ui.widgets.kit import PageHeader, InfoChip, SectionPanel, ScorePill, format_timestamp
from app.ui.widgets.icons import make_icon


class HistoryWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.repo = Repository(db_manager)
        self.history = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 18)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_row.addWidget(PageHeader("History", "Scan History", "View past scan results and track code quality over time.", "history"))
        header_row.addStretch()
        self.scan_chip = InfoChip("Total Scans", "0", "clock")
        header_row.addWidget(self.scan_chip)
        layout.addLayout(header_row)

        table_panel = SectionPanel()
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search history...")
        self.search.setMinimumHeight(42)
        self.search.textChanged.connect(self.filter_history)
        toolbar.addWidget(self.search, 1)
        clear_btn = QPushButton("Clear History")
        clear_btn.setIcon(make_icon("file", COLORS["primary"], 22))
        clear_btn.setIconSize(QSize(20, 20))
        clear_btn.setMinimumHeight(42)
        clear_btn.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { background-color: transparent; color: #2df29d; border: 1px solid #2df29d; border-radius: 8px; }")
        toolbar.addWidget(clear_btn)
        table_panel.layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["#", "Date & Time", "Quality", "Security", "Complexity", "Maintainability", "Duplication", "Tech Debt", "Grade"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 54)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        table_panel.layout.addWidget(self.table, 1)

        footer = QHBoxLayout()
        self.footer_label = QLabel("")
        self.footer_label.setStyleSheet(LABEL_STYLE)
        footer.addWidget(self.footer_label)
        footer.addStretch()
        for text in ["‹", "1", "›"]:
            page = QLabel(text)
            page.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page.setFixedSize(34, 34)
            bg = COLORS["primary"] if text == "1" else "#0b1b29"
            fg = COLORS["primary_text"] if text == "1" else COLORS["muted"]
            page.setStyleSheet(f"background-color: {bg}; color: {fg}; border-radius: 8px; font-weight: 800;")
            footer.addWidget(page)
        table_panel.layout.addLayout(footer)
        layout.addWidget(table_panel, 1)

        self.load_history()

    def load_history(self):
        latest = self.repo.get_latest_analysis()
        if not latest:
            self.history = []
            self.populate_table([])
            return
        self.history = self.repo.get_analysis_history(latest.project_id, limit=20)
        self.scan_chip.findChildren(QLabel)[-1].setText(str(len(self.history)))
        self.populate_table(self.history)

    def populate_table(self, history):
        self.table.setRowCount(0)
        for index, run in enumerate(history, start=1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 54)
            self.table.setItem(row, 0, QTableWidgetItem(str(index)))
            self.table.setItem(row, 1, QTableWidgetItem(format_timestamp(run.timestamp)))
            self.table.setCellWidget(row, 2, ScorePill(f"{run.quality_score:.1f}", self._score_color(run.quality_score)))
            self.table.setCellWidget(row, 3, ScorePill(f"{run.security_score:.1f}", self._score_color(run.security_score)))
            self.table.setCellWidget(row, 4, ScorePill(f"{run.complexity_score:.1f}", self._score_color(run.complexity_score)))
            self.table.setCellWidget(row, 5, ScorePill(f"{run.maintainability_score:.1f}", self._score_color(run.maintainability_score)))
            self.table.setCellWidget(row, 6, ScorePill(f"{run.duplication_score:.1f}", self._score_color(run.duplication_score)))
            self.table.setCellWidget(row, 7, ScorePill(f"{run.technical_debt:.1f}h", COLORS["high"]))
            self.table.setCellWidget(row, 8, ScorePill(self._grade(run.quality_score), self._score_color(run.quality_score)))
        self.footer_label.setText(f"Showing 1 - {len(history)} of {len(self.history)} scans")

    def filter_history(self):
        search = self.search.text().lower()
        filtered = [run for run in self.history if search in format_timestamp(run.timestamp).lower()]
        self.populate_table(filtered)

    def _score_color(self, score):
        if score >= 80:
            return COLORS["low"]
        if score >= 60:
            return COLORS["medium"]
        return COLORS["danger"]

    def _grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"
