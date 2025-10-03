from PyQt5 import QtWidgets, QtCore, QtGui
from backend.internal_data import InternalData
from frontend.widgets.toggle_switch import ToggleSwitch

class SettingsPage(QtWidgets.QFrame):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings
        self.setupUi()

    def setupUi(self):
        self.setObjectName("settings_page")
        self.setGeometry(QtCore.QRect(0, 110, 1411, 661))
        self.setStyleSheet("QFrame {background-color: #202120;}")
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        self.source_sans_3 = QtGui.QFontDatabase.applicationFontFamilies(
            QtGui.QFontDatabase.addApplicationFontFromData(InternalData.source_sans_3)
        )[0]
        self.source_sans_3_black = QtGui.QFontDatabase.applicationFontFamilies(
            QtGui.QFontDatabase.addApplicationFontFromData(InternalData.source_sans_3_black)
        )[0]

        self.title_label = self.create_label(
            50, 40, 241, 61, "Settings", self.source_sans_3_black, 16, True,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter
        )

        self.scroll_frame = self.create_frame(
            self, 50, 140, 1311, 531,
            stylesheet = "QScrollArea { border: none; }\nQScrollBar:vertical { background: transparent; width: 12px; margin: 2px 0 2px 0; border-radius: 6px; }\nQScrollBar::handle:vertical { background: rgb(90,93,90); min-height: 20px; border-radius: 6px; }\nQScrollBar::handle:vertical:hover { background: rgb(80,83,80); }\nQScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; height: 0; }\nQScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }\n"
        )

        self.scroll_area = QtWidgets.QScrollArea(self.scroll_frame)
        self.scroll_area.setGeometry(QtCore.QRect(10, 0, 1291, 501))
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scrollable_content = QtWidgets.QWidget()
        self.scrollable_content.setGeometry(QtCore.QRect(0, 0, 1279, 0))
        self.scrollable_content.setStyleSheet("background-color: transparent;")

        self.vertical_layout = QtWidgets.QVBoxLayout(self.scrollable_content)

        self.scrollable_content_frame = self.create_frame(self.scrollable_content, 0, 0, 1279, 658, "transparent")
        self.scrollable_content_frame.setMinimumSize(QtCore.QSize(0, 640))

        self.information_rows = {}
        self.create_info_row("Theme", "Dark")
        self.create_info_row("Start on boot", "Enabled")
        self.create_info_row("Check for updates", "Enabled")
        self.minimize_to_tray_toggle = ToggleSwitch()
        self.minimize_to_tray_toggle.setChecked(self.settings.get('minimize_to_tray'))
        self.minimize_to_tray_toggle.update()
        self.minimize_to_tray_toggle.toggled.connect(self.update_minimize_to_tray)
        self.create_info_row("Minimize to Tray on Exit", self.minimize_to_tray_toggle)


        self.vertical_layout.addWidget(self.scrollable_content_frame)
        self.scroll_area.setWidget(self.scrollable_content)

    def update_minimize_to_tray(self, state):
        print(f"Updating minimize_to_tray to: {state}")
        self.settings.set('minimize_to_tray', state)

    def create_frame(
        self,
        parent,
        x_position: int,
        y_position: int,
        width: int,
        height: int,
        bg_color: str = "transparent",
        border: str = "none",
        stylesheet: str = None,
    ):
        frame = QtWidgets.QFrame(parent)
        frame.setGeometry(QtCore.QRect(x_position, y_position, width, height))
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        if stylesheet:
            frame.setStyleSheet(stylesheet)
        else:
            frame.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border: {border}; }}")
        return frame

    def create_info_row(
        self,
        label_text: str,
        value: [str, QtWidgets.QWidget] = "",
        index: int = -1,
    ):
        if index == -1:
            index = len(self.information_rows)
        
        assert index not in self.information_rows, "Index already exists in information rows"

        double_label = True if value else False
        dark = index != 0 and (index + 1) % 2 == 0
        
        self.information_rows[index] = self.create_frame(
            parent = self.scrollable_content_frame,
            x_position = 0,
            y_position = -10 if index == 0 else index * 50,
            width = 1241,
            height = 51,
            bg_color = "rgb(42, 43, 42)" if dark else "transparent",
        )

        self.create_label(
            x_position = 10,
            y_position = 0,
            width = 211 if double_label else 471,
            height = 51,
            text = label_text,
            font_name = self.source_sans_3,
            font_size = 12,
            is_bold = False,
            parent = self.information_rows[index],
            alignment = QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter, # type: ignore
        )

        if isinstance(value, str):
            self.create_label(
                x_position = 1020,
                y_position = 0,
                width = 211,
                height = 51,
                text = value, # type: ignore
                font_name = self.source_sans_3,
                font_size = 12,
                is_bold = False,
                parent = self.information_rows[index],
                alignment = QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter, # type: ignore
            )
        elif isinstance(value, QtWidgets.QWidget):
            value.setParent(self.information_rows[index])
            value.setGeometry(QtCore.QRect(1180, 15, 51, 21))

        
        self.scrollable_content.setMinimumSize(QtCore.QSize(0, (index + 1) * 50 + 15))

    def create_label(
        self,
        x_position: int,
        y_position: int,
        width: int,
        height: int,
        text: str,
        font_name: str,
        font_size: int,
        is_bold: bool = False,
        parent: QtWidgets.QWidget = None,
        alignment:QtCore.Qt.AlignmentFlag =QtCore.Qt.AlignmentFlag.AlignCenter,
    ):
        label = QtWidgets.QLabel(parent or self)
        label.setGeometry(QtCore.QRect(x_position, y_position, width, height))
        font = QtGui.QFont()
        font.setFamily(font_name)
        font.setPointSize(font_size)
        font.setBold(is_bold)
        font.setWeight(75 if is_bold else 50)
        label.setFont(font)
        label.setStyleSheet("QLabel { background-color: none; color: white; }")
        label.setAlignment(alignment)
        label.setText(text)
        return label
