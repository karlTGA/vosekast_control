from lib.UI.ControlField import ControlField, NoImageForIconError
from lib.ExperimentEnvironment import ExperimentEnvironment
import os
import logging
from lib.Log import LOGGER
from PyQt5.QtGui import QIcon

from lib.EnumStates import States

class StopButton(ControlField):

    def __init__(self, text):
        super().__init__(text)
        self.logger = logging.getLogger(LOGGER)

    def toggle_control_instance(self):
        self.control_instance.stop_experiment()

    def handle_state_change(self, new_state):
        self.button.setIcon(QIcon(self.get_icon(new_state)))
        print('OnOff State change')
        self.label.setText(self.text + ' - ' + new_state.name)# + str(new_state.name))
        self.state = new_state

    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))
        if state == States.NONE or state == States.STOPPED:
            icon_path = os.path.join(path, 'icons/stop_icons/stop_sw.png')
        else:
            icon_path = os.path.join(path, 'icons/stop_icons/stop_color.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path
