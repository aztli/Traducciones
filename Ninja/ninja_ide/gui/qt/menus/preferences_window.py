from __future__ import absolute_import

import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QCoreApplication

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QSpinBox
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QRadioButton
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QFontDialog
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QSize

from ninja_ide import resources
from ninja_ide.tools import manage_files
from ninja_ide.tools import loader
from ninja_ide.gui.generic.main_panel import EditorGeneric


class PreferencesWindow(QDialog):

    def __init__(self, main):
        QDialog.__init__(self, main)
        self.setWindowTitle('NINJA - Preferences')
        self.setMaximumSize(QSize(0, 0))
        #self.setFixedWidth(600)
        self.setModal(True)
        self._main = main

        #Tabs
        vbox = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setMovable(False)
        self.general = GeneralTab()
        self.interface = InterfaceTab(self._main)
        self.skins = SkinsTab()
        self.editor = EditorTab(self._main)
        self.tabs.addTab(self.general, 'General')
        self.tabs.addTab(self.interface, 'Interface')
        self.tabs.addTab(self.editor, 'Editor')
        self.tabs.addTab(self.skins, 'Skins')
        #Buttons (save-cancel)
        hbox = QHBoxLayout()
        self.btnSave = QPushButton('Save')
        self.btnCancel = QPushButton('Cancel')
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnCancel)
        hbox.addWidget(self.btnSave)
        gridFooter = QGridLayout()
        gridFooter.addLayout(hbox, 0, 0, Qt.AlignRight)

        vbox.addWidget(self.tabs)
        vbox.addLayout(gridFooter)

        self.connect(self.btnSave, SIGNAL("clicked()"), self._save)
        self.connect(self.btnCancel, SIGNAL("clicked()"), self.close)

    def _save(self):
        for i in range(self.tabs.count()):
            self.tabs.widget(i).save()
        self.close()


class GeneralTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)

        groupBoxStart = QGroupBox('On Start:')
        groupBoxClose = QGroupBox('On Close:')
        groupBoxWorkspace = QGroupBox('Workspace and Project:')

        #Start
        vboxStart = QVBoxLayout(groupBoxStart)
        self.checkLastSession = QCheckBox('Load files from last session')
        self.checkActivatePlugins = QCheckBox('Activate Plugins')
        self.checkNotifyUpdates = QCheckBox('Nofity me for new available updates.')
        vboxStart.addWidget(self.checkLastSession)
        vboxStart.addWidget(self.checkActivatePlugins)
        vboxStart.addWidget(self.checkNotifyUpdates)
        #Close
        vboxClose = QVBoxLayout(groupBoxClose)
        self.checkConfirmExit = QCheckBox('Confirm Exit.')
        vboxClose.addWidget(self.checkConfirmExit)
        #Workspace and Project
        gridWorkspace = QGridLayout(groupBoxWorkspace)
        self.txtWorkspace = QLineEdit()
        self.txtWorkspace.setReadOnly(True)
        self.btnWorkspace = QPushButton(QIcon(resources.images['openFolder']), '')
        gridWorkspace.addWidget(QLabel('Workspace'), 0, 0, Qt.AlignRight)
        gridWorkspace.addWidget(self.txtWorkspace, 0, 1)
        gridWorkspace.addWidget(self.btnWorkspace, 0, 2)
        self.txtExtensions = QLineEdit()
        gridWorkspace.addWidget(QLabel('Supported Extensions:'), 1, 0, Qt.AlignRight)
        gridWorkspace.addWidget(self.txtExtensions, 1, 1)
        self.txtPythonPath = QLineEdit()
        self.btnPythonPath = QPushButton(QIcon(resources.images['open']), '')
        gridWorkspace.addWidget(QLabel('Python Path:'), 2, 0, Qt.AlignRight)
        gridWorkspace.addWidget(self.txtPythonPath, 2, 1)
        gridWorkspace.addWidget(self.btnPythonPath, 2, 2)
        gridWorkspace.addWidget(QLabel('(This property need to be configured for Windows)'), 3, 1, Qt.AlignRight)

        #Settings
        settings = QSettings()
        settings.beginGroup('preferences')
        settings.beginGroup('general')
        self.checkLastSession.setCheckState(settings.value('loadFiles', Qt.Checked).toInt()[0])
        self.checkActivatePlugins.setCheckState(settings.value('activatePlugins', Qt.Checked).toInt()[0])
        self.checkNotifyUpdates.setCheckState(settings.value('notifyUpdates', Qt.Checked).toInt()[0])
        self.checkConfirmExit.setCheckState(settings.value('confirmExit', Qt.Checked).toInt()[0])
        self.txtWorkspace.setText(settings.value('workspace', '').toString())
        self.txtPythonPath.setText(settings.value('pythonPath', resources.python_path).toString())
        extensions = tuple(settings.value('extensions', list(manage_files.supported_extensions)).toList())
        extensions = ', '.join([str(e.toString()) for e in extensions])
        self.txtExtensions.setText(extensions)
        settings.endGroup()
        settings.endGroup()

        vbox.addWidget(groupBoxStart)
        vbox.addWidget(groupBoxClose)
        vbox.addWidget(groupBoxWorkspace)

        #Signals
        self.connect(self.btnWorkspace, SIGNAL("clicked()"), self._load_workspace)
        self.connect(self.btnPythonPath, SIGNAL("clicked()"), self._load_python_path)

    def _load_workspace(self):
        path = str(QFileDialog.getExistingDirectory(self, 'Select Workspace'))
        self.txtWorkspace.setText(path)

    def _load_python_path(self):
        path = str(QFileDialog.getOpenFileName(self, 'Select Python Path'))
        self.txtPythonPath.setText(path)

    def save(self):
        settings = QSettings()
        settings.beginGroup('preferences')
        settings.beginGroup('general')
        settings.setValue('loadFiles', self.checkLastSession.checkState())
        settings.setValue('activatePlugins', self.checkActivatePlugins.checkState())
        settings.setValue('notifyUpdates', self.checkNotifyUpdates.checkState())
        settings.setValue('confirmExit', self.checkConfirmExit.checkState())
        settings.setValue('workspace', self.txtWorkspace.text())
        settings.setValue('pythonPath', self.txtPythonPath.text())
        resources.python_path = str(self.txtPythonPath.text())
        resources.workspace = str(self.txtWorkspace.text())
        extensions = str(self.txtExtensions.text()).split(',')
        extensions = [e.strip() for e in extensions]
        settings.setValue('extensions', extensions)
        manage_files.supported_extensions = tuple(extensions)
        settings.endGroup()
        settings.endGroup()


