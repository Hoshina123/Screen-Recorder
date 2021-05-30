import sys
import threading
import time

import cv2
import numpy as np
from PIL import ImageGrab
from PyQt5 import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Recorder(QWidget):
    def __init__(self):
        super().__init__()
        self.recordMode = 1
        self.desktop = QApplication.desktop()
        self.w = self.desktop.width()
        self.h = self.desktop.height()
        self.timeString = "00:00:00"

    #rewrite window events
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton and not self.isMaximized():
            self.m_flag=True
            self.m_Position=event.globalPos()-self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.SizeAllCursor)) 
    def mouseMoveEvent(self,QMouseEvent):
        if Qt.LeftButton and self.m_flag:  
            self.move(QMouseEvent.globalPos()-self.m_Position)
            QMouseEvent.accept()
    def mouseReleaseEvent(self,QMouseEvent):
        self.m_flag=False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def record(self):
        #initalize
        desktop = ImageGrab.grab()
        w,h = desktop.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        currentTime = time.localtime()
        videoName = time.strftime("%Y%m%d-%H%M%S")+".avi"
        video = cv2.VideoWriter(videoName,fourcc,5,(w,h))
        while True:
            if self.recordMode == 1:
                currentImg = ImageGrab.grab()
                writeImg = cv2.cvtColor(np.array(currentImg),cv2.COLOR_RGB2BGR)
                video.write(writeImg)
            elif self.recordMode == 0:
                break
        video.release()
    # time update
    def updateTime(self):
        tList = self.timeString().split(":")
        #  calculate time
        h = int(tList[0])
        m = int(tList[0])
        s = int(tList[0])
        s += 1
        if s >= 60:
            m += 1
            if m >= 60:
                h += 1
        #  convert to string (00:00:00)
        h = str(h)
        m = str(m)
        s = str(s)
        timeList = ["0"+s for s in [h,m,s] if len(s)==1]
        result = "{}:{}:{}".format(timeList)
        self.time.display(result)

    def showWindow(self):
        self.setFixedSize(int(self.w*0.35),int(self.h*0.05))
        self.setWindowTitle("Screen Recorder")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        #set style sheet
        styleSheet = open("recorderStyle.css","r")
        style = styleSheet.read()
        self.setStyleSheet(style)

        #main widget
        content = QWidget(self)
        content.setObjectName("recorder")
        content.setFixedSize(self.width(),self.height())
        content.move(0,0)
        # main layout
        recorderLayout = QHBoxLayout()
        content.setLayout(recorderLayout)

        # time show
        self.time = QLCDNumber()
        self.time.setObjectName("recordTime")
        self.time.setFixedSize(int(self.w*0.1),int(self.h*0.03))
        self.time.setSegmentStyle(QLCDNumber.Flat)
        self.time.setDigitCount(8)
        self.time.display(self.timeString)
        recorderLayout.addWidget(self.time,0,(Qt.AlignLeft|Qt.AlignTop))

        # pause button
        pause = QToolButton()
        pause.setObjectName("pauseButton")
        pause.setFixedSize(int(self.w*0.03),int(self.w*0.03))
        recorderLayout.addWidget(pause,0,(Qt.AlignLeft|Qt.AlignTop))

        self.show()

app = QApplication(sys.argv)
test = Recorder()
test.showWindow()
sys.exit(app.exec_())
