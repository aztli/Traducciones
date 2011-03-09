from __future__ import absolute_import

import os
import math
import urllib
try:
    import json
except ImportError:
    import simplejson as json

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QTableWidget
from PyQt4.QtGui import QTableWidgetItem
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QPalette
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QPen
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL

import ninja_ide.core
from ninja_ide import resources
from ninja_ide.tools import manage_files


def set_data(skins, table):
    table.setHorizontalHeaderLabels(['Name', 'URL'])
    table.horizontalHeader().setStretchLastSection(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    for i in xrange(table.rowCount()):
        table.removeRow(0)
    r = 0
    for skin in skins:
        table.insertRow(r)
        #Column 1
        item = QTableWidgetItem(skin[1])
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        table.setItem(r, 1, item)
        #Column 0
        item = QTableWidgetItem(skin[0])
        table.setItem(r, 0, item)
        item.setCheckState(Qt.Unchecked)
        r += 1


class SkinsManagerWidget(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Dialog)
        self._parent = parent
        self.setWindowTitle('Skins and Schemes Manager')
        self.resize(700, 500)

        vbox = QVBoxLayout(self)
        self._tabs = QTabWidget()
        vbox.addWidget(self._tabs)
        self.overlay = Overlay(self)
        self.overlay.show()

        self._skins = []
        self._schemes = []
        self.loading = True

        self.thread = ThreadLoadSkins(self)
        self.connect(self.thread, SIGNAL("finished()"), self.load_skins_data)
        self.thread.start()

    def load_skins_data(self):
        if self.loading:
            self.skinsWidget = SkinsWidget(self, self._skins)
            self.schemeWidget = SchemeWidget(self, self._schemes)
            self._tabs.addTab(self.skinsWidget, 'Skins')
            self._tabs.addTab(self.schemeWidget, 'Schemes')
            self.loading = False
        self.overlay.hide()

    def download_skin(self, skin):
        self.overlay.show()
        self.thread.skin = skin
        self.thread.runnable = self.thread.download_skins_thread
        self.thread.start()

    def download_scheme(self, scheme):
        self.overlay.show()
        self.thread.skin = scheme
        self.thread.runnable = self.thread.download_scheme_thread
        self.thread.start()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()


class SkinsWidget(QWidget):

    def __init__(self, parent, skins):
        QWidget.__init__(self)
        self._parent = parent
        self._skins = skins
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 2)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        set_data(skins, self._table)
        btnUpdate = QPushButton('Download')
        btnUpdate.setMaximumWidth(100)
        vbox.addWidget(btnUpdate)

        self.connect(btnUpdate, SIGNAL("clicked()"), self._download_skin)

    def _download_skin(self):
        rows = self._table.rowCount()
        pos = rows - 1
        skins = []
        for i in xrange(rows):
            if self._table.item(pos - i, 0) is not None and \
              self._table.item(pos - i, 0).checkState() == Qt.Checked:
                skins.append(self._skins.pop(pos - i))
                self._table.removeRow(pos - i)
        self._parent.download_skin(skins)


class SchemeWidget(QWidget):

    def __init__(self, parent, schemes):
        QWidget.__init__(self)
        self._parent = parent
        self._schemes = schemes
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 2)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        set_data(self._schemes, self._table)
        btnUninstall = QPushButton('Download')
        btnUninstall.setMaximumWidth(100)
        vbox.addWidget(btnUninstall)

        self.connect(btnUninstall, SIGNAL("clicked()"), self._download_scheme)

    def _download_scheme(self):
        rows = self._table.rowCount()
        pos = rows - 1
        schemes = []
        for i in xrange(rows):
            if self._table.item(pos - i, 0) is not None and \
              self._table.item(pos - i, 0).checkState() == Qt.Checked:
                schemes.append(self._schemes.pop(pos - i))
                self._table.removeRow(pos - i)
        self._parent.download_scheme(schemes)


class ThreadLoadSkins(QThread):

    def __init__(self, manager):
        QThread.__init__(self)
        self._manager = manager
        self.runnable = self.execute_thread
        self.skin = None

    def run(self):
        self.runnable()
        self.skin = None

    def execute_thread(self):
        descriptor_skins = urllib.urlopen('http://plugins.ninja-ide.googlecode.com/hg/skins.json')
        skins = json.load(descriptor_skins)
        skins = [[name, skins[name]] for name in skins]
        local_skins = self.get_local_skins()
        skins = [skins[i] for i in range(len(skins)) if os.path.basename(skins[i][1]) not in local_skins]
        self._manager._skins = skins
        descriptor_schemes = urllib.urlopen('http://plugins.ninja-ide.googlecode.com/hg/schemes.json')
        schemes = json.load(descriptor_schemes)
        schemes = [[name, schemes[name]] for name in schemes]
        local_schemes = self.get_local_schemes()
        schemes = [schemes[i] for i in range(len(schemes)) if os.path.basename(schemes[i][1]) not in local_schemes]
        self._manager._schemes = schemes

    def get_local_skins(self):
        if not os.path.isdir(resources.gui_skins):
            os.makedirs(resources.gui_skins)
        skins = os.listdir(resources.gui_skins)
        skins = [s for s in skins if s.endswith('.skin')]
        return skins

    def get_local_schemes(self):
        if not os.path.isdir(resources.editor_skins):
            os.makedirs(resources.editor_skins)
        schemes = os.listdir(resources.editor_skins)
        schemes = [s for s in schemes if s.endswith('.color')]
        return schemes

    def download_skins_thread(self):
        for s in self.skin:
            self.download(s[1], resources.gui_skins)

    def download_scheme_thread(self):
        for s in self.skin:
            self.download(s[1], resources.editor_skins)

    def download(self, url, folder):
        fileName = resources.createpath(folder, os.path.basename(url))
        content = urllib.urlopen(url)
        f = open(fileName, 'w')
        f.write(content.read())
        f.close()


class Overlay(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(Qt.NoPen))

        for i in xrange(6):
            if (self.counter / 5) % 6 == i:
                painter.setBrush(QBrush(QColor(127 + (self.counter % 5)*32, 127, 127)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))
            painter.drawEllipse(
                self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                20, 20)

        painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(50)
        self.counter = 0

    def timerEvent(self, event):
        self.counter += 1
        self.update()
