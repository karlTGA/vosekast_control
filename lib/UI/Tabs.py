from PyQt5.QtWidgets import QWidget, QTabWidget, QLineEdit, QFormLayout
from lib.UI.TabStatus import TabStatus


class Tabs(QTabWidget):

    def __init__(self):
        super().__init__()

        self.tabStatus = TabStatus()
        self.addTab(self.tabStatus, "Tab Status")
        self.setTabText(0, "Tab Status")
