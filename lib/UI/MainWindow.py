from PyQt5.QtWidgets import QMainWindow, QWidget, QToolTip, QPushButton, QApplication, QMessageBox, QDesktopWidget, QHBoxLayout, QVBoxLayout, QAction
from PyQt5.QtCore import pyqtSlot, QSize
from PyQt5.QtGui import QIcon
from lib.UI.Tabs import Tabs


class MainWindow(QMainWindow):
    # Process States
    GUI_RUNNING = 'GUI_RUNNING'
    GUI_TERMINATED = 'GUI_TERMINATED'

    def __init__(self, app, app_control):
        super().__init__()
        self.main_app = app
        self.app_control = app_control
        self.status_bar = None
        self.tabs = None
        self.layout = None
        self.initUI()
        self.state = self.GUI_RUNNING

    def initUI(self):
        self.resize(1024, 600)
        self.center()

        # init status bar
        self.status_bar = self.statusBar()

        # actions
        exitAction = QAction(QIcon.fromTheme("application-exit"), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.closeEvent)

        self.toolbar = self.addToolBar('main')
        self.toolbar.addAction(exitAction)
        self.toolbar.setIconSize(QSize(64, 64))

        # tabs with different informations and control
        self.tabs = Tabs()
        self.setCentralWidget(self.tabs)

        self.show()
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

