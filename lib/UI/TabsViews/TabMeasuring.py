from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QGroupBox

class TabMeasuring(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        windowLayout = QGridLayout()
        self.setLayout(windowLayout)
