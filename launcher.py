import sys
import time
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
        self.setFixedSize(int(self.w*0.5),int(self.h*0.5))
        self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        self.move(int(self.w*0.25),int(self.h*0.25))
        self.launch()

    def launch(self):
        #read stylesheet
        styleFile = open("launcherStyle.css","r")
        stylesheet = styleFile.read()
        self.setStyleSheet(stylesheet)

        windowLayout = QGridLayout()
        windowLayout.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.setLayout(windowLayout)

        # icon
        icon = QWidget()
        icon.setObjectName("icon")
        icon.setFixedSize(int(self.width()*0.07),int(self.width()*0.07))
        windowLayout.addWidget(icon,0,0)
        # title
        title = QLabel("Screen Recorder")
        title.setObjectName("title")
        title.setFixedSize(int(self.width()*0.5),int(self.height()*0.1))
        windowLayout.addWidget(title,0,1)

        # content
        txt = QLabel()
        txt.setObjectName("text")
        txt.setFixedSize(int(self.width()*0.6),int(self.height()*0.85))
        windowLayout.addWidget(txt,1,1)

        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcherWindow = Launcher()
    sys.exit(app.exec_())
