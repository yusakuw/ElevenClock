import platform
import subprocess
import os
import sys
import locale
import time
from PySide2 import QtGui
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import FramelessWindow

import globals

from languages import * 
from tools import *
from tools import _



class WelcomeWindow(QMainWindow):
    def __init__(self, parent: QObject = None, flags: Qt.WindowFlags = Qt.WindowFlags()) -> None:
        super().__init__()
        
        self.switched = False
        
        self.widgetOrder = (
            FirstRunWidget(self),
            SelectModeWidget(self),
            LastWidget(self),
        )
        
        for w in self.widgetOrder:
            w.next.connect(self.nextWidget)
            w.previous.connect(self.previousWidget)
            w.skipped.connect(self.lastWidget)
            w.finished.connect(self.close)
            
        
        self.currentIndex = -1
        
        self.setFixedSize(self.getPx(800), self.getPx(600))
        self.setStyleSheet("background-color: transparent;")
        self.bgWidget = QStackedWidget(self)
        self.bgWidget.setObjectName("BackgroundWidget")
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        self.setWindowTitle(_("Welcome to ElevenClock"))
        self.setWindowIcon(QIcon(getPath("icon.png")))
        self.setCentralWidget(self.bgWidget)
        
        
        self.bgWindow = QMainWindow()
        self.bgWindow.setFocusPolicy(Qt.NoFocus)
        self.bgWindow.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowDoesNotAcceptFocus | Qt.Tool)
        self.bgWindow.setAttribute(Qt.WA_TranslucentBackground)
        self.bgWindow.setCentralWidget(QWidget())
        self.bgWindow.centralWidget().setStyleSheet("background-color: rgba(30, 30, 30, 0.6)")
        self.bgWindow.hide()
        self.bgWindow.setWindowTitle("ElenenClock_IgnoreFullscreenEvent")
        self.bgWindow.move(0, 0)
        self.bgWindow.resize(1, 1)
        
        colors = ['215,226,228', '160,174,183', '101,116,134', '81,92,107', '69,78,94', '41,47,64', '15,18,36', '239,105,80']
        string = readRegedit(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Accent", "AccentPalette", b'\xe9\xd8\xf1\x00\xcb\xb7\xde\x00\x96}\xbd\x00\x82g\xb0\x00gN\x97\x00H4s\x00#\x13K\x00\x88\x17\x98\x00')
        i  =  0
        acc = False
        for color in string.split(b"\x00"):
            add = True
            try:
                if len(color) == 3:
                    colors[i] = f"{color[0]},{color[1]},{color[2]}"
                elif len(color) == 0:
                    acc = True   
                    add = False
                elif len(color) == 2 and acc:
                    acc = False
                    colors[i] = f"0,{color[0]},{color[1]}"
                else:
                    pass
            except IndexError:
                pass
            finally:
                if add:
                    i += 1
                    
                    
        self.bgWidget.setStyleSheet(f"""
            * {{
                color: #eeeeee;
                background-color: #282828;
                border-radius: 4px;
                font-family: "Segoe UI Variable Display"
            }}
            #BackgroundWidget {{
                border: 0px solid #121212;
                padding: 20px;
                border-radius: 0px;
                padding-left: 30px;
                padding-right: 30px;
            }}
            QLabel {{
                background-color: none;
            }}
            #SampleItem {{
                font-family: "Segoe UI Variable Display semib";
                width: 100px;
                background-color: #303030;
                padding: 20px;
                border-radius: {self.getPx(8)}px;
                border: {self.getPx(1)}px solid #393939;
                height: {self.getPx(25)}px;
                border-top: {self.getPx(1)}px solid #404040;
            }}
            #FramelessSampleItem {{
                font-family: "Segoe UI Variable Display semib";
                width: 100px;
                background-color: transparent;
                padding: 20px;
                border-radius: {self.getPx(8)}px;
                border: none;
                height: {self.getPx(25)}px;
            }}
            QPushButton {{
                font-family: "Segoe UI Variable Display semib";
                font-size: 8pt;
                width: 100px;
                background-color: #363636;
                border-radius: {self.getPx(4)}px;
                border: {self.getPx(1)}px solid #393939;
                height: {self.getPx(25)}px;
                border-top: {self.getPx(1)}px solid #404040;
            }}
            QPushButton:hover {{
                background-color: #393939;
                border: {self.getPx(1)}px solid #414141;
                height: {self.getPx(25)}px;
                border-top: {self.getPx(1)}px solid #454545;
            }}
            QPushButton:pressed {{
                background-color: rgb({colors[2]});
                border-color: rgb({colors[2]});
                border-bottom-color: rgb({colors[3]});
                height: {self.getPx(25)}px;
            }}
            #AccentButton{{
                color: black;
                background-color: rgb({colors[1]});
                border-color: rgb({colors[1]});
                border-bottom-color: rgb({colors[2]});
            }}
            #AccentButton:hover{{
                background-color: rgb({colors[2]});
                border-color: rgb({colors[2]});
                border-bottom-color: rgb({colors[3]});
            }}
            #AccentButton:disabled{{
                background-color: #212121;
                border-color: #303030;
                border-bottom-color: #363636;
            }}
            QLabel {{
                border: none;
                border-radius: 6px;
            }}
            #TitleLabel {{
                font-size: 26pt;
            }}
            """)
        
        self.nextWidget(anim=False)

        self.show()
        
    def fillScreen(self) -> None:
        if not self.switched:
            self.switched = True
            GlobalBlur(self.bgWindow.winId(), Acrylic=False)
            fGeometry = QGuiApplication.primaryScreen().geometry()
            #fGeometry.setHeight(fGeometry.height()-10)
            self.bgWindow.setGeometry(self.geometry())
            bgAnim = QPropertyAnimation(self.bgWindow, b"geometry", self)
            bgAnim.setStartValue(self.geometry())
            bgAnim.setEndValue(fGeometry)
            bgAnim.setEasingCurve(QEasingCurve.InOutCirc)
            bgAnim.setDuration(400)
            bgAnim.start()
            self.bgWindow.show()
            x = (QGuiApplication.primaryScreen().geometry().width()-self.getPx(800))//2
            y = (QGuiApplication.primaryScreen().geometry().height()-self.getPx(600))//2
            self.resize(self.getPx(800), self.getPx(600))
            self.setFixedSize(self.getPx(800), self.getPx(600))
            self.hide()
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.show()
            uiAnim = QPropertyAnimation(self, b"pos", self)
            uiAnim.setStartValue(self.pos())
            uiAnim.setEndValue(QPoint(x, y))
            uiAnim.setEasingCurve(QEasingCurve.InOutCirc)
            uiAnim.setDuration(400)
            uiAnim.start()
    
    def paintEvent(self, event: QMouseEvent) -> None:
        self.bgWindow.show()
        self.bgWindow.raise_()
        return super().paintEvent(event)
    
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))
        
    def setWidget(self, w: QWidget, back=False, anim=True) -> None:
        self.bgWidget.setCurrentIndex(self.bgWidget.addWidget(w))
        if anim:
            if back:
                w.invertedinAnim()
            else:
                w.inAnim()
        
    def nextWidget(self, anim=True) -> None:
        if self.currentIndex == len(self.widgetOrder)-1:
            self.close()
        else:
            self.currentIndex += 1
            w: BasicNavWidget = self.widgetOrder[self.currentIndex]
            self.setWidget(w, anim=anim)
    
    def previousWidget(self) -> None:
        if self.currentIndex == 0:
            try:
                raise ValueError("The specified index is not present in the list of wizard widgets")
            except Exception as e:
                report(e)
        else:
            self.currentIndex -= 1
            w: BasicNavWidget = self.widgetOrder[self.currentIndex]
            self.setWidget(w, back=True)
    
    def lastWidget(self) -> None:
        self.currentIndex = len(self.widgetOrder)-1
        w: BasicNavWidget = self.widgetOrder[-1]
        self.setWidget(w)
        
        
    def closeEvent(self, event: QCloseEvent) -> None:
        self.bgWindow.close()
        return super().closeEvent(event)

