from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize


class Toolbar(QToolBar):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # actions
        exitAction = QAction(QIcon.fromTheme("application-exit"), 'Exit', self.main_window)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.main_window.closeEvent)

        self.addAction(exitAction)
        self.setIconSize(QSize(64, 64))

    def add_link(self, tabsWidget, indexToChange, name, icon):
        link_action = QAction(QIcon.fromTheme(icon), name, self.main_window)
        link_action.triggered.connect(lambda: tabsWidget.setCurrentIndex(indexToChange))

        self.addAction(link_action)
