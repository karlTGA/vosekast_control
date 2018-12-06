from lib.UI.ControlField import ControlField, NoImageForIconError
from lib.ExperimentEnvironment import ExperimentEnvironment
import os


class OnOffControl(ControlField):

    def __init__(self, text):
        super().__init__(text, default_state = None)

        self.experiment_environment = None

    def set_exp_env(self, exp_env):
        self.set_control_instance(exp_env)
        self.experiment_environment = exp_env
        print('Hallo!!!')



    def toggle_control_instance(self):
        self.experiment_environment.start_run()

    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))
        print(state)
        if state is None:
            icon_path = os.path.join(path, 'icons/on_off_icons/color.png')
        else:
            icon_path = os.path.join(path, 'icons/on_off_icons/sw.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path