class BasicNavWidget(QWidget):
    next = Signal()
    previous = Signal()
    finished = Signal()
    skipped = Signal()
    
    def __init__(self, parent=None, startEnabled=False, closeEnabled=False, finishEnabled=False, nextGreyed=False) -> None:
        super().__init__(parent=parent)
        self.l = QVBoxLayout()
        self.setLayout(self.l)
        
        if(readRegedit(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", 1)==0):
            self.iconMode = "white"
            self.negIconMode = "black"
        else:
            self.iconMode = "black"
            self.negIconMode = "white"
        
        self.navLayout = QHBoxLayout()
        if closeEnabled:
            closeButton = QPushButton(_("Skip"))
            closeButton.setFixedSize(self.getPx(96), self.getPx(36))
            closeButton.setIcon(QIcon(getPath(f"close_{self.iconMode}.png")))
            closeButton.clicked.connect(lambda: self.outAnim(self.skipped.emit))
            self.navLayout.addWidget(closeButton)
        self.navLayout.addStretch()
        if startEnabled:
            startButton = QPushButton(_("Start"))
            startButton.setLayoutDirection(Qt.RightToLeft)
            startButton.setFixedSize(self.getPx(96), self.getPx(36))
            startButton.setIcon(QIcon(getPath(f"next_{self.negIconMode}.png")))
            startButton.clicked.connect(lambda: self.outAnim(self.next.emit))
            startButton.setObjectName("AccentButton")
            self.navLayout.addWidget(startButton)
        else:
            backButton = QPushButton("")
            backButton.setFixedSize(self.getPx(36), self.getPx(36))
            backButton.clicked.connect(lambda: self.invertedOutAnim(self.previous.emit))
            backButton.setIcon(QIcon(getPath(f"previous_{self.iconMode}.png")))
            self.navLayout.addWidget(backButton)
            if finishEnabled:
                finishButton = QPushButton(_("Finish"))
                finishButton.setObjectName("AccentButton")
                finishButton.setFixedSize(self.getPx(96), self.getPx(36))
                finishButton.setLayoutDirection(Qt.RightToLeft)
                finishButton.clicked.connect(lambda: self.outAnim(self.finished.emit))
                self.navLayout.addWidget(finishButton)
            else:
                self.nextButton = QPushButton("")
                self.nextButton.setEnabled(not nextGreyed)
                self.nextButton.setFixedSize(self.getPx(36), self.getPx(36))
                self.nextButton.clicked.connect(lambda:self.outAnim(self.next.emit))
                self.nextButton.setIcon(QIcon(getPath(f"next_{self.negIconMode}.png")))
                self.nextButton.setObjectName("AccentButton")
                self.navLayout.addWidget(self.nextButton)
                
    def enableNextButton(self) -> None:
        self.nextButton.setEnabled(True)
           
    def nextWidget(self):
        self.outAnim(self.next.emit)
    
    def setCentralWidget(self, w: QWidget) -> QWidget:
        self.l.addWidget(w, stretch=1)
        self.l.addLayout(self.navLayout, stretch=0)
        
    def inAnim(self) -> None:
        bgAnim = QPropertyAnimation(self, b"pos", self)
        pos = self.pos()
        pos.setX(pos.x()+self.width())
        bgAnim.setStartValue(pos)
        bgAnim.setEndValue(self.pos())
        bgAnim.setEasingCurve(QEasingCurve.OutExpo)
        bgAnim.setDuration(200)
        bgAnim.start()
        
    def invertedinAnim(self) -> None:
        bgAnim = QPropertyAnimation(self, b"pos", self)
        pos = self.pos()
        pos.setX(pos.x()-self.width())
        bgAnim.setStartValue(pos)
        bgAnim.setEndValue(self.pos())
        bgAnim.setEasingCurve(QEasingCurve.OutExpo)
        bgAnim.setDuration(200)
        bgAnim.start()
        
    def outAnim(self, f) -> None:
        bgAnim = QPropertyAnimation(self, b"pos", self)
        bgAnim.setStartValue(self.pos())
        pos = self.pos()
        pos.setX(pos.x()-self.width())
        bgAnim.setEndValue(pos)
        bgAnim.setEasingCurve(QEasingCurve.InExpo)
        bgAnim.setDuration(200)
        bgAnim.start()
        bgAnim.finished.connect(f)
    
    def invertedOutAnim(self, f) -> None:
        bgAnim = QPropertyAnimation(self, b"pos", self)
        bgAnim.setStartValue(self.pos())
        pos = self.pos()
        pos.setX(pos.x()+self.width())
        bgAnim.setEndValue(pos)
        bgAnim.setEasingCurve(QEasingCurve.InExpo)
        bgAnim.setDuration(200)
        bgAnim.start()
        bgAnim.finished.connect(f)
    
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))
    
    def window(self) -> WelcomeWindow:
        return super().window()


