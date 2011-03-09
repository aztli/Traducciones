from __future__ import absolute_import

import subprocess

from PyQt4.QtGui import QAction
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject

from ninja_ide import resources
from ninja_ide.resources import OS_KEY

from ninja_ide.tools import runner


class MenuProject(object):

    def __init__(self, menu, tool, main):
        self._main = main

        runAction = menu.addAction(QIcon(resources.images['play']), 'Run Project (F6)')
        runFileAction = menu.addAction(QIcon(resources.images['file-run']), 'Run File ('+OS_KEY+'+F6)')
        stopAction = menu.addAction(QIcon(resources.images['stop']), 'Stop')

        tool.addSeparator()
        tool.addAction(runAction)
        tool.addAction(runFileAction)
        tool.addAction(stopAction)

        QObject.connect(runAction, SIGNAL("triggered()"), lambda: self._main._run_program())
        QObject.connect(runFileAction, SIGNAL("triggered()"), lambda: self._main._run_code())
        QObject.connect(stopAction, SIGNAL("triggered()"), lambda: self._main._stop_program())
