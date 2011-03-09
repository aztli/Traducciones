from __future__ import absolute_import

from PyQt4.QtGui import QSplitter
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QShortcut
from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide.tools import manage_files

from ninja_ide.gui.generic import CentralGeneric

from ninja_ide.gui.qt.tab_central_widget import TabCentralWidget
from ninja_ide.gui.qt.main_panel import Editor
from ninja_ide.gui.qt.main_panel import factory_editor


class CentralWidget(QSplitter, CentralGeneric):

    def __init__(self, main):
        QSplitter.__init__(self)
        CentralGeneric.__init__(self)
        self._main = main

        self._tabs = TabCentralWidget()
        self._tabs2 = TabCentralWidget()
        self.addWidget(self._tabs)
        self.addWidget(self._tabs2)
        self._tabs2.hide()
        self.setSizes([1, 1])

        shortChangeTab = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Tab), self._main)
        self.connect(shortChangeTab, SIGNAL("activated()"), self.actual_tab().change_tab)
        self.connect(self._tabs, SIGNAL("currentChanged(int)"), self._main._update_window_name)
        self.connect(self._tabs2, SIGNAL("currentChanged(int)"), self._main._update_window_name)
        self.connect(self._tabs, SIGNAL("currentChanged(int)"), self._main._refresh_symbols)
        self.connect(self._tabs, SIGNAL("currentChanged(int)"), self._exit_follow_mode)
        self.connect(self._tabs, SIGNAL("changeActualTab(QTabWidget)"), self._change_actual)
        self.connect(self._tabs2, SIGNAL("changeActualTab(QTabWidget)"), self._change_actual)
        self.connect(self._tabs, SIGNAL("dropTab(QTabWidget)"), self._move_tab)
        self.connect(self._tabs2, SIGNAL("dropTab(QTabWidget)"), self._move_tab)
        self.connect(self._tabs, SIGNAL("emitSaveSignal()"), self._main.save)
        self.connect(self._tabs2, SIGNAL("emitSaveSignal()"), self._main.save)
        self.connect(self._tabs, SIGNAL("allTabsClosed()"), self._main.new_editor)
        self.connect(self._tabs2, SIGNAL("allTabsClosed()"), self.tabs2_without_tabs)
        self.connect(self._tabs, SIGNAL("editorFontChanged(QString, int)"), self.update_editor_font)
        self.connect(self._tabs2, SIGNAL("editorFontChanged(QString, int)"), self.update_editor_font)
        self.connect(self._tabs, SIGNAL("scrollEditor(QWheelEvent, QTabWidget)"), self._scroll_follow_mode)
        self.connect(self._tabs2, SIGNAL("scrollEditor(QWheelEvent, QTabWidget)"), self._scroll_follow_mode)
        #refresh file
        self.connect(self._tabs, SIGNAL("emitReloadSignal()"), self._main.reload_file)
        self.connect(self._tabs2, SIGNAL("emitReloadSignal()"), self._main.reload_file)

    def tabs2_without_tabs(self):
        self.show_split(self.orientation())
        if self._tabs.count() == 0:
            self._main.new_editor()

    def update_editor_font(self, family, size):
        print family, size
        self._tabs.set_editor_font(family, size)
        self._tabs2.set_editor_font(family, size)

    def show_split(self, orientation):
        if self._follow_mode:
            self._show_follow_mode()
        if self._tabs2.isVisible() and orientation == self.orientation():
            self._tabs2.hide()
            for i in xrange(self._tabs2.count()):
                editor = self._tabs2.obtain_editor()
                editor.parent = self._tabs
                name = self._tabs2.tabText(self._tabs2.currentIndex())
                self._tabs.add_tab(editor, name)
                if editor.textModified:
                    self._tabs.mark_as_changed(True)
            self._mainTabSelected = True
        elif not self._tabs2.isVisible():
            editor = self._tabs.obtain_editor()
            editor.parent = self._tabs2
            name = self._tabs.tabText(self._tabs.currentIndex())
            self._tabs2.add_tab(editor, name)
            if editor.textModified:
                self._tabs2.mark_as_changed(True)
            self._tabs2.show()
            self.setSizes([1, 1])
            self._mainTabSelected = False
        self.setOrientation(orientation)

    def _move_tab(self, tab):
        if self._follow_mode:
            return
        if tab == self._tabs2:
            editor = self._tabs.obtain_editor()
            editor.parent = self._tabs2
            name = self._tabs.tabText(self._tabs.currentIndex())
            self._tabs2.add_tab(editor, name)
            if editor.textModified:
                self._tabs2.mark_as_changed(True)
        else:
            editor = self._tabs2.obtain_editor()
            if editor is not None:
                editor.parent = self._tabs
                name = self._tabs2.tabText(self._tabs2.currentIndex())
                self._tabs.add_tab(editor, name)
                if editor.textModified:
                    self._tabs.mark_as_changed(True)

    def _show_follow_mode(self):
        if type(self._tabs.obtain_editor()) is not Editor:
            return
        if self._tabs2.isVisible() and not self._follow_mode:
            self.show_split(self.orientation())
        if self._follow_mode:
            self._follow_mode = False
            self._tabs2._close_tab(0)
            self._tabs2.hide()
            self._tabs2.setTabsClosable(True)
            self._tabs._follow_mode = False
            self._tabs2._follow_mode = False
        else:
            #check if is instance of Editor
            self._follow_mode = True
            self.setOrientation(Qt.Horizontal)
            editor = self._tabs.obtain_editor()
            name = str(self._tabs.tabText(self._tabs.currentIndex()))
            editor2 = factory_editor(
                manage_files.get_file_extension(name)[1:], self._tabs2)
            editor2.setPlainText(editor.get_text())
            editor2.setReadOnly(True)
            self._tabs2.add_tab(editor2, name)
            if editor.textModified:
                self._tabs2.mark_as_changed(True)
            self._tabs._follow_mode = True
            self._tabs2._follow_mode = True
            self._tabs2.show()
            editor2.verticalScrollBar().setRange(editor.sidebarWidget.highest_line - 2, 0)
            self._tabs2.setTabsClosable(False)
            self.setSizes([1, 1])

    def check_for_unsaved(self):
        return self._tabs.check_for_unsaved() or self._tabs2.check_for_unsaved()

    def save_project_files(self, path):
        for i in xrange(self._tabs.count()):
            editor = self._tabs.widget(i)
            fileName = editor.path if editor != 0 else ' '
            if fileName.startswith(path) and type(editor) == Editor:
                self._tabs.setCurrentIndex(i)
                self._main.save()

    def _exit_follow_mode(self, val):
        if self._follow_mode:
            self._show_follow_mode()

    def _scroll_follow_mode(self, event, tab):
        editor = self._tabs.obtain_editor()
        editor2 = self._tabs2.obtain_editor()
        firstLine = editor2.firstVisibleBlock().firstLineNumber()
        lastLine = editor.sidebarWidget.highest_line
        if tab == self._tabs:
            if lastLine < (firstLine + 2):
                editor2.wheelEvent(event, True)
        else:
            if firstLine >= (lastLine - 4):
                editor.wheelEvent(event, True)