class IconLabel(QWidget):
    def __init__(self, size=96, frame=True) -> None:
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)
        if frame:
            self.setObjectName("SampleItem")
        else:
            self.setObjectName("FramelessSampleItem")
        self.iconSize = size
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.iconLabel = QLabel()
        self.iconLabel.setMinimumHeight(self.getPx(self.iconSize+40))
        self.iconLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setMinimumHeight(self.getPx(self.iconSize))
        self.textLabel = QLabel()
        self.textLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.textLabel.setWordWrap(True)
        self.textLabel.setStyleSheet("font-size: 10pt;")
        self.textLabel.setOpenExternalLinks(True)
        if frame: self.layout().addSpacing(self.getPx(40/96*self.iconSize))
        self.layout().addWidget(self.iconLabel, stretch=0)
        self.layout().addSpacing(self.getPx(30/96*self.iconSize))
        self.layout().addWidget(self.textLabel, stretch=1)
        if frame: self.layout().addSpacing(self.getPx(30/96*self.iconSize))
        
    def setText(self, text: str) -> None:
        self.textLabel.setText(text)
        
    def setIcon(self, path: str) -> None:
        self.iconLabel.setPixmap(QIcon(getPath(path)).pixmap(self.getPx(self.iconSize), self.getPx(self.iconSize)))
        
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))

