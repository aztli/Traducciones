from __future__ import absolute_import

import math

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QTableWidget
from PyQt4.QtGui import QTableWidgetItem
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QMessageBox
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
from ninja_ide.tools import manage_files


def set_data(plugins, table):
    table.setHorizontalHeaderLabels(['Name', 'Version', 'Description'])
    table.horizontalHeader().setStretchLastSection(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    for i in xrange(table.rowCount()):
        table.removeRow(0)
    r = 0
    for plug in plugins:
        table.insertRow(r)
        #Column 2
        item = QTableWidgetItem(plug[1])
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        table.setItem(r, 2, item)
        #Column 1
        item = QTableWidgetItem(plug[2])
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        table.setItem(r, 1, item)
        #Column 0
        item = QTableWidgetItem(plug[0])
        table.setItem(r, 0, item)
        item.setCheckState(Qt.Unchecked)
        r += 1


class PluginsManagerWidget(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Dialog)
        self._parent = parent
        self.setWindowTitle('Plugins Manager')
        self.resize(700, 500)

        vbox = QVBoxLayout(self)
        self._tabs = QTabWidget()
        vbox.addWidget(self._tabs)
        self.overlay = Overlay(self)
        self.overlay.show()

        self._available = []
        self._locals = []
        self._updates = []
        self.loading = True

        self.thread = ThreadLoadPlugins(self)
        self.connect(self.thread, SIGNAL("finished()"), self.load_plugins_data)
        self.connect(self.thread, SIGNAL("plugin_downloaded(PyQt_PyObject)"), self._after_download_plugin)
        self.thread.start()

    def _after_download_plugin(self, plugin):
        self.installedWidget.add_table_items([plugin])
        val = ninja_ide.core.load_installed_plugin(self._parent, plugin)
        if val:
            QMessageBox.information(self, 'GUI Plugins Installed', 'NINJA needs to be restarted' \
                ' for changes to take effect.\nPlugin: ' + plugin[0])

    def load_plugins_data(self):
        if self.loading:
            self.updatesWidget = UpdatesWidget(self, self._updates)
            self.availableWidget = AvailableWidget(self, self._available)
            self.installedWidget = InstalledWidget(self, self._locals)
            self._tabs.addTab(self.updatesWidget, 'Updates')
            self._tabs.addTab(self.availableWidget, 'Available Plugins')
            self._tabs.addTab(self.installedWidget, 'Installed')
            self.loading = False
        self.overlay.hide()

    def download_plugins(self, plugs):
        self.overlay.show()
        self.thread.plug = plugs
        self.thread.runnable = self.thread.download_plugins_thread
        self.thread.start()

    def mark_as_available(self, plug):
        ninja_ide.core.uninstall_plugin(plug)
        self.availableWidget.add_table_items([plug])

    def update_plugin(self, plugs):
        self.overlay.show()
        self.thread.plug = plugs
        self.thread.runnable = self.thread.update_plugin_thread
        self.thread.start()

    def reset_installed_plugins(self):
        local_plugins = ninja_ide.core.local_plugins()
        local_plugins = [[k, local_plugins[k][0], local_plugins[k][1], local_plugins[k][2]] for k in local_plugins]
        self.installedWidget.reset_table(local_plugins)

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()


class UpdatesWidget(QWidget):

    def __init__(self, parent, updates):
        QWidget.__init__(self)
        self._parent = parent
        self._updates = updates
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 3)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        set_data(updates, self._table)
        btnUpdate = QPushButton('Update')
        btnUpdate.setMaximumWidth(100)
        vbox.addWidget(btnUpdate)

        self.connect(btnUpdate, SIGNAL("clicked()"), self._update_plugins)

    def _update_plugins(self):
        rows = self._table.rowCount()
        pos = rows - 1
        plugins = []
        for i in xrange(rows):
            if self._table.item(pos-i, 0) is not None and \
                self._table.item(pos-i, 0).checkState() == Qt.Checked:
                plugins.append(self._updates.pop(pos-i))
                self._table.removeRow(pos-i)
        self._parent.update_plugin(plugins)


