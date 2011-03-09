from __future__ import absolute_import

import re

from PyQt4.QtGui import QAction
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject

from ninja_ide import resources
from ninja_ide.resources import OS_KEY
from ninja_ide.gui.generic.main_panel import EditorGeneric


class MenuSource(object):

    def __init__(self, menu, main):
        self._main = main

        showHideFindErrors = menu.addAction(QIcon(resources.images['bug']), 'Show/&Hide Find Errors in this File')
        showHideCheckStyle = menu.addAction('Sho&w/Hide Find Check Style in this File')
        menu.addSeparator()
        indentMoreAction = menu.addAction(QIcon(resources.images['indent-more']), 'Indent More (Tab)')
        indentLessAction = menu.addAction(QIcon(resources.images['indent-less']), 'Indent Less (Shift+Tab)')
        menu.addSeparator()
        commentAction = menu.addAction(QIcon(resources.images['comment-code']),'Comment (' + OS_KEY + '+D)')
        unCommentAction = menu.addAction(QIcon(resources.images['uncomment-code']),'Uncomment ('+OS_KEY+'+D)')
        horizontalLineAction = menu.addAction('Insert Horizontal Line ('+OS_KEY+'+R)')
        titleCommentAction = menu.addAction('Insert Title Comment ('+OS_KEY+'+T)')
        menu.addSeparator()
#        addMissingImportsAction = menu.addAction('Add &Missing Imports')
        organizeImportsAction = menu.addAction('&Organize Imports')
        removeUnusedImportsAction = menu.addAction('Remove Unused &Imports')
        extractMethodAction = menu.addAction('Extract selected &code as Method')
        menu.addSeparator()
        removeTrailingSpaces = menu.addAction('&Remove Trailing Spaces')
        replaceTabsSpaces = menu.addAction('Replace Tabs With &Spaces')
        moveUp = menu.addAction('Move &Up')
        moveDown = menu.addAction('Move &Down')
        duplicate = menu.addAction('Duplica&te')

        QObject.connect(indentMoreAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().indent_more())
        QObject.connect(indentLessAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().indent_less())
        QObject.connect(commentAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().comment())
        QObject.connect(unCommentAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().uncomment())
        QObject.connect(horizontalLineAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().insert_horizontal_line())
        QObject.connect(titleCommentAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().insert_title_comment())
        QObject.connect(removeUnusedImportsAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().remove_unused_imports())
#        QObject.connect(addMissingImportsAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().add_missing_imports())
        QObject.connect(organizeImportsAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().organize_imports())
        QObject.connect(extractMethodAction, SIGNAL("triggered()"), lambda: self._main._central.obtain_editor().extract_method())
        QObject.connect(moveUp, SIGNAL("triggered()"), self._move_up)
        QObject.connect(moveDown, SIGNAL("triggered()"), self._move_down)
        QObject.connect(duplicate, SIGNAL("triggered()"), self._duplicate)
        QObject.connect(replaceTabsSpaces, SIGNAL("triggered()"), self._replace_tabs_with_spaces)
        QObject.connect(removeTrailingSpaces, SIGNAL("triggered()"), self._remove_trailing_spaces)
        QObject.connect(showHideFindErrors, SIGNAL("triggered()"), self._show_hide_find_errors)

    def _show_hide_find_errors(self):
        editor = self._main._central.obtain_editor()
        editor.findErrors = not editor.findErrors

    def _replace_tabs_with_spaces(self):
        editor = self._main._central.obtain_editor()
        cursor = editor.textCursor()
        text = editor.toPlainText()
        text = text.replace('\t', ' ' * EditorGeneric.indent)
        editor.setPlainText(text)

    def _remove_trailing_spaces(self):
        editor = self._main._central.obtain_editor()
        cursor = editor.textCursor()
        cursor.setPosition(0)
        cursor.beginEditBlock()
        pat = re.compile('.*\\s$')
        block = editor.document().findBlockByLineNumber(0)
        while block.isValid():
            if pat.match(block.text()):
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
                cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
                cursor.insertText(unicode(block.text()).rstrip())
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor)
            block = block.next()

    def _move_up(self):
        editor = self._main._central.obtain_editor()
        cursor = editor.textCursor()
        cursor.beginEditBlock()
        block = cursor.block()
        if block.blockNumber() > 0:
            block2 = block.previous()
            tempLine = unicode(block.text())
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            cursor.insertText(block2.text())
            cursor.movePosition(QTextCursor.Up, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            cursor.insertText(tempLine)
        cursor.endEditBlock()

    def _move_down(self):
        editor = self._main._central.obtain_editor()
        cursor = editor.textCursor()
        cursor.beginEditBlock()
        block = cursor.block()
        if block.blockNumber() < (editor.blockCount() - 1):
            block2 = block.next()
            tempLine = unicode(block.text())
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            cursor.insertText(block2.text())
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            cursor.insertText(tempLine)
        cursor.endEditBlock()

    def _duplicate(self):
        editor = self._main._central.obtain_editor()
        cursor = editor.textCursor()
        cursor.beginEditBlock()
        block = cursor.block()
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
        cursor.insertBlock()
        cursor.insertText(block.text())
        cursor.endEditBlock()
