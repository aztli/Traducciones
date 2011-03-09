from __future__ import absolute_import

from PyQt4.QtGui import QAction
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QWheelEvent
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPoint

from ninja_ide import resources
from ninja_ide.resources import OS_KEY


class MenuView(object):

    def __init__(self, menu, parent, main):
        self._main = main
        self._parent = parent

        self.hideConsoleAction = menu.addAction('Show/Hide &Console (F4)')
        self.hideConsoleAction.setCheckable(True)
        self.hideEditorAction = menu.addAction('Show/Hide &Editor (F3)')
        self.hideEditorAction.setCheckable(True)
        self.hideAllAction = menu.addAction('Show/Hide &All (F11)')
        self.hideAllAction.setCheckable(True)
        self.hideExplorerAction = menu.addAction('Show/Hide &Explorer (F2)')
        self.hideExplorerAction.setCheckable(True)
        self.hideToolbarAction = menu.addAction('Show/Hide &Toolbar')
        self.hideToolbarAction.setCheckable(True)
        menu.addSeparator()
        splitTabHAction = menu.addAction(QIcon(resources.images['splitH']), 'Split Tabs Horizontally (F10)')
        splitTabVAction = menu.addAction(QIcon(resources.images['splitV']), 'Split Tabs Vertically (F9)')
        followModeAction = menu.addAction(QIcon(resources.images['follow']), 'Follow Mode (Ctrl+F10)')
        menu.addSeparator()
        #Zoom
        zoomInAction = menu.addAction('Zoom &In ('+OS_KEY+'+Wheel-Up)')
        zoomOutAction = menu.addAction('Zoom &Out ('+OS_KEY+'+Wheel-Down)')
        menu.addSeparator()
        fadeInAction = menu.addAction('Fade In (Alt+Wheel-Up)')
        fadeOutAction = menu.addAction('Fade Out (Alt+Wheel-Down)')

        self._parent._toolbar.addSeparator()
        self._parent._toolbar.addAction(splitTabHAction)
        self._parent._toolbar.addAction(splitTabVAction)
        self._parent._toolbar.addAction(followModeAction)

        QObject.connect(self.hideConsoleAction, SIGNAL("triggered()"), self._main._hide_container)
        QObject.connect(self.hideEditorAction, SIGNAL("triggered()"), self._main._hide_editor)
        QObject.connect(self.hideExplorerAction, SIGNAL("triggered()"), self._main._hide_explorer)
        QObject.connect(self.hideAllAction, SIGNAL("triggered()"), self._main._hide_all)
        QObject.connect(splitTabHAction, SIGNAL("triggered()"), lambda: self._main.split_tab(True))
        QObject.connect(splitTabVAction, SIGNAL("triggered()"), lambda: self._main.split_tab(False))
        QObject.connect(followModeAction, SIGNAL("triggered()"), self._main._view_follow_mode)
        QObject.connect(zoomInAction, SIGNAL("triggered()"), lambda: self._main._central.actual_tab().obtain_editor().zoom_in())
        QObject.connect(zoomOutAction, SIGNAL("triggered()"), lambda: self._main._central.actual_tab().obtain_editor().zoom_out())
        QObject.connect(fadeInAction, SIGNAL("triggered()"), self._fade_in)
        QObject.connect(fadeOutAction, SIGNAL("triggered()"), self._fade_out)
        QObject.connect(self.hideToolbarAction, SIGNAL("triggered()"), self._hide_show_toolbar)

    def _hide_show_toolbar(self):
        if self.hideToolbarAction.isChecked():
            self._parent._toolbar.hide()
        else:
            self._parent._toolbar.show()

    def _fade_in(self):
        event = QWheelEvent(QPoint(), 120, Qt.NoButton, Qt.AltModifier)
        self._parent.wheelEvent(event)

    def _fade_out(self):
        event = QWheelEvent(QPoint(), -120, Qt.NoButton, Qt.AltModifier)
        self._parent.wheelEvent(event)