class ButtonLabel(QWidget):
    clicked = Signal()
    def __init__(self, size=96) -> None:
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("SampleItem")
        self.iconSize = size
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.iconLabel = QLabel()
        self.iconLabel.setMinimumHeight(self.getPx(self.iconSize+40))
        self.iconLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setMinimumHeight(self.getPx(self.iconSize))
        self.textLabel = QLabel()
        self.textLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.textLabel.setWordWrap(True)
        self.textLabel.setStyleSheet("font-size: 10pt;")
        self.textLabel.setOpenExternalLinks(True)
        self.button = QPushButton()
        self.button.clicked.connect(self.clicked.emit)
        self.layout().addSpacing(self.getPx(40/96*self.iconSize))
        self.layout().addWidget(self.iconLabel, stretch=0)
        self.layout().addSpacing(self.getPx(20/96*self.iconSize))
        self.layout().addWidget(self.textLabel, stretch=1)
        self.layout().addSpacing(self.getPx(20/96*self.iconSize))
        self.layout().addWidget(self.button, stretch=0)
        self.layout().addSpacing(self.getPx(40/96*self.iconSize))
        
    def setText(self, text: str) -> None:
        self.textLabel.setText(text)
    
    def setButtonText(self, t: str) -> None:
        self.button.setText(t)
        
    def setIcon(self, path: str) -> None:
        self.iconLabel.setPixmap(QIcon(getPath(path)).pixmap(self.getPx(self.iconSize), self.getPx(self.iconSize)))
        
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))