class InterfaceTab(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)
        self._main = parent

        groupBoxExplorer = QGroupBox('Explorer Panel:')
        groupBoxGui = QGroupBox('GUI Customization:')

        #Explorer
        vboxExplorer = QVBoxLayout(groupBoxExplorer)
        self.checkProjectExplorer = QCheckBox('Show Project Explorer.')
        self.checkSymbols = QCheckBox('Show Symbols List.')
        vboxExplorer.addWidget(self.checkProjectExplorer)
        vboxExplorer.addWidget(self.checkSymbols)
        #GUI
        self.btnCentralRotate = QPushButton(QIcon(resources.images['splitCPosition']), '')
        self.btnCentralRotate.setIconSize(QSize(64, 64))
        self.btnCentralRotate.setCheckable(True)
        self.btnPanelsRotate = QPushButton(QIcon(resources.images['splitMPosition']), '')
        self.btnPanelsRotate.setIconSize(QSize(64, 64))
        self.btnPanelsRotate.setCheckable(True)
        self.btnCentralOrientation = QPushButton(QIcon(resources.images['splitCRotate']), '')
        self.btnCentralOrientation.setIconSize(QSize(64, 64))
        self.btnCentralOrientation.setCheckable(True)
        gridGuiConfig = QGridLayout(groupBoxGui)
        gridGuiConfig.addWidget(self.btnCentralRotate, 0, 0)
        gridGuiConfig.addWidget(self.btnPanelsRotate, 0, 1)
        gridGuiConfig.addWidget(self.btnCentralOrientation, 0, 2)
        gridGuiConfig.addWidget(QLabel("Rotate Central"), 1, 0, Qt.AlignCenter)
        gridGuiConfig.addWidget(QLabel("Rotate Lateral"), 1, 1, Qt.AlignCenter)
        gridGuiConfig.addWidget(QLabel("Central Orientation"), 1, 2, Qt.AlignCenter)

        #Settings
        settings = QSettings()
        settings.beginGroup('preferences')
        settings.beginGroup('interface')
        self.checkProjectExplorer.setCheckState(settings.value('showProjectExplorer', Qt.Checked).toInt()[0])
        self.checkSymbols.setCheckState(settings.value('showSymbolsList', Qt.Checked).toInt()[0])
        self.btnCentralRotate.setChecked(settings.value('centralRotate', False).toBool())
        self.btnPanelsRotate.setChecked(settings.value('panelsRotate', False).toBool())
        self.btnCentralOrientation.setChecked(settings.value('centralOrientation', False).toBool())
        settings.endGroup()
        settings.endGroup()

        vbox.addWidget(groupBoxExplorer)
        vbox.addWidget(groupBoxGui)

        #Signals
        self.connect(self.btnCentralRotate, SIGNAL('clicked()'), parent._splitter_central_rotate)
        self.connect(self.btnPanelsRotate, SIGNAL('clicked()'), parent._splitter_main_rotate)
        self.connect(self.btnCentralOrientation, SIGNAL('clicked()'), parent._splitter_central_orientation)

    def save(self):
        settings = QSettings()
        settings.beginGroup('preferences')
        settings.beginGroup('interface')
        settings.setValue('showProjectExplorer', self.checkProjectExplorer.checkState())
        settings.setValue('showSymbolsList', self.checkSymbols.checkState())
        settings.setValue('centralRotate', self.btnCentralRotate.isChecked())
        settings.setValue('panelsRotate', self.btnPanelsRotate.isChecked())
        settings.setValue('centralOrientation', self.btnCentralOrientation.isChecked())
        settings.endGroup()
        settings.endGroup()


class SkinsTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)

        #Top Bar
        hbox = QHBoxLayout()
        self.radioDefault = QRadioButton("Default Skin")
        self.radioCustom = QRadioButton("Custom")
        self.comboSkins = QComboBox()
        self.skins = loader.load_gui_skins()
        for item in self.skins:
            self.comboSkins.addItem(item)
        hbox.addWidget(self.radioDefault)
        hbox.addWidget(self.radioCustom)
        hbox.addWidget(self.comboSkins)
        #Text Area
        self.txtStyle = QPlainTextEdit()
        self.txtStyle.setReadOnly(True)

        #Settings
        settings = QSettings()
        settings.beginGroup('preferences')
        settings.beginGroup('skins')
        if settings.value('default', True).toBool():
            self.radioDefault.setChecked(True)
            self.comboSkins.setEnabled(False)
        else:
            self.radioCustom.setChecked(True)
            index = self.comboSkins.findText(settings.value('selectedSkin', '').toString())
            self.comboSkins.setCurrentIndex(index)
            content = self.skins[str(self.comboSkins.currentText())]
            self.txtStyle.setPlainText(content)
        settings.endGroup()
        settings.endGroup()

        vbox.addLayout(hbox)
        vbox.addWidget(self.txtStyle)
        vbox.addWidget(QLabel('Requires restart the IDE'))

        #Signals
        self.connect(self.radioDefault, SIGNAL("clicked()"), self._default_clicked)
        self.connect(self.radioCustom, SIGNAL("clicked()"), self._custom_clicked)

    def _default_clicked(self):
        self.comboSkins.setEnabled(False)
        self.txtStyle.setPlainText('')

    def _custom_clicked(self):
        self.comboSkins.setEnabled(True)
        content = self.skins[str(self.comboSkins.currentText())]
        self.txtStyle.setPlainText(content)

    def save(self):
        settings = QSettings()
        settings.beginGroup('preferences')
        settings.beginGroup('skins')
        settings.setValue('default', self.radioDefault.isChecked())
        settings.setValue('selectedSkin', self.comboSkins.currentText())
        settings.endGroup()
        settings.endGroup()


class EditorTab(QWidget):

    def __init__(self, main):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.editorGeneral = EditorGeneral(main)
        self.editorConfiguration = EditorConfiguration(main)
        self.tabs.addTab(self.editorGeneral, 'General')
        self.tabs.addTab(self.editorConfiguration, 'Configuration')

        vbox.addWidget(self.tabs)

    def save(self):
        for i in range(self.tabs.count()):
            self.tabs.widget(i).save()


