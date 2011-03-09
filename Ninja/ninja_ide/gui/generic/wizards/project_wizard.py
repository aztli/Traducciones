class ProjectWizard(object):

    types = {}

    def __init__(self):
        pass

    def getPages(self):
        return []

    def onWizardFinish(self, wizard):
        raise NotImplementedError()