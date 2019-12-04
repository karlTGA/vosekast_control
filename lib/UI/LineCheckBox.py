from PyQt5.QtWidgets import QCheckBox


class LineCheckBox(QCheckBox):
    """ Inherites QCheckBox; A line can be added so that toggling the button
    toggles the added line
    """

    def __init__(self, TabProgramms, name, default_state=True):
        super().__init__(name)
        self.TabProgramms = TabProgramms
        self.default_state = default_state
        self.setChecked(self.default_state)
        self.stateChanged.connect(self.toggle_line)

    def toggle_line(self):
        if self.line.get_visible():
            self.line.set_visible(False)
        else:
            self.line.set_visible(True)
        self.TabProgramms.screen.draw_idle()

    def add_line(self, line):
        self.line = line
