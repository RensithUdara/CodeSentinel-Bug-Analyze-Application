"""
Chart widgets using matplotlib embedded in PySide6.
"""
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QSizePolicy
from app.ui.theme import COLORS


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor(COLORS["surface"])
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.axes = self.fig.add_subplot(111)
        self._style_axes()

    def _style_axes(self):
        self.axes.set_facecolor(COLORS["surface"])
        self.axes.tick_params(colors=COLORS["muted"], labelsize=9)
        self.axes.xaxis.label.set_color(COLORS["muted"])
        self.axes.yaxis.label.set_color(COLORS["muted"])
        self.axes.title.set_color(COLORS["text"])
        for spine in self.axes.spines.values():
            spine.set_color(COLORS["border"])
        self.axes.grid(True, alpha=0.18, color=COLORS["border_hover"])
        self.axes.set_axisbelow(True)
        self.fig.tight_layout(pad=1.4)

    def clear(self):
        self.axes.clear()
        self._style_axes()
