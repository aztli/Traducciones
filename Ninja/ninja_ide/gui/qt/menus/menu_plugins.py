from __future__ import absolute_import

from PyQt4.QtGui import QAction
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.qt.menus.plugins_manager_widget import PluginsManagerWidget
from ninja_ide.gui.qt.menus.skins_manager import SkinsManagerWidget


class MenuPlugins(object):

    def __init__(self, menu, ide):
        self._ide = ide

        manageAction = menu.addAction('Manage Plugins')
        skinsAction = menu.addAction('Skins and Schemes')

        QObject.connect(manageAction, SIGNAL("triggered()"), self._show_manager)
        QObject.connect(skinsAction, SIGNAL("triggered()"), self._show_skins)

    def _show_manager(self):
        manager = PluginsManagerWidget(self._ide)
        manager.show()

    def _show_skins(self):
        manager = SkinsManagerWidget(self._ide)
        manager.show()
