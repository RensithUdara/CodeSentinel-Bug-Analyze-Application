"""
Findings explorer with filtering and detail view.
"""
from PySide6.QtCore import Qt, QRegularExpression, QSize
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QPushButton, QLabel, QTextEdit, QSplitter,
    QFrame, QTabWidget
)

from app.database.repository import Repository
from app.ui.theme import COLORS, LABEL_STYLE, META_LABEL_STYLE, PRIMARY_BUTTON_STYLE, panel_style, severity_color
from app.ui.widgets.kit import PageHeader, SectionPanel, SeverityBadge, clear_layout
from app.ui.widgets.icons import make_icon


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.highlighting_rules = []
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(COLORS["info"]))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        for kw in ["def", "class", "if", "elif", "else", "for", "while", "import", "from", "return", "try", "except", "finally", "with", "as", "lambda", "yield", "raise", "assert", "self"]:
            self.highlighting_rules.append((QRegularExpression(f"\\b{kw}\\b"), keyword_format))
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(COLORS["low"]))
        self.highlighting_rules.append((QRegularExpression('".*"'), string_format))
        self.highlighting_rules.append((QRegularExpression("'.*'"), string_format))
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(COLORS["subtle"]))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class CountTile(QFrame):
    def __init__(self, label: str, value: int, color: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(2)
        number = QLabel(str(value))
        number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 850;")
        text = QLabel(label)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setStyleSheet(META_LABEL_STYLE)
        layout.addWidget(number)
        layout.addWidget(text)


class IssuesWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.repo = Repository(db_manager)
        self.all_issues = []
        self.filtered_issues = []
        self._current_issue = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 18)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_row.addWidget(PageHeader("Code Analysis", "Findings", "Review issues found in your code and improve code quality."))
        header_row.addStretch()
        self.count_panel = QFrame()
        self.count_panel.setStyleSheet(panel_style())
        self.count_layout = QHBoxLayout(self.count_panel)
        self.count_layout.setContentsMargins(18, 8, 18, 8)
        self.count_layout.setSpacing(12)
        header_row.addWidget(self.count_panel)
        layout.addLayout(header_row)

        filter_frame = QFrame()
        filter_frame.setStyleSheet(panel_style())
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(14, 12, 14, 12)
        filter_layout.setSpacing(12)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search findings...")
        self.search_edit.setMinimumHeight(42)
        self.search_edit.textChanged.connect(self.filter_issues)
        filter_layout.addWidget(self.search_edit, 2)

        filter_layout.addWidget(QLabel("Severity"))
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["All Severities", "Critical", "High", "Medium", "Low"])
        self.severity_combo.setMinimumHeight(42)
        self.severity_combo.setMinimumWidth(170)
        self.severity_combo.currentTextChanged.connect(self.filter_issues)
        filter_layout.addWidget(self.severity_combo)

        filter_layout.addWidget(QLabel("Type"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All Types", "Complexity", "Code Smell", "Security", "Duplication", "Maintainability"])
        self.type_combo.setMinimumHeight(42)
        self.type_combo.setMinimumWidth(190)
        self.type_combo.currentTextChanged.connect(self.filter_issues)
        filter_layout.addWidget(self.type_combo)

        clear_btn = QPushButton("Clear Filters")
        clear_btn.setIcon(make_icon("refresh", COLORS["primary"], 22))
        clear_btn.setIconSize(QSize(20, 20))
        clear_btn.setMinimumHeight(42)
        clear_btn.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { background-color: transparent; color: #2df29d; border: 1px solid #2df29d; border-radius: 8px; }")
        clear_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_btn)
        layout.addWidget(filter_frame)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)

        table_panel = SectionPanel()
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "Severity", "Type", "File", "Line", "Message", "Recommendation"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 52)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 112)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 72)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.show_issue_detail)
        table_panel.layout.addWidget(self.table)
        splitter.addWidget(table_panel)

        detail_panel = SectionPanel()
        detail_header = QHBoxLayout()
        self.tabs = QTabWidget()
        self.detail_tab = QWidget()
        detail_layout = QVBoxLayout(self.detail_tab)
        detail_layout.setContentsMargins(14, 14, 14, 14)
        self.detail_label = QLabel("Select a finding to view details")
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet(LABEL_STYLE)
        detail_layout.addWidget(self.detail_label)

        self.code_tab = QWidget()
        code_layout = QVBoxLayout(self.code_tab)
        code_layout.setContentsMargins(14, 14, 14, 14)
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMinimumHeight(120)
        self.detail_text.setStyleSheet(
            f"QTextEdit {{ background-color: {COLORS['input']}; border: 1px solid {COLORS['border']}; "
            "border-radius: 8px; font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; padding: 12px; }}"
        )
        code_layout.addWidget(self.detail_text)
        self.highlighter = PythonHighlighter(self.detail_text.document())

        self.tabs.addTab(self.detail_tab, "Finding Details")
        self.tabs.addTab(self.code_tab, "Code Context")
        detail_header.addWidget(self.tabs, 1)

        self.ai_button = QPushButton("Suggest Fix")
        self.ai_button.setIcon(make_icon("wrench", COLORS["primary_text"], 22))
        self.ai_button.setIconSize(QSize(20, 20))
        self.ai_button.setMinimumHeight(42)
        self.ai_button.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { border-radius: 8px; }")
        self.ai_button.clicked.connect(self.ai_suggest)
        detail_header.addWidget(self.ai_button)
        detail_panel.layout.addLayout(detail_header)
        splitter.addWidget(detail_panel)
        splitter.setSizes([430, 180])
        layout.addWidget(splitter, 1)

        self.load_issues()

    def load_issues(self):
        latest = self.repo.get_latest_analysis()
        if not latest:
            self.all_issues = []
            self.filtered_issues = []
            self.populate_table([])
            self.update_counts([])
            return
        self.all_issues = self.repo.get_issues_for_analysis(latest.analysis_id)
        self.filter_issues()

    def update_counts(self, issues):
        clear_layout(self.count_layout)
        critical = sum(1 for item in issues if item.severity == "Critical")
        high = sum(1 for item in issues if item.severity == "High")
        medium = sum(1 for item in issues if item.severity == "Medium")
        low = sum(1 for item in issues if item.severity == "Low")
        for label, value, color in [
            ("Total Findings", len(issues), COLORS["primary"]),
            ("Critical", critical, COLORS["critical"]),
            ("High", high, COLORS["high"]),
            ("Medium", medium, COLORS["medium"]),
            ("Low", low, COLORS["low"]),
        ]:
            self.count_layout.addWidget(CountTile(label, value, color))

    def populate_table(self, issues):
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        self.filtered_issues = sorted(issues, key=lambda x: severity_order.get(x.severity, 4))
        self.table.setRowCount(0)
        for index, issue in enumerate(self.filtered_issues, start=1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 42)
            self.table.setItem(row, 0, QTableWidgetItem(str(index)))
            self.table.setCellWidget(row, 1, SeverityBadge(issue.severity))
            self.table.setItem(row, 2, QTableWidgetItem(issue.type))
            self.table.setItem(row, 3, QTableWidgetItem(issue.file_path or "Unknown"))
            self.table.setItem(row, 4, QTableWidgetItem(str(issue.line or "")))
            self.table.setItem(row, 5, QTableWidgetItem(issue.message[:72] + "..." if len(issue.message) > 72 else issue.message))
            self.table.setItem(row, 6, QTableWidgetItem(issue.recommendation[:72] + "..." if len(issue.recommendation) > 72 else issue.recommendation))

    def filter_issues(self):
        search = self.search_edit.text().lower()
        severity = self.severity_combo.currentText()
        type_ = self.type_combo.currentText()
        filtered = self.all_issues
        if severity != "All Severities":
            filtered = [item for item in filtered if item.severity == severity]
        if type_ != "All Types":
            filtered = [item for item in filtered if item.type == type_]
        if search:
            filtered = [
                item for item in filtered
                if search in item.message.lower()
                or search in item.category.lower()
                or search in (item.file_path or "").lower()
            ]
        self.populate_table(filtered)
        self.update_counts(filtered)

    def clear_filters(self):
        self.search_edit.clear()
        self.severity_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)

    def show_issue_detail(self, row, col):
        if row >= len(self.filtered_issues):
            return
        issue = self.filtered_issues[row]
        self._current_issue = issue
        color = severity_color(issue.severity)
        self.detail_label.setText(
            f"<table>"
            f"<tr><td style='color:{COLORS['muted']}; width:120px;'>Severity</td><td style='color:{color}; font-weight:800;'>{issue.severity}</td></tr>"
            f"<tr><td style='color:{COLORS['muted']};'>Type</td><td>{issue.type}</td></tr>"
            f"<tr><td style='color:{COLORS['muted']};'>File</td><td>{issue.file_path}</td></tr>"
            f"<tr><td style='color:{COLORS['muted']};'>Line</td><td>{issue.line or ''}</td></tr>"
            f"<tr><td style='color:{COLORS['muted']};'>Message</td><td>{issue.message}</td></tr>"
            f"<tr><td style='color:{COLORS['muted']};'>Recommendation</td><td>{issue.recommendation}</td></tr>"
            f"</table>"
        )

    def ai_suggest(self):
        self.detail_text.setPlainText("Fix suggestions are available after selecting a finding.")
