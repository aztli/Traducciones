from __future__ import absolute_import

import re

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QToolTip
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QTextOption
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QToolTip
from PyQt4.QtGui import QTextCharFormat
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QTextFormat
from PyQt4.QtGui import QTextBlock
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QWheelEvent
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QPen
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QFont
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QThread
from PyQt4.QtCore import QRegExp
from PyQt4.QtCore import QPointF
from PyQt4.QtCore import SIGNAL
from PyQt4 import QtCore

from rope.contrib import finderrors
from rope.refactor import extract
from rope.refactor.importutils import ImportTools
from rope.refactor.rename import Rename

from ninja_ide.gui.generic.main_panel import EditorGeneric
from ninja_ide.gui.generic import BaseCentralWidget

from ninja_ide import resources
from ninja_ide.gui.qt.qtcss import styles
from ninja_ide.tools import loader
from ninja_ide.tools import pep8mod
from ninja_ide.tools import manage_files

from ninja_ide.gui.qt.main_panel.editor.completer import Completer
from ninja_ide.gui.qt.main_panel.editor.highlighter import Highlighter
from ninja_ide.gui.qt.main_panel.editor.highlighter_pygments import HighlighterPygments


class Editor(QPlainTextEdit, EditorGeneric, BaseCentralWidget):

    def __init__(self, parent, project=None):
        QPlainTextEdit.__init__(self)
        EditorGeneric.__init__(self)
        BaseCentralWidget.__init__(self)
        self.parent = parent
        self.completer = Completer(self, project)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setMouseTracking(True)
        doc = self.document()
        option = QTextOption()
        option.setFlags(QTextOption.ShowTabsAndSpaces)
        doc.setDefaultTextOption(option)
        self.setDocument(doc)
        self.setCenterOnScroll(True)
        self.foldedBlocks = []
        self.pep8lines = []
        self.pep8checks = []
        self.result = []
        self.patIsWord = re.compile('\w+')
        self.okPrefix = QRegExp('[.)}:,\]]')

        #file modification time POSIX
        self._mtime = None
        #Flag to dont bug the user when answer 'dont show the modification dialog'
        self.ask_if_externally_modified = True

        #Brace matching
        self.braces = None

        self.sidebarWidget = self.SidebarWidget(self)
        self.viewport().installEventFilter(self)

        self.highlighter = None
        styles.set_editor_style(self, resources.custom_scheme)
        #Thread to check errors and check style
        self._threadErros = ThreadErrors(self)

        self.connect(self, SIGNAL("cursorPositionChanged()"), self.highlight_current_line)
        self.connect(self, SIGNAL("modificationChanged(bool)"), self.modif_changed)
        self.connect(self, SIGNAL("undoAvailable(bool)"), self.undo_available)
        self.connect(self._threadErros, SIGNAL("finished()"), self.highlight_current_line)
        self.highlight_current_line()

    def find_errors_and_check_style(self):
        self._threadErros.start()

    def _find_errors(self):
        if self.findErrors and manage_files.get_file_extension(self.path) == '.py':
            self.result = []
            try:
                self.completer._project.validate()
                resPath = manage_files.convert_to_relative(self.completer._project._address, self.path)
                resource = self.completer._project.get_resource(resPath)
                self.result = finderrors.find_errors(self.completer._project, resource)
            except:
                self.result = []
        else:
            self.result = []

    def _check_style(self):
        if self.checkStyle and manage_files.get_file_extension(self.path) == '.py':
            self.pep8lines = []
            tempChecks = []
            self.pep8checks = pep8mod.run_check(['--show-source', self.path])
            comments = False
            line = ''
            addLine = True
            for p in self.pep8checks:
                if p.find('.py:') > 0:
                    comments = True
                    if len(line) != 0:
                        tempChecks.append(line)
                        line = ''
                        addLine = True
                    startPos = p.find('.py:') + 4
                    endPos = p.find(':', startPos)
                    self.pep8lines.append(int(p[startPos:endPos]))
                    line += str(p[p.find(':', endPos + 1) + 2:]) + '\n'
                elif addLine:
                    line += p
                    addLine = False
            if len(line) != 0:
                tempChecks.append(line)
            self.pep8checks = tempChecks
        else:
            self.pep8checks = []
            self.pep8lines = []

    def remove_unused_imports(self):
        try:
            self.completer._project.validate()
            resPath = manage_files.convert_to_relative(self.completer._project._address, self.path)
            resource = self.completer._project.get_file(resPath)
            import_tools = ImportTools(self.completer._project.pycore)
            modname = self.completer._project.pycore.modname(resource)
            pymod = self.completer._project.pycore.get_module(modname)
            module_with_imports = import_tools.module_imports(pymod)
            module_with_imports.remove_unused_imports()
            source = module_with_imports.get_changed_source()
            self.textCursor().beginEditBlock()
            self.selectAll()
            self.insertPlainText(source)
            self.textCursor().endEditBlock()
        except Exception, reason:
            print 'not removed: ' + str(reason)

    def organize_imports(self):
        try:
            self.completer._project.validate()
            resPath = manage_files.convert_to_relative(self.completer._project._address, self.path)
            resource = self.completer._project.get_file(resPath)
            import_tools = ImportTools(self.completer._project.pycore)
            modname = self.completer._project.pycore.modname(resource)
            pymod = self.completer._project.pycore.get_module(modname)
            source = import_tools.organize_imports(pymod)
            self.textCursor().beginEditBlock()
            self.selectAll()
            self.insertPlainText(source)
            self.textCursor().endEditBlock()
        except Exception, reason:
            print 'not organized: ' + str(reason)

    def extract_method(self):
        try:
            self.completer._project.validate()
            extracted = QInputDialog.getText(self, 'Extract as Method', 'New Method Name:')
            if not extracted[1]:
                return
            else:
                extracted = str(extracted[0])
            resPath = manage_files.convert_to_relative(self.completer._project._address, self.path)
            resource = self.completer._project.get_file(resPath)
            cursor = self.textCursor()
            start = self.document().findBlock(cursor.selectionStart()).position()
            end = self.document().findBlock(cursor.selectionEnd()).next().position()
            extractor = extract.ExtractMethod(self.completer._project, resource, start, end)
            source = extractor.get_changes(extracted, similar=False, global_=False)
            source = source.get_description()
            lines = [line[1:] for line in source.splitlines() if line.startswith('+')]
            del lines[0]
            self.textCursor().beginEditBlock()
            self.insertPlainText('')
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            cursor.insertText(lines[0])
            del lines[0]
            self._insert_code_fragment(cursor, lines, 1)
            self.textCursor().endEditBlock()
        except Exception, reason:
            print 'not extracted: ' + str(reason)

    def refactor_rename(self, lineno, oldName):
        try:
            self.completer._project.validate()
            rename = QInputDialog.getText(self, 'Refactor Rename', 'Enter New Name:')
            if not rename[1]:
                return
            else:
                rename = str(rename[0])
            resPath = manage_files.convert_to_relative(self.completer._project._address, self.path)
            resource = self.completer._project.get_file(resPath)
            self.textCursor().setPosition(self.document().findBlockByLineNumber(lineno-1).position())
            if oldName.index('(') > -1:
                oldName = oldName.split('(')[0]
            self.find_match(oldName)
            cursor = self.textCursor()
            offset = cursor.selectionStart()
            changes = Rename(self.completer._project, resource, offset).get_changes(rename)
            dialog = RefactorDialog(self, changes, self.completer._project)
            dialog.show()
        except Exception, reason:
            print 'not extracted: ' + str(reason)

    def create_property(self, lineno, attribute):
        propName = QInputDialog.getText(self, 'Property Name', 'Enter the Property Name:')
        if not propName[1]:
            return
        propName = str(propName[0])
        lines = [
            '',
            (' ' * EditorGeneric.indent) + 'def get_' + attribute + '(self):',
            (' ' * EditorGeneric.indent * 2) + 'return self.' + attribute + '',
            '',
            (' ' * EditorGeneric.indent) + 'def set_' + attribute + '(self, ' + attribute + '):',
            (' ' * EditorGeneric.indent * 2) + 'self.' + attribute + ' = ' + attribute + '',
            '',
            (' ' * EditorGeneric.indent) + propName + \
                ' = property(get_' + attribute + ', set_' + attribute + ')']
        self.textCursor().beginEditBlock()
        cursor = self.textCursor()
        cursor.setPosition(self.document().findBlockByLineNumber(lineno).position())
        self._insert_code_fragment(cursor, lines, 1)
        self.textCursor().endEditBlock()

