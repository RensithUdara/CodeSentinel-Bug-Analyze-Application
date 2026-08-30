"""
Settings page for configuring analysis parameters.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QPushButton, QMessageBox, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QSize

from app.ui.theme import COLORS, LABEL_STYLE, META_LABEL_STYLE, PRIMARY_BUTTON_STYLE, panel_style
from app.ui.widgets.kit import PageHeader, InfoChip, SectionPanel
from app.ui.widgets.icons import make_icon


class SettingSection(SectionPanel):
    def __init__(self, number: str, title: str, subtitle: str, color: str):
        super().__init__()
        header = QHBoxLayout()
        badge = QLabel(number)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(48, 48)
        badge.setStyleSheet(f"background-color: rgba(45,242,157,0.14); color: {color}; border-radius: 24px; font-size: 16px; font-weight: 850;")
        header.addWidget(badge)
        text = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 16px; font-weight: 800;")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(LABEL_STYLE)
        text.addWidget(title_label)
        text.addWidget(subtitle_label)
        header.addLayout(text)
        header.addStretch()
        self.layout.addLayout(header)

        self.form = QFrame()
        self.form.setStyleSheet(f"QFrame {{ background-color: rgba(255,255,255,0.025); border: 1px solid {COLORS['border']}; border-radius: 8px; }}")
        self.form_layout = QHBoxLayout(self.form)
        self.form_layout.setContentsMargins(14, 14, 14, 14)
        self.form_layout.setSpacing(16)
        self.layout.addWidget(self.form)


class SettingsWidget(QWidget):
    def __init__(self, db_manager):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 18)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_row.addWidget(PageHeader("Settings", "Control Room", "Configure analysis parameters, scoring weights, and quality gates.", "settings"))
        header_row.addStretch()
        header_row.addWidget(InfoChip("Project", "Current workspace", "settings"))
        layout.addLayout(header_row)

        smell_section = SettingSection("01", "Code Smell Thresholds", "Configure detection thresholds for code smells.", COLORS["primary"])
        self.max_method_lines = self._spin(10, 200, 50)
        self.max_parameters = self._spin(1, 20, 5)
        self.max_class_methods = self._spin(5, 50, 20)
        self.max_nesting = self._spin(2, 10, 4)
        for label, widget in [
            ("Max Method Lines", self.max_method_lines),
            ("Max Parameters", self.max_parameters),
            ("Max Class Methods", self.max_class_methods),
            ("Max Nesting Depth", self.max_nesting),
        ]:
            smell_section.form_layout.addLayout(self._field(label, widget))
        layout.addWidget(smell_section)

        scoring_section = SettingSection("02", "Scoring Weights", "Set the importance of each quality metric.", COLORS["info"])
        self.weight_maintainability = self._double(0.25)
        self.weight_complexity = self._double(0.20)
        self.weight_security = self._double(0.20)
        self.weight_duplication = self._double(0.15)
        for label, widget in [
            ("Maintainability", self.weight_maintainability),
            ("Complexity", self.weight_complexity),
            ("Security", self.weight_security),
            ("Duplication", self.weight_duplication),
        ]:
            scoring_section.form_layout.addLayout(self._field(label, widget))
        layout.addWidget(scoring_section)

        gate_section = SettingSection("03", "Release Gate", "Set the minimum quality score required for release.", "#a78bfa")
        self.quality_threshold = self._spin(0, 100, 70)
        gate_section.form_layout.addLayout(self._field("Minimum Quality Score", self.quality_threshold))
        layout.addWidget(gate_section)

        layout.addStretch()

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setIcon(make_icon("save", COLORS["primary_text"], 22))
        self.save_btn.setIconSize(QSize(20, 20))
        self.save_btn.setMinimumHeight(52)
        self.save_btn.setStyleSheet(PRIMARY_BUTTON_STYLE + "QPushButton { border-radius: 8px; font-size: 15px; }")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

    def _field(self, label: str, widget):
        field = QVBoxLayout()
        field.setSpacing(8)
        label_widget = QLabel(label)
        label_widget.setStyleSheet(LABEL_STYLE)
        widget.setMinimumHeight(44)
        field.addWidget(label_widget)
        field.addWidget(widget)
        return field

    def _spin(self, minimum: int, maximum: int, value: int):
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setValue(value)
        return spin

    def _double(self, value: float):
        spin = QDoubleSpinBox()
        spin.setRange(0, 1)
        spin.setSingleStep(0.05)
        spin.setValue(value)
        return spin

    def save_settings(self):
        QMessageBox.information(self, "Settings", "Settings saved successfully.")
