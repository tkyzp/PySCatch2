
import sys

import webbrowser

from PIL import ImageQt
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QDesktopWidget, QMessageBox, QSystemTrayIcon, \
    QMenu, QAction, QGraphicsOpacityEffect
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui

import pyzbar.pyzbar as zbar


class Scaner(QWidget):


    def __init__(self):
        super(Scaner, self).__init__()
        self.INIT()

    def INIT(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        desktopRect = QDesktopWidget().screenGeometry()
        self.setGeometry(desktopRect)
        self.setStyleSheet('''background-color:black; ''')
        #self.setWindowOpacity(0.4)
        self.setCursor(Qt.CrossCursor)
        self.blackMask = QBitmap(desktopRect.size())
        self.blackMask.fill(Qt.black)
        self.mask = self.blackMask.copy()
        self.isDrawing = False
        self.startPoint = QPoint()
        self.endPoint = QPoint()
        self.bg = QLabel(self)
        self.bg.lower()
        self.fg = QLabel(self)
        self.fg.raise_()
        self.fg.setPixmap(self.blackMask)
        op = QGraphicsOpacityEffect()
        op.setOpacity(0.4)
        self.fg.setGraphicsEffect(op)


    def scan(self):
        #截图
        self.screenshot = QApplication.primaryScreen().grabWindow(0)
        self.bg.setPixmap(self.screenshot)
        self.show()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            self.isDrawing = False
            self.hide()

    def paintEvent(self, event):
        if self.isDrawing:
            self.mask = self.blackMask.copy()
            pp = QPainter(self.mask)
            pen = QPen()
            pen.setStyle(Qt.NoPen)
            pp.setPen(pen)
            brush = QBrush(Qt.white)
            pp.setBrush(brush)
            pp.drawRect(QRect(self.startPoint, self.endPoint))
            self.fg.setMask(QBitmap(self.mask))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPoint = event.pos()
            self.endPoint = self.startPoint
            self.isDrawing = True

    def mouseMoveEvent(self, event):
        if self.isDrawing:
            self.endPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.isDrawing = False


        rect = QRect(self.startPoint, self.endPoint)
        self.result = self.screenshot.copy(rect)

        scan_result = zbar.decode(ImageQt.fromqpixmap(self.result))
        self.fg.clearMask()
        self.hide()
        if len(scan_result) > 0:
            result_str = scan_result[0].data.decode()

            QApplication.clipboard().setText(result_str)
            QMessageBox.information(None, "结果",result_str + "\n内容已复制到剪贴板!")
        else:
            QMessageBox.warning(None, "错误", "没有发现二维码，请重试!")



class TaskBar(QSystemTrayIcon):

    def __init__(self, scan, app):
        super(TaskBar, self).__init__()
        self.setParent(app)
        self.scan = scan
        self.app = app
        self.setToolTip("PySCatch2\n [F7] 扫描屏幕中的二维码\nGitHub:https://github.com/tkyzp/PySCatch2")
        self.setIcon(QIcon("icon.png"))
        self.activated.connect(self.iconActivated)
        menu = QMenu()
        self.scanAction = QAction("识别")
        self.scanAction.triggered.connect(self.scanEvent)
        self.exitAction = QAction("退出")
        self.exitAction.triggered.connect(self.exitEvent)
        self.aboutAction = QAction("关于")
        self.aboutAction.triggered.connect(self.aboutEvent)
        menu.addAction(self.scanAction)
        menu.addAction(self.aboutAction)
        menu.addSeparator()
        menu.addAction(self.exitAction)
        self.setContextMenu(menu)
        self.show()

    def aboutEvent(self):
        try:
            webbrowser.open("https://github.com/tkyzp/PySCatch2")
        except:
            QMessageBox(None, "关于", "By tkyzp\n 详见：https://github.com/tkyzp/PySCatch2")

    def scanEvent(self):
        self.scan.scan()

    def exitEvent(self):
        sys.exit()

    def iconActivated(self, reason: 'QSystemTrayIcon.ActivationReason') -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.scan.scan()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setQuitOnLastWindowClosed(False)
    scaner = Scaner()
    taskbar = TaskBar(scaner, app)
    taskbar.showMessage("通知", "点击系统托盘中的的图标即可扫描屏幕中的二维码", QIcon("icon.png"))
    app.exec_()



