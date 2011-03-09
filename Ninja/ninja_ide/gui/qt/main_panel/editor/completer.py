from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QVariant
from PyQt4.QtCore import SIGNAL


from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QListWidgetItem

import rope.base.project
from rope.contrib import codeassist

from ninja_ide import resources


class Completer(QCompleter):

    def __init__(self, editor, project):
        QCompleter.__init__(self)

        self.icons = {'function': QIcon(resources.images['function']),
            'instance': QIcon(resources.images['attribute']),
            'module': QIcon(resources.images['module']),
            'class': QIcon(resources.images['class'])}

        self._editor = editor
        self._fromProject = False
        if project is not None:
            if type(project) is str:
                project = rope.base.project.Project(project, None, '.ninjaproject')
            self._project = project
            self._fromProject = True
        else:
            self._project = rope.base.project.get_no_project()
        self.setWidget(self._editor)
        self.popupView = QListWidget()
        self.popupView.setAlternatingRowColors(True)
        self.popupView.setWordWrap(False)
        self.setPopup(self.popupView)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)

        self.connect(self, SIGNAL("activated(QString)"), self.insert_completion)

    def insert_completion(self, insert):
        extra = insert.length() - self.completionPrefix().length()
        self._editor.textCursor().insertText(insert.right(extra))

    def complete(self, cr):
        if self._project:
            try:
                self.popupView.clear()
                code = str(self._editor.toPlainText())
                start = self._editor.textCursor().position()
                if self._fromProject:
                    self._project.validate()
                proposals = codeassist.code_assist(self._project, code, start)
                proposals = codeassist.sorted_proposals(proposals)
                model = self.obtain_model_items(proposals)
                self.setModel(model)
                self.popup().setCurrentIndex(model.index(0, 0))
                cr.setWidth(self.popup().sizeHintForColumn(0) \
                    + self.popup().verticalScrollBar().sizeHint().width() + 10)
                self.popupView.updateGeometries()
                super(Completer, self).complete(cr)
            except:
                return

    def obtain_model_items(self, proposals):
        for p in proposals:
            if p.type == 'function':
                self.popupView.addItem(QListWidgetItem(self.icons[p.type], 
                    '%s(%s)' % (p.name, ', '.join(
                    [n for n in p.pyname.get_object().get_param_names() if n != 'self']))))
            else:
                self.popupView.addItem(QListWidgetItem(
                    self.icons.get(p.type, self.icons['class']), p.name))
        return self.popupView.model()

    def get_path_from_project(self):
        if self._fromProject:
            return self._project.root.real_path
        else:
            return None
