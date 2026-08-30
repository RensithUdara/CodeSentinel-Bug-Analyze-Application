"""
File-level analysis view.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QLabel, QFrame, QComboBox, QPushButton
)

from app.database.repository import Repository
from app.ui.theme import COLORS, LABEL_STYLE, META_LABEL_STYLE, PRIMARY_BUTTON_STYLE, panel_style
from app.ui.widgets.kit import PageHeader, InfoChip, SectionPanel, ScorePill, project_name_from_path
from app.ui.widgets.icons import make_icon


class FilesWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.repo = Repository(db_manager)
        self.all_files = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 18)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_row.addWidget(PageHeader("Inventory", "File Inventory", "Browse analyzed files and their metrics.", "file"))
        header_row.addStretch()
        self.project_chip = InfoChip("Project", "No project scanned", "folder")
        self.file_chip = InfoChip("Files", "0 files analyzed", "file")
        header_row.addWidget(self.project_chip)
        header_row.addWidget(self.file_chip)
        layout.addLayout(header_row)

        filter_frame = QFrame()
        filter_frame.setStyleSheet(panel_style())
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(14, 12, 14, 12)
        filter_layout.setSpacing(12)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search files...")
        self.search.setMinimumHeight(42)
        self.search.textChanged.connect(self.filter_files)
        filter_layout.addWidget(self.search, 2)

        self.language_combo = QComboBox()
        self.language_combo.addItem("All Languages")
        self.language_combo.setMinimumHeight(42)
        self.language_combo.setMinimumWidth(180)
        self.language_combo.currentTextChanged.connect(self.filter_files)
        filter_layout.addWidget(QLabel("Language"))
        filter_layout.addWidget(self.language_combo)

        self.complexity_combo = QComboBox()
        self.complexity_combo.addItems(["All", "Low", "Medium", "High"])
        self.complexity_combo.setMinimumHeight(42)
        self.complexity_combo.setMinimumWidth(160)
        self.complexity_combo.currentTextChanged.connect(self.filter_files)
        filter_layout.addWidget(QLabel("Complexity"))
        filter_layout.addWidget(self.complexity_combo)

        clear_btn = QPushButton("Clear Filters")
        clear_btn.setIcon(make_icon("refresh", COLORS["primary"], 22))
        clear_btn.setIconSize(QSize(20, 20))
        clear_btn.setMinimumHeight(42)
        clear_btn.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { background-color: transparent; color: #2df29d; border: 1px solid #2df29d; border-radius: 8px; }")
        clear_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_btn)
        layout.addWidget(filter_frame)

        table_panel = SectionPanel()
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "File", "Language", "LOC", "Complexity", "Maintainability", "Issues"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 54)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        table_panel.layout.addWidget(self.table)

        self.footer_label = QLabel("")
        self.footer_label.setStyleSheet(LABEL_STYLE)
        table_panel.layout.addWidget(self.footer_label)
        layout.addWidget(table_panel, 1)

        self.load_files()

    def load_files(self):
        latest = self.repo.get_latest_analysis()
        if not latest:
            self.all_files = []
            self.populate_table([])
            return
        project = self.repo.get_project_by_id(latest.project_id)
        self.project_chip.findChildren(QLabel)[-1].setText(project_name_from_path(project.path if project else ""))
        self.all_files = self.repo.get_files_for_analysis(latest.analysis_id)
        self.file_chip.findChildren(QLabel)[-1].setText(f"{len(self.all_files)} files analyzed")
        self.language_combo.blockSignals(True)
        current = self.language_combo.currentText()
        self.language_combo.clear()
        self.language_combo.addItem("All Languages")
        for language in sorted({item.language or "Unknown" for item in self.all_files}):
            self.language_combo.addItem(language)
        index = self.language_combo.findText(current)
        self.language_combo.setCurrentIndex(index if index >= 0 else 0)
        self.language_combo.blockSignals(False)
        self.filter_files()

    def populate_table(self, files):
        self.table.setRowCount(0)
        for index, file_info in enumerate(files, start=1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 42)
            self.table.setItem(row, 0, QTableWidgetItem(str(index)))
            self.table.setItem(row, 1, QTableWidgetItem(file_info.path or ""))
            self.table.setItem(row, 2, QTableWidgetItem(file_info.language or "Unknown"))
            self.table.setItem(row, 3, QTableWidgetItem(str(file_info.loc or 0)))

            complexity = file_info.complexity or 0
            color = COLORS["low"] if complexity <= 5 else COLORS["medium"] if complexity <= 10 else COLORS["danger"]
            self.table.setCellWidget(row, 4, ScorePill(f"●  {complexity:.1f}", color))
            maintainability = file_info.maintainability or 0
            maint_color = COLORS["low"] if maintainability >= 80 else COLORS["medium"] if maintainability >= 60 else COLORS["danger"]
            self.table.setCellWidget(row, 5, ScorePill(f"{maintainability:.1f}", maint_color))
            self.table.setItem(row, 6, QTableWidgetItem(str(self.repo.get_issue_count_for_file(file_info.file_id) or 0)))
        self.footer_label.setText(f"Showing 1 - {len(files)} of {len(self.all_files)} files")

    def filter_files(self):
        search = self.search.text().lower()
        language = self.language_combo.currentText()
        complexity = self.complexity_combo.currentText()
        filtered = [item for item in self.all_files if search in (item.path or "").lower()]
        if language != "All Languages":
            filtered = [item for item in filtered if (item.language or "Unknown") == language]
        if complexity == "Low":
            filtered = [item for item in filtered if (item.complexity or 0) <= 5]
        elif complexity == "Medium":
            filtered = [item for item in filtered if 5 < (item.complexity or 0) <= 10]
        elif complexity == "High":
            filtered = [item for item in filtered if (item.complexity or 0) > 10]
        self.populate_table(filtered)

    def clear_filters(self):
        self.search.clear()
        self.language_combo.setCurrentIndex(0)
        self.complexity_combo.setCurrentIndex(0)