class ClickableLabel(QLabel):
    clicked = Signal()
    def __init__(self) -> None:
        super().__init__()
        self.setMouseTracking(True)
    
    def mousePressEvent(self, ev) -> None:
        self.clicked.emit()
        return super().mousePressEvent(ev)
    
class ClickableButtonLabel(QPushButton):
    clicked = Signal()
    def __init__(self, size=96) -> None:
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("ButtonItem")
        self.iconSize = size
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.iconLabel = QLabel()
        self.iconLabel.setMinimumHeight(self.getPx(self.iconSize))
        self.iconLabel.setMinimumWidth(self.getPx(size))
        self.iconLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setMinimumHeight(self.getPx(self.iconSize))
        self.textLabel = QLabel()
        self.textLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.textLabel.setWordWrap(True)
        self.textLabel.setStyleSheet("font-size: 10pt;")
        self.textLabel.setOpenExternalLinks(True)
        self.layout().addSpacing(self.getPx(40/96*self.iconSize))
        self.layout().addWidget(self.iconLabel, stretch=0)
        self.layout().addSpacing(self.getPx(20/96*self.iconSize))
        self.layout().addWidget(self.textLabel, stretch=1)
        self.layout().addSpacing(self.getPx(40/96*self.iconSize))
        
    def setText(self, text: str) -> None:
        self.textLabel.setText(text)
    
    def setButtonText(self, t: str) -> None:
        self.button.setText(t)
        
    def setIcon(self, path: str) -> None:
        self.iconLabel.setPixmap(QIcon(getPath(path)).pixmap(self.getPx(self.iconSize), self.getPx(self.iconSize), Mode=Qt.KeepAspectRatio))
        
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))

class ClickableButtonLabelWithBiggerIcon(QPushButton):
    def __init__(self, size=96) -> None:
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("ButtonItem")
        self.iconSize = size
        self.setCheckable(True)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.iconLabel = ClickableLabel()
        self.iconLabel.setMinimumHeight(self.getPx(self.iconSize))
        self.iconLabel.setMinimumWidth(self.getPx(size))
        self.iconLabel.clicked.connect(self.click)
        self.iconLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setMinimumHeight(self.getPx(self.iconSize))
        self.textLabel = ClickableLabel()
        self.textLabel.clicked.connect(self.click)
        self.textLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.textLabel.setWordWrap(True)
        self.textLabel.setStyleSheet("font-size: 10pt;")
        self.textLabel.setOpenExternalLinks(True)
        self.layout().addSpacing(self.getPx(20/96*self.iconSize))
        self.layout().addWidget(self.iconLabel, stretch=0)
        self.layout().addSpacing(self.getPx(20/96*self.iconSize))
        self.layout().addWidget(self.textLabel, stretch=1)
        self.layout().addSpacing(self.getPx(40/96*self.iconSize))
        
    def setText(self, text: str) -> None:
        self.textLabel.setText(text)
    
    def setButtonText(self, t: str) -> None:
        self.button.setText(t)
        
    def setIcon(self, path: str) -> None:
        self.iconLabel.setPixmap(QIcon(getPath(path)).pixmap(self.getPx(self.iconSize+20), self.getPx(self.iconSize+20), Mode=Qt.KeepAspectRatio))
        
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))  
   
