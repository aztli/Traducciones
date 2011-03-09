from __future__ import absolute_import

from PyQt4.QtGui import QWizard
from PyQt4.QtGui import QWizardPage
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QPixmap
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.gui.generic.wizards import ProjectWizard
from ninja_ide.tools import loader
from ninja_ide.tools import manage_files


class WizardNewProject(QWizard, ProjectWizard):

    def __init__(self, parent):
        QWizard.__init__(self, parent, Qt.Dialog)
        ProjectWizard.__init__(self)
        self._main = parent
        ProjectWizard.types['Python'] = self
        self.setWindowTitle('NINJA - New Project Wizard')
        self.setPixmap(QWizard.LogoPixmap, QPixmap(resources.images['icon']))
        self.option = 'Python'

        pageType = PageProjectType(self)
        self.addPage(pageType)

        self.addPage(PageProjectProperties())

    def add_project_pages(self, option):
        self.option = option
        pages = ProjectWizard.types[option].getPages()
        listIds = self.pageIds()
        listIds.pop(listIds.index(0))
        for p in pages:
            self.addPage(p)
        self.addPage(PageProjectProperties())
        for i in listIds:
            self.removePage(i)

    def done(self, result):
        if result == 1:
            ProjectWizard.types[self.option].onWizardFinish(self)
        super(WizardNewProject, self).done(result)

    def onWizardFinish(self, wizard):
        ids = wizard.pageIds()
        page = wizard.page(ids[1])
        place = str(page.txtPlace.text())
        if place == '':
            QMessageBox.critical(self, 'Incorrect Location', 'The project couldn\'t be create')
            return
        folder = str(page.txtFolder.text()).replace(' ', '_')
        path = resources.createpath(place, folder)
        if not manage_files.folder_exists(path):
            manage_files.create_folder(path)
        project = {}
        name = str(page.txtName.text())
        project['name'] = name
        project['description'] = str(page.txtDescription.toPlainText())
        project['license'] = str(page.cboLicense.currentText())
        loader.create_ninja_project(path, name, project)
        self.load_project(path)

    def load_project(self, path):
        self._main._properties._treeProjects.load_project(self._main.open_project(path), path)
        self._main.add_to_recent_projects(path)

    def load_project_with_extensions(self, path, extensions):
        self._main._properties._treeProjects.load_project(self._main.open_project_with_extensions(path), path)


class PageProjectType(QWizardPage):

    def __init__(self, wizard):
        QWizardPage.__init__(self)
        self.setTitle('Project Type')
        self.setSubTitle('Choose the Project Type')
        self._wizard = wizard
        vbox = QVBoxLayout(self)
        self.listWidget = QListWidget()
        vbox.addWidget(self.listWidget)
        types = self._wizard.types.keys()
        types.sort()
        self.listWidget.addItems(types)
        index = types.index('Python')
        self.listWidget.setCurrentRow(index)

        self.connect(self.listWidget, SIGNAL("itemSelectionChanged()"), self.item_changed)

    def item_changed(self):
        self._wizard.add_project_pages(str(self.listWidget.currentItem().text()))


class PageProjectProperties(QWizardPage):

    def __init__(self):
        QWizardPage.__init__(self)
        self.setTitle('New Project Data')
        self.setSubTitle('Complete the following fields to create the Project Structure')

        g_box = QGridLayout(self)
        #Names of the blanks to complete
        self.lbl_Name = QLabel('New Project Name (*):')
        self.lbl_Place = QLabel('Project Location (*):')
        self.lbl_Folder = QLabel('Projet Folder:')
        self.lbl_Description = QLabel('Project Description:')
        self.lbl_License = QLabel('Project License:')
        g_box.addWidget(self.lbl_Name, 0, 0,Qt.AlignRight)
        g_box.addWidget(self.lbl_Folder, 1, 0,Qt.AlignRight)
        g_box.addWidget(self.lbl_Place, 2, 0,Qt.AlignRight)
        g_box.addWidget(self.lbl_Description, 3, 0,Qt.AlignTop)
        g_box.addWidget(self.lbl_License, 4, 0,Qt.AlignRight)

        #Blanks on de right of the grid
        self.txtName = QLineEdit()
        self.registerField('projectName*', self.txtName)
        #Here comes a LineEdit and a PushButton in a HBoxLayout
        h_Place = QHBoxLayout()
        self.txtPlace = QLineEdit()
        self.txtPlace.setReadOnly(True)
        self.registerField('place*', self.txtPlace)
        self.btnExamine = QPushButton('Examine...')
        h_Place.addWidget(self.txtPlace)
        h_Place.addWidget(self.btnExamine)
        #Now lets continue with the rest
        self.txtFolder = QLineEdit()
        self.txtDescription = QPlainTextEdit()
        self.cboLicense = QComboBox()
        self.cboLicense.setFixedWidth(250)
        self.cboLicense.addItem('Apache License 2.0')
        self.cboLicense.addItem('Artistic License/GPL')
        self.cboLicense.addItem('Eclipse Public License 1.0')
        self.cboLicense.addItem('GNU General Public License v2')
        self.cboLicense.addItem('GNU General Public License v3')
        self.cboLicense.addItem('GNU Lesser General Public License')
        self.cboLicense.addItem('MIT License')
        self.cboLicense.addItem('Mozilla Public License 1.1')
        self.cboLicense.addItem('New BSD License')
        self.cboLicense.addItem('Other Open Source')
        self.cboLicense.addItem('Other')
        self.cboLicense.setCurrentIndex(4)
        g_box.addWidget(self.txtName, 0, 1)
        g_box.addWidget(self.txtFolder, 1, 1)
        g_box.addLayout(h_Place, 2, 1)
        g_box.addWidget(self.txtDescription, 3, 1)
        g_box.addWidget(self.cboLicense, 4, 1)

        #Signal
        self.connect(self.btnExamine, SIGNAL('clicked()'), self.load_folder)

    def load_folder(self):
        self.txtPlace.setText(str(QFileDialog.getExistingDirectory(self, 'New Project Folder')))
