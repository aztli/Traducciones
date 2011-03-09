class CentralGeneric(object):

    def __init__(self):
        self._mainTabSelected = True
        self._follow_mode = False
        self._tabs = None
        self._tabs2 = None

    def _change_actual(self, tab):
        if tab == self._tabs:
            self._mainTabSelected = True
        else:
            self._mainTabSelected = False

    def actual_tab(self):
        if self._mainTabSelected or not self._tabs2.isVisible():
            return self._tabs
        else:
            return self._tabs2

    def obtain_editor(self):
        return self.actual_tab().obtain_editor()