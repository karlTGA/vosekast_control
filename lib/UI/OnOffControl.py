from lib.UI.ControlField import ControlField, NoImageForIconError
from lib.ExperimentEnvironment import ExperimentEnvironment, RUNNING
import os
import logging
from lib.Log import LOGGER
from PyQt5.QtGui import QIcon

from lib.EnumStates import States

class OnOffControl(ControlField):

    def __init__(self, text):
        super().__init__(text, default_state = None)
        self.logger = logging.getLogger(LOGGER)
        self.experiment_environment = None

    def toggle_control_instance(self):
        self.control_instance.start_run()

    def handle_state_change(self, new_state):
        self.button.setIcon(QIcon(self.get_icon(new_state)))
        self.label.setText(self.text + ' - ' + str(States(new_state).name))
        print('Hallo!!')
        self.state = new_state





    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))
        logger = logging.getLogger(LOGGER)
        logger.debug('New State ' + str(state == RUNNING))
        if state == RUNNING:
            icon_path = os.path.join(path, 'icons/on_off_icons/color.png')
        else:
            icon_path = os.path.join(path, 'icons/on_off_icons/sw.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path
