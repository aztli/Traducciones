from __future__ import absolute_import

import sys

from PyQt4.QtGui import QAction
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QShortcut
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QCoreApplication

from ninja_ide import resources
from ninja_ide.resources import OS_KEY
from ninja_ide.gui.generic.wizards import ProjectWizard


class MenuFile(object):

    def __init__(self, menu, tool, main):
        self._main = main

        newAction = menu.addAction(QIcon(resources.images['new']), '&New ('+OS_KEY+'+N)')
        newProjectAction = menu.addAction(QIcon(resources.images['newProj']), 'New Pro&ject ('+OS_KEY+'+J)')
        menu.addSeparator()
        saveAction = menu.addAction(QIcon(resources.images['save']), '&Save ('+OS_KEY+'+S)')
        saveAsAction = menu.addAction(QIcon(resources.images['saveAs']), 'Save &As')
        saveAllAction = menu.addAction(QIcon(resources.images['saveAll']), 'Save A&ll ('+OS_KEY+'+Shift+S)')
        menu.addSeparator()
        reloadFileAction = menu.addAction(QIcon(resources.images['reload-file']), 'Reload File (F5)')
        menu.addSeparator()
        openAction = menu.addAction(QIcon(resources.images['open']), '&Open ('+OS_KEY+'+O)')
        openProjectAction = menu.addAction(QIcon(resources.images['openProj']), 'Open &Project ('+OS_KEY+'+P)')
        openProjectTypeAction = menu.addAction(QIcon(resources.images['openProj']), 'Open Project &Type')
        menu.addSeparator()
        printFile = menu.addAction(QIcon(resources.images['print']), 'Pr&int File (' + OS_KEY + '+I)')
        closeAction = menu.addAction(self._main.style().standardIcon(QStyle.SP_DialogCloseButton), '&Close Tab')
        menu.addSeparator()
        exitAction = menu.addAction(self._main.style().standardIcon(QStyle.SP_DialogCloseButton), '&Exit')

        tool.addAction(newAction)
        tool.addAction(newProjectAction)
        tool.addAction(openAction)
        tool.addAction(openProjectAction)
        tool.addAction(saveAction)
        #tool.addAction(saveAllAction)

        QObject.connect(newAction, SIGNAL("triggered()"), main.new_editor)
        QObject.connect(newProjectAction, SIGNAL("triggered()"), main.new_project)
        QObject.connect(openAction, SIGNAL("triggered()"), main.open_file)
        QObject.connect(saveAction, SIGNAL("triggered()"), main.save)
        QObject.connect(saveAsAction, SIGNAL("triggered()"), main.save_as)
        QObject.connect(saveAllAction, SIGNAL("triggered()"), main.save_project)
        QObject.connect(openProjectAction, SIGNAL("triggered()"), main.open_project_folder)
        QObject.connect(openProjectTypeAction, SIGNAL("triggered()"), self._open_project_type)
        QObject.connect(closeAction, SIGNAL("triggered()"), main.close_actual_tab)
        QObject.connect(exitAction, SIGNAL("triggered()"), QCoreApplication.quit)
        QObject.connect(reloadFileAction, SIGNAL("triggered()"), main.reload_file)
        QObject.connect(printFile, SIGNAL("triggered()"), main._print_file)

    def _open_project_type(self):
        self.openType = OpenProjectType(self._main)
        self.openType.show()


class OpenProjectType(QDialog, ProjectWizard):

    def __init__(self, main):
        QDialog.__init__(self)
        ProjectWizard.__init__(self)
        self._main = main
        self.setModal(True)
        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel('Select the Type of Project:'))
        self.listWidget = QListWidget()
        projectTypes = self.types.keys()
        projectTypes.sort()
        self.listWidget.addItems(projectTypes)
        vbox.addWidget(self.listWidget)
        btnNext = QPushButton('Next')
        vbox.addWidget(btnNext)
        if len(projectTypes) > 0:
            self.listWidget.setCurrentRow(0)
        else:
            btnNext.setEnabled(False)

        self.connect(btnNext, SIGNAL("clicked()"), self._open_project)

    def _open_project(self):
        type_ = str(self.listWidget.currentItem().text())
        extensions = self.types[type_].projectFiles()
        if extensions is None:
            self._main.open_project_folder()
        else:
            self._main.open_project_type(extensions)
