class TreeProjectGeneric(object):

    def __init__(self):
        pass

    def get_selected_project_path(self):
        raise NotImplementedError()


class Project(object):

    def __init__(self):
        self.name = ''
        self.description = ''
        self.url = ''
        self.license = ''
        self.mainFile = ''