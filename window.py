import os
import sys
import threading
import time

import sounddevice as sd
from PIL import ImageGrab
from PyQt5 import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import recorder


class Window(QMainWindow):
    #initialize window
    def __init__(self):
        super().__init__()
        self.m_flag = False
        self.desktop = QApplication.desktop()
        self.w = self.desktop.width()
        self.h = self.desktop.height()
        #set window
        self.setFixedSize(int(self.w*0.6),int(self.h*0.7))
        self.setWindowTitle("Screen recorder")
        self.setWindowIcon(QIcon("./required/icon.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)
        self.recArea = (0,0,self.w,self.h)
        self.videoList = QTableWidget(0,5)
        self.videoList.lines = 0
        self.updateVideoInfo()
    
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
    def closeEvent(self,event):
        os.remove("required/buttons/desktop.png")
        event.accept()

    #show window
    def showWindow(self):
        #read style sheet
        style = open("windowStyle.css","r",encoding="UTF-8")
        self.setStyleSheet(style.read())
        style.close()

        #title bar
        titleBar = QWidget(self)
        titleBar.setObjectName("titleBar")
        titleBar.setFixedSize(self.width(),int(self.height()*0.06))

        #main widget
        content = QWidget(self)
        content.setObjectName("content")
        content.setFixedSize(self.width(),int(self.height()*0.94))
        content.move(0,titleBar.height())

        # icon
        icon = QWidget()
        icon.setObjectName("windowIcon")
        icon.setFixedSize(int(self.width()*0.03),int(self.width()*0.03))
        # title
        title = QLabel(text="Screen Recorder")
        title.setObjectName("windowTitle")
        title.setFixedSize(int(self.width()*0.18),int(self.height()*0.036))
        # buttons
        minbtn = QToolButton()
        minbtn.setObjectName("showmin")
        minbtn.setFixedSize(int(self.width()*0.02),int(self.width()*0.02))
        minbtn.clicked.connect(self.showMinimized)
        minbtn.setToolTip("Show minimized (Alt+N)")
        minbtn.setShortcut("Alt+N")
        def toggleMax():
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
            titleBar.setFixedSize(self.width(),80)
            content.setFixedSize(self.width(),self.height()-80)
        maxbtn = QToolButton()
        maxbtn.setObjectName("showmax")
        maxbtn.setFixedSize(int(self.width()*0.02),int(self.width()*0.02))
        maxbtn.clicked.connect(toggleMax)
        maxbtn.setToolTip("Show maximized (Alt+X)")
        maxbtn.setShortcut("Alt+X")
        closebtn = QToolButton()
        closebtn.setObjectName("closeWindow")
        closebtn.setFixedSize(int(self.width()*0.02),int(self.width()*0.02))
        closebtn.clicked.connect(self.close)
        closebtn.setToolTip("Close (Alt+F4)")
        closebtn.setShortcut("Alt+F4")
        
        # title bar layout
        titleLayout = QHBoxLayout()
        titleLayout.addWidget(icon,alignment=Qt.AlignLeft)
        titleLayout.addWidget(title,alignment=Qt.AlignLeft)
        titleLayout.addStretch(0.5)
        titleLayout.addWidget(minbtn,alignment=Qt.AlignRight)
        titleLayout.addWidget(maxbtn,alignment=Qt.AlignRight)
        titleLayout.addWidget(closebtn,alignment=Qt.AlignRight)
        titleBar.setLayout(titleLayout)

        # window contents
        windowLayout = QVBoxLayout()
        windowLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        content.setLayout(windowLayout)

        # record button
        def loadRecorder():
            self.hide()
            record = recorder.Recorder(area=self.recArea,devID=sdChoose.currentIndex())
            record.showWindow()
            def recordListener():
                while True:
                    if record.recordMode == 0:
                        self.show()
                        break
                while True:
                    if record.isExit:
                        self.updateVideoInfo()
                        break
            recThread = threading.Thread(target=record.recordScreen,name="Recorder")
            recThread.start()
            listenThread = threading.Thread(target=recordListener,name="Record-Listener")
            listenThread.start()
        topLayout = QHBoxLayout()
        topLayout.setAlignment(Qt.AlignLeft)
        topLayout.setSpacing(int(self.width()*0.056))
        windowLayout.addLayout(topLayout)
        recordbtn = QPushButton(content)
        recordbtn.setObjectName("recordButton")
        recordbtn.setFixedSize(int(self.width()*0.25),int(self.width()*0.25))
        recordbtn.clicked.connect(loadRecorder)
        topLayout.addWidget(recordbtn)

        # record area set
        recArea = QWidget()
        recArea.setObjectName("recordAreaSet")
        recArea.setFixedSize(int(self.width()*0.18),int(self.height()*0.357))
        topLayout.addWidget(recArea)
        # widget layout
        areaLayout = QVBoxLayout(recArea)
        areaLayout.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        areaLayout.setSpacing(int(self.width()*0.015))
        # label
        areaLabel = QLabel(text="Record area")
        areaLabel.setObjectName("recordAreaLabel")
        areaLabel.setFixedSize(int(self.width()*0.26),int(self.height()*0.036))
        areaLayout.addWidget(areaLabel)
        # area select
        # full screen #
        fullScreen = QRadioButton(text="Full screen")
        fullScreen.setObjectName("recordFullScreen")
        fullScreen.setChecked(True)
        fullScreen.setFixedSize(int(self.width()*0.16),int(self.height()*0.036))
        areaLayout.addWidget(fullScreen)
        # custom area #
        cusLayout = QGridLayout()
        cusLayout.setSpacing(int(self.width()*0.005))
        cusLayout.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        tickScreen = QRadioButton(text="Custom area")
        tickScreen.setObjectName("recordCustomArea")
        tickScreen.setFixedSize(int(self.width()*0.16),int(self.height()*0.036))
        cusLayout.addWidget(tickScreen,0,0)

        # position #
        areaPos = QLabel(text="Position:")
        areaPos.setObjectName("areaPosition")
        areaPos.setFixedSize(int(self.width()*0.15),int(self.height()*0.036))
        cusLayout.addWidget(areaPos,1,0)

        areaX = QLineEdit()
        areaX.setObjectName("areaXPosition")
        areaX.setFixedSize(int(self.width()*0.07),int(self.height()*0.04))
        areaX.setAlignment(Qt.AlignCenter)
        areaX.setPlaceholderText("X")
        areaX.setValidator(QIntValidator())

        areaY = QLineEdit()
        areaY.setObjectName("areaYPosition")
        areaY.setFixedSize(int(self.width()*0.07),int(self.height()*0.04))
        areaY.setAlignment(Qt.AlignCenter)
        areaY.setPlaceholderText("Y")
        areaY.setValidator(QIntValidator())

        areaWidth = QLineEdit()
        areaWidth.setObjectName("areaWidth")
        areaWidth.setFixedSize(int(self.width()*0.07),int(self.height()*0.04))
        areaWidth.setAlignment(Qt.AlignCenter)
        areaWidth.setPlaceholderText("Width")
        areaWidth.setValidator(QIntValidator())

        areaHeight = QLineEdit()
        areaHeight.setObjectName("areaHeight")
        areaHeight.setFixedSize(int(self.width()*0.07),int(self.height()*0.04))
        areaHeight.setAlignment(Qt.AlignCenter)
        areaHeight.setPlaceholderText("Height")
        areaHeight.setValidator(QIntValidator())

        cusLayout.addWidget(areaX,2,0)
        cusLayout.addWidget(areaY,2,1)
        cusLayout.addWidget(areaWidth,3,0)
        cusLayout.addWidget(areaHeight,3,1)
        areaLayout.addLayout(cusLayout)

        # area preview
        previewImage = ImageGrab.grab()
        previewImage.save("./required/buttons/desktop.png")
        previewWidget = QWidget()
        previewWidget.setObjectName("recordPreviewImage")
        previewWidget.setFixedSize(int(self.w*0.25),int(self.h*0.25))
        topLayout.addWidget(previewWidget)
        previewArea = QWidget(previewWidget)
        previewArea.setObjectName("recordAreaPreview")
        previewArea.setFixedSize(int(self.w*0.25),int(self.h*0.25))
        previewArea.move(0,0)

        # sound device choose
        sdcLabel = QLabel(text="Sound device:")
        sdcLabel.setObjectName("sdc")
        sdcLabel.setFixedSize(int(self.width()*0.16),int(self.height()*0.036))
        cusLayout.addWidget(sdcLabel,4,0)
        
        sdChoose = QComboBox()
        sdChoose.setObjectName("sdChoose")
        sdChoose.setFixedSize(int(self.width()*0.165),int(self.height()*0.036))
        sds = ["None"]+[i["name"] for i in list(sd.query_devices())]
        sdChoose.addItems(sds)
        cusLayout.addWidget(sdChoose,5,0)

        def checkArea():
            try:
                x = int(areaX.text())
                y = int(areaY.text())
                w = int(areaWidth.text())
                h = int(areaHeight.text())
            except:
                areaX.setText("0")
                areaY.setText("0")
                areaWidth.setText(str(self.w))
                areaHeight.setText(str(self.h))
                x = 0
                y = 0
                w = self.w
                h = self.h
            if tickScreen.isChecked():
                maxWidth = self.w-x
                maxHeight = self.h-y
                if w > maxWidth:
                    w = maxWidth
                    areaWidth.setText(str(w))
                if h > maxHeight:
                    h = maxHeight
                    areaHeight.setText(str(h))
                previewArea.setFixedSize(int(w*0.25),int(h*0.25))
                previewArea.move(int(x*0.25),int(y*0.25))
                self.recArea = (x,y,x+w,y+h)
            else:
                previewArea.setFixedSize(int(self.w*0.25),int(self.h*0.25))
                previewArea.move(0,0)
                self.recArea = (0,0,self.w,self.h)
        areaX.textChanged.connect(checkArea)
        areaY.textChanged.connect(checkArea)
        areaWidth.textChanged.connect(checkArea)
        areaHeight.textChanged.connect(checkArea)
        fullScreen.toggled.connect(checkArea)
        tickScreen.toggled.connect(checkArea)

        # video list
        self.videoList.setObjectName("videoList")
        self.videoList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.videoList.setFixedSize(int(self.width()*0.98),int(self.height()*0.55))
        self.videoList.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.videoList.horizontalHeader().setObjectName("videoListHHeader")
        self.videoList.verticalHeader().setObjectName("videoListVHeader")
        self.videoList.setHorizontalHeaderLabels(["Name","Time","Size","Duration","FPS"])
        self.videoList.setSelectionBehavior(QAbstractItemView.SelectRows)
        windowLayout.addWidget(self.videoList)

        # settings
        #  settings page
        settingsPage = QWidget(self)
        settingsPage.setObjectName("settingsPage")
        settingsPage.setFixedSize(int(self.width()*0.9),int(self.height()*0.9))
        settingsPage.move(int(self.width()*0.05),int(self.height()*0.08))
        settingsPage.setVisible(False)

        #  settings button
        settings = QToolButton(self)
        settings.setObjectName("settings")
        settings.setFixedSize(int(self.width()*0.05),int(self.width()*0.05))
        settings.move(int(self.width()*0.94),int(self.height()*0.93))
        def showSettingsPage():
            settingsPage.setVisible(True)
            settings.setVisible(False)
        settings.clicked.connect(showSettingsPage)

        #   settings widget
        settingsWidget = QWidget(settingsPage)
        settingsWidget.setObjectName("settingsWidget")
        settingsWidget.setFixedSize(settingsPage.width(),settingsPage.height())
        settingsWidget.move(0,0)

        #   settings page - title
        settingsTitle = QLabel(settingsWidget,text="Settings")
        settingsTitle.setObjectName("settingsTitle")
        settingsTitle.setFixedSize(int(self.width()*0.25),int(self.height()*0.11))
        settingsTitle.setAlignment(Qt.AlignCenter)
        settingsTitle.move(0,0)
        #   splitline
        split = QWidget(settingsWidget)
        split.setObjectName("settingsSplitline")
        split.setFixedSize(int(self.width()*0.9),int(self.height()*0.005))
        split.move(0,int(self.height()*0.11))
        #   settings page - tab widget
        settingsContent = QTabWidget(settingsWidget)
        settingsContent.setObjectName("settingsContent")
        settingsContent.setIconSize(QSize(int(self.width()*0.04),int(self.width()*0.04)))
        settingsContent.tabBar().setObjectName("settingsContentSelector")
        settingsContent.setFixedSize(int(self.width()*0.9),int(self.height()*0.78))
        settingsContent.move(0,int(self.height()*0.115))

        # record settings
        recordSettings = QWidget()
        recordSettings.setObjectName("recordSettings")
        recordLayout = QVBoxLayout()
        recordLayout.setAlignment(Qt.AlignTop)
        recordSettings.setLayout(recordLayout)

        #  FPS
        fpsLayout = QHBoxLayout()
        fpsLayout.setAlignment(Qt.AlignLeft)
        fpsLabel = QLabel("FPS: ")
        fpsLabel.setObjectName("record-fpsLabel")
        fpsLabel.setFixedSize(int(self.width()*0.06),int(self.height()*0.05))
        fpsAuto = QRadioButton("Auto")
        fpsAuto.setObjectName("record-fps")
        fpsAuto.setFixedSize(int(self.width()*0.08),int(self.height()*0.05))
        fpsAuto.setChecked(True)
        fpsManual = QRadioButton("Manual")
        fpsManual.setObjectName("record-fps")
        fpsManual.setFixedSize(int(self.width()*0.1),int(self.height()*0.05))
        fpsInput = QLineEdit()
        fpsInput.setObjectName("record-fpsinput")
        fpsInput.setValidator(QIntValidator())
        fpsInput.setPlaceholderText("1~120")
        fpsInput.setAlignment(Qt.AlignCenter)
        fpsInput.setFixedSize(int(self.width()*0.06),int(self.height()*0.04))
        fpsLayout.addWidget(fpsLabel)
        fpsLayout.addWidget(fpsAuto)
        fpsLayout.addWidget(fpsManual)
        fpsLayout.addWidget(fpsInput)
        recordLayout.addLayout(fpsLayout)

        settingsContent.addTab(recordSettings,QIcon("./required/buttons/recordSettings.svg"),
        "Record")

        appearanceSettings = QWidget()
        recordSettings.setObjectName("appearanceSettings")
        settingsContent.addTab(appearanceSettings,QIcon("./required/buttons/appearanceSettings.svg"),
        "Appearance")

        #   settings page - close button
        def hideSettingsPage():
            settingsPage.setVisible(False)
            settings.setVisible(True)
        settingsHide = QToolButton(settingsWidget)
        settingsHide.setObjectName("settingsClose")
        settingsHide.setFixedSize(int(self.width()*0.06),int(self.width()*0.06))
        settingsHide.move(int(self.width()*0.82),int(self.height()*0.02))
        settingsHide.clicked.connect(hideSettingsPage)

        self.show()
    def updateVideoInfo(self):
        f = open("required/videoInfo.inf","a+",encoding="UTF-8")
        f.seek(0)
        infos = f.read().split("\n")[:-1]
        # update video list
        dicts = [eval(i) for i in infos]
        for i in range(len(dicts)):
            self.videoList.lines += 1
            self.videoList.setRowCount(self.videoList.lines)
            name = QTableWidgetItem(dicts[i]["name"])
            t = QTableWidgetItem(dicts[i]["time"])
            size = QTableWidgetItem(dicts[i]["size"])
            duration = QTableWidgetItem(dicts[i]["duration"])
            fps = QTableWidgetItem(dicts[i]["fps"])
            self.videoList.setItem(i,0,name)
            self.videoList.setItem(i,1,t)
            self.videoList.setItem(i,2,size)
            self.videoList.setItem(i,3,duration)
            self.videoList.setItem(i,4,fps)
        f.close()
