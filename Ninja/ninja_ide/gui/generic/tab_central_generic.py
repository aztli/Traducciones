class TabCentralGeneric(object):

    def __init__(self):
        self._follow_mode = False

    def obtain_editor(self):
        raise NotImplementedError()