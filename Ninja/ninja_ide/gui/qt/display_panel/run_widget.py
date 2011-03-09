import sys
import math

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QPalette
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QPen
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QString
from PyQt4.QtCore import Qt

from ninja_ide.tools import runner
from ninja_ide.gui.qt.qtcss import styles
from ninja_ide import resources

class RunWidget(QPlainTextEdit):

    def __init__(self):
        QWidget.__init__(self)
        self.setReadOnly(True)
        styles.set_style(self, 'editor')
        self.setPlainText('For the moment NINJA only show output when the Program ends.')

        self.overlay = Overlay(self)
        self.overlay.hide()

        self.proc = QProcess(self)
        #self.proc.setProcessChannelMode(QProcess.ForwardedChannels)
        self.connect(self.proc, SIGNAL("readyReadStandardOutput()"), self.refresh_output)
        self.connect(self.proc, SIGNAL("readyReadStandardError()"), self.refresh_error)
        self.connect(self.proc, SIGNAL("finished(int, QProcess::ExitStatus)"), self._finish_process)

    def start_process(self, fileName, pythonPath=False):
        self.setPlainText('Running: ' + fileName + '\n'\
                + 'For the moment NINJA only show output when the Program ends.' + '\n\n')
        self.moveCursor(QTextCursor.Down)
        self.moveCursor(QTextCursor.Down)
        self.moveCursor(QTextCursor.Down)

        #runner.run_code_from_file(fileName)
        if not pythonPath:
            pythonPath = resources.python_path
        self.proc.start(pythonPath, [fileName])
        self.overlay.show()

    def kill_process(self):
        self.proc.kill()

    def refresh_output(self):
        text = str(self.proc.readAllStandardOutput().data())
        self.textCursor().insertText(text)

    def refresh_error(self):
        text = str(self.proc.readAllStandardError().data())
        self.textCursor().insertText(text)

    def _finish_process(self):
        self.overlay.killTimer(self.overlay.timer)
        self.overlay.hide()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()


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
