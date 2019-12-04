from lib.UI.ControlField import ControlField, NoImageForIconError
from lib.ExperimentEnvironment import ExperimentEnvironment
import os
import logging
from lib.Log import LOGGER
from PyQt5.QtGui import QIcon

from lib.EnumStates import States


class StartPauseButton(ControlField):
    """ Button which controls the experiment. Starts and pauses this experiment.
    Inherites from ControlField. A control instance has to be added.
    """

    def __init__(self, text):
        super().__init__(text)
        self.logger = logging.getLogger(LOGGER)

    def toggle_control_instance(self):
        if self.control_instance.state == States.RUNNING:
            self.control_instance.pause_experiment()
        elif self.control_instance.state == States.PAUSE:
            self.control_instance.continue_experiment()
        else:
            self.control_instance.start_experiment()

    def handle_state_change(self, new_state):
        self.button.setIcon(QIcon(self.get_icon(new_state)))
        self.label.setText(self.text + " - " + new_state.name)  # + str(new_state.name))
        self.state = new_state

    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))
        if state == States.RUNNING:
            icon_path = os.path.join(path, "icons/on_off_icons/PauseRed.png")
        else:
            icon_path = os.path.join(path, "icons/on_off_icons/StartGreen.png")

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path
