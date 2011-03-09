from __future__ import absolute_import

import sys
import os

from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QSplashScreen
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QCoreApplication

import ninja_ide.core
from ninja_ide import resources
from ninja_ide.tools import loader
from ninja_ide.tools import manage_files

from ninja_ide.gui.generic import IDEGeneric
from ninja_ide.gui.generic.main_panel import EditorGeneric

from ninja_ide.gui.qt import updates
from ninja_ide.gui.qt.main_window import MainWindow
from ninja_ide.gui.qt.menus import MenuFile
from ninja_ide.gui.qt.menus import MenuEdit
from ninja_ide.gui.qt.menus import MenuSource
from ninja_ide.gui.qt.menus import MenuProject
from ninja_ide.gui.qt.menus import MenuPlugins
from ninja_ide.gui.qt.menus import MenuView
from ninja_ide.gui.qt.menus import MenuAbout
from ninja_ide.gui.qt.status_bar import StatusBar
from ninja_ide.gui.qt.qtcss import styles


class IDE(QMainWindow, IDEGeneric):

    max_opacity = 1
    min_opacity = 0.3

    def __init__(self):
        QWidget.__init__(self)
        IDEGeneric.__init__(self)
        self.setWindowTitle('NINJA-IDE {Ninja Is Not Just Another IDE}')
        self.setWindowIcon(QIcon(resources.images['icon']))
        self.setWindowState(Qt.WindowMaximized)
        self.setMinimumSize(700, 500)

        #Opactity
        self.opacity = 1

        #ToolBar
        self._toolbar = QToolBar()
        self._toolbar.setToolTip('Press and Drag to Move')
        styles.set_style(self._toolbar, 'toolbar-default')
        self.addToolBar(Qt.LeftToolBarArea, self._toolbar)
        self._toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)

        #StatusBar
        self._status = StatusBar()
        self._status.hide()
        self.setStatusBar(self._status)

        #Main Widgets
        self.main = MainWindow(self)
        self.setCentralWidget(self.main)

        #Menu
        menubar = self.menuBar()
        file_ = menubar.addMenu('&File')
        edit = menubar.addMenu('&Edit')
        view = menubar.addMenu('&View')
        source = menubar.addMenu('&Source')
        project = menubar.addMenu('&Project')
        self.pluginsMenu = menubar.addMenu('P&lugins')
        about = menubar.addMenu('&About')

        #The order of the icons in the toolbar is defined by this calls
        self._menuFile = MenuFile(file_, self._toolbar, self.main)
        self._menuView = MenuView(view, self, self.main)
        self._menuEdit = MenuEdit(edit, self._toolbar, self.main, self._status)
        self._menuSource = MenuSource(source, self.main)
        self._menuProject = MenuProject(project, self._toolbar, self.main)
        self._menuPlugins = MenuPlugins(self.pluginsMenu, self)
        self._menuAbout = MenuAbout(about, self.main)

        self.main.container.load_toolbar(self._toolbar)
        self.main._central.actual_tab().obtain_editor().setFocus()

        #Tray Icon
        self.trayIcon = updates.TrayIconUpdates(self)
        self.trayIcon.show()

        self.connect(self.main, SIGNAL("fileSaved(QString)"), self.show_status_message)

    def show_status_message(self, message):
        self._status.showMessage(message, 2000)

    def add_toolbar_item(self, plugin, name, icon):
        self._toolbar.addSeparator()
        action = self._toolbar.addAction(QIcon(icon), name)
        self.connect(action, SIGNAL("triggered()"), lambda: plugin.toolbarAction())

    def closeEvent(self, event):
        settings = QSettings()
        if settings.value('preferences/general/loadFiles', Qt.Checked).toInt()[0] == Qt.Checked:
            settings.setValue('openFiles/projects', self.main.get_open_projects())
            settings.setValue('openFiles/tab1', self.main._central._tabs.get_open_files())
            settings.setValue('openFiles/tab2', self.main._central._tabs2.get_open_files())
        else:
            settings.setValue('openFiles/projects', [])

        confirm = settings.value('preferences/general/confirmExit', Qt.Checked).toInt()[0]
        if (confirm == Qt.Checked) and self.main._central.check_for_unsaved():
            val = QMessageBox.question(self, 'Some changes were not saved',
                        'Do you want to exit anyway?', QMessageBox.Yes, QMessageBox.No)
            if val == QMessageBox.No:
                event.ignore()
            else:
                self.main._properties._treeProjects.close_open_projects()
        else:
            self.main._properties._treeProjects.close_open_projects()

    def wheelEvent(self, event):
        if event.modifiers() == Qt.AltModifier:
            if event.delta() == 120 and self.opacity < self.max_opacity:
                self.opacity += 0.1
            elif event.delta() == -120 and self.opacity > self.min_opacity:
                self.opacity -= 0.1
            self.setWindowOpacity(self.opacity)
            event.ignore()
        else:
            super(IDE, self).wheelEvent(event)


def set_plugin_access(ide):
    ninja_ide.core.register_plugin_access(ide.main._central.obtain_editor,
        ide.main._central.obtain_editor().get_text,
        ide.main._central.obtain_editor().get_path,
        ide.main.new_editor,
        ide.main.add_tab,
        ide.main.save,
        ide.main.open_document,
        ide.main.open_image,
        ide.main._properties._treeProjects.get_selected_project_path,
        ide.main._properties._treeProjects)