class AvailableWidget(QWidget):

    def __init__(self, parent, available):
        QWidget.__init__(self)
        self._parent = parent
        self._available = available
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 3)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        set_data(available, self._table)
        btnInstall = QPushButton('Install')
        btnInstall.setMaximumWidth(100)
        vbox.addWidget(btnInstall)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Add an external Plugin. URL Zip File:'))
        self.link = QLineEdit()
        hbox.addWidget(self.link)
        btnAdd = QPushButton('Add')
        hbox.addWidget(btnAdd)
        vbox.addLayout(hbox)
        lblExternalPlugin = QLabel('(Write the URL of the Plugin and press "Add")')
        lblExternalPlugin.setAlignment(Qt.AlignRight)
        vbox.addWidget(lblExternalPlugin)

        self.connect(btnInstall, SIGNAL("clicked()"), self._install_plugins)
        self.connect(btnAdd, SIGNAL("clicked()"), self._install_external)

    def _install_plugins(self):
        rows = self._table.rowCount()
        pos = rows - 1
        plugins = []
        for i in xrange(rows):
            if self._table.item(pos-i, 0) is not None and \
              self._table.item(pos-i, 0).checkState() == Qt.Checked:
                plugins.append(self._available.pop(pos-i))
                self._table.removeRow(pos-i)
        self._parent.download_plugins(plugins)

    def _install_external(self):
        if self.link.text().isEmpty():
            QMessageBox.information(self, 'External Plugins', 'URL from Plugin missing...')
            return
        plug = [
            manage_files.get_module_name(str(self.link.text())),
            'External Plugin',
            '1.0',
            str(self.link.text())
            ]
        self._parent.download_plugins(plug)
        self.link.setText('')

    def add_table_items(self, plugs):
        self._available += plugs
        set_data(self._available, self._table)


class InstalledWidget(QWidget):

    def __init__(self, parent, installed):
        QWidget.__init__(self)
        self._parent = parent
        self._installed = installed
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 3)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        set_data(self._installed, self._table)
        btnUninstall = QPushButton('Uninstall')
        btnUninstall.setMaximumWidth(100)
        vbox.addWidget(btnUninstall)

        self.connect(btnUninstall, SIGNAL("clicked()"), self._uninstall_plugins)

    def add_table_items(self, plugs):
        self._installed += plugs
        set_data(self._installed, self._table)

    def _uninstall_plugins(self):
        rows = self._table.rowCount()
        pos = rows - 1
        for i in xrange(rows):
            if self._table.item(pos-i, 0) is not None and \
                self._table.item(pos-i, 0).checkState() == Qt.Checked:
                self._parent.mark_as_available(self._installed.pop(pos-i))
                self._table.removeRow(pos-i)

    def reset_table(self, installed):
        self._installed = installed
        while self._table.rowCount() > 0:
            self._table.removeRow(0)
        set_data(self._installed, self._table)


class ThreadLoadPlugins(QThread):

    def __init__(self, manager):
        QThread.__init__(self)
        self._manager = manager
        self.runnable = self.execute_thread
        self.plug = None

    def run(self):
        self.runnable()
        self.plug = None

    def execute_thread(self):
        available = ninja_ide.core.available_plugins()
        local_plugins = ninja_ide.core.local_plugins()
        updates = []
        for lp in local_plugins:
            if lp in available:
                ava = available.pop(lp)
                if float(ava[1]) > float(local_plugins[lp][1]):
                    updates += [[lp, ava[0], ava[1], ava[2]]]
        available = [[k, available[k][0], available[k][1], available[k][2]] for k in available]
        local_plugins = [[k, local_plugins[k][0], local_plugins[k][1], local_plugins[k][2]] for k in local_plugins]
        self._manager._available = available
        self._manager._locals = local_plugins
        self._manager._updates = updates

    def download_plugins_thread(self):
        for p in self.plug:
            ninja_ide.core.download_plugin(p[3])
            ninja_ide.core.update_local_plugin_descriptor([p])
            self.emit(SIGNAL("plugin_downloaded(PyQt_PyObject)"), p)

    def update_plugin_thread(self):
        for p in self.plug:
            ninja_ide.core.uninstall_plugin(p)
            ninja_ide.core.download_plugin(p[3])
            ninja_ide.core.update_local_plugin_descriptor([p])
            self._manager.reset_installed_plugins()


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
