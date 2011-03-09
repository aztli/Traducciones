from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QCompleter

class PluginBase(object):
    _name = 'Unnamed Plugin'
    _description = "No description"
    _version = 1.0
    _authors = []

    def __init__(self, access):
        """Set the Plugin configuration"""
        self.access = access

    def eventKeyReturn(self):
        pass

    def eventKeyAny(self):
        pass

    def executeProgram(self):
        pass

    def executeFile(self):
        pass

    def toolbarAction(self):
        pass

    def addMenuApp(self):
        pass

    def stackWidget(self):
        raise NotImplementedError()

    def propertiesWidget(self):
        raise NotImplementedError()

    def menuProject(self):
        raise NotImplementedError()

    def menuEditor(self):
        raise NotImplementedError()

    def getPages(self):
        return []

    def onWizardFinish(self, wizard):
        pass

    def projectFiles(self):
        pass


class TextLanguage(QLineEdit):

    langs = []

    def __init__(self):
        QLineEdit.__init__(self)
        completer = QCompleter(sorted(self.langs), self)
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(completer)


class TextProjectType(QLineEdit):

    types = ['python']

    def __init__(self):
        QLineEdit.__init__(self)
        completer = QCompleter(sorted(self.types))
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(completer)
