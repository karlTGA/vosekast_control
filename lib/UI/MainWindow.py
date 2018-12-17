from PyQt5.QtWidgets import QMainWindow, QWidget, QToolTip, QPushButton, QApplication, QMessageBox, QDesktopWidget, QHBoxLayout, QVBoxLayout, QAction
from PyQt5.QtCore import pyqtSlot, QSize
from PyQt5.QtGui import QIcon
from lib.UI.Tabs import Tabs
from lib.UI.Toolbar import Toolbar


class MainWindow(QMainWindow):
    # Process States
    GUI_RUNNING = 'GUI_RUNNING'
    GUI_TERMINATED = 'GUI_TERMINATED'

    def __init__(self, app, app_control, debug, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_app = app
        self.app_control = app_control
        self.status_bar = None
        self.tabs = None
        self.layout = None
        self.debug = debug
        self.initUI()
        self.state = self.GUI_RUNNING

    def initUI(self):
        self.resize(1024, 600)
        self.center()

        # init status bar
        self.status_bar = self.statusBar()

        # init toolbar
        self.toolbar = Toolbar(self)
        self.addToolBar(self.toolbar)

        # tabs with different informations and control
        self.tabs = Tabs(self.toolbar)
        self.setCentralWidget(self.tabs)

        self.show()
        if not self.debug:
            self.showFullScreen()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if hasattr(event, 'accept'):
                event.accept()
            self.state = self.GUI_TERMINATED
            self.app_control.shutdown()
            self.main_app.quit()
        else:
            if hasattr(event, 'ignore'):
                event.ignore()

    @pyqtSlot(str)
    def send_status_message(self, message):
        if not self.app_control.is_terminating() and self.state == self.GUI_RUNNING:
            self.status_bar.showMessage(message)

