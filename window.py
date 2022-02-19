from fileinput import filename
import os
import sys
import threading
import time

import cv2
import sounddevice as sd
from PIL import ImageGrab
from PyQt5 import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import recorder
import sizeFormatter as sf

# options widget
class optWidget(QWidget):
    def __init__(self, index:int, name:str, winWidth=1200, winHeight=800):
        super().__init__()

        self.vIndex = index
        self.name = name
        self.w = winWidth
        self.h = winHeight
        self.deleted = False

        optionsLayout = QHBoxLayout()
        optionsLayout.setAlignment(Qt.AlignCenter)
        optionsLayout.setSpacing(15)

        deleteButton = QPushButton("Delete")
        deleteButton.setObjectName("vOptButton")
        deleteButton.setFixedSize(int(self.w*0.07),int(self.h*0.03))
        deleteButton.clicked.connect(self.delete)
        self.setLayout(optionsLayout)

        optionsLayout.addWidget(deleteButton)

    # delete #
    def delete(self):
        rep = QMessageBox.question(self, "Confirm delete?", "Are you sure to delete {}?".format(self.name),
            QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if rep == QMessageBox.Yes:
            try:
                os.remove("./videos/"+self.name)
                self.deleted = True
            except:
                QMessageBox.critical(self, "Error", "File not found: {}".format(self.name),
                    QMessageBox.Ok)
            


class Window(QMainWindow):
    #initialize window
    def __init__(self):
        super().__init__()
        self.m_flag = False
        self.desktop = QApplication.desktop()
        self.w = self.desktop.width()
        self.h = self.desktop.height()
        self.isAlive = True
        
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
        self.optWidgets = []
        self.videoOptions = QWidget()
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
        self.isAlive = False
        inst = QApplication.instance()
        event.accept()
        inst.quit()

    #show window
    def showWindow(self):
        videoEncodes = [("MP4V","mpeg4",".mp4"),("XVID","png",".avi"),("PIM1","png",".avi"),
        ("I420","png",".avi")]

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
            record = recorder.Recorder(area=self.recArea,devID=sdChoose.currentIndex(),
            encode = videoEncodes[fourccSect.currentIndex()])
            record.showWindow()
            def recordListener():
                while True:
                    if record.recordMode == 0:
                        self.show()
                        break
                while not record.isExit:
                    pass
                time.sleep(0.1)
                self.updateVideoInfo(addOpt=False)
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
        
        #  tooltip
        def sdToolTip():
            sdChoose.setToolTip("Device: {}".format(sdChoose.currentText()))

        sdChoose = QComboBox()
        sdChoose.setObjectName("record-choose")
        sdChoose.setFixedSize(int(self.width()*0.165),int(self.height()*0.036))
        sdChoose.setView(QListView())
        sds = ["None"]+[i["name"] for i in list(sd.query_devices())]
        sdChoose.addItems(sds)
        sdChoose.currentIndexChanged.connect(sdToolTip)
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
        self.videoList.setHorizontalHeaderLabels(["Name","Time","Size","Duration","Options"])
        self.videoList.setSelectionBehavior(QAbstractItemView.SelectRows)
        windowLayout.addWidget(self.videoList)

        # refresh button
        refresh = QToolButton(self)
        refresh.setObjectName("refresh")
        refresh.setToolTip("Refresh")
        refresh.setFixedSize(int(self.width()*0.05),int(self.width()*0.05))
        # refresh.move(int(self.width()*0.89),int(self.height()*0.93))
        refresh.move(int(self.width()*0.94),int(self.height()*0.93))
        def updateVInfoWithoutKWargs():
            self.updateVideoInfo(addOpt=True)
        refresh.clicked.connect(updateVInfoWithoutKWargs)

        # settings
        #  settings page
        settingsPage = QWidget(self)
        settingsPage.setObjectName("settingsPage")
        settingsPage.setFixedSize(int(self.width()*0.9),int(self.height()*0.9))
        settingsPage.move(int(self.width()*0.05),int(self.height()*0.08))
        settingsPage.setGeometry(QRect(int(self.width()*0.05),int(self.height()*0.08),
            int(self.width()*0.05),int(self.width()*0.05)))
        settingsPage.setVisible(False)


        #  settings button
        settings = QToolButton(self)
        settings.setVisible(False)
        settings.setObjectName("settings")
        settings.setFixedSize(int(self.width()*0.05),int(self.width()*0.05))
        settings.move(int(self.width()*0.94),int(self.height()*0.93))

        def showSettingsPage():
            settingsPage.setVisible(True)
            settings.setVisible(False)

            settingsAnimation = QPropertyAnimation(settingsPage, b"geometry")
            settingsAnimation.setDuration(3000)
            settingsAnimation.setStartValue(QRect(int(self.width()*0.05),int(self.height()*0.08),
            int(self.width()*0.05),int(self.width()*0.05)))
            settingsAnimation.setEndValue(QRect(int(self.width()*0.05),int(self.height()*0.08),
            int(self.width()*0.9),int(self.height()*0.9)))
            settingsAnimation.start()

        #settings.clicked.connect(showSettingsPage)

        #   settings widget
        settingsWidget = QWidget(settingsPage)
        settingsWidget.setObjectName("settingsWidget")
        settingsWidget.setAutoFillBackground(True)
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
        settingsLayout = QVBoxLayout()
        settingsLayout.setAlignment(Qt.AlignTop)
        recordSettings.setLayout(settingsLayout)

        #  FPS
        fpsLayout = QHBoxLayout()
        fpsLayout.setAlignment(Qt.AlignLeft)

        fpsLabel = QLabel("FPS: ")
        fpsLabel.setObjectName("record-label")
        fpsLabel.setFixedSize(int(self.width()*0.06),int(self.height()*0.05))
        fpsAuto = QRadioButton("Auto")
        fpsAuto.setObjectName("record-sect")
        fpsAuto.setFixedSize(int(self.width()*0.08),int(self.height()*0.05))
        fpsAuto.setChecked(True)
        fpsManual = QRadioButton("Manual")
        fpsManual.setObjectName("record-sect")
        fpsManual.setFixedSize(int(self.width()*0.1),int(self.height()*0.05))
        fpsInput = QLineEdit()
        fpsInput.setObjectName("record-input")
        fpsInput.setValidator(QIntValidator())
        fpsInput.setPlaceholderText("1~120")
        fpsInput.setAlignment(Qt.AlignCenter)
        fpsInput.setFixedSize(int(self.width()*0.06),int(self.height()*0.04))
        fpsLayout.addWidget(fpsLabel)
        fpsLayout.addWidget(fpsAuto)
        fpsLayout.addWidget(fpsManual)
        fpsLayout.addWidget(fpsInput)
        settingsLayout.addLayout(fpsLayout)

        # encode select
        fourccLayout = QHBoxLayout()
        fourccLayout.setAlignment(Qt.AlignLeft)
        fourccLabel = QLabel("Encode: ")
        fourccLabel.setObjectName("record-label")
        fourccLabel.setFixedSize(int(self.width()*0.1),int(self.height()*0.05))
        fourccSect = QComboBox()
        fourccSect.setObjectName("record-choose")
        fourccSect.setFixedSize(int(self.width()*0.15),int(self.height()*0.036))
        fourccSect.setView(QListView())
        fourccSect.addItems(["MPEG4 (mp4)","MPEG4 (avi)","MPEG1 (avi)","YUV (avi)"])
        fourccLayout.addWidget(fourccLabel)
        fourccLayout.addWidget(fourccSect)
        settingsLayout.addLayout(fourccLayout)

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

        # video info listener #
        def vInfoListen():
            while self.isAlive:
                for i in range(len(self.optWidgets)):
                    if self.optWidgets[i].deleted:
                        self.videoList.removeRow(i)
        infoListener = threading.Thread(target=vInfoListen,name="VideoInfoListener")
        infoListener.start()

    # update video info #
    def updateVideoInfo(self, addOpt=True):
        if list(os.walk("./videos")) == []:
            return 0
        fileNames = list(os.walk("./videos"))[0][2]
        delIndexs = []
        for i in range(len(fileNames)):
            vCap = cv2.VideoCapture("./videos/"+fileNames[i])
            #print(vCap.get(5))
            if (fileNames[i]=="TEMP") or (fileNames[i].split('.')[-1].lower() not in ["mp4","avi","mov","mpeg","m4v","mkv","flv"]) or (vCap.get(5)==0):
                delIndexs.append(i)
        
        for i in delIndexs:
            fileNames.pop(i)
        self.videoList.setRowCount(len(fileNames))

        for i in range(len(fileNames)):
            name = QTableWidgetItem(fileNames[i])
            t = QTableWidgetItem(str(time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(os.path.getctime("./videos/"+fileNames[i])))))
            size = QTableWidgetItem(sf.formatTopLevel("./videos/"+fileNames[i]))
            if vCap.get(5) == 0:
                duration = QTableWidgetItem("<1 Sec")
            else:
                duration = QTableWidgetItem("{} Sec".format(vCap.get(7)/vCap.get(5)))

            self.videoList.setItem(i,0,name)
            self.videoList.setItem(i,1,t)
            self.videoList.setItem(i,2,size)
            self.videoList.setItem(i,3,duration)
            if addOpt:
                self.optWidgets.append(optWidget(i, fileNames[i], self.width(), self.height()))
                self.videoList.setCellWidget(i,4,self.optWidgets[-1])
