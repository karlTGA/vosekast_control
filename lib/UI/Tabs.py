from PyQt5.QtWidgets import QTabWidget, QTextEdit, QMenu, QToolButton, QTabBar

from lib.UI.TabsViews.TabStatus import TabStatus
from lib.UI.TabsViews.TabMeasuring import TabMeasuring
from lib.UI.TabsViews.TabProgramms import TabProgramms

class Tabs(QTabWidget):

    # tab names
    TAB_STATUS = "Tab Status"
    TAB_MEASURING = "Tab Measuring"
    TAB_PROGRAMMS = "Tab Programms"

    def __init__(self, main_toolbar):
        super().__init__()

        self.main_toolbar = main_toolbar

        status_index = 0
        self.tabStatus = TabStatus()
        self.addTab(self.tabStatus, self.TAB_STATUS)
        self.setTabText(status_index, self.TAB_STATUS)
        self.main_toolbar.add_link(self, status_index, self.TAB_STATUS, 'multimedia-volume-control')

        measuring_index = 1
        self.tabMeasuring = TabMeasuring()
        self.addTab(self.tabMeasuring, self.TAB_MEASURING)
        self.setTabText(measuring_index, self.TAB_MEASURING)
        self.main_toolbar.add_link(self, measuring_index, self.TAB_MEASURING, 'x-office-spreadsheet')

        programms_index = 2
        self.tabProgramms = TabProgramms()
        self.addTab(self.tabProgramms, self.TAB_PROGRAMMS)
        self.setTabText(programms_index, self.TAB_PROGRAMMS)
        self.main_toolbar.add_link(self, programms_index, self.TAB_PROGRAMMS, 'x-office-spreadsheet')



        # utilities-system-monitor   -- Window with EKG
        # utilities-terminal  -- Window with terminal
