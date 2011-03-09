# based on Python Syntax highlighting from:
# http://diotavelli.net/PyQtWiki/Python%20syntax%20highlighting

from __future__ import absolute_import

import sys

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QPen

from ninja_ide.resources import color_scheme
from ninja_ide.resources import custom_scheme
from ninja_ide.tools import loader


def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setFontFamily('monospace')
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format(custom_scheme.get('keyword', color_scheme['keyword']), 'bold'),
    'operator': format(custom_scheme.get('operator', color_scheme['operator'])),
    'brace': format(custom_scheme.get('brace', color_scheme['brace'])),
    'definition': format(custom_scheme.get('definition', color_scheme['definition']), 'bold'),
    'string': format(custom_scheme.get('string', color_scheme['string'])),
    'string2': format(custom_scheme.get('string2', color_scheme['string2'])),
    'comment': format(custom_scheme.get('comment', color_scheme['comment']), 'italic'),
    'properObject': format(custom_scheme.get('properObject', color_scheme['properObject']), 'italic'),
    'numbers': format(custom_scheme.get('numbers', color_scheme['numbers'])),
    'spaces': format(custom_scheme.get('spaces', color_scheme['spaces'])),
    'extras': format(custom_scheme.get('extras', color_scheme['extras']))
}


def restyle(scheme):
    STYLES['keyword'] = format(scheme.get('keyword', color_scheme['keyword']), 'bold')
    STYLES['operator'] = format(scheme.get('operator', color_scheme['operator']))
    STYLES['brace'] = format(scheme.get('brace', color_scheme['brace']))
    STYLES['definition'] = format(scheme.get('definition', color_scheme['definition']), 'bold')
    STYLES['string'] = format(scheme.get('string', color_scheme['string']))
    STYLES['string2'] = format(scheme.get('string2', color_scheme['string2']))
    STYLES['comment'] = format(scheme.get('comment', color_scheme['comment']), 'italic')
    STYLES['properObject'] = format(scheme.get('properObject', color_scheme['properObject']), 'italic')
    STYLES['numbers'] = format(scheme.get('numbers', color_scheme['numbers']))
    STYLES['spaces'] = format(scheme.get('spaces', color_scheme['spaces']))
    STYLES['extras'] = format(scheme.get('extras', color_scheme['extras']))


class Highlighter (QSyntaxHighlighter):

    # braces
    braces = ['\\(', '\\)', '\\{', '\\}', '\\[', '\\]']

    def __init__(self, document, lang, scheme=None):
        QSyntaxHighlighter.__init__(self, document)
        langSyntax = loader.syntax[lang]
        if scheme is not None and not {}:
            restyle(scheme)

        keywords = langSyntax.get('keywords', [])
        operators = langSyntax.get('operators', [])
        extras = langSyntax.get('extras', [])

        rules = []

        # Keyword, operator, brace and extras rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in Highlighter.braces]
        rules += [(r'\b%s\b' % e, 0, STYLES['extras'])
            for e in extras]

        # All other rules
        proper = langSyntax.get('properObject', None)
        if proper is not None:
            proper = '\\b' + str(proper[0]) + '\\b'
            rules += [(proper, 0, STYLES['properObject'])]

        rules.append((r'__\w+__', 0, STYLES['properObject']))

        definition = langSyntax.get('definition', [])
        for de in definition:
            expr = '\\b' + de + '\\b\\s*(\\w+)'
            rules.append((expr, 1, STYLES['definition']))

        # Numeric literals
        rules += [
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        regex = langSyntax.get('regex', [])
        for reg in regex:
            expr = reg[0]
            color = color_scheme['extras']
            style = ''
            if len(reg) > 2:
                color = reg[1]
                style = reg[2]
            elif len(reg) > 1:
                color = reg[1]
            rules.append((expr, 0, format(color, style)))

        comments = langSyntax.get('comment', [])
        for co in comments:
            expr = co + '[^\\n]*'
            rules.append((expr, 0, STYLES['comment']))

        stringChar = langSyntax.get('string', [])
        for sc in stringChar:
            expr = r'"[^"\\]*(\\.[^"\\]*)*"' if sc == '"' else r"'[^'\\]*(\\.[^'\\]*)*'"
            rules.append((expr, 0, STYLES['string']))

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])    #'''
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])    #"""

        multi = langSyntax.get('multiline_comment', [])
        if multi:
            self.multi_start = (QRegExp(multi['open']), STYLES['comment'])
            self.multi_end = (QRegExp(multi['close']), STYLES['comment'])
        else:
            self.multi_start = None

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = expression.cap(nth).length()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
        if not self.multi_start:
            # Do multi-line strings
            in_multiline = self.match_multiline(text, *self.tri_single)
            if not in_multiline:
                in_multiline = self.match_multiline(text, *self.tri_double)
        else:
            # Do multi-line comment
            self.comment_multiline(text, self.multi_end[0], *self.multi_start)

        #Spaces
        expression = QRegExp('\s+')
        index = expression.indexIn(text, 0)
        while index >= 0:
            index = expression.pos(0)
            length = expression.cap(0).length()
            self.setFormat(index, length, STYLES['spaces'])
            index = expression.indexIn(text, index + length)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

    def comment_multiline(self, text, delimiter_end, delimiter_start, style):
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = delimiter_start.indexIn(text)
        while startIndex >= 0:
            endIndex = delimiter_end.indexIn(text, startIndex)
            commentLength = 0
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = text.length() - startIndex
            else:
                commentLength = endIndex - startIndex + delimiter_end.matchedLength()

            self.setFormat(startIndex, commentLength, style)
            startIndex = delimiter_start.indexIn(text, startIndex + commentLength)