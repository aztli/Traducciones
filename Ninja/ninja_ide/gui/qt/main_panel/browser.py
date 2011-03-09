from __future__ import absolute_import

import sys
import os
import time

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtWebKit import QWebView
from PyQt4.QtWebKit import QWebPage
from PyQt4.QtWebKit import QWebSettings
from PyQt4.QtWebKit import QWebPluginFactory
from PyQt4.QtCore import QThread

from ninja_ide import resources
from ninja_ide.tools import manage_files
from ninja_ide.gui.generic import BaseCentralWidget


class Browser(QWidget, BaseCentralWidget):

    def __init__(self, URL, process=None, main=None):
        QWidget.__init__(self)
        BaseCentralWidget.__init__(self)
        self.path = URL
        self.process = process

        v_box = QVBoxLayout(self)
        #Web Frame
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
        self.webFrame = QWebView()
        self.webFrame.setAcceptDrops(False)
        factory = WebPluginFactory(self, main)
        self.webFrame.page().setPluginFactory(factory)
        self.webFrame.load(QUrl(URL))

        v_box.addWidget(self.webFrame)

        if process is not None:
            time.sleep(0.5)
            self.webFrame.reload()

        if self.path.endswith('startPage.html') and sys.platform.find('win') != -1:
            content = manage_files.read_file_content(self.path)
            pathCss = os.path.join(resources.PRJ_PATH, 'doc', 'styles', 'ninja.css')
            pathJs = os.path.join(resources.PRJ_PATH, 'doc', 'rsc')
            content = content.replace('styles/ninja.css', pathCss).replace('src="rsc', 'src="' + pathJs)
            self.webFrame.setHtml(content)

    def shutdown_pydoc(self):
        if self.process is not None:
            self.process.kill()

    def find_match(self, word, back=False, sensitive=False, whole=False):
        b = QWebPage.FindBackward if back else None
        s = QWebPage.FindCaseSensitively if sensitive else None
        self.webFrame.page().findText(word)


class WebPluginList(QListWidget):

    def __init__(self, main):
        QListWidget.__init__(self)
        self.setStyleSheet("""
        WebPluginList {
          color: black;
          background-color: white;
          selection-color: blue;
          border-radius: 10px;
          selection-background-color: #437DCD;
        }
        WebPluginList:Item {
            border-radius: 10px;
            border-style: solid;
            background-color: white;
        }
        WebPluginList:Item:hover {
            border-radius: 10px;
            border-style: solid;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #FAFBFE, stop: 1 #6181E0);
        }""")
        self.connect(self, SIGNAL("itemSelectionChanged()"), self.openSelected)
        self._main = main
        settings = QSettings()
        i = 1
        for recent_project in settings.value('recentProjects', []).toStringList():
            if manage_files.folder_exists(str(recent_project)):
                item = QListWidgetItem(str(recent_project.split('/')[-1]))
                item.setToolTip(recent_project)
                item.setIcon(QIcon(resources.images['tree-app']))
                self.addItem(item)
            i = i + 1
            if i == 10:
                break

    def openSelected(self):
        settings = QSettings()
        recent_project = settings.value('recentProjects', []).toStringList()[self.currentRow()]
        self._main.open_project_folder(str(recent_project), False)


class WebPluginFactory(QWebPluginFactory):

    def __init__(self, parent=None, main=None):
        QWebPluginFactory.__init__(self, parent)
        self._main = main

    def create(self, mimeType, url, names, values):
        if mimeType == "x-pyqt/widget":
            return WebPluginList(self._main)

    def plugins(self):
        plugin = QWebPluginFactory.Plugin()
        plugin.name = "PyQt Widget"
        plugin.description = "An example Web plugin written with PyQt."
        mimeType = QWebPluginFactory.MimeType()
        mimeType.name = "x-pyqt/widget"
        mimeType.description = "PyQt widget"
        mimeType.fileExtensions = []
        plugin.mimeTypes = [mimeType]
        return [plugin]
