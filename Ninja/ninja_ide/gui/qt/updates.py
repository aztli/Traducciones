import urllib
import webbrowser
try:
    import json
except ImportError:
    import simplejson as json

from PyQt4.QtGui import QSystemTrayIcon
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL

import ninja_ide
import ninja_ide.core
from ninja_ide import resources


class TrayIconUpdates(QSystemTrayIcon):

    def __init__(self, parent):
        QSystemTrayIcon.__init__(self, parent)
        icon = QIcon(resources.images['iconUpdate'])
        self.setIcon(icon)

        self.thread = ThreadUpdates()

        self.connect(self, SIGNAL("messageClicked()"), self._show_download)
        self.connect(self.thread, SIGNAL("finished()"), self._show_messages)
        self.thread.start()

    def _show_messages(self):
        if float(ninja_ide.VERSION) < float(self.thread.ide['version']):
            if self.supportsMessages():
                self.showMessage('NINJA-IDE Updates',
                    'New Version of NINJA-IDE\nAvailable: ' + \
                    self.thread.ide['version'] + '\n\nClick here to Download',
                    QSystemTrayIcon.Information, 10000)
            else:
                button = QMessageBox.information(self.parent(), 'NINJA-IDE Updates',
                        'New Version of NINJA-IDE\nAvailable: ' + self.thread.ide['version'])
                if button == QMessageBox.Ok:
                    self._show_download()
        else:
            self.hide()

    def _show_download(self):
        webbrowser.open(self.thread.ide['downloads'])
        self.hide()


class ThreadUpdates(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.ide = {}
        self.plugins = []

    def run(self):
        try:
            ninja_version = urllib.urlopen('http://plugins.ninja-ide.googlecode.com/hg/version.json')
            self.ide = json.load(ninja_version)

            available = ninja_ide.core.available_plugins()
            local_plugins = ninja_ide.core.local_plugins()
            updates = []
            for lp in local_plugins:
                if lp in available:
                    ava = available.pop(lp)
                    if float(ava[1]) > float(local_plugins[lp][1]):
                        updates += [[lp, ava[0], ava[1], ava[2]]]
            self.plugins = updates
        except:
            print 'no connection available'
