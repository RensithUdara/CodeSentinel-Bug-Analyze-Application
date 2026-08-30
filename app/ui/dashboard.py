"""
Dashboard page with summary metrics, charts, and priority findings.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QFrame

from app.database.repository import Repository
from app.ui.widgets.charts import MplCanvas
from app.ui.widgets.kit import PageHeader, InfoChip, StatCard, SectionPanel, BigProgressCard, clear_layout, project_name_from_path, format_timestamp
from app.ui.widgets.icons import make_icon
from app.ui.theme import COLORS, LABEL_STYLE, META_LABEL_STYLE, PRIMARY_BUTTON_STYLE, severity_color


class FindingsMixCard(SectionPanel):
    def __init__(self, critical: int, high: int, medium: int, low: int):
        super().__init__("Findings Mix", "issue")
        total = critical + high + medium + low
        total_row = QHBoxLayout()
        total_row.addStretch()
        total_label = QLabel("Total")
        total_label.setStyleSheet(LABEL_STYLE)
        total_value = QLabel(str(total))
        total_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_value.setMinimumWidth(44)
        total_value.setStyleSheet(f"background-color: #142438; color: {COLORS['text']}; border-radius: 8px; padding: 7px 12px; font-weight: 800;")
        total_row.addWidget(total_label)
        total_row.addWidget(total_value)
        self.layout.addLayout(total_row)

        for name, count, color in [
            ("Critical", critical, COLORS["critical"]),
            ("High", high, COLORS["high"]),
            ("Medium", medium, COLORS["medium"]),
            ("Low", low, COLORS["low"]),
        ]:
            row = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 13px;")
            label = QLabel(name)
            label.setStyleSheet(LABEL_STYLE)
            value = QLabel(str(count))
            value.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 800;")
            row.addWidget(dot)
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            self.layout.addLayout(row)


class DebtCard(SectionPanel):
    def __init__(self, hours: float):
        super().__init__("Technical Debt", "clock")
        value = QLabel(f"{hours:.1f}h")
        value.setStyleSheet(f"color: {COLORS['high']}; font-size: 34px; font-weight: 850;")
        note = QLabel("Estimated time to resolve all findings.")
        note.setStyleSheet(LABEL_STYLE)
        self.layout.addWidget(value)
        self.layout.addWidget(note)
        self.layout.addStretch()


class DashboardWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.repo = Repository(db_manager)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        root.addWidget(scroll)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(18)
        scroll.setWidget(content)

        self.load_dashboard()

    def load_dashboard(self):
        clear_layout(self.content_layout)
        latest = self.repo.get_latest_analysis()
        project = self.repo.get_project_by_id(latest.project_id) if latest else None
        project_name = project_name_from_path(project.path if project else "")

        header_row = QHBoxLayout()
        header_row.addWidget(PageHeader("Overview", "Mission Control", "Analyze. Improve. Build Better Code."))
        header_row.addStretch()
        header_row.addWidget(InfoChip("Project", project_name, "folder"))
        header_row.addWidget(InfoChip("Last Scan", format_timestamp(latest.timestamp if latest else None), "clock"))
        scan_again = QPushButton("Scan Again")
        scan_again.setIcon(make_icon("refresh", COLORS["primary"], 22))
        scan_again.setIconSize(QSize(20, 20))
        scan_again.setMinimumHeight(58)
        scan_again.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { background-color: transparent; color: #2df29d; border: 1px solid #2df29d; border-radius: 8px; padding: 0 22px; } QPushButton:hover { background-color: rgba(45, 242, 157, 0.12); }")
        scan_again.clicked.connect(lambda: self.window().analyze_project() if hasattr(self.window(), "analyze_project") else None)
        header_row.addWidget(scan_again)
        self.content_layout.addLayout(header_row)

        if not latest:
            empty = SectionPanel()
            empty.layout.addWidget(QLabel("No scan yet. Use Scan Project to build the first quality snapshot."))
            self.content_layout.addWidget(empty)
            self.content_layout.addStretch()
            return

        metrics = QHBoxLayout()
        metrics.setSpacing(16)
        metrics.addWidget(StatCard("Quality Score", f"{latest.quality_score:.0f}", COLORS["low"], "shield"))
        metrics.addWidget(StatCard("Complexity", f"{latest.complexity_score:.0f}", COLORS["medium"], "layers"))
        metrics.addWidget(StatCard("Security", f"{latest.security_score:.0f}", COLORS["danger"], "shield"))
        metrics.addWidget(StatCard("Maintainability", f"{latest.maintainability_score:.0f}", COLORS["info"], "wrench"))
        self.content_layout.addLayout(metrics)

        issues = self.repo.get_issues_for_analysis(latest.analysis_id)
        critical = sum(1 for item in issues if item.severity == "Critical")
        high = sum(1 for item in issues if item.severity == "High")
        medium = sum(1 for item in issues if item.severity == "Medium")
        low = sum(1 for item in issues if item.severity == "Low")

        summary = QHBoxLayout()
        summary.setSpacing(16)
        summary.addWidget(FindingsMixCard(critical, high, medium, low), 1)
        summary.addWidget(BigProgressCard(int(latest.quality_score)), 1)
        summary.addWidget(DebtCard(latest.technical_debt), 1)
        self.content_layout.addLayout(summary)

        chart_panel = SectionPanel("Findings by Severity", "chart")
        chart = MplCanvas(self, width=10, height=2.5, dpi=100)
        chart.setMinimumHeight(220)
        chart.axes.bar(
            ["Low", "Medium", "High", "Critical"],
            [low, medium, high, critical],
            color=[COLORS["low"], COLORS["medium"], COLORS["high"], COLORS["critical"]],
            width=0.36,
        )
        chart.axes.set_ylabel("Count", color=COLORS["muted"])
        chart.axes.set_title("")
        chart_panel.layout.addWidget(chart)
        self.content_layout.addWidget(chart_panel)

        priority = SectionPanel("Priority Findings", "issue")
        if issues:
            for issue in issues[:3]:
                row = QFrame()
                row.setStyleSheet(f"QFrame {{ background-color: #071622; border: 1px solid {COLORS['border']}; border-radius: 8px; }}")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(14, 10, 14, 10)
                row_layout.setSpacing(12)
                color = severity_color(issue.severity)
                dot = QLabel("●")
                dot.setStyleSheet(f"color: {color}; font-size: 14px;")
                title = QLabel(f"{issue.type} - {issue.category}")
                title.setStyleSheet(f"color: {COLORS['text']}; font-weight: 700;")
                msg = QLabel(issue.message[:90] + "..." if len(issue.message) > 90 else issue.message)
                msg.setStyleSheet(META_LABEL_STYLE)
                text = QVBoxLayout()
                text.addWidget(title)
                text.addWidget(msg)
                badge = QLabel(issue.severity)
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                badge.setStyleSheet(f"color: {color}; background-color: rgba(255,255,255,0.07); border-radius: 7px; padding: 6px 14px; font-weight: 800;")
                location = QLabel(f"{issue.file_path}:{issue.line or ''}")
                location.setStyleSheet(META_LABEL_STYLE)
                row_layout.addWidget(dot)
                row_layout.addLayout(text, 1)
                row_layout.addWidget(badge)
                row_layout.addWidget(location)
                priority.layout.addWidget(row)
        else:
            no_findings = QLabel("No priority findings in the latest scan.")
            no_findings.setStyleSheet(LABEL_STYLE)
            priority.layout.addWidget(no_findings)
        self.content_layout.addWidget(priority)
        self.content_layout.addStretch()