class EditorGeneral(QWidget):

    def __init__(self, main):
        QWidget.__init__(self)
        self._main = main
        vbox = QVBoxLayout(self)

        groupBoxTypo = QGroupBox('Typography:')
        groupBoxScheme = QGroupBox('Scheme Color:')

        #Settings
        settings = QSettings()
        settings.beginGroup('preferences')
        settings.beginGroup('editor')
        #Typo
        gridTypo = QGridLayout(groupBoxTypo)
        self.btnEditorFont = QPushButton(settings.value('font', 'Monospace, 11').toString())
        gridTypo.addWidget(QLabel('Editor Font:'), 0, 0, Qt.AlignRight)
        gridTypo.addWidget(self.btnEditorFont, 0, 1)
        #Scheme
        hbox = QHBoxLayout(groupBoxScheme)
        self.listScheme = QListWidget()
        self.listScheme.addItem('default')
        self.schemes = loader.load_editor_skins()
        for item in self.schemes:
            self.listScheme.addItem(item)
        items = self.listScheme.findItems(settings.value('scheme', '').toString(), Qt.MatchExactly)
        if items:
            self.listScheme.setCurrentItem(items[0])
        else:
            self.listScheme.setCurrentRow(0)
        hbox.addWidget(self.listScheme)
        settings.endGroup()
        settings.endGroup()

        vbox.addWidget(groupBoxTypo)
        vbox.addWidget(groupBoxScheme)
        vbox.addWidget(QLabel('Scheme Color requires restart.'))

        #Signals
        self.connect(self.btnEditorFont, SIGNAL("clicked()"), self._load_editor_font)

    def _load_editor_font(self):
        font = self._load_font(self._get_font_from_string(self.btnEditorFont.text()), self)
        self.btnEditorFont.setText(font)

    def _get_font_from_string(self, font):
        if (font.isEmpty()):
            return QFont("Monospace", 11)

        listFont = font.remove(' ').split(',')
        return QFont(listFont[0], listFont[1].toInt()[0])

    def _load_font(self, initialFont, parent=0):
        font, ok = QFontDialog.getFont(initialFont, parent)
        if ok:
            newFont = font.toString().split(',')
            return newFont[0] + ', ' + newFont[1]
        else:
            return initialFont

    def save(self):
        settings = QSettings()
        settings.beginGroup('preferences')
        settings.beginGroup('editor')
        settings.setValue('font', self.btnEditorFont.text())
        editor = self._main._central.obtain_editor()
        editor.set_font(self._get_font_from_string(self.btnEditorFont.text()))
        settings.setValue('scheme', self.listScheme.currentItem().text())
        settings.endGroup()
        settings.endGroup()


