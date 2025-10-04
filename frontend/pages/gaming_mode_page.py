import json
import os
import time
import psutil
import win32gui
import win32ui
import win32con
import win32api

from PyQt5 import QtCore, QtGui, QtWidgets

from backend.nyx_base import NyxBase
from backend.logger import Logger
from backend.timer import Timer

from backend.internal_data import InternalData

class GameWidget(QtWidgets.QWidget):
    def __init__(self, game, parent=None, font=None):
        super().__init__(parent)
        self.game = game
        self.parent = parent

        self.setFixedSize(100, 130)
        self.setStyleSheet("background-color: transparent;")

        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setGeometry(10, 10, 80, 80)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)

        self.name_label = QtWidgets.QLabel(self)
        self.name_label.setGeometry(10, 90, 80, 30)
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.setStyleSheet("color: white;")
        if font:
            font_obj = QtGui.QFont()
            font_obj.setFamily(font)
            font_obj.setPointSize(10)
            self.name_label.setFont(font_obj)

        self.delete_button = QtWidgets.QPushButton(self)
        self.delete_button.setGeometry(75, 5, 20, 20)
        self.delete_button.setIcon(QtGui.QIcon("frontend/icons/minus.png"))
        self.delete_button.setStyleSheet("background-color: transparent; border: none;")
        self.delete_button.hide()
        self.delete_button.clicked.connect(self.delete_game)

        self.set_icon()
        self.name_label.setText(os.path.splitext(self.game["name"])[0])

    def set_icon(self):
        icon = self.parent.get_icon(self.game["path"])
        self.icon_label.setPixmap(icon.scaled(64, 64, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def mousePressEvent(self, event):
        self.parent.select_game(self)

    def delete_game(self):
        self.parent.delete_game(self.game)

class GamingModePage(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__()
        with Timer(__class__.__name__):
            self.logger = Logger()
            self.nyx_base = NyxBase()
            self.games = self.load_games()
            self.title = "Gaming Mode"
            self.selected_game = None
            
            self.setGeometry(QtCore.QRect(0, 110, 1411, 661))
            self.setStyleSheet("QFrame {background-color: #202120;}")
            self.setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.setFrameShadow(QtWidgets.QFrame.Raised)
            self.setObjectName("section_gamingMode")
            self.setParent(parent)

            self.source_sans_3 = QtGui.QFontDatabase.applicationFontFamilies(
                QtGui.QFontDatabase.addApplicationFontFromData(InternalData.source_sans_3)
            )[0]
            self.source_sans_3_black = QtGui.QFontDatabase.applicationFontFamilies(
                QtGui.QFontDatabase.addApplicationFontFromData(InternalData.source_sans_3_black)
            )[0]

            self.title_label = QtWidgets.QLabel(self)
            self.title_label.setGeometry(QtCore.QRect(50, 40, 241, 61))
            font = QtGui.QFont()
            font.setFamily(self.source_sans_3_black)
            font.setPointSize(16)
            font.setBold(True)
            self.title_label.setFont(font)
            self.title_label.setStyleSheet("color: white;")
            self.title_label.setText("Gaming Mode")
            self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)

            self.description_label = QtWidgets.QLabel(self)
            self.description_label.setGeometry(QtCore.QRect(260, 40, 1000, 61))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.description_label.setFont(font)
            self.description_label.setStyleSheet("color: #808080;")
            self.description_label.setText("MSI Gaming Mode Provides auto-tuning function for the game you are playing with the best possible visual & audio lighting setting and brings you a superior gaming experience!")
            self.description_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)

            self.add_game_button = QtWidgets.QPushButton(self)
            self.add_game_button.setGeometry(QtCore.QRect(50, 105, 150, 30))
            font = QtGui.QFont()
            font.setFamily(self.source_sans_3_black)
            font.setPointSize(10)
            self.add_game_button.setFont(font)
            self.add_game_button.setText("Add Game")
            self.add_game_button.setStyleSheet("QPushButton { background-color: white; color: black; border-radius: 5px; } QPushButton:hover { background-color: #DDDDDD; }")
            self.add_game_button.clicked.connect(self.add_game)

            self.scroll_area = QtWidgets.QScrollArea(self)
            self.scroll_area.setGeometry(QtCore.QRect(50, 150, 1311, 461))
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setStyleSheet("QScrollArea { border: none; }")

            self.games_widget = QtWidgets.QWidget()
            self.games_widget.setStyleSheet("background-color: #282928; border-radius: 10px;")
            self.scroll_area.setWidget(self.games_widget)
            self.games_layout = QtWidgets.QGridLayout(self.games_widget)
            self.games_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

            self.populate_games_list()

            self.process_checker = ProcessChecker(self.games)
            self.process_checker.game_started.connect(self.game_started)
            self.process_checker.game_stopped.connect(self.game_stopped)
            self.process_checker.start()

    def load_games(self):
        try:
            with open("backend/games.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_games(self):
        with open("backend/games.json", "w") as f:
            json.dump(self.games, f, indent=4)

    def add_game(self):
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Game Executable", "", "Executable files (*.exe)")
        if file_path:
            game_name = os.path.basename(file_path)
            self.games.append({"name": game_name, "path": file_path})
            self.save_games()
            self.populate_games_list()

    def populate_games_list(self):
        for i in reversed(range(self.games_layout.count())):
            self.games_layout.itemAt(i).widget().setParent(None)

        for i, game in enumerate(self.games):
            row = i // 10
            col = i % 10
            game_widget = GameWidget(game, self, font=self.source_sans_3)
            self.games_layout.addWidget(game_widget, row, col)

    def get_icon(self, file_path):
        try:
            large, small = win32gui.ExtractIconEx(file_path, 0)
            win32gui.DestroyIcon(small[0])
            hicon = large[0]
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, 32, 32)
            hdc = hdc.CreateCompatibleDC()
            hdc.SelectObject(hbmp)
            hdc.DrawIcon((0, 0), hicon)
            
            bmp_info = hbmp.GetInfo()
            bmp_str = hbmp.GetBitmapBits(True)
            
            image = QtGui.QImage(bmp_str, bmp_info['bmWidth'], bmp_info['bmHeight'], QtGui.QImage.Format_ARGB32)
            return QtGui.QPixmap.fromImage(image)
        except Exception as e:
            self.logger.error(f"Error extracting icon: {e}")
            return QtGui.QPixmap("frontend/icons/joystick.png")

    def select_game(self, game_widget):
        if self.selected_game:
            self.selected_game.delete_button.hide()
        self.selected_game = game_widget
        self.selected_game.delete_button.show()

    def delete_game(self, game_to_delete):
        self.games = [game for game in self.games if game["path"] != game_to_delete["path"]]
        self.save_games()
        self.populate_games_list()

    def game_started(self, game_name):
        self.logger.debug(f"Game started: {game_name}")
        _, self.original_power_plan = self.nyx_base.get_power_plan()
        high_performance_guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
        self.nyx_base.set_power_plan(high_performance_guid)

    def game_stopped(self, game_name):
        self.logger.debug(f"Game stopped: {game_name}")
        self.nyx_base.set_power_plan(self.original_power_plan)

class ProcessChecker(QtCore.QThread):
    game_started = QtCore.pyqtSignal(str)
    game_stopped = QtCore.pyqtSignal(str)

    def __init__(self, games):
        super().__init__()
        self.games = games
        self.running_games = set()

    def run(self):
        while True:
            running_processes = {p.name() for p in psutil.process_iter()}
            for game in self.games:
                game_name = os.path.basename(game["path"])
                if game_name in running_processes:
                    if game_name not in self.running_games:
                        self.running_games.add(game_name)
                        self.game_started.emit(game_name)
                elif game_name in self.running_games:
                    self.running_games.remove(game_name)
                    self.game_stopped.emit(game_name)
            time.sleep(5)
