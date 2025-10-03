from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor
from backend.logger import Logger

class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger()
        self.logger.debug("ToggleSwitch initialized")
        self.setCursor(Qt.PointingHandCursor)
        self._bg_color = QColor("#202120")
        self._on_color = QColor("#00BFFF")
        self._off_color = QColor("#404040")
        self._thumb_color = QColor("#FFFFFF")
        self.stateChanged.connect(self.on_state_changed)

    def on_state_changed(self, state):
        self.logger.debug(f"ToggleSwitch state changed to: {state}")
        self.update()

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self.isChecked())
        event.accept()

    def paintEvent(self, event):
        self.logger.debug("ToggleSwitch paintEvent called")
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        rect = QRect(0, 0, self.width(), self.height())

        if self.isChecked():
            self.logger.debug("ToggleSwitch is checked")
            p.setBrush(self._on_color)
            p.drawRoundedRect(rect, self.height() / 2, self.height() / 2)
            p.setBrush(self._thumb_color)
            p.drawEllipse(QRect(self.width() - self.height(), 0, self.height(), self.height()))
        else:
            self.logger.debug("ToggleSwitch is not checked")
            p.setBrush(self._off_color)
            p.drawRoundedRect(rect, self.height() / 2, self.height() / 2)
            p.setBrush(self._thumb_color)
            p.drawEllipse(QRect(0, 0, self.height(), self.height()))

        p.end()
