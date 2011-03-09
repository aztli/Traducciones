from __future__ import absolute_import

from PyQt4.QtGui import QAction
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.qt.menus.about_ninja import AboutNinja

class MenuAbout(object):

    def __init__(self, menu, main):
        self._main = main

        startPageAction = menu.addAction('Mostrar pagina de Inicio')
        helpAction = menu.addAction('Ayuda de Python[F1]')
        reportBugAction = menu.addAction('Reportar BUGS')
        pluginsDocAction = menu.addAction('Documentacion de Plugins')
        menu.addSeparator()
        aboutNinjaAction = menu.addAction('Acerca de NINJA-IDE')
        aboutQtAction = menu.addAction('Acerca de NINJA-IDE')

        QObject.connect(startPageAction, SIGNAL("triggered()"), self._main.show_start_page)
        QObject.connect(reportBugAction, SIGNAL("triggered()"), self._main.show_report_bugs)
        QObject.connect(aboutQtAction, SIGNAL("triggered()"), self._show_about_qt)
        QObject.connect(helpAction, SIGNAL("triggered()"), self._main._show_python_doc)
        QObject.connect(aboutNinjaAction, SIGNAL("triggered()"), self._show_about_ninja)
        QObject.connect(pluginsDocAction, SIGNAL("triggered()"), self._main.show_plugins_doc)

    def _show_about_qt(self):
        QMessageBox.aboutQt(self._main, 'Acerca de QT')

    def _show_about_ninja(self):
        self.about = AboutNinja(self._main)
        self.about.show()