#    def add_missing_imports(self):
#        try:
#            self.completer._project.validate()
#            resPath = manage_files.convert_to_relative(self.completer._project._address, self.path)
#            resource = self.completer._project.get_file(resPath)
#            import_tools = ImportTools(self.completer._project.pycore)
#            modname = self.completer._project.pycore.modname(resource)
#            pymod = self.completer._project.pycore.get_module(modname)
#            module_with_imports = import_tools.module_imports(pymod)
#            new_import = import_tools.get_import(resource)
#            module_with_imports.add_import(new_import)
#            source = module_with_imports.get_changed_source()
#            self.textCursor().beginEditBlock()
#            self.selectAll()
#            self.insertPlainText(source)
#            self.textCursor().endEditBlock()
#        except Exception, reason:
#            print 'not removed: ' + str(reason)

    def _insert_code_fragment(self, cursor, lines, lineNro):
        pat = re.compile('^\s*$|^\s*#')
        spaces = self.get_leading_spaces(lines[lineNro])
        block = cursor.block()
        block = block.next()
        while block.isValid():
            text2 = unicode(block.text())
            if not pat.match(text2):
                spacesEnd = self.get_leading_spaces(text2)
                if len(spacesEnd) <= len(spaces):
                    if pat.match(unicode(block.previous().text())):
                        block = block.previous()
                        break
                    else:
                        break
            block = block.next()
        if not block.isValid():
            block = block.previous()
        cursor.setPosition(block.position())
        for line in lines:
            cursor.insertText(line)
            cursor.insertBlock()

    def undo_available(self, val):
        if not val:
            self.parent.mark_as_saved()

    def set_path(self, fileName):
        super(Editor, self).set_path(fileName)
        self.newDocument = False
        self._mtime = manage_files.get_last_modification(fileName)

    def get_project_folder(self):
        return self.completer.get_path_from_project()

    def get_cursor_position(self):
        return self.textCursor().position()

    def set_cursor_position(self, pos):
        cursor = self.textCursor()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)

    def check_external_modification(self):
        if self.newDocument:
            return False
        #Saved document we can ask for modification!
        return manage_files.check_for_external_modification(self.path, self._mtime)

    def has_write_permission(self):
        if self.newDocument:
            return True
        return manage_files.has_write_prmission(self.path)

    def register_syntax(self, fileName):
        ext = manage_files.get_file_extension(fileName)[1:]
        if self.highlighter is not None and \
            not self.path.endswith(ext):
            self.highlighter.deleteLater()
        if not self.path.endswith(ext):
            if ext in loader.extensions:
                self.highlighter = Highlighter(self.document(),
                    loader.extensions.get(ext, 'py'), resources.custom_scheme)
            else:
                try:
                    self.highlighter = HighlighterPygments(self.document(), fileName)
                except:
                    print 'There is no lexer for this file'
            #for apply rehighlighting (rehighlighting form highlighter not responding)
            self.firstVisibleBlock().document().find('\n').insertText('')

    def set_font(self, font):
        self.document().setDefaultFont(font)
        self.font_family = str(font.family())
        self.font_size = font.pointSize()
        self.parent.notify_font_change(self.font_family, self.font_size)

    def set_font_notify(self, family, size):
        font = QFont(family, size)
        self.document().setDefaultFont(font)
        self.font_family = family
        self.font_size = size

    def get_font(self):
        return self.document().defaultFont()

    def get_text(self):
        return self.toPlainText()

    def modif_changed(self, val):
        if self.parent is not None:
            self.parent.mark_as_changed(val)

    def zoom_in(self):
        font = self.font()
        size = font.pointSize()
        if size < self.font_max_size:
            size += 2
            font.setPointSize(size)
        self.setFont(font)

    def zoom_out(self):
        font = self.font()
        size = font.pointSize()
        if size > self.font_min_size:
            size -= 2
            font.setPointSize(size)
        self.setFont(font)

    def go_to_line(self, lineno):
        cursor = self.textCursor()
        cursor.setPosition(self.document().findBlockByLineNumber(lineno).position())
        self.setTextCursor(cursor)

    def comment(self):
        lang = manage_files.get_file_extension(self.get_path())[1:]
        key = loader.extensions.get(lang, 'python')
        comment_wildcard = loader.syntax[key]['comment'][0]

        #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor!!!
        cursor = self.textCursor()
        start = self.document().findBlock(cursor.selectionStart()).firstLineNumber()
        end = self.document().findBlock(cursor.selectionEnd()).firstLineNumber()
        startPosition = self.document().findBlockByLineNumber(start).position()

        #Start a undo block
        cursor.beginEditBlock()

        #Move the COPY cursor
        cursor.setPosition(startPosition)
        #Move the QPlainTextEdit Cursor where the COPY cursor IS!
        self.setTextCursor(cursor)
        self.moveCursor(QTextCursor.StartOfLine)
        self.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
        text = self.textCursor().selectedText()
        if text == comment_wildcard:
            cursor.endEditBlock()
            self.uncomment(start, end, startPosition)
            return
        else:
            self.moveCursor(QTextCursor.StartOfLine)
        for i in xrange(start, end + 1):
            self.textCursor().insertText(comment_wildcard)
            self.moveCursor(QTextCursor.Down)
            self.moveCursor(QTextCursor.StartOfLine)

        #End a undo block
        cursor.endEditBlock()

    def uncomment(self, start=-1, end=-1, startPosition=-1):
        lang = manage_files.get_file_extension(self.get_path())[1:]
        key = loader.extensions.get(lang, 'python')
        comment_wildcard = loader.syntax[key]['comment'][0]

        #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor!!!
        cursor = self.textCursor()
        if start == -1 and end == -1 and startPosition == -1:
            start = self.document().findBlock(cursor.selectionStart()).firstLineNumber()
            end = self.document().findBlock(cursor.selectionEnd()).firstLineNumber()
            startPosition = self.document().findBlockByLineNumber(start).position()

        #Start a undo block
        cursor.beginEditBlock()

        #Move the COPY cursor
        cursor.setPosition(startPosition)
        #Move the QPlainTextEdit Cursor where the COPY cursor IS!
        self.setTextCursor(cursor)
        self.moveCursor(QTextCursor.StartOfLine)
        for i in xrange(start, end + 1):
            self.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
            text = self.textCursor().selectedText()
            if text == comment_wildcard:
                self.textCursor().removeSelectedText()
            elif u'\u2029' in text:
                #\u2029 is the unicode char for \n
                #if there is a newline, rollback the selection made above.
                self.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)

            self.moveCursor(QTextCursor.Down)
            self.moveCursor(QTextCursor.StartOfLine)

        #End a undo block
        cursor.endEditBlock()

    def insert_horizontal_line(self):
        self.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        text = unicode(self.textCursor().selection().toPlainText())
        self.moveCursor(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
        comment = '#' * (80 - len(text))
        self.textCursor().insertText(comment)

    def insert_title_comment(self):
        result = str(QInputDialog.getText(self, 'Title Comment', 'Enter the Title Name:')[0])
        self.textCursor().beginEditBlock()
        self.moveCursor(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        comment = '#' * 80
        self.textCursor().insertText(comment)
        self.textCursor().insertBlock()
        self.textCursor().insertText('# ' + result)
        self.textCursor().insertBlock()
        self.textCursor().insertText(comment)
        self.textCursor().endEditBlock()

    def indent_more(self):
        #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor!!!
        cursor = self.textCursor()
        selectionStart = cursor.selectionStart()
        selectionEnd = cursor.selectionEnd()
        #line where indent_more should start and end
        start = self.document().findBlock(cursor.selectionStart()).firstLineNumber()
        end = self.document().findBlock(cursor.selectionEnd()).firstLineNumber()
        startPosition = self.document().findBlockByLineNumber(start).position()

        #Start a undo block
        cursor.beginEditBlock()

        #Decide which lines will be indented
        cursor.setPosition(selectionEnd)
        self.setTextCursor(cursor)
        #Select one char at left
        #If there is a newline \u2029 (\n) then skip it
        self.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)
        if u'\u2029' in self.textCursor().selectedText():
            end -= 1

        cursor.setPosition(selectionStart)
        self.setTextCursor(cursor)
        self.moveCursor(QTextCursor.StartOfLine)
        #Indent loop; line by line
        for i in xrange(start, end + 1):
            self.textCursor().insertText(' ' * Editor.indent)
            self.moveCursor(QTextCursor.Down, QTextCursor.MoveAnchor)

        #Restore the user selection
        cursor.setPosition(startPosition)
        selectionEnd = selectionEnd + (EditorGeneric.indent * (end-start + 1))
        cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        #End a undo block
        cursor.endEditBlock()

    def indent_less(self):
        #save the total of movements made after indent_less
        totalIndent = 0
        #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor!!!
        cursor = self.textCursor()
        selectionEnd = cursor.selectionEnd()
        #line where indent_less should start and end
        start = self.document().findBlock(cursor.selectionStart()).firstLineNumber()
        end = self.document().findBlock(cursor.selectionEnd()).firstLineNumber()
        startPosition = self.document().findBlockByLineNumber(start).position()

        #Start a undo block
        cursor.beginEditBlock()

        #Decide which lines will be indented_less
        cursor.setPosition(selectionEnd)
        self.setTextCursor(cursor)
        #Select one char at left
        self.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)
        #If there is a newline \u2029 (\n) then dont indent this line; skip it!
        if u'\u2029' in self.textCursor().selectedText():
            end -= 1

        cursor.setPosition(startPosition)
        self.setTextCursor(cursor)
        self.moveCursor(QTextCursor.StartOfLine)
        #Indent_less loop; line by line
        for i in xrange(start, end+1):
            #Select EditorGeneric.indent chars from the current line
            for j in xrange(EditorGeneric.indent):
                self.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)

            text = self.textCursor().selectedText()
            if text == ' '*EditorGeneric.indent:
                self.textCursor().removeSelectedText()
                totalIndent += EditorGeneric.indent
            elif u'\u2029' in text:
                #\u2029 is the unicode char for \n
                #if there is a newline, rollback the selection made above.
                for j in xrange(EditorGeneric.indent):
                    self.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)

            #Go Down to the next line!
            self.moveCursor(QTextCursor.Down)
        #Restore the user selection
        cursor.setPosition(startPosition)
        cursor.setPosition(selectionEnd - totalIndent, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        #End a undo block
        cursor.endEditBlock()

    def _match_braces(self, position, brace, forward):
        """based on: http://gitorious.org/khteditor"""
        if forward:
            braceMatch = {'(': ')', '[': ']', '{': '}'}
            text = self.get_selection(position, QTextCursor.End)
            braceOpen, braceClose = 1, 1
        else:
            braceMatch = {')': '(', ']': '[', '}': '{'}
            text = self.get_selection(QTextCursor.Start, position)
            braceOpen, braceClose = len(text)-1, len(text)-1
        while True:
            if forward:
                posClose = text.find(braceMatch[brace], braceClose)
            else:
                posClose = text.rfind(braceMatch[brace], 0, braceClose + 1)
            if posClose > -1:
                if forward:
                    braceClose = posClose + 1
                    posOpen = text.find(brace, braceOpen, posClose)
                else:
                    braceClose = posClose - 1
                    posOpen = text.rfind(brace, posClose, braceOpen + 1)
                if posOpen > -1:
                    if forward:
                        braceOpen = posOpen + 1
                    else:
                        braceOpen = posOpen - 1
                else:
                    if forward:
                        return position + posClose
                    else:
                        return position - (len(text) - posClose)
            else:
                return

    def get_selection(self, posStart, posEnd):
        cursor = self.textCursor()
        cursor.setPosition(posStart)
        cursor2 = self.textCursor()
        if posEnd == QTextCursor.End:
            cursor2.movePosition(posEnd)
            cursor.setPosition(cursor2.position(), QTextCursor.KeepAnchor)
        else:
            cursor.setPosition(posEnd, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        return unicode(text)

    def find_match(self, word, back=False, sensitive=False, whole=False):
        b = QTextDocument.FindBackward if back else None
        s = QTextDocument.FindCaseSensitively if sensitive else None
        w = QTextDocument.FindWholeWords if whole else None
        self.moveCursor(QTextCursor.NoMove, QTextCursor.KeepAnchor)
        if back or sensitive or whole:
            self.find(word, b or s or w)
        else:
            self.find(word)

    def replace_match(self, wordOld, wordNew, sensitive=False, whole=False, all=False):
        s = QTextDocument.FindCaseSensitively if sensitive else None
        w = QTextDocument.FindWholeWords if whole else None
        self.moveCursor(QTextCursor.NoMove, QTextCursor.KeepAnchor)

        cursor = self.textCursor()
        cursor.beginEditBlock()

        self.moveCursor(QTextCursor.Start)
        replace = True
        while (replace or all):
            result = False
            if sensitive or whole:
                result = self.find(wordOld, s or w)
            else:
                result = self.find(wordOld)

            if result:
                tc = self.textCursor()
                if tc.hasSelection():
                    tc.insertText(wordNew)
            else:
                break
            replace = False

        cursor.endEditBlock()

    def highlight_current_line(self):
        self.extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(resources.custom_scheme.get('current-line',
                        resources.color_scheme['current-line']))
            lineColor.setAlpha(20)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)

        #Highlight selected variable
        if not self.isReadOnly() and self.highlightVariables:
            word = self.text_under_cursor()
            if self.patIsWord.match(word):
                lineColor = QColor(resources.custom_scheme.get('selected-word',
                            resources.color_scheme['selected-word']))
                lineColor.setAlpha(100)
                block = self.firstVisibleBlock()
                cursor = self.document().find(word, block.position(),
                    QTextDocument.FindCaseSensitively or QTextDocument.FindWholeWords)
                while block.isValid() and \
                  block.blockNumber() <= self.sidebarWidget.highest_line and\
                  cursor.position() != -1:
                    selection = QTextEdit.ExtraSelection()
                    selection.format.setBackground(lineColor)
                    selection.cursor = cursor
                    self.extraSelections.append(selection)
                    cursor = self.document().find(word, cursor.position(),
                        QTextDocument.FindCaseSensitively or QTextDocument.FindWholeWords)
                    block = block.next()
        self.setExtraSelections(self.extraSelections)

        #Find Errors
        if self.checkStyle:
            cursor = self.textCursor()
            for error in self.result:
                block = self.document().findBlockByLineNumber(error.lineno - 1)
                if not block.isValid():
                    continue
                cursor.setPosition(block.position())
                selection = QTextEdit.ExtraSelection()
                selection.format.setUnderlineColor(Qt.red)
                selection.format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
                selection.cursor = cursor
                selection.cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                self.extraSelections.append(selection)
            if self.result:
                self.setExtraSelections(self.extraSelections)

        #Check Style
        cursor = self.textCursor()
        xline = 0
        for line in self.pep8lines:
            block = self.document().findBlockByLineNumber(line - 1)
            if not block.isValid():
                continue
            cursor.setPosition(block.position())
            selection = QTextEdit.ExtraSelection()
            selection.format.setToolTip(self.pep8checks[xline])
            xline += 1
            selection.format.setUnderlineColor(Qt.darkYellow)
            selection.format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            selection.cursor = cursor
            selection.cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            self.extraSelections.append(selection)
        if self.pep8lines:
            self.setExtraSelections(self.extraSelections)

        if self.braces is not None:
            self.braces = None
        cursor = self.textCursor()
        if cursor.position() == 0:
            self.setExtraSelections(self.extraSelections)
            return
        cursor.movePosition(QTextCursor.PreviousCharacter,
                             QTextCursor.KeepAnchor)
        text = unicode(cursor.selectedText())
        pos1 = cursor.position()
        if text in (')', ']', '}'):
            pos2 = self._match_braces(pos1, text, forward=False)
        elif text in ('(', '[', '{'):
            pos2 = self._match_braces(pos1, text, forward=True)
        else:
            self.setExtraSelections(self.extraSelections)
            return
        if pos2 is not None:
            self.braces = (pos1, pos2)
            selection = QTextEdit.ExtraSelection()
            selection.format.setForeground(Qt.red)
            selection.format.setBackground(QColor('#5BC85B'))
            selection.cursor = cursor
            self.extraSelections.append(selection)
            selection = QTextEdit.ExtraSelection()
            selection.format.setForeground(Qt.red)
            selection.format.setBackground(QColor('#5BC85B'))
            selection.cursor = self.textCursor()
            selection.cursor.setPosition(pos2)
            selection.cursor.movePosition(QTextCursor.NextCharacter,
                             QTextCursor.KeepAnchor)
            self.extraSelections.append(selection)
        else:
            self.braces = (pos1,)
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor('#5BC85B'))
            selection.format.setForeground(Qt.red)
            selection.cursor = cursor
            self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)

    def code_folding_event(self, lineNumber):
        if self._is_folded(lineNumber):
            self._fold(lineNumber)
        else:
            self._unfold(lineNumber)

        self.update()
        self.sidebarWidget.update()

    def _fold(self, lineNumber):
        startBlock = self.document().findBlockByNumber(lineNumber - 1)
        endPos = self._find_fold_closing(startBlock)
        endBlock = self.document().findBlockByNumber(endPos)

        block = startBlock.next()
        while block.isValid() and block != endBlock:
            block.setVisible(False)
            block.setLineCount(0)
            block = block.next()

        self.foldedBlocks.append(startBlock.blockNumber())
        self.document().markContentsDirty(startBlock.position(), endPos)

    def _unfold(self, lineNumber):
        startBlock = self.document().findBlockByNumber(lineNumber - 1)
        endPos = self._find_fold_closing(startBlock)
        endBlock = self.document().findBlockByNumber(endPos)

        block = startBlock.next()
        while block.isValid() and block != endBlock:
            block.setVisible(True)
            block.setLineCount(block.layout().lineCount())
            endPos = block.position() + block.length()
            if block.blockNumber() in self.foldedBlocks:
                close = self._find_fold_closing(block)
                block = self.document().findBlockByNumber(close)
            else:
                block = block.next()

        self.foldedBlocks.remove(startBlock.blockNumber())
        self.document().markContentsDirty(startBlock.position(), endPos)

    def _is_folded(self, line):
        block = self.document().findBlockByNumber(line)
        if not block.isValid():
            return False
        return block.isVisible()

    def _find_fold_closing(self, block):
        text = unicode(block.text())
        pat = re.compile('(\s)*#begin-fold:')
        if pat.match(text):
            return self._find_fold_closing_label(block)

        spaces = self.get_leading_spaces(text)
        pat = re.compile('^\s*$|^\s*#')
        block = block.next()
        while block.isValid():
            text2 = unicode(block.text())
            if not pat.match(text2):
                spacesEnd = self.get_leading_spaces(text2)
                if len(spacesEnd) <= len(spaces):
                    if pat.match(unicode(block.previous().text())):
                        return block.previous().blockNumber()
                    else:
                        return block.blockNumber()
            block = block.next()
        return block.previous().blockNumber()

    def _find_fold_closing_label(self, block):
        text = unicode(block.text())
        label = text.split(':')[1]
        block = block.next()
        pat = re.compile('\s*#end-fold:' + label)
        while block.isValid():
            if pat.match(unicode(block.text())):
                return block.blockNumber() + 1
            block = block.next()
        return block.blockNumber()

    def resizeEvent(self, e):
        self.sidebarWidget.setFixedHeight(self.height())
        QPlainTextEdit.resizeEvent(self, e)

    def eventFilter(self, object, event):
        if object is self.viewport():
            self.sidebarWidget.update()
            return False
        return QPlainTextEdit.eventFilter(object, event)

    def keyPressEvent(self, event):
        if self.completer is not None and self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab,
              Qt.Key_Escape, Qt.Key_Backtab):
                event.ignore()
                self.completer.popup().hide()
                return
            elif event.key == Qt.Key_Space:
                self.completer.popup().hide()

        if event.key() == Qt.Key_Tab:
            if self.textCursor().hasSelection():
                self.indent_more()
                return
            else:
                self.textCursor().insertText(' ' * EditorGeneric.indent)
                return
        elif event.key() == Qt.Key_Backspace:
            if self.textCursor().hasSelection():
                super(Editor, self).keyPressEvent(event)
                return
            for i in xrange(EditorGeneric.indent):
                self.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)
            text = self.textCursor().selection()
            if unicode(text.toPlainText()) == ' '*EditorGeneric.indent:
                self.textCursor().removeSelectedText()
                return
            else:
                for i in xrange(EditorGeneric.indent):
                    self.moveCursor(QTextCursor.Right)
        elif event.key() == Qt.Key_Home:
            if event.modifiers() == Qt.ShiftModifier:
                move = QTextCursor.KeepAnchor
            else:
                move = QTextCursor.MoveAnchor
            if self.textCursor().atBlockStart():
                self.moveCursor(QTextCursor.WordRight, move)
                return
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return) and \
          event.modifiers() != Qt.NoModifier:
            return

        super(Editor, self).keyPressEvent(event)

        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            text = unicode(self.document().findBlock(self.textCursor().position()-1).text())
            spaces = self.get_indentation(text)
            self.textCursor().insertText(spaces)
            if text != '' and text == ' '*len(text):
                previousLine = self.document().findBlock(self.textCursor().position()-1)
                self.moveCursor(QTextCursor.Up)
                self.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                self.textCursor().removeSelectedText()
                self.moveCursor(QTextCursor.Down)
            self.eventKeyReturn()
        elif unicode(event.text()) in self.braces_strings:
            self.textCursor().insertText(self.braces_strings[str(event.text())])
            self.moveCursor(QTextCursor.Left)
        completionPrefix = self.text_under_cursor()
        if completionPrefix.contains(self.okPrefix):
            completionPrefix = completionPrefix.remove(self.okPrefix)
        if self.codeCompletion and event.key() == Qt.Key_Period or \
          (event.key() == Qt.Key_Space and event.modifiers() == Qt.ControlModifier):
            self.completer.setCompletionPrefix('')
            cr = self.cursorRect()
            self.completer.complete(cr)
        if self.completer is not None and self.completer.popup().isVisible():
            if completionPrefix != self.completer.completionPrefix():
                self.completer.setCompletionPrefix(completionPrefix)
                self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))
                self.completer.setCurrentRow(0)
                cr = self.cursorRect()
                self.completer.complete(cr)
        self.eventKeyAny()

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def wheelEvent(self, event, follow=False):
        if event.modifiers() == Qt.ControlModifier:
            if event.delta() == 120:
                self.zoom_in()
            elif event.delta() == -120:
                self.zoom_out()
            event.ignore()
        else:
            super(Editor, self).wheelEvent(event)
            if not follow:
                self.parent.wheelScroll(event)

    def focusInEvent(self, event):
        super(Editor, self).focusInEvent(event)
        self.parent.editor_focus()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            fileName = str(event.mimeData().text())[7:].rstrip()
            content = manage_files.read_file_content(fileName)
            self.setPlainText(content)

    def contextMenuEvent(self, event):
        popup_menu = self.createStandardContextMenu()

        lang = manage_files.get_file_extension(self.get_path())[1:]
        if EditorGeneric.extraMenus.get(lang, False):
            popup_menu.insertSeparator(popup_menu.actions()[0])
            popup_menu.insertMenu(popup_menu.actions()[0], EditorGeneric.extraMenus[lang])

        menuRefactor = QMenu('Refactor')
        extractMethodAction = menuRefactor.addAction('Extract as Method')
        organizeImportsAction = menuRefactor.addAction('Organize Imports')
        removeUnusedAction = menuRefactor.addAction('Remove Unused Imports')
        self.connect(organizeImportsAction, SIGNAL("triggered()"), self.organize_imports)
        self.connect(removeUnusedAction, SIGNAL("triggered()"), self.remove_unused_imports)
        self.connect(extractMethodAction, SIGNAL("triggered()"), self.extract_method)
        popup_menu.insertSeparator(popup_menu.actions()[0])
        popup_menu.insertMenu(popup_menu.actions()[0], menuRefactor)

        popup_menu.exec_(event.globalPos())

    def mouseMoveEvent(self, event):
        position = event.pos()
        cursor = self.cursorForPosition(position)
        block = cursor.block()
        if (block.blockNumber() + 1) in self.pep8lines:
            index = self.pep8lines.index(block.blockNumber() + 1)
            QToolTip.showText(self.mapToGlobal(position), self.pep8checks[index], self)
        for error in self.result:
            if block.blockNumber() == (error.lineno - 1):
                QToolTip.showText(self.mapToGlobal(position), error.error, self)
                break
        super(Editor, self).mouseMoveEvent(event)


    #based on: http://john.nachtimwald.com/2009/08/15/qtextedit-with-line-numbers/ (MIT license)
    class SidebarWidget(QWidget):

        def __init__(self, editor):
            QWidget.__init__(self, editor)
            self.edit = editor
            self.highest_line = 0
            self.foldArea = 15
            self.rightArrowIcon = QPixmap()
            self.downArrowIcon = QPixmap()
            self.pat = re.compile('(\s)*def|(\s)*class|(\s)*#begin-fold:')
            css = '''
            QWidget {
              font-family: monospace;
              font-size: 10;
              color: black;
            }'''
            self.setStyleSheet(css)

        def update(self, *args):
            width = QFontMetrics(self.edit.document().defaultFont()).width(str(self.highest_line)) \
                    + 10 + self.foldArea
            if self.width() != width:
                self.setFixedWidth(width)
                self.edit.setViewportMargins(width, 0, 0, 0)
            QWidget.update(self, *args)

        def paintEvent(self, event):
            contents_y = 0
            page_bottom = self.edit.viewport().height()
            font_metrics = QFontMetrics(self.edit.document().defaultFont())
            current_block = self.edit.document().findBlock(self.edit.textCursor().position())

            painter = QPainter(self)
            painter.fillRect(self.rect(), Qt.lightGray)

            block = self.edit.firstVisibleBlock()
            viewport_offset = self.edit.contentOffset()
            line_count = block.blockNumber()
            painter.setFont(self.edit.document().defaultFont())
            while block.isValid():
                line_count += 1
                # The top left position of the block in the document
                position = self.edit.blockBoundingGeometry(block).topLeft() + viewport_offset
                # Check if the position of the block is out side of the visible area
                if position.y() > page_bottom:
                    break

                # We want the line number for the selected line to be bold.
                bold = False
                if block == current_block:
                    bold = True
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)

                # Draw the line number right justified at the y position of the
                # line. 3 is a magic padding number. drawText(x, y, text).
                if block.isVisible():
                    painter.drawText(self.width() - self.foldArea - font_metrics.width(str(line_count)) - 3,
                        round(position.y()) + font_metrics.ascent()+font_metrics.descent()-1,
                        str(line_count))

                # Remove the bold style if it was set previously.
                if bold:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)

                block = block.next()

            self.highest_line = line_count

            #Code Folding
            xofs = self.width() - self.foldArea
            painter.fillRect(xofs, 0, self.foldArea, self.height(),
                    QColor(resources.custom_scheme.get('fold-area', resources.color_scheme['fold-area'])))
            if self.foldArea != self.rightArrowIcon.width():
                polygon = QPolygonF()

                self.rightArrowIcon = QPixmap(self.foldArea, self.foldArea)
                self.rightArrowIcon.fill(Qt.transparent)
                self.downArrowIcon = QPixmap(self.foldArea, self.foldArea)
                self.downArrowIcon.fill(Qt.transparent)

                polygon.append(QPointF(self.foldArea * 0.4, self.foldArea * 0.25))
                polygon.append(QPointF(self.foldArea * 0.4, self.foldArea * 0.75))
                polygon.append(QPointF(self.foldArea * 0.8, self.foldArea * 0.5))
                iconPainter = QPainter(self.rightArrowIcon)
                iconPainter.setRenderHint(QPainter.Antialiasing)
                iconPainter.setPen(Qt.NoPen)
                iconPainter.setBrush(QColor(resources.custom_scheme.get('fold-arrow',
                            resources.color_scheme['fold-arrow'])))
                iconPainter.drawPolygon(polygon)

                polygon.clear()
                polygon.append(QPointF(self.foldArea * 0.25, self.foldArea * 0.4))
                polygon.append(QPointF(self.foldArea * 0.75, self.foldArea * 0.4))
                polygon.append(QPointF(self.foldArea * 0.5, self.foldArea * 0.8))
                iconPainter = QPainter(self.downArrowIcon)
                iconPainter.setRenderHint(QPainter.Antialiasing)
                iconPainter.setPen(Qt.NoPen)
                iconPainter.setBrush(QColor(resources.custom_scheme.get('fold-arrow',
                            resources.color_scheme['fold-arrow'])))
                iconPainter.drawPolygon(polygon)

            block = self.edit.firstVisibleBlock()
            while block.isValid():
                position = self.edit.blockBoundingGeometry(block).topLeft() + viewport_offset
                # Check if the position of the block is out side of the visible area
                if position.y() > page_bottom:
                    break

                if self.pat.match(unicode(block.text())) and block.isVisible():
                    if block.blockNumber() in self.edit.foldedBlocks:
                        painter.drawPixmap(xofs, round(position.y()), self.rightArrowIcon)
                    else:
                        painter.drawPixmap(xofs, round(position.y()), self.downArrowIcon)

                block = block.next()

            painter.end()
            QWidget.paintEvent(self, event)

        def mousePressEvent(self, event):
            if self.foldArea > 0:
                xofs = self.width() - self.foldArea
                font_metrics = QFontMetrics(self.edit.document().defaultFont())
                fh = font_metrics.lineSpacing()
                ys = event.posF().y()
                lineNumber = 0

                if event.pos().x() > xofs:
                    block = self.edit.firstVisibleBlock()
                    viewport_offset = self.edit.contentOffset()
                    page_bottom = self.edit.viewport().height()
                    while block.isValid():
                        position = self.edit.blockBoundingGeometry(block).topLeft() + viewport_offset
                        if position.y() > page_bottom:
                            break
                        if position.y() < ys and (position.y() + fh) > ys and \
                          self.pat.match(str(block.text())):
                            lineNumber = block.blockNumber() + 1
                            break

                        block = block.next()
                if lineNumber > 0:
                    self.edit.code_folding_event(lineNumber)


