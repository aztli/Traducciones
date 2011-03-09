from __future__ import absolute_import

from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QDrag
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QMimeData
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.qt.main_panel import Editor
from ninja_ide.gui.qt.main_panel import Browser
from ninja_ide.gui.generic import TabCentralGeneric


class TabCentralWidget(QTabWidget, TabCentralGeneric):

    def __init__(self):
        QTabWidget.__init__(self)
        TabCentralGeneric.__init__(self)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setAcceptDrops(True)
        self.notOpening = True

        self.connect(self, SIGNAL("tabCloseRequested(int)"), self._close_tab)

    def obtain_editor(self):
        return self.currentWidget()

    def notify_font_change(self, font_family, font_size):
        self.emit(SIGNAL("editorFontChanged(QString, int)"), font_family, font_size)

    def set_editor_font(self, family, size):
        for i in range(self.count()):
            if type(self.widget(i)) == Editor:
                self.widget(i).set_font_notify(family, size)

    def add_tab(self, widget, title):
        self.addTab(widget, title)
        self.setCurrentIndex(self.count()-1)
        widget.setFocus()

    def mark_as_changed(self, val):
        ed = self.obtain_editor()
        if self.notOpening and ed is not None and val:
            ed.textModified = True
            self.tabBar().setTabTextColor(self.currentIndex(), QColor(Qt.red))

    def mark_as_saved(self):
        ed = self.obtain_editor()
        if type(ed) == Editor:
            ed.textModified = False
            ed.document().setModified(ed.textModified)
            self.tabBar().setTabTextColor(self.currentIndex(), QColor(Qt.gray))

    def is_open(self, fileName):
        for i in xrange(self.count()):
            if self.widget(i).path == fileName:
                return True
        return False

    def move_to_open(self, fileName):
        for i in xrange(self.count()):
            if self.widget(i).path == fileName:
                self.setCurrentIndex(i)

    def removeTab(self, index):
        if index != -1:
            self.setCurrentIndex(index)
            editor = self.currentWidget()
            if type(editor) == Editor:
                val = QMessageBox.No
                if editor.textModified:
                    fileName = self.tabBar().tabText(self.currentIndex())
                    val = QMessageBox.question(self, 'The file %s was not saved' % fileName,
                            'Do you want to save before closing?',
                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Close)
                if val == QMessageBox.Close:
                    return
                elif val == QMessageBox.Yes:
                    self.emit(SIGNAL("emitSaveSignal()"))
                    if editor.textModified:
                        return
            if type(editor) == Browser:
                editor.shutdown_pydoc()
            super(TabCentralWidget, self).removeTab(index)
            if self.currentWidget() is not None:
                self.currentWidget().setFocus()
            else:
                self.emit(SIGNAL("allTabsClosed()"))

    def _close_tab(self, index):
        self.removeTab(index)

    def check_for_unsaved(self):
        val = False
        for i in range(self.count()):
            val = val or self.widget(i).textModified
        return val

    def get_open_files(self):
        files = []
        for i in range(self.count()):
            if (type(self.widget(i)) is Editor) \
            and self.widget(i).path != '':
                files.append([self.widget(i).path,
                            self.widget(i).get_project_folder(),
                            self.widget(i).get_cursor_position()])
        return files

    def change_tab(self):
        if self.currentIndex() < (self.count()-1):
            self.setCurrentIndex(self.currentIndex() + 1)
        else:
            self.setCurrentIndex(0)

    def editor_focus(self):
        editor = self.obtain_editor()
        #Don't change the Main Tab Selected if it is in Follow Mode
        if editor.isReadOnly():
            return

        self.emit(SIGNAL("changeActualTab(QTabWidget)"), self)
        #custom behavior after the default
        #Check never saved
        if editor.newDocument:
            return
        #Check if we should ask to the user
        if not editor.ask_if_externally_modified:
            return
        #Check external modifications!
        if editor.check_external_modification():
            fileName = self.tabBar().tabText(self.currentIndex())
            val = QMessageBox.question(self, 'The file %s has changed on disc!' % fileName,
                                'Do you want to reload it?', QMessageBox.Yes, QMessageBox.No)
            if val == QMessageBox.Yes:
                self.emit(SIGNAL("emitReloadSignal()"))
            else:
                #dont ask again while the current file is open
                editor.ask_if_externally_modified = False

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.RightButton:
            return
        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())
        dropAction = drag.start(Qt.MoveAction)
        if dropAction == Qt.MoveAction:
            self.close()

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        event.accept()
        self.emit(SIGNAL("dropTab(QTabWidget)"), self)

    def wheelScroll(self, event):
        if self._follow_mode:
            self.emit(SIGNAL("scrollEditor(QWheelEvent, QTabWidget)"), event, self)