class FirstRunWidget(BasicNavWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent, startEnabled=True, closeEnabled=True)
        widget = QWidget()
        self.next.connect(self.startWin)
        l = QHBoxLayout()
        l.setContentsMargins(0, self.getPx(10), 0, self.getPx(10))
        widget.setLayout(l)
        vl = QVBoxLayout()
        l.addSpacing(self.getPx(10))
        l.addLayout(vl)
        vl.addSpacing(self.getPx(30))
        
        label1 = IconLabel(size=64, frame=False)
        label1.setIcon("icon.png")
        label1.setText(f"""
 <h1>Welcome to Elevenclock!</h1>
 If you already know how does this work, or you want to skip the welcome wizard, please click on the bottom-left <i>Skip</i> button.""")
        
        
        label3 = IconLabel(size=64)
        label3.setIcon("msstore_color.png")
        label3.setText("""
 <h3>Wait a minute!</h3>
 Please make sure to install ElevenClock from official sources only, such as the Microsoft Store, Github, SomePythonThings or other trustworthy webpages. Also, using ElevenClock implies the acceptation of the <b>Apache 2.0 license</b>""")

        label2 = IconLabel(size=64)
        label2.setIcon("customize_color.png")
        label2.setText("""
 <h3>Do you have a minute? This wizard will help you configure and customize ElevenClock. Click Start to get started!</h3>
 Remember that this wizard can be run at any time from the Settings Window""")
        
        vl.addWidget(label1)
        vl.addStretch()
        vl.addWidget(label2)
        vl.addStretch()
        vl.addWidget(label3)
        vl.addStretch()
        self.setCentralWidget(widget)
        
    def startWin(self) -> None:
        self.window().fillScreen()
    
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))
           
class LastWidget(BasicNavWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent, finishEnabled=True)
        widget = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(0, self.getPx(10), 0, self.getPx(10))
        widget.setLayout(l)
        vl = QVBoxLayout()
        l.addSpacing(self.getPx(10))
        l.addLayout(vl)
        
        label1 = IconLabel(size=64, frame=False)
        label1.setIcon("")
        label1.setText(f"""<h1>You are now ready to go!</h1>
                       <h3>But here are other things you can do:</h3>""")
        
        settings = ButtonLabel(size=64)
        settings.setIcon("deskSettings_color.png")
        settings.setText("""
 <h3>Customize ElevenClock even more</h3>
 Open the settings window and customize ElevenClock even more.""")
        settings.setButtonText("Open")
        settings.clicked.connect(lambda: closeAndOpenSettings())
        
        def closeAndOpenSettings():
            globals.sw.show()
            self.finished.emit()
        
        donate = ButtonLabel(size=64)
        donate.setIcon("coffee_color.png")
        donate.setText("""
 <h3>Suport the developer</h3>
 Developing is hard, and this aplication is free. But if you liked the application, you can always <b>buy me a coffee</b> :)""")
        donate.setButtonText("Make a donation!")
        donate.clicked.connect(lambda: os.startfile("https://ko-fi.com/martinet101"))
        
        report = ButtonLabel(size=64)
        report.setIcon("github_color.png")
        report.setText("""
 <h3>View ElevenClock on GitHub</h3>
 View ElevenClock's source code. From there, you can report bugs or suggest features, or even contribute direcly to The ElevenClock Project""")
        report.setButtonText("Open GitHub")
        report.clicked.connect(lambda: os.startfile("https://github.com/martinet101/ElevenClock"))

        vl.addWidget(label1)
        vl.addStretch()
        vl.addWidget(settings)
        vl.addStretch()
        vl.addWidget(donate)
        vl.addStretch()
        vl.addWidget(report)
        vl.addStretch()
        self.setCentralWidget(widget)
        
    
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))
        