def start():
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName('NINJA-IDE')
    QCoreApplication.setOrganizationDomain('ninja-ide.org.ar')
    QCoreApplication.setApplicationName('Kunai')

    # Create and display the splash screen
    splash_pix = QPixmap(resources.images['splash'])
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    loader.load_syntax()

    #Loading GUI
    splash.showMessage("Loading GUI", Qt.AlignRight | Qt.AlignBottom, Qt.white)
    settings = QSettings()
    if not settings.value('preferences/skins/default', True).toBool():
        selectedSkin = settings.value('preferences/skins/selectedSkin', '').toString()
        skins = loader.load_gui_skins()
        css = skins.get(str(selectedSkin), '')
        app.setStyleSheet(css)
    schemeColor = str(settings.value('preferences/editor/scheme', 'default').toString())
    if schemeColor != 'default':
        resources.custom_scheme = loader.load_editor_skins().get(schemeColor, {})
    #Editor Configuration
    EditorGeneric.codeCompletion = settings.value('preferences/editor/codeCompletion', True).toBool()
    EditorGeneric.indent = settings.value('preferences/editor/indent', 4).toInt()[0]
    EditorGeneric.findErrors = settings.value('preferences/editor/errors', False).toBool()
    EditorGeneric.checkStyle = settings.value('preferences/editor/checkStyle', True).toBool()
    EditorGeneric.highlightVariables = settings.value('preferences/editor/highlightWord', True).toBool()
    if not settings.value('preferences/editor/parentheses', True).toBool():
        del EditorGeneric.braces_strings['(']
    if not settings.value('preferences/editor/brackets', True).toBool():
        del EditorGeneric.braces_strings['[']
    if not settings.value('preferences/editor/keys', True).toBool():
        del EditorGeneric.braces_strings['{']
    if not settings.value('preferences/editor/simpleQuotes', True).toBool():
        del EditorGeneric.braces_strings["'"]
    if not settings.value('preferences/editor/doubleQuotes', True).toBool():
        del EditorGeneric.braces_strings['"']

    ide = IDE()
    if settings.value('preferences/interface/centralRotate', False).toBool():
        ide.main._splitter_central_rotate()
    if settings.value('preferences/interface/panelsRotate', False).toBool():
        ide.main._splitter_main_rotate()
    if settings.value('preferences/interface/centralOrientation', False).toBool():
        ide.main._splitter_central_orientation()

    #Settings
    splash.showMessage("Loading Settings", Qt.AlignRight | Qt.AlignBottom, Qt.white)
    resources.python_path = str(settings.value('preferences/general/pythonPath', 'python').toString())
    if (settings.value('preferences/general/activatePlugins', Qt.Checked) == Qt.Checked):
        set_plugin_access(ide)
        ninja_ide.core.load_plugins(ide)
    resources.workspace = str(settings.value('preferences/general/workspace', '').toString())
    supportedExtensions = settings.value('preferences/general/extensions', []).toList()
    if supportedExtensions:
        tempExtensions = []
        for se in supportedExtensions:
            tempExtensions.append(str(se.toString()))
        manage_files.supported_extensions = tuple(tempExtensions)

    #Load Font preference
    font = str(settings.value('preferences/editor/font', "Monospace, 11").toString())
    EditorGeneric.font_family = font.split(', ')[0]
    EditorGeneric.font_size = int(font.split(', ')[1])

    ide.show()
    splash.showMessage("Loading Projects", Qt.AlignRight | Qt.AlignBottom, Qt.white)
    for projectFolder in settings.value('openFiles/projects', []).toStringList():
        if os.path.isdir(projectFolder):
            ide.main.open_project_folder(str(projectFolder), False)

    if (settings.value('preferences/general/loadFiles', Qt.Checked) == Qt.Checked):
        for openFile in settings.value('openFiles/tab1', []).toList():
            if len(openFile.toList()) > 0:
                fileList = openFile.toList()
                fileName = str(fileList[0].toString())
                projectPath = str(fileList[1].toString())
                if len(projectPath) == 0:
                    projectPath = None
                cursorPosition = fileList[2].toInt()[0]
                if os.path.isfile(fileName):
                    ide.main.open_document(fileName, projectPath)
                    ide.main._central.obtain_editor().set_cursor_position(cursorPosition)

        for openFile2 in settings.value('openFiles/tab2', []).toList():
            #ide.main.split_tab(True)
            if len(openFile2.toList()) > 0:
                ide.main._central._tabs2.show()
                ide.main._central._mainTabSelected = False
                fileList = openFile2.toList()
                fileName = fileList[0].toString()
                projectPath = fileList[1].toString()
                cursorPosition = fileList[2].toInt()[0]
                if os.path.isfile(fileName):
                    ide.main.open_document(str(fileName), str(projectPath))
                    ide.main._central.obtain_editor().set_cursor_position(cursorPosition)
                ide.main._central._mainTabSelected = True

    filenames, projects_path = ninja_ide.core.cliparser.parse()

    for filename in filenames:
        ide.main.open_document(filename)

    for project_path in projects_path:
        ide.main.open_project_folder(project_path)

    splash.finish(ide)
    sys.exit(app.exec_())