class RefactorDialog(QDialog):

    def __init__(self, parent, changes, project):
        QDialog.__init__(self, parent, Qt.Dialog)
        self._parent = parent
        self._changes = changes
        self._project = project
        self.setFixedWidth(600)
        self.setFixedHeight(400)
        self.setModal(True)
        self.setWindowTitle('Refactor Dialog')
        vbox = QVBoxLayout(self)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        styles.set_editor_style(self.text, resources.color_scheme)
        self.text.setPlainText(changes.get_description())
        self.btnProceed = QPushButton('Proceed!')
        self.btnCancel = QPushButton('Cancel')

        vbox.addWidget(self.text)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnCancel)
        hbox.addWidget(self.btnProceed)
        vbox.addLayout(hbox)

        self.extraSelections = []
        cursor = self.text.textCursor()
        block = self.text.firstVisibleBlock()
        while block.isValid():
            cursor.setPosition(block.position())
            if str(block.text()).startswith('+'):
                selection = QTextEdit.ExtraSelection()
                selection.format.setForeground(Qt.green)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                selection.cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                self.extraSelections.append(selection)
            elif str(block.text()).startswith('-'):
                selection = QTextEdit.ExtraSelection()
                selection.format.setForeground(Qt.red)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                selection.cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                self.extraSelections.append(selection)
            block = block.next()
        self.text.setExtraSelections(self.extraSelections)

        self.connect(self.btnCancel, SIGNAL("clicked()"), self.close)
        self.connect(self.btnProceed, SIGNAL("clicked()"), self.do_proceed)

    def do_proceed(self):
        self._project.do(self._changes)
        self._parent.setFocus()
        self.close()


class ThreadErrors(QThread):

    def __init__(self, editor):
        QThread.__init__(self)
        self._editor = editor

    def run(self):
        self._editor._find_errors()
        self._editor._check_style()



def factory_editor(fileName, parent, project=None):
    editor = Editor(parent, project)
    editor.register_syntax('lang.' + fileName)
    return editor