class SelectModeWidget(BasicNavWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent, nextGreyed=True)
        widget = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(0, self.getPx(10), 0, self.getPx(10))
        widget.setLayout(l)
        vl = QVBoxLayout()
        l.addSpacing(self.getPx(10))
        l.addLayout(vl)
        
        label1 = IconLabel(size=self.getPx(96), frame=False)
        label1.setIcon(getPath("monitor_color.png"))
        label1.setText(f"""<h1>How do you want ElevenClock to work?</h1>
                       <h3>Please select one of the following and click next</h3>""")
        
        basicReplace = ClickableButtonLabelWithBiggerIcon(size=96)
        basicReplace.setIcon(getPath(f"defaultClock_{self.iconMode}.png"))
        basicReplace.clicked.connect(lambda: toggleClockMode("secondary"))
        basicReplace.setText("""
 <h3>Add the secondary clock</h3>
 Simple clock that mimics the default clock behaviour""")
        
        formatCustom = ClickableButtonLabelWithBiggerIcon(size=96)
        formatCustom.setIcon(getPath(f"formatClock_{self.iconMode}.png"))
        formatCustom.clicked.connect(lambda: toggleClockMode("format"))
        formatCustom.setText("""
 <h3>Show clocks on every monitor and customize the date and time</h3>
 Enable seconds, weekday, disable date, time, set custom formats...""")
        
        fullCustom = ClickableButtonLabelWithBiggerIcon(size=96)
        fullCustom.setIcon(getPath(f"customClock_{self.iconMode}.png"))
        fullCustom.clicked.connect(lambda: toggleClockMode("custom"))
        fullCustom.setText("""
 <h3>Show clocks on every monitor and customize them entierly</h3>
 Add seconds, weekday, weeknumber, remove date, change font, color background, etc...""")
        
        def toggleClockMode(mode: str) -> None:
            self.enableNextButton()
            if mode == "secondary":
                setSettings("ForceClockOnFirstMonitor", False, r=False)
                setSettings("HideClockOnSecondaryMonitors", False, r=False)
                setSettings("DisableTime", False, r=False)
                setSettings("EnableSeconds", False, r=False)
                setSettings("DisableDate", False, r=False)
                setSettings("EnableWeekNumber", False, r=False)
                setSettings("EnableWeekDay", False, r=False)
                setSettings("UseCustomFont", False, r=False)
                setSettings("UseCustomFontSize", False, r=False)
                setSettings("UseCustomFontColor", False, r=False)
                setSettings("UseCustomBgColor", False, r=False)
                setSettings("CenterAlignment", False)
            elif mode == "format":
                geometry = QGuiApplication.primaryScreen().geometry()
                self.window().bgWindow.hide()
                rgb = QColor(QGuiApplication.primaryScreen().grabWindow(0, geometry.width()-self.getPx(45), geometry.height()-1, 1, 1).toImage().pixel(0, 0))
                self.window().bgWindow.show()
                setSettingsValue("UseCustomBgColor", f"{rgb.red()}, {rgb.green()}, {rgb.blue()}, 100", r=False)
                setSettings("ForceClockOnFirstMonitor", True, r=False)
                setSettings("HideClockOnSecondaryMonitors", False, r=False)
                setSettings("UseCustomFont", False, r=False)
                setSettings("UseCustomFontSize", False, r=False)
                setSettings("UseCustomFontColor", False, r=False)
                setSettings("CenterAlignment", False, r=True)
            elif mode == "custom":
                geometry = QGuiApplication.primaryScreen().geometry()
                self.window().bgWindow.hide()
                rgb = QColor(QGuiApplication.primaryScreen().grabWindow(0, geometry.width()-self.getPx(45), geometry.height()-1, 1, 1).toImage().pixel(0, 0))
                self.window().bgWindow.show()
                setSettingsValue("UseCustomBgColor", f"{rgb.red()}, {rgb.green()}, {rgb.blue()}, 100", r=False)
                setSettings("ForceClockOnFirstMonitor", True, r=False)
                setSettings("HideClockOnSecondaryMonitors", False, r=False)
            else:
                raise ValueError("Function toggleCheckMode() called with invalid arguments. Accepted values are: custom, format, secondary")
                
        vl.addWidget(label1)
        vl.addStretch()
        vl.addWidget(basicReplace)
        vl.addStretch()
        vl.addWidget(formatCustom)
        vl.addStretch()
        vl.addWidget(fullCustom)
        vl.addStretch()
        self.setCentralWidget(widget)
        
    
    def getPx(self, original) -> int:
        return round(original*(self.screen().logicalDotsPerInch()/96))


if __name__ == "__main__":
    import __init__