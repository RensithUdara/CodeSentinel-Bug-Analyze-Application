"""
Dashboard page with summary metrics, charts, and priority findings.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QFrame, QSizePolicy
)

from app.database.repository import Repository
from app.ui.widgets.charts import MplCanvas
from app.ui.widgets.icons import make_icon
from app.ui.widgets.kit import (
    PageHeader, InfoChip, StatCard, SectionPanel, BigProgressCard,
    clear_layout, project_name_from_path, format_timestamp
)
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
        total_value.setStyleSheet(
            f"background-color: #142438; color: {COLORS['text']}; "
            "border-radius: 8px; padding: 7px 12px; font-weight: 800;"
        )
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
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
            label = QLabel(name)
            label.setStyleSheet(LABEL_STYLE)
            value = QLabel(str(count))
            value.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 800;")
            row.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)
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


class PriorityFindingRow(QFrame):
    def __init__(self, issue):
        super().__init__()
        color = severity_color(issue.severity)
        location_text = _short_location(issue.file_path, issue.line)
        full_location = f"{issue.file_path}:{issue.line or ''}"

        self.setMinimumHeight(64)
        self.setMaximumHeight(68)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #071622;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border-color: {COLORS['border_hover']};
                background-color: #0a1d2c;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 9, 14, 9)
        layout.setSpacing(14)

        stripe = QFrame()
        stripe.setFixedSize(4, 42)
        stripe.setStyleSheet(f"background-color: {color}; border: none; border-radius: 2px;")
        layout.addWidget(stripe, 0, Qt.AlignmentFlag.AlignVCenter)

        text = QVBoxLayout()
        text.setSpacing(5)
        title = QLabel(f"{issue.type} - {issue.category}")
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title.setStyleSheet(
            f"color: {COLORS['text']}; font-weight: 800; font-size: 13px; "
            "background: transparent; border: none;"
        )
        msg = QLabel(issue.message[:110] + "..." if len(issue.message) > 110 else issue.message)
        msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        msg.setStyleSheet(
            f"color: {COLORS['muted']}; font-size: 12px; "
            "background: transparent; border: none;"
        )
        text.addWidget(title)
        text.addWidget(msg)
        layout.addLayout(text, 1)

        badge = QLabel(issue.severity)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(92, 38)
        badge.setStyleSheet(f"""
            color: {color};
            background-color: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.04);
            border-radius: 8px;
            font-weight: 800;
        """)
        layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)

        location = QLabel(location_text)
        location.setToolTip(full_location)
        location.setFixedWidth(390)
        location.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        location.setStyleSheet(
            f"color: {COLORS['muted']}; font-size: 12px; "
            "background: transparent; border: none;"
        )
        layout.addWidget(location, 0, Qt.AlignmentFlag.AlignVCenter)


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
        scan_again.setStyleSheet(
            PRIMARY_BUTTON_STYLE +
            "QPushButton { background-color: transparent; color: #2df29d; "
            "border: 1px solid #2df29d; border-radius: 8px; padding: 0 22px; } "
            "QPushButton:hover { background-color: rgba(45, 242, 157, 0.12); }"
        )
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
            severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
            for issue in sorted(issues, key=lambda item: severity_order.get(item.severity, 4))[:3]:
                priority.layout.addWidget(PriorityFindingRow(issue))
        else:
            no_findings = QLabel("No priority findings in the latest scan.")
            no_findings.setStyleSheet(LABEL_STYLE)
            priority.layout.addWidget(no_findings)
        self.content_layout.addWidget(priority)
        self.content_layout.addStretch()


def _short_location(path: str, line) -> str:
    if not path:
        return f"Unknown:{line or ''}"
    normalized = path.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part]
    tail = "/".join(parts[-4:]) if len(parts) > 4 else normalized
    return f"{tail}:{line or ''}"
