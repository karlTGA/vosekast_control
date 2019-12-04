from lib.Valve import Valve
from lib.UI.ControlField import ControlField, NoImageForIconError
import os
from lib.EnumStates import States


class ValveControl(ControlField):
    def __init__(self, text):
        super().__init__(text, default_state=States.OPEN)
        self.valve = None

    def set_valve(self, valve_instance):
        self.set_control_instance(valve_instance)
        self.valve = valve_instance

    def toggle_control_instance(self):
        if self.state == States.CLOSED:
            self.valve.open()
        else:
            self.valve.close()

    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))

        if state == States.OPEN:
            icon_path = os.path.join(path, "icons/valve_icons/valve_color_1.png")
        else:
            icon_path = os.path.join(path, "icons/valve_icons/valve_sw.png")

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path
