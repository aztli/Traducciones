from __future__ import absolute_import

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import SIGNAL

from ninja_ide.tools import manage_files
from ninja_ide.tools import loader
from ninja_ide import resources
from ninja_ide.extras.plugins import TextProjectType


class ProjectProperties(QDialog):

    def __init__(self, parent, item):
        QDialog.__init__(self, parent)
        self.setModal(True)
        self._item = item
        self.setWindowTitle('Project Properties')
        grid = QGridLayout(self)
        grid.addWidget(QLabel('Name:'), 0, 0)
        self.name = QLineEdit()
        if self._item.name == '':
            self.name.setText(manage_files.get_basename(self._item.path))
        else:
            self.name.setText(self._item.name)
        grid.addWidget(self.name, 0, 1)
        grid.addWidget(QLabel('Project Type:'), 1, 0)
        self.txtType = TextProjectType()
        self.txtType.setText(self._item.projectType)
        grid.addWidget(self.txtType, 1, 1)
        grid.addWidget(QLabel('Description:'), 2, 0)
        self.description = QPlainTextEdit()
        self.description.setPlainText(self._item.description)
        grid.addWidget(self.description, 2, 1)
        grid.addWidget(QLabel('URL:'), 3, 0)
        self.url = QLineEdit()
        self.url.setText(self._item.url)
        grid.addWidget(self.url, 3, 1)
        grid.addWidget(QLabel('Licence:'), 4, 0)
        self.cboLicense = QComboBox()
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
        index = self.cboLicense.findText(self._item.license)
        self.cboLicense.setCurrentIndex(index)
        grid.addWidget(self.cboLicense, 4, 1)
        grid.addWidget(QLabel('Main File:'), 5, 0)
        self.path = QLineEdit()
        self.path.setText(self._item.mainFile)
        self.path.setReadOnly(True)
        self.btnBrowse = QPushButton('Browse')
        hbox = QHBoxLayout()
        hbox.addWidget(self.path)
        hbox.addWidget(self.btnBrowse)
        grid.addLayout(hbox, 5, 1)

        self.txtExtensions = QLineEdit()
        self.txtExtensions.setText(str(', '.join(self._item.extensions)))
        grid.addWidget(QLabel('Supported Extensions:'), 6, 0)
        grid.addWidget(self.txtExtensions, 6, 1)

        self.txtPythonPath = QLineEdit()
        self.txtPythonPath.setText(self._item.pythonPath)
        self.btnPythonPath = QPushButton(QIcon(resources.images['open']), '')
        grid.addWidget(QLabel('Python Path:'), 7, 0)
        grid.addWidget(self.txtPythonPath, 7, 1)
        grid.addWidget(self.btnPythonPath, 7, 2)

        self.btnSave = QPushButton('Save')
        self.btnCancel = QPushButton('Cancel')
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.btnCancel)
        hbox3.addWidget(self.btnSave)
        grid.addLayout(hbox3, 8, 1)

        self.connect(self.btnBrowse, SIGNAL("clicked()"), self.select_file)
        self.connect(self.btnCancel, SIGNAL("clicked()"), self.close)
        self.connect(self.btnSave, SIGNAL("clicked()"), self.save_properties)
        self.connect(self.btnPythonPath, SIGNAL("clicked()"), self._load_python_path)

    def _load_python_path(self):
        path = str(QFileDialog.getOpenFileName(self, 'Select Python Path'))
        self.txtPythonPath.setText(path)

    def select_file(self):
        fileName = str(QFileDialog.getOpenFileName(self, 'Select Main File',
                        self._item.path, '(*.py);;(*.*)'))
        if fileName != '':
            fileName = manage_files.convert_to_relative(self._item.path, fileName)
            self.path.setText(fileName)

    def save_properties(self):
        if str(self.name.text()).strip() == '':
            QMessageBox.critical(self, 'Properties Invalid', 'The Project must have a name.')
            return
        tempName = self._item.name
        self._item.name = str(self.name.text())
        self._item.description = str(self.description.toPlainText())
        self._item.license = str(self.cboLicense.currentText())
        self._item.mainFile = str(self.path.text())
        self._item.url = str(self.url.text())
        self._item.projectType = str(self.txtType.text())
        self._item.pythonPath = str(self.txtPythonPath.text())
        extensions = str(self.txtExtensions.text()).split(', ')
        self._item.extensions = tuple(extensions)
        #save project properties
        project = {}
        project['name'] = self._item.name
        project['description'] = self._item.description
        project['url'] = self._item.url
        project['license'] = self._item.license
        project['mainFile'] = self._item.mainFile
        project['project-type'] = self._item.projectType
        project['supported-extensions'] = self._item.extensions
        project['pythonPath'] = self._item.pythonPath
        if tempName != self._item.name and \
            manage_files.file_exists(self._item.path, tempName + '.nja'):
            manage_files.delete_file(self._item.path, tempName + '.nja')
        loader.create_ninja_project(self._item.path, self._item.name, project)
        self._item.setText(0, self._item.name)
        self._item.setToolTip(0, self._item.name)
        if self._item.extensions != manage_files.supported_extensions:
            self._item._parent._refresh_project(self._item)
        self.close()
