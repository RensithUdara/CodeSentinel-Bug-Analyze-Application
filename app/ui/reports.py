"""
Reports generation UI.
"""
import os
import subprocess
from datetime import datetime

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTextEdit, QCheckBox, QButtonGroup, QFrame,
    QSizePolicy
)

from app.core.analyzer.scoring import ScoringEngine
from app.database.repository import Repository
from app.reports.report_generator import ReportGenerator
from app.ui.theme import (
    APP_NAME, APP_VERSION, COLORS, LABEL_STYLE, META_LABEL_STYLE,
    PRIMARY_BUTTON_STYLE, DEFAULT_REPORT_BASENAME
)
from app.ui.widgets.icons import make_icon, make_pixmap
from app.ui.widgets.kit import PageHeader, InfoChip, SectionPanel, project_name_from_path


class FormatButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setCheckable(True)
        self.setMinimumHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-weight: 800;
            }}
            QPushButton:checked {{
                color: {COLORS['primary']};
                border-color: {COLORS['primary']};
                background-color: rgba(45, 242, 157, 0.08);
            }}
            QPushButton:hover {{
                border-color: {COLORS['primary']};
            }}
        """)


class DetailRows(QFrame):
    def __init__(self):
        super().__init__()
        self.rows = {}
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 14, 18, 14)
        self.layout.setSpacing(0)
        for label in ["Project", "Format", "Generated On", "Total Issues", "Report Size", "Status"]:
            self._add_row(label)

    def _add_row(self, label: str):
        row = QHBoxLayout()
        row.setContentsMargins(0, 8, 0, 8)
        key = QLabel(label)
        key.setFixedWidth(145)
        key.setStyleSheet(LABEL_STYLE)
        value = QLabel("")
        value.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px; font-weight: 600;")
        row.addWidget(key)
        row.addWidget(value, 1)
        self.layout.addLayout(row)
        self.rows[label] = value

    def set_value(self, label: str, value: str, color: str = None):
        target = self.rows[label]
        target.setText(value)
        target.setStyleSheet(f"color: {color or COLORS['text']}; font-size: 14px; font-weight: 700;")


class StatusCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(108)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(45,242,157,0.16), stop:1 rgba(45,242,157,0.05));
                border: 1px solid rgba(45,242,157,0.28);
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(18)

        icon = QLabel()
        icon.setFixedSize(48, 48)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setPixmap(make_pixmap("check", COLORS["low"], 34))
        layout.addWidget(icon)

        text = QVBoxLayout()
        self.title = QLabel("Report generated successfully!")
        self.title.setStyleSheet(f"color: {COLORS['primary']}; font-size: 14px; font-weight: 800;")
        self.subtitle = QLabel("Your evidence report is ready to view and share.")
        subtitle = self.subtitle
        subtitle.setStyleSheet(META_LABEL_STYLE)
        text.addWidget(self.title)
        text.addWidget(subtitle)
        layout.addLayout(text)
        layout.addStretch()

    def set_waiting(self):
        self.title.setText("Ready to generate")
        self.subtitle.setText("Choose a format, then generate the report.")

    def set_success(self, path: str):
        self.title.setText("Report generated successfully!")
        self.subtitle.setText(path)


class ReportsWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.repo = Repository(db_manager)
        self.last_report_path = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 18)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_row.addWidget(PageHeader("Reports", "Evidence Reports", "Generate professional reports for your code analysis."))
        header_row.addStretch()
        self.project_chip = InfoChip("Project", "No project scanned", "report")
        self.project_chip.setMinimumWidth(250)
        header_row.addWidget(self.project_chip)
        layout.addLayout(header_row)

        layout.addWidget(self._build_options_panel())

        body = QHBoxLayout()
        body.setSpacing(18)
        body.addWidget(self._build_preview_panel(), 5)
        body.addWidget(self._build_details_panel(), 4)
        layout.addLayout(body, 1)

        self.refresh_preview()

    def _build_options_panel(self):
        panel = SectionPanel()
        row = QHBoxLayout()
        row.setContentsMargins(6, 4, 6, 4)
        row.setSpacing(26)

        format_col = QVBoxLayout()
        format_col.setSpacing(8)
        format_label = QLabel("Report Format")
        format_label.setStyleSheet(LABEL_STYLE)
        format_col.addWidget(format_label)

        segmented = QFrame()
        segmented.setFixedWidth(320)
        segmented.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        segmented_layout = QHBoxLayout(segmented)
        segmented_layout.setContentsMargins(0, 0, 0, 0)
        segmented_layout.setSpacing(0)
        self.format_group = QButtonGroup(self)
        self.format_buttons = {}
        for name in ["HTML", "PDF"]:
            button = FormatButton(name)
            self.format_group.addButton(button)
            self.format_buttons[name] = button
            segmented_layout.addWidget(button)
        self.format_buttons["HTML"].setChecked(True)
        self.format_group.buttonClicked.connect(lambda _: self.refresh_preview())
        format_col.addWidget(segmented)
        row.addLayout(format_col)

        divider = QFrame()
        divider.setFixedWidth(1)
        divider.setStyleSheet(f"background-color: {COLORS['border']}; border: none;")
        row.addWidget(divider)

        content_col = QVBoxLayout()
        content_col.setSpacing(10)
        content_label = QLabel("Report Content")
        content_label.setStyleSheet(LABEL_STYLE)
        content_col.addWidget(content_label)
        checks = QHBoxLayout()
        checks.setSpacing(22)
        for text in ["Summary", "Issues", "Metrics", "Charts", "Recommendations"]:
            check = QCheckBox(text)
            check.setChecked(True)
            check.setMinimumHeight(28)
            checks.addWidget(check)
        checks.addStretch()
        content_col.addLayout(checks)
        row.addLayout(content_col, 1)

        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setIcon(make_icon("report", COLORS["primary_text"], 22))
        self.generate_btn.setIconSize(QSize(20, 20))
        self.generate_btn.setMinimumSize(210, 54)
        self.generate_btn.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { border-radius: 8px; font-size: 14px; }")
        self.generate_btn.clicked.connect(self.generate_report)
        row.addWidget(self.generate_btn, 0, Qt.AlignmentFlag.AlignBottom)

        panel.layout.addLayout(row)
        return panel

    def _build_preview_panel(self):
        panel = SectionPanel("Report Preview", "eye")
        subtitle = QLabel("Preview of the generated report")
        subtitle.setStyleSheet(LABEL_STYLE)
        panel.layout.insertWidget(1, subtitle)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(430)
        self.preview.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text']};
                padding: 22px;
                font-size: 14px;
            }}
        """)
        panel.layout.addWidget(self.preview)
        return panel

    def _build_details_panel(self):
        panel = SectionPanel("Report Details", "info")
        subtitle = QLabel("Information about the generated report")
        subtitle.setStyleSheet(LABEL_STYLE)
        panel.layout.insertWidget(1, subtitle)

        self.details = DetailRows()
        panel.layout.addWidget(self.details)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        self.open_btn = self._detail_button("Open Report", "open", primary=True)
        self.folder_btn = self._detail_button("Show in Folder", "folder")
        self.share_btn = self._detail_button("Share", "share")
        self.open_btn.setEnabled(False)
        self.folder_btn.setEnabled(False)
        self.share_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_report)
        self.folder_btn.clicked.connect(self.show_in_folder)
        self.share_btn.clicked.connect(self.copy_report_path)
        buttons.addWidget(self.open_btn)
        buttons.addWidget(self.folder_btn)
        buttons.addWidget(self.share_btn)
        panel.layout.addLayout(buttons)

        self.status_card = StatusCard()
        self.status_card.set_waiting()
        panel.layout.addWidget(self.status_card)
        panel.layout.addStretch()
        return panel

    def _detail_button(self, text: str, icon_name: str, primary: bool = False):
        button = QPushButton(text)
        button.setIcon(make_icon(icon_name, COLORS["primary_text"] if primary else COLORS["text"], 20))
        button.setIconSize(QSize(18, 18))
        button.setMinimumHeight(48)
        if primary:
            button.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { border-radius: 8px; }")
        return button

    def selected_format(self) -> str:
        for name, button in self.format_buttons.items():
            if button.isChecked():
                return name
        return "HTML"

    def refresh_preview(self):
        latest = self.repo.get_latest_analysis()
        now = datetime.now().strftime("%b %d, %Y  %I:%M %p")
        fmt = self.selected_format()
        if not latest:
            self.project_chip.findChildren(QLabel)[-1].setText("No project scanned")
            self.preview.setHtml(self._preview_html("No project scanned", 0, 0, 0, 0, now))
            self.details.set_value("Project", "No project scanned")
            self.details.set_value("Format", fmt)
            self.details.set_value("Generated On", now)
            self.details.set_value("Total Issues", "0")
            self.details.set_value("Report Size", "-")
            self.details.set_value("Status", "Waiting for scan", COLORS["medium"])
            self.status_card.set_waiting()
            return

        project = self.repo.get_project_by_id(latest.project_id)
        project_name = project_name_from_path(project.path if project else "")
        issues = self.repo.get_issues_for_analysis(latest.analysis_id)
        self.project_chip.findChildren(QLabel)[-1].setText(project_name)
        self.preview.setHtml(self._preview_html(
            project_name, latest.quality_score, latest.security_score,
            latest.complexity_score, latest.maintainability_score, now
        ))
        self.details.set_value("Project", project_name)
        self.details.set_value("Format", fmt)
        self.details.set_value("Generated On", now)
        self.details.set_value("Total Issues", str(len(issues)))
        self.details.set_value("Report Size", self._estimated_size(len(issues)))
        self.details.set_value("Status", "Ready", COLORS["primary"])
        if not self.last_report_path:
            self.status_card.set_waiting()

    def _preview_html(self, project_name, quality, security, complexity, maintainability, timestamp):
        return f"""
        <div style="font-family: Segoe UI; color: {COLORS['text']};">
          <p align="center" style="color:{COLORS['primary']}; font-size:22px; font-weight:800; margin:10px 0 4px 0;">{APP_NAME}</p>
          <p align="center" style="font-size:26px; font-weight:900; margin:0;">Code Quality Report</p>
          <p align="center" style="font-size:15px; margin:10px 0 22px 0;">{project_name}</p>
          <hr style="border:0; border-top:1px solid {COLORS['border']}; margin: 8px 0 20px 0;" />
          <table width="100%" cellspacing="12">
            <tr>
              {self._metric_cell("Quality", quality, COLORS["primary"])}
              {self._metric_cell("Security", security, COLORS["danger"])}
              {self._metric_cell("Complexity", complexity, COLORS["medium"])}
              {self._metric_cell("Maintainability", maintainability, COLORS["info"])}
            </tr>
          </table>
          <h3 style="font-size:18px; margin:24px 0 8px 0;">Overview</h3>
          <p style="color:{COLORS['muted']}; font-size:15px; line-height:1.45;">
            This report provides a comprehensive analysis of the code quality, security, and maintainability of the project.
            It includes key metrics, identified issues, and recommendations for improvement.
          </p>
          <hr style="border:0; border-top:1px solid {COLORS['border']}; margin: 18px 0 12px 0;" />
          <table width="100%"><tr>
            <td style="color:{COLORS['subtle']};">Generated by {APP_NAME} v{APP_VERSION}</td>
            <td align="right" style="color:{COLORS['muted']};">{timestamp}</td>
          </tr></table>
        </div>
        """

    def _metric_cell(self, label, value, color):
        return f"""
        <td style="background:#0b1b29; border:1px solid {COLORS['border']}; border-radius:8px; padding:16px;">
          <div style="color:{COLORS['muted']}; font-size:13px;">{label}</div>
          <div style="color:{color}; font-size:24px; font-weight:900;">{float(value):.1f} <span style="color:{COLORS['muted']}; font-size:12px;">/ 100</span></div>
        </td>
        """

    def _estimated_size(self, issue_count: int) -> str:
        size_kb = 118 + issue_count * 6
        return f"{size_kb} KB"

    def generate_report(self):
        latest = self.repo.get_latest_analysis()
        if not latest:
            QMessageBox.warning(self, "No Data", "No analysis data available. Run an analysis first.")
            return

        fmt = self.selected_format().lower()
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
            elif fmt == "pdf":
                gen.generate_pdf(file_path)
            self.last_report_path = file_path
            self.open_btn.setEnabled(True)
            self.folder_btn.setEnabled(True)
            self.share_btn.setEnabled(True)
            self.refresh_preview()
            self.details.set_value("Report Size", self._file_size(file_path))
            self.details.set_value("Status", "Ready", COLORS["primary"])
            self.status_card.set_success(file_path)
        except ImportError as e:
            QMessageBox.warning(self, "Missing Dependency", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

    def open_report(self):
        if self.last_report_path and os.path.exists(self.last_report_path):
            os.startfile(self.last_report_path)

    def show_in_folder(self):
        if self.last_report_path and os.path.exists(self.last_report_path):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(self.last_report_path)])

    def copy_report_path(self):
        if self.last_report_path:
            QApplication.clipboard().setText(self.last_report_path)

    def _file_size(self, path: str) -> str:
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} B"
        return f"{size / 1024:.0f} KB"
