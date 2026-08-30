"""
Lightweight line icons rendered as QIcon/QPixmap objects.
"""
from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

from app.ui.theme import COLORS


def make_icon(name: str, color: str = None, size: int = 22) -> QIcon:
    pixmap = make_pixmap(name, color, size)
    return QIcon(pixmap)


def make_pixmap(name: str, color: str = None, size: int = 22) -> QPixmap:
    color = color or COLORS["muted"]
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color), max(1.8, size / 12), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    s = float(size)
    n = name.lower()

    if n == "home":
        _poly(painter, s, [(0.18, 0.48), (0.5, 0.2), (0.82, 0.48)])
        painter.drawRect(QRectF(0.28 * s, 0.45 * s, 0.44 * s, 0.36 * s))
        painter.drawLine(QPointF(0.45 * s, 0.81 * s), QPointF(0.45 * s, 0.62 * s))
        painter.drawLine(QPointF(0.55 * s, 0.62 * s), QPointF(0.55 * s, 0.81 * s))
    elif n == "code":
        _poly(painter, s, [(0.42, 0.24), (0.28, 0.5), (0.42, 0.76)])
        _poly(painter, s, [(0.58, 0.24), (0.72, 0.5), (0.58, 0.76)])
        painter.drawLine(QPointF(0.52 * s, 0.2 * s), QPointF(0.46 * s, 0.8 * s))
    elif n in {"issue", "file", "report"}:
        path = QPainterPath()
        path.moveTo(0.28 * s, 0.14 * s)
        path.lineTo(0.6 * s, 0.14 * s)
        path.lineTo(0.78 * s, 0.32 * s)
        path.lineTo(0.78 * s, 0.86 * s)
        path.lineTo(0.28 * s, 0.86 * s)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawLine(QPointF(0.6 * s, 0.14 * s), QPointF(0.6 * s, 0.34 * s))
        painter.drawLine(QPointF(0.6 * s, 0.34 * s), QPointF(0.78 * s, 0.34 * s))
        if n == "issue":
            painter.drawLine(QPointF(0.5 * s, 0.38 * s), QPointF(0.5 * s, 0.62 * s))
            painter.drawPoint(QPointF(0.5 * s, 0.72 * s))
        else:
            painter.drawLine(QPointF(0.38 * s, 0.48 * s), QPointF(0.68 * s, 0.48 * s))
            painter.drawLine(QPointF(0.38 * s, 0.62 * s), QPointF(0.68 * s, 0.62 * s))
    elif n == "history":
        painter.drawArc(QRectF(0.18 * s, 0.18 * s, 0.64 * s, 0.64 * s), 30 * 16, 300 * 16)
        _poly(painter, s, [(0.21, 0.32), (0.19, 0.18), (0.34, 0.2)])
        painter.drawLine(QPointF(0.5 * s, 0.34 * s), QPointF(0.5 * s, 0.52 * s))
        painter.drawLine(QPointF(0.5 * s, 0.52 * s), QPointF(0.63 * s, 0.6 * s))
    elif n == "settings":
        painter.drawEllipse(QRectF(0.34 * s, 0.34 * s, 0.32 * s, 0.32 * s))
        for x1, y1, x2, y2 in [(0.5, 0.1, 0.5, 0.24), (0.5, 0.76, 0.5, 0.9), (0.1, 0.5, 0.24, 0.5), (0.76, 0.5, 0.9, 0.5), (0.22, 0.22, 0.32, 0.32), (0.68, 0.68, 0.78, 0.78), (0.78, 0.22, 0.68, 0.32), (0.32, 0.68, 0.22, 0.78)]:
            painter.drawLine(QPointF(x1 * s, y1 * s), QPointF(x2 * s, y2 * s))
    elif n == "chart":
        for x, h in [(0.26, 0.28), (0.48, 0.48), (0.7, 0.66)]:
            painter.drawLine(QPointF(x * s, 0.82 * s), QPointF(x * s, (0.82 - h) * s))
    elif n == "play":
        path = QPainterPath()
        path.moveTo(0.34 * s, 0.22 * s)
        path.lineTo(0.78 * s, 0.5 * s)
        path.lineTo(0.34 * s, 0.78 * s)
        path.closeSubpath()
        painter.setBrush(QColor(color))
        painter.drawPath(path)
    elif n == "refresh":
        painter.drawArc(QRectF(0.2 * s, 0.2 * s, 0.6 * s, 0.6 * s), 35 * 16, 275 * 16)
        _poly(painter, s, [(0.77, 0.31), (0.82, 0.15), (0.63, 0.2)])
    elif n == "folder":
        path = QPainterPath()
        path.moveTo(0.14 * s, 0.32 * s)
        path.lineTo(0.38 * s, 0.32 * s)
        path.lineTo(0.46 * s, 0.42 * s)
        path.lineTo(0.86 * s, 0.42 * s)
        path.lineTo(0.86 * s, 0.8 * s)
        path.lineTo(0.14 * s, 0.8 * s)
        path.closeSubpath()
        painter.drawPath(path)
    elif n == "clock":
        painter.drawEllipse(QRectF(0.18 * s, 0.18 * s, 0.64 * s, 0.64 * s))
        painter.drawLine(QPointF(0.5 * s, 0.32 * s), QPointF(0.5 * s, 0.52 * s))
        painter.drawLine(QPointF(0.5 * s, 0.52 * s), QPointF(0.64 * s, 0.6 * s))
    elif n == "shield":
        path = QPainterPath()
        path.moveTo(0.5 * s, 0.14 * s)
        path.lineTo(0.78 * s, 0.26 * s)
        path.lineTo(0.72 * s, 0.64 * s)
        path.quadTo(0.5 * s, 0.86 * s, 0.28 * s, 0.64 * s)
        path.lineTo(0.22 * s, 0.26 * s)
        path.closeSubpath()
        painter.drawPath(path)
    elif n == "layers":
        _poly(painter, s, [(0.5, 0.16), (0.82, 0.34), (0.5, 0.52), (0.18, 0.34), (0.5, 0.16)])
        _poly(painter, s, [(0.18, 0.5), (0.5, 0.68), (0.82, 0.5)])
        _poly(painter, s, [(0.18, 0.64), (0.5, 0.82), (0.82, 0.64)])
    elif n == "wrench":
        painter.drawLine(QPointF(0.32 * s, 0.72 * s), QPointF(0.68 * s, 0.36 * s))
        painter.drawArc(QRectF(0.58 * s, 0.12 * s, 0.28 * s, 0.28 * s), 45 * 16, 230 * 16)
        painter.drawEllipse(QRectF(0.2 * s, 0.66 * s, 0.16 * s, 0.16 * s))
    elif n == "search":
        painter.drawEllipse(QRectF(0.18 * s, 0.18 * s, 0.44 * s, 0.44 * s))
        painter.drawLine(QPointF(0.56 * s, 0.56 * s), QPointF(0.82 * s, 0.82 * s))
    elif n == "eye":
        path = QPainterPath()
        path.moveTo(0.12 * s, 0.5 * s)
        path.quadTo(0.5 * s, 0.18 * s, 0.88 * s, 0.5 * s)
        path.quadTo(0.5 * s, 0.82 * s, 0.12 * s, 0.5 * s)
        painter.drawPath(path)
        painter.drawEllipse(QRectF(0.42 * s, 0.42 * s, 0.16 * s, 0.16 * s))
    elif n == "save":
        painter.drawRect(QRectF(0.18 * s, 0.16 * s, 0.64 * s, 0.68 * s))
        painter.drawLine(QPointF(0.32 * s, 0.16 * s), QPointF(0.32 * s, 0.38 * s))
        painter.drawLine(QPointF(0.32 * s, 0.38 * s), QPointF(0.66 * s, 0.38 * s))
        painter.drawRect(QRectF(0.34 * s, 0.6 * s, 0.32 * s, 0.24 * s))
    elif n == "info":
        painter.drawEllipse(QRectF(0.18 * s, 0.18 * s, 0.64 * s, 0.64 * s))
        painter.drawLine(QPointF(0.5 * s, 0.46 * s), QPointF(0.5 * s, 0.68 * s))
        painter.drawPoint(QPointF(0.5 * s, 0.34 * s))
    elif n == "minimize":
        painter.drawLine(QPointF(0.25 * s, 0.68 * s), QPointF(0.75 * s, 0.68 * s))
    elif n == "maximize":
        painter.drawRect(QRectF(0.25 * s, 0.25 * s, 0.5 * s, 0.5 * s))
    elif n == "restore":
        painter.drawRect(QRectF(0.22 * s, 0.34 * s, 0.44 * s, 0.44 * s))
        painter.drawRect(QRectF(0.34 * s, 0.22 * s, 0.44 * s, 0.44 * s))
    elif n == "close":
        painter.drawLine(QPointF(0.28 * s, 0.28 * s), QPointF(0.72 * s, 0.72 * s))
        painter.drawLine(QPointF(0.72 * s, 0.28 * s), QPointF(0.28 * s, 0.72 * s))
    else:
        painter.drawEllipse(QRectF(0.24 * s, 0.24 * s, 0.52 * s, 0.52 * s))

    painter.end()
    return pixmap


def _poly(painter: QPainter, size: float, points):
    qpoints = [QPointF(x * size, y * size) for x, y in points]
    for start, end in zip(qpoints, qpoints[1:]):
        painter.drawLine(start, end)
