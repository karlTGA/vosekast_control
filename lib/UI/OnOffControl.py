from lib.UI.ControlField import ControlField, NoImageForIconError
import os


class OnOffControl(ControlField):

    def __init__(self, text):
        super().__init__(text, default_state = None)

#    def toggle_on_off(self):
#        if self.state ==

    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))
        print('On/Off', state)
        if state == None:
            icon_path = os.path.join(path, 'icons/on_off_icons/color.png')
        else:
            icon_path = os.path.join(path, 'icons/on_off_icons/sw.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path
