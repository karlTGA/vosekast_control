from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QApplication, QMessageBox
from PyQt5.QtGui import QFont, QIcon


class MainWindow(QWidget):
    # Process States
    GUI_RUNNING = 'GUI_RUNNING'
    GUI_TERMINATED = 'GUI_TERMINATED'

    def __init__(self, app):
        super().__init__()
        self.main_app = app
        self.initUI()
        self.state = self.GUI_RUNNING

    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))

        self.setToolTip('This is a <b>QWidget</b> widget')

        btn = QPushButton('Quit', self)
        btn.resize(btn.sizeHint())
        btn.move(50, 50)

        self.setGeometry(600, 600, 300, 220)
        self.setWindowTitle('Tooltips')
        self.setWindowIcon(QIcon('web.png'))

        self.show()

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            self.state = self.GUI_TERMINATED
            self.main_app.quit()
        else:
            event.ignore()