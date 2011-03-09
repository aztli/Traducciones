import re

from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QBrush

class ParentheseMatcher(object):

    matching = {
      "(": ")",
      "[": "]",
      "{": "}",
    }

    def __init__(self):
        pattern = "[%s]" % re.escape("".join(self.matching.keys()))
        self.textedit.CharData.add_char(pattern)
        self.color = QColor(self.textedit.settings.scheme.paren_color)
        self.brush = QBrush(QColor(self.textedit.settings.scheme.paren_background))
        self.selections = []
        self.animated_selections = []
        self.textedit.connect(self.textedit,
                              SIGNAL("cursorPositionChanged()"),
                              self.on_cursor_position_changed)
        self.animate = True
        self.select_inner = False

    def on_cursor_position_changed(self):
        cursor = self.textedit.textCursor()
        block = cursor.block()
        text = unicode(block.text()) + "\n"
        pos = cursor.position()
        col = cursor.columnNumber()
        char = text[col]
        if char in "([{":
            found = self.find_paren(pos, char, block)
        else:
            char = text[col-1]
            if char in ")]}":
                found = self.find_paren(pos-1, char, block, False)
            else:
                found = -1

        if self.selections:
            self.textedit.remove_extra_selections(self.selections)
            self.selections = []

        if self.animated_selections:
            self.textedit.remove_extra_selections(self.animated_selections)
            self.animated_selections = []

        if found == -1:
            return

        if found < pos:
            pos, found = found, pos

        if self.select_inner:
            sel = ExtraSelection(block, pos, found)
            sel.set_background(self.brush)
            self.animated_selections.append(sel)
        else:
            sel = ExtraSelection(block, pos, pos+1)
            sel.set_foreground(self.color)
            sel.set_background(self.brush)
            sel.set_bold(True)
            self.animated_selections.append(sel)
    
            sel = ExtraSelection(block, found, found-1)
            sel.set_foreground(self.color)
            sel.set_background(self.brush)
            sel.set_bold(True)
            self.animated_selections.append(sel)

        sel = ExtraSelection(block, pos, pos+1)
        sel.set_foreground(self.color)
        sel.set_bold(True)
        self.selections.append(sel)

        sel = ExtraSelection(block, found, found-1)
        sel.set_foreground(self.color)
        sel.set_bold(True)
        self.selections.append(sel)

        self.textedit.add_extra_selections(self.selections + self.animated_selections)

        if self.animate:
            QTimer.singleShot(500, self.remove_animated)

    def remove_animated(self):
        if self.animated_selections:
            self.textedit.remove_extra_selections(self.animated_selections)
            self.animated_selections = []

    def find_paren(self, start_pos, paren_char, block, forward=True):
        count = 1
        matching = self.matching[paren_char]
        get_user_data = self.textedit.user_data
        while block and block.isValid():
            char_data = get_user_data(block).get("char_data", {})
            if char_data:
                block_pos = block.position()
                for (char, (col,end)) in char_data:
                    pos = block_pos + col
                    if forward:
                        if pos > start_pos:
                            if char == paren_char:
                                count += 1
                            elif char == matching:
                                count -= 1
                                if count == 0:
                                    return pos + 1
                    else:
                        if pos < start_pos:
                            if char == paren_char:
                                count += 1
                            elif char == matching:
                                count -= 1
                                if count == 0:
                                    return pos
            if forward:
                block = block.next()
            else:
                block = block.previous()
        return -1


class ExtraSelection(QTextEdit.ExtraSelection):

    def __init__(self, cursor_or_block_or_document,
                 start_pos=None, end_pos=None):
        QTextEdit.ExtraSelection.__init__(self)
        cursor = QTextCursor(cursor_or_block_or_document)
        if start_pos != None:
            cursor.setPosition(start_pos)
        if end_pos:
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        self.cursor = cursor

    def set_bold(self, flag):
        #font = self.format.font()
        #font.setBold(flag)
        #self.format.setFont(font)
        self.format.setFontWeight(QFont.Bold)

    def set_foreground(self, color):
        self.format.setForeground(color)

    def set_background(self, brush):
        self.format.setBackground(brush)

    def set_full_width(self, flag=True):
        self.format.setProperty(
            QTextFormat.FullWidthSelection, QVariant(flag))

    def set_spellchecking(self, color=Qt.red):
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color) 

    def set_error(self, color=Qt.red):
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)

    def set_warning(self, color=QColor("orange")):
        self.format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        self.format.setUnderlineColor(color)