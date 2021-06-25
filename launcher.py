import sys
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import window

class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        desktop = QApplication.desktop()
        self.w = desktop.width()
        self.h = desktop.height()
        self.setFixedSize(int(self.w*0.6),int(self.h*0.6))
        self.move(int(self.w*0.2),int(self.h*0.2))
        self.launch()
    def launch(self):
        self.show()
