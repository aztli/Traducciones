from __future__ import absolute_import

from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt

from ninja_ide.gui.qt.properties_panel.tree_symbols_widget \
     import TreeSymbolsWidget

from ninja_ide.gui.qt.properties_panel.tree_projects_widget \
     import TreeProjectsWidget

from ninja_ide.gui.generic.properties_panel import PropertiesGeneric


class PropertiesWidget(QTabWidget, PropertiesGeneric):

    def __init__(self, main):
        QTabWidget.__init__(self)
        PropertiesGeneric.__init__(self)
        self.setTabPosition(QTabWidget.East)
        self._main = main
        self._treeProjects = TreeProjectsWidget(main)
        self._treeSymbols = TreeSymbolsWidget(main)
        #Searching the Preferences
        settings = QSettings()
        if settings.value('preferences/interface/showProjectExplorer', Qt.Checked).toInt()[0] == Qt.Checked:
            self.addTab(self._treeProjects, 'Projects')
        if settings.value('preferences/interface/showSymbolsList', Qt.Checked).toInt()[0] == Qt.Checked:
            self.addTab(self._treeSymbols, 'Symbols')

        #Now we see if there is any tab, if there is not, we hide the widget
        if self.count() == 0:
            self.hide()

    def add_tab(self, widget, name, icon):
        self.addTab(widget, QIcon(icon), name)

    def install_project_menu(self, menu, lang):
        if lang not in self._treeProjects.extraMenus:
            self._treeProjects.extraMenus[lang] = [menu]
        else:
            self._treeProjects.extraMenus[lang] += [menu]
