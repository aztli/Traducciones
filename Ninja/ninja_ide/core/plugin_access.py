class PluginAccess(object):

    tabs = None
    editor = None
    projects = None

    def __init__(self):
        self.tabs = Tabs()
        self.editor = Editor()
        self.projects = Projects()


class Tabs(object):

    add_new_editor = None
    add_tab = None
    save_file = None
    open_document = None
    open_image = None

    def __init__(self):
        pass


class Editor(object):

    __get_editor = None
    get_text = None
    editor_path = None

    def __init__(self):
        pass


class Projects(object):

    selected_project_path = None
    tree_projects = None

    def __init__(self):
        pass