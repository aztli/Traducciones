from __future__ import absolute_import

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtGui import QTextFormat
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QPainter
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.qt.main_panel.editor.highlighter import Highlighter
from ninja_ide.gui.generic.display_panel import ConsoleGeneric
from ninja_ide.gui.generic.main_panel import EditorGeneric
from ninja_ide.gui.qt.qtcss import styles


class ConsoleWidget(QPlainTextEdit, ConsoleGeneric):

    def __init__(self):
        QPlainTextEdit.__init__(self, '>>> ')
        ConsoleGeneric.__init__(self)
        self.setUndoRedoEnabled(False)
        styles.set_style(self, 'editor')
        self.setToolTip('Show/Hide (F4)')

        self.highlighter = Highlighter(self.document(), 'python')

        self.connect(self, SIGNAL("cursorPositionChanged()"), self.highlight_current_line)
        self.highlight_current_line()

    def setCursorPosition(self, position):
        self.moveCursor(QTextCursor.StartOfLine)
        for i in xrange(len(self.prompt) + position):
            self.moveCursor(QTextCursor.Right)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.write_command()
            return
        if self.get_cursor_position()  < 0:
            self.set_cursor_position(0)
        if event.key() == Qt.Key_Tab:
            self.textCursor().insertText(' '*EditorGeneric.indent)
            return
        if event.key() == Qt.Key_Home:
            self.set_cursor_position(0)
            return
        if event.key() == Qt.Key_PageUp:
            return
        elif event.key() in (Qt.Key_Left, Qt.Key_Backspace):
            if self.get_cursor_position() == 0:
                return
        elif event.key() == Qt.Key_Up:
            self.set_command(self.get_prev_history_entry())
            return
        elif event.key() == Qt.Key_Down:
            self.set_command(self.get_next_history_entry())
            return
        super(ConsoleWidget, self).keyPressEvent(event)

    def add_prompt(self, incomplete):
        if incomplete:
            prompt = '.' * 3 + ' '
        else:
            prompt = self.prompt
        self.appendPlainText(prompt)
        self.moveCursor(QTextCursor.End)

    def get_cursor_position(self):
        return self.textCursor().columnNumber() - len(self.prompt)

    def set_cursor_position(self, position):
        self.moveCursor(QTextCursor.StartOfLine)
        for i in xrange(len(self.prompt) + position):
            self.moveCursor(QTextCursor.Right)

    def write_command(self):
        command = str(self.document().findBlockByLineNumber(
                    self.document().lineCount() - 1).text())
        command = command.rstrip()[len(self.prompt):]
        self.add_history(command)

        incomplete = self.write(command)
        if not incomplete:
            output = self.read()
            if output is not None:
                self.appendPlainText(output)
        self.add_prompt(incomplete)

    def set_command(self, command):
        self.moveCursor(QTextCursor.End)
        self.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        for i in xrange(len(self.prompt)):
            self.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
        self.textCursor().removeSelectedText()
        self.textCursor().insertText(command)
        self.moveCursor(QTextCursor.End)

    def highlight_current_line(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.darkCyan)
            lineColor.setAlpha(20)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def mousePressEvent(self, event):
        #to avoid selection
        pass