class EditorConfiguration(QWidget):

    def __init__(self, main):
        QWidget.__init__(self)
        self._main = main
        grid = QGridLayout(self)

        #Indentation
        groupBoxFeatures = QGroupBox('Features:')
        grid.addWidget(groupBoxFeatures, 0, 0)
        grid.addWidget(QLabel('Indentation Length:'), 1, 0, Qt.AlignRight)
        self.spin = QSpinBox()
        self.spin.setValue(EditorGeneric.indent)
        grid.addWidget(self.spin, 1, 1)
        #Find Errors
        self.checkErrors = QCheckBox('Find and Show Errors')
        errorState = Qt.Checked if EditorGeneric.findErrors else Qt.Unchecked
        self.checkErrors.setCheckState(errorState)
        grid.addWidget(self.checkErrors, 2, 1)
        #Find Check Style
        self.checkStyle = QCheckBox('Find and Show Check Style errors.')
        styleState = Qt.Checked if EditorGeneric.checkStyle else Qt.Unchecked
        self.checkStyle.setCheckState(styleState)
        grid.addWidget(self.checkStyle, 3, 1)
        #Highlight words
        self.checkWords = QCheckBox('Highlight current word.')
        wordsState = Qt.Checked if EditorGeneric.highlightVariables else Qt.Unchecked
        self.checkWords.setCheckState(wordsState)
        grid.addWidget(self.checkWords, 4, 1)

        groupBoxClose = QGroupBox('Complete:')
        grid.addWidget(groupBoxClose, 5, 0)
        self.checkParentheses = QCheckBox('Parentheses: ()')
        state = Qt.Checked if EditorGeneric.braces_strings.get('(', False) else Qt.Unchecked
        self.checkParentheses.setCheckState(state)
        self.checkKeys = QCheckBox('Keys: {}')
        state = Qt.Checked if EditorGeneric.braces_strings.get('{', False) else Qt.Unchecked
        self.checkKeys.setCheckState(state)
        self.checkBrackets = QCheckBox('Brackets: []')
        state = Qt.Checked if EditorGeneric.braces_strings.get('[', False) else Qt.Unchecked
        self.checkBrackets.setCheckState(state)
        self.checkSimpleQuotes = QCheckBox("Simple Quotes: ''")
        state = Qt.Checked if EditorGeneric.braces_strings.get("'", False) else Qt.Unchecked
        self.checkSimpleQuotes.setCheckState(state)
        self.checkDoubleQuotes = QCheckBox('Double Quotes: ""')
        state = Qt.Checked if EditorGeneric.braces_strings.get('"', False) else Qt.Unchecked
        self.checkDoubleQuotes.setCheckState(state)
        grid.addWidget(self.checkParentheses, 6, 1)
        grid.addWidget(self.checkKeys, 7, 1)
        grid.addWidget(self.checkBrackets, 8, 1)
        grid.addWidget(self.checkSimpleQuotes, 9, 1)
        grid.addWidget(self.checkDoubleQuotes, 10, 1)

        groupBoxCode = QGroupBox('Code Completion:')
        grid.addWidget(groupBoxCode, 11, 0)
        self.checkCodeDot = QCheckBox('Activate Code Completion with: "."')
        state = Qt.Checked if EditorGeneric.codeCompletion else Qt.Unchecked
        self.checkCodeDot.setCheckState(state)
#        self.checkCodeChar = QCheckBox('Activate Code Completion after:')
#        self.spinCode = QSpinBox()
#        self.spinCode.setSuffix(' characters')
        grid.addWidget(self.checkCodeDot, 12, 1)
#        grid.addWidget(self.checkCodeChar, 13, 0)
#        grid.addWidget(self.spinCode, 13, 1)

    def save(self):
        settings = QSettings()
        settings.beginGroup('preferences')
        settings.beginGroup('editor')
        settings.setValue('indent', self.spin.value())
        EditorGeneric.indent = self.spin.value()
        settings.setValue('errors', self.checkErrors.isChecked())
        EditorGeneric.findErrors = self.checkErrors.isChecked()
        settings.setValue('checkStyle', self.checkStyle.isChecked())
        EditorGeneric.checkStyle = self.checkStyle.isChecked()
        settings.setValue('highlightWord', self.checkWords.isChecked())
        EditorGeneric.highlightVariables = self.checkWords.isChecked()
        settings.setValue('parentheses', self.checkParentheses.isChecked())
        if self.checkParentheses.isChecked():
            EditorGeneric.braces_strings['('] = ')'
        elif EditorGeneric.braces_strings.has_key('('):
            del EditorGeneric.braces_strings['(']
        settings.setValue('brackets', self.checkBrackets.isChecked())
        if self.checkBrackets.isChecked():
            EditorGeneric.braces_strings['['] = ']'
        elif EditorGeneric.braces_strings.has_key('['):
            del EditorGeneric.braces_strings['[']
        settings.setValue('keys', self.checkKeys.isChecked())
        if self.checkKeys.isChecked():
            EditorGeneric.braces_strings['{'] = '}'
        elif EditorGeneric.braces_strings.has_key('{'):
            del EditorGeneric.braces_strings['{']
        settings.setValue('simpleQuotes', self.checkSimpleQuotes.isChecked())
        if self.checkSimpleQuotes.isChecked():
            EditorGeneric.braces_strings["'"] = "'"
        elif EditorGeneric.braces_strings.has_key("'"):
            del EditorGeneric.braces_strings["'"]
        settings.setValue('doubleQuotes', self.checkDoubleQuotes.isChecked())
        if self.checkDoubleQuotes.isChecked():
            EditorGeneric.braces_strings['"'] = '"'
        elif EditorGeneric.braces_strings.has_key('"'):
            del EditorGeneric.braces_strings['"']
        settings.setValue('codeCompletion', self.checkCodeDot .isChecked())
        settings.endGroup()
        settings.endGroup()
