from __future__ import absolute_import

from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QCursor
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QStringList

from ninja_ide import resources
from ninja_ide.tools import introspection


class TreeSymbolsWidget(QTreeWidget):

    def __init__(self, main):
        QTreeWidget.__init__(self)
        self.header().setHidden(True)
        self.setSelectionMode(self.SingleSelection)
        self.setAnimated(True)
        self._main = main
        self.globals = None
        self.classes = None
        self.functions = None

        self.header().setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        #Thread to Refresh
        self._thread = ThreadRefresh(self)

        self.connect(self, SIGNAL("itemClicked(QTreeWidgetItem *, int)"), self._main.go_to_line)
        self.connect(self, SIGNAL("customContextMenuRequested(const QPoint &)"), self.menuContextTree)
        self.connect(self._thread, SIGNAL("finished()"), self._load_tree)

    def refresh(self, path_to_file, fileName):
        self._thread.fileName = fileName
        self._thread.path_to_file = path_to_file
        self._thread.start()

    def _load_tree(self):
        self.clear()
        try:
            if self.globals:
                globals_item = ItemTree(self, QStringList('self.globals'))
                globals_item.isClickable = False
                for glob in self.globals:
                    glob_item = ItemTree(globals_item, QStringList(glob['name']), lineno=glob['lineno'])
                    glob_item.setIcon(0, QIcon(resources.images['attribute']))
            if self.classes:
                #classes
                for klass in self.classes:
                    name = "%s(%s)" % (klass['name'], ', '.join([k for k in klass['superclasses']]))
                    class_item = ItemTree(self, QStringList(name), lineno=klass['lineno'])
                    class_item.setIcon(0, QIcon(resources.images['class']))
                    #attributes
                    if klass['attributes']:
                        attributes_item = ItemTree(class_item, QStringList('Attributes'))
                        attributes_item.isClickable = False
                        for attribute in klass['attributes']:
                            item = ItemTree(attributes_item, QStringList(attribute['name']), lineno=attribute['lineno'])
                            item.isAttribute = True
                            item.setIcon(0, QIcon(resources.images['attribute']))
                    #metodos
                    if klass['methods']:
                        methods_item = ItemTree(class_item, QStringList('Methods'))
                        methods_item.isClickable = False
                        for method in klass['methods']:
                            item = ItemTree(methods_item, QStringList(method['name']), lineno=method['lineno'])
                            item.setIcon(0, QIcon(resources.images['function']))
            #functions
            if self.functions:
                functions_item = QTreeWidgetItem(self, QStringList('self.functions'))
                functions_item.isClickable = False
                for func in self.functions:
                    item = ItemTree(functions_item, QStringList(func['name']), lineno=func['lineno'])
                    item.setIcon(0, QIcon(resources.images['function']))
            self.expandAll()
        except Exception:
            print 'Error parsing this file for Tree Symbols: method refresh'

    def menuContextTree(self, point):
        index = self.indexAt(point)
        if not index.isValid():
            return

        item = self.itemAt(point)
        name = str(item.text(0))
        if item.isClickable:
            self.emit(SIGNAL("itemClicked(QTreeWidgetItem *, int)"), item, item.lineno)

        menu = QMenu(self)
        if item.isAttribute:
            createPropertyAction = menu.addAction('Create Property')
            self.connect(createPropertyAction, SIGNAL("triggered()"),
                lambda: self._main._central.obtain_editor().create_property(item.lineno, name))
        if item.isClickable:
            renameAction = menu.addAction('Rename')
            self.connect(renameAction, SIGNAL("triggered()"),
                lambda: self._main._central.obtain_editor().refactor_rename(item.lineno, name))
        menu.exec_(QCursor.pos())


class ThreadRefresh(QThread):

    def __init__(self, tree):
        QThread.__init__(self)
        self._tree = tree
        self.fileName = None
        self.path_to_file = None

    def run(self):
        self.fileName = self.fileName[:-3]
        #Get data using the introspection module
        self._tree.globals, self._tree.classes, self._tree.functions = introspection.inspect_file(self.path_to_file, self.fileName)


class ItemTree(QTreeWidgetItem):

    def __init__(self, parent, name, lineno=None):
        QTreeWidgetItem.__init__(self, parent, name)
        self.lineno = lineno
        self.isClickable = True
        self.isAttribute = False

