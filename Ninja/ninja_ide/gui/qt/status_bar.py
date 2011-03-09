from __future__ import absolute_import

from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QShortcut
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt

import re

from ninja_ide import resources


class StatusBar(QStatusBar):

    def __init__(self):
        QStatusBar.__init__(self)
        self.editor = None

        self.widgetStatus = QWidget()
        vbox = QVBoxLayout(self.widgetStatus)
        vbox.setContentsMargins(0, 0, 0, 0)
        #Search Layout
        hSearch = QHBoxLayout()
        self.line = TextLine(self)
        self.line.setMinimumWidth(250)
        self.checkBackward = QCheckBox('Find Backward')
        self.checkSensitive = QCheckBox('Respect Case Sensitive')
        self.checkWholeWord = QCheckBox('Find Whole Words')
        self.btnClose = QPushButton(self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self.btnFind = QPushButton(QIcon(resources.images['find']), '')
        self.btnPrevious = QPushButton(self.style().standardIcon(QStyle.SP_ArrowLeft), '')
        self.btnNext = QPushButton(self.style().standardIcon(QStyle.SP_ArrowRight), '')
        hSearch.addWidget(self.btnClose)
        hSearch.addWidget(self.line)
        hSearch.addWidget(self.btnFind)
        hSearch.addWidget(self.btnPrevious)
        hSearch.addWidget(self.btnNext)
        hSearch.addWidget(self.checkBackward)
        hSearch.addWidget(self.checkSensitive)
        hSearch.addWidget(self.checkWholeWord)
        vbox.addLayout(hSearch)
        #Replace Layout
        hReplace = QHBoxLayout()
        self.lineReplace = TextLine(self)
        self.lineReplace.setMinimumWidth(250)
        self.btnCloseReplace = QPushButton(self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self.btnReplace = QPushButton('Replace')
        self.btnReplaceAll = QPushButton('Replace All')
        hReplace.addWidget(self.btnCloseReplace)
        hReplace.addWidget(self.lineReplace)
        hReplace.addWidget(self.btnReplace)
        hReplace.addWidget(self.btnReplaceAll)
        vbox.addLayout(hReplace)
        self.replace_visibility(False)

        self.addWidget(self.widgetStatus)

        self.shortEsc = QShortcut(QKeySequence(Qt.Key_Escape), self)

        self.connect(self.btnClose, SIGNAL("clicked()"), self.hide_status)
        self.connect(self.btnFind, SIGNAL("clicked()"), self.find)
        self.connect(self.btnNext, SIGNAL("clicked()"), self.find_next)
        self.connect(self.btnPrevious, SIGNAL("clicked()"), self.find_previous)
        self.connect(self, SIGNAL("messageChanged(QString)"), self.message_end)
        self.connect(self.btnCloseReplace, SIGNAL("clicked()"), lambda: self.replace_visibility(False))
        self.connect(self.btnReplace, SIGNAL("clicked()"), self.replace)
        self.connect(self.btnReplaceAll, SIGNAL("clicked()"), self.replace_all)
        self.connect(self.shortEsc, SIGNAL("activated()"), self.hide_status)

    def focus_find(self, editor):
        self.line.setFocus()
        self.editor = editor
        self.line.selectAll()

    def replace_visibility(self, val):
        self.lineReplace.setVisible(val)
        self.btnCloseReplace.setVisible(val)
        self.btnReplace.setVisible(val)
        self.btnReplaceAll.setVisible(val)

    def hide_status(self):
        self.checkSensitive.setCheckState(Qt.Unchecked)
        self.checkWholeWord.setCheckState(Qt.Unchecked)
        self.checkBackward.setCheckState(Qt.Unchecked)
        self.hide()
        self.replace_visibility(False)
        if self.editor is not None:
            self.editor.setFocus()

    def replace(self):
        s = False if self.checkSensitive.checkState() == Qt.Unchecked else True
        w = False if self.checkWholeWord.checkState() == Qt.Unchecked else True
        self.editor.replace_match(str(self.line.text()), str(self.lineReplace.text()), s, w)

    def replace_all(self):
        s = False if self.checkSensitive.checkState() == Qt.Unchecked else True
        w = False if self.checkWholeWord.checkState() == Qt.Unchecked else True
        self.editor.replace_match(str(self.line.text()), str(self.lineReplace.text()), s, w, True)

    def find(self):
        b = False if self.checkBackward.checkState() == Qt.Unchecked else True
        s = False if self.checkSensitive.checkState() == Qt.Unchecked else True
        w = False if self.checkWholeWord.checkState() == Qt.Unchecked else True
        self.editor.find_match(str(self.line.text()), b, s, w)

    def find_next(self):
        s = False if self.checkSensitive.checkState() == Qt.Unchecked else True
        w = False if self.checkWholeWord.checkState() == Qt.Unchecked else True
        self.editor.find_match(str(self.line.text()), False, s, w)

    def find_previous(self):
        s = False if self.checkSensitive.checkState() == Qt.Unchecked else True
        w = False if self.checkWholeWord.checkState() == Qt.Unchecked else True
        self.editor.find_match(str(self.line.text()), True, s, w)

    def showMessage(self, message, timeout):
        self.widgetStatus.hide()
        self.replace_visibility(False)
        self.show()
        super(StatusBar, self).showMessage(message, timeout)

    def message_end(self, message):
        if message == '':
            self.hide()
            super(StatusBar, self).clearMessage()
            self.widgetStatus.show()


class TextLine(QLineEdit):

    def __init__(self, parent):
        QLineEdit.__init__(self)
        self._parent = parent

    def keyPressEvent(self, event):
        if self._parent.editor is not None and event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self._parent.find()
        elif event.key() == Qt.Key_Right:
            self._parent.find_next()
        elif event.key() == Qt.Key_Left:
            self._parent.find_previous()
        super(TextLine, self).keyPressEvent(event)
