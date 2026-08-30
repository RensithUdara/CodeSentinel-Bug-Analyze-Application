"""
Reports generation UI.
"""
from datetime import datetime

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QFileDialog, QMessageBox, QTextEdit, QCheckBox
)

from app.core.analyzer.scoring import ScoringEngine
from app.database.repository import Repository
from app.reports.report_generator import ReportGenerator
from app.ui.theme import COLORS, LABEL_STYLE, META_LABEL_STYLE, PRIMARY_BUTTON_STYLE, DEFAULT_REPORT_BASENAME
from app.ui.widgets.kit import PageHeader, InfoChip, SectionPanel, project_name_from_path
from app.ui.widgets.icons import make_icon


class ReportsWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.repo = Repository(db_manager)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 18)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_row.addWidget(PageHeader("Reports", "Evidence Reports", "Generate professional reports for your code analysis."))
        header_row.addStretch()
        self.project_chip = InfoChip("Project", "No project scanned", "folder")
        header_row.addWidget(self.project_chip)
        layout.addLayout(header_row)

        options = SectionPanel()
        options_row = QHBoxLayout()
        format_col = QVBoxLayout()
        format_label = QLabel("Report Format")
        format_label.setStyleSheet(LABEL_STYLE)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML", "PDF", "JSON", "CSV"])
        self.format_combo.setMinimumHeight(42)
        self.format_combo.setMinimumWidth(260)
        self.format_combo.currentTextChanged.connect(lambda _: self.refresh_preview())
        format_col.addWidget(format_label)
        format_col.addWidget(self.format_combo)
        options_row.addLayout(format_col)

        content_col = QVBoxLayout()
        content_label = QLabel("Report Content")
        content_label.setStyleSheet(LABEL_STYLE)
        checks = QHBoxLayout()
        for text in ["Summary", "Issues", "Metrics", "Charts", "Recommendations"]:
            check = QCheckBox(text)
            check.setChecked(True)
            checks.addWidget(check)
        content_col.addWidget(content_label)
        content_col.addLayout(checks)
        options_row.addLayout(content_col, 1)

        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setIcon(make_icon("report", COLORS["primary_text"], 22))
        self.generate_btn.setIconSize(QSize(20, 20))
        self.generate_btn.setMinimumHeight(52)
        self.generate_btn.setMinimumWidth(190)
        self.generate_btn.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { border-radius: 8px; }")
        self.generate_btn.clicked.connect(self.generate_report)
        options_row.addWidget(self.generate_btn)
        options.layout.addLayout(options_row)
        layout.addWidget(options)

        body = QHBoxLayout()
        body.setSpacing(18)

        preview_panel = SectionPanel("Report Preview", "eye")
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(360)
        self.preview.setStyleSheet(
            f"QTextEdit {{ background-color: {COLORS['input']}; border: 1px solid {COLORS['border']}; "
            f"border-radius: 8px; color: {COLORS['text']}; padding: 20px; font-size: 14px; }}"
        )
        preview_panel.layout.addWidget(self.preview)
        body.addWidget(preview_panel, 3)

        detail_panel = SectionPanel("Report Details", "info")
        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet(LABEL_STYLE)
        detail_panel.layout.addWidget(self.details_label)

        buttons = QHBoxLayout()
        for text, icon_name in [("Open Report", "refresh"), ("Show in Folder", "folder"), ("Share", "layers")]:
            btn = QPushButton(text)
            btn.setIcon(make_icon(icon_name, COLORS["primary_text"] if text == "Open Report" else COLORS["muted"], 20))
            btn.setIconSize(QSize(18, 18))
            btn.setMinimumHeight(42)
            if text == "Open Report":
                btn.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { border-radius: 8px; }")
            buttons.addWidget(btn)
        detail_panel.layout.addLayout(buttons)

        self.status_label = QLabel("No report generated yet.")
        self.status_label.setStyleSheet(
            f"color: {COLORS['muted']}; background-color: rgba(45,242,157,0.08); "
            f"border: 1px solid rgba(45,242,157,0.18); border-radius: 8px; padding: 18px;"
        )
        detail_panel.layout.addWidget(self.status_label)
        detail_panel.layout.addStretch()
        body.addWidget(detail_panel, 2)
        layout.addLayout(body, 1)

        self.refresh_preview()

    def refresh_preview(self):
        latest = self.repo.get_latest_analysis()
        if not latest:
            self.preview.setPlainText("CodeSentinel\nCode Quality Report\n\nRun a scan to preview report content.")
            self.details_label.setText("Project: No project scanned\nStatus: Waiting for scan")
            return
        project = self.repo.get_project_by_id(latest.project_id)
        project_name = project_name_from_path(project.path if project else "")
        self.project_chip.findChildren(QLabel)[-1].setText(project_name)
        issues = self.repo.get_issues_for_analysis(latest.analysis_id)
        self.preview.setPlainText(
            f"CodeSentinel\nCode Quality Report\n{project_name}\n\n"
            f"Quality: {latest.quality_score:.1f} / 100\n"
            f"Security: {latest.security_score:.1f} / 100\n"
            f"Complexity: {latest.complexity_score:.1f} / 100\n"
            f"Maintainability: {latest.maintainability_score:.1f} / 100\n\n"
            "Overview\n"
            "This report provides a comprehensive analysis of code quality, security, and maintainability.\n\n"
            f"Generated by CodeSentinel v1.0.0    {datetime.now().strftime('%b %d, %Y  %I:%M %p')}"
        )
        self.details_label.setText(
            f"Project: {project_name}\n"
            f"Format: {self.format_combo.currentText()}\n"
            f"Generated On: {datetime.now().strftime('%b %d, %Y  %I:%M %p')}\n"
            f"Total Issues: {len(issues)}\n"
            "Status: Ready"
        )

    def generate_report(self):
        latest = self.repo.get_latest_analysis()
        if not latest:
            QMessageBox.warning(self, "No Data", "No analysis data available. Run an analysis first.")
            return

        fmt = self.format_combo.currentText().lower()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"{DEFAULT_REPORT_BASENAME}.{fmt}", f"*.{fmt}")
        if not file_path:
            return

        project = self.repo.get_project_by_id(latest.project_id)
        issues = self.repo.get_issues_for_analysis(latest.analysis_id)
        data = {
            "project_name": project_name_from_path(project.path if project else ""),
            "project_path": project.path if project else "",
            "quality_score": latest.quality_score,
            "grade": ScoringEngine().grade(latest.quality_score),
            "maintainability": latest.maintainability_score,
            "complexity": latest.complexity_score,
            "security": latest.security_score,
            "duplication": latest.duplication_score,
            "technical_debt": latest.technical_debt,
            "issues": [{
                "severity": i.severity,
                "type": i.type,
                "category": i.category,
                "file_path": i.file_path,
                "line": i.line,
                "message": i.message,
                "recommendation": i.recommendation,
            } for i in issues],
        }

        gen = ReportGenerator(data)
        try:
            if fmt == "html":
                gen.generate_html(file_path)
            elif fmt == "json":
                gen.generate_json(file_path)
            elif fmt == "csv":
                gen.generate_csv(file_path)
            elif fmt == "pdf":
                gen.generate_pdf(file_path)
            self.status_label.setText(f"Report generated successfully.\n{file_path}")
            self.status_label.setStyleSheet(
                f"color: {COLORS['primary']}; background-color: rgba(45,242,157,0.10); "
                f"border: 1px solid rgba(45,242,157,0.28); border-radius: 8px; padding: 18px; font-weight: 700;"
            )
            self.refresh_preview()
        except ImportError as e:
            QMessageBox.warning(self, "Missing Dependency", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
