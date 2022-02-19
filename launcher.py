import sys
import os
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

        self.setWindowTitle("Screen Recorder")
        self.setFixedSize(int(self.w*0.4),int(self.h*0.2))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.move(int(self.w*0.3),int(self.h*0.4))

        if not os.path.exists("./videos"):
            os.mkdir("videos")

        self.launch()

    def launch(self):
        #read stylesheet
        styleFile = open("launcherStyle.css","r")
        stylesheet = styleFile.read()
        self.setStyleSheet(stylesheet)

        windowLayout = QVBoxLayout()
        windowLayout.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.setLayout(windowLayout)

        titleLayout = QHBoxLayout()
        titleLayout.setAlignment(Qt.AlignLeft)
        # icon
        icon = QWidget()
        icon.setObjectName("icon")
        icon.setFixedSize(int(self.width()*0.07),int(self.width()*0.07))
        titleLayout.addWidget(icon)
        # title
        title = QLabel("Screen Recorder")
        title.setObjectName("title")
        title.setFixedSize(int(self.width()*0.5),int(self.height()*0.1))
        titleLayout.addWidget(title)
        windowLayout.addLayout(titleLayout)
        # version
        version = QLabel("v2.1.1")
        version.setObjectName("version")
        version.setFixedSize(int(self.width()*0.2),int(self.height()*0.05))
        titleLayout.addWidget(version,0,(Qt.AlignRight|Qt.AlignBottom))

        # state
        self.state = QLabel("Launching...")
        self.state.setObjectName("state")
        self.state.setFixedSize(int(self.width()*0.6),int(self.height()*0.05))
        windowLayout.addWidget(self.state)

        # content
        txt = QLabel()
        txt.setObjectName("text")
        txt.setFixedSize(int(self.width()*0.9),int(self.height()*0.75))
        txt.setText('''©2021 Administator-user''')
        windowLayout.addWidget(txt)

        self.show()

        self.launchWindow()
    
    # launch window
    def launchWindow(self):
        win = window.Window()
        win.showWindow()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcherWindow = Launcher()
    sys.exit(app.exec_())
