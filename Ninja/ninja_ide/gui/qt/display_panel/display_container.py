from __future__ import absolute_import

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QStackedWidget
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QButtonGroup
from PyQt4.QtCore import QTimeLine
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources

from ninja_ide.gui.qt.display_panel.console_widget import ConsoleWidget
from ninja_ide.gui.qt.display_panel.run_widget import RunWidget
from ninja_ide.gui.qt.display_panel.html_render import WebRender

from ninja_ide.gui.generic.display_panel import DisplayContainerGeneric


class DisplayContainer(QWidget, DisplayContainerGeneric):

    def __init__(self, main):
        QWidget.__init__(self)
        DisplayContainerGeneric.__init__(self)
        self._main = main
        vbox = QVBoxLayout(self)
        self.stack = StackedWidget()

        vbox.addWidget(self.stack)
        self._console = ConsoleWidget()
        self.stack.addWidget(self._console)

        self.runWidget = RunWidget()
        self.stack.addWidget(self.runWidget)

        self.web = WebRender()
        self.stack.addWidget(self.web)

        self.combo = QComboBox()
        self.combo.addItem(QIcon(resources.images['console']), '')
        self.combo.addItem(QIcon(resources.images['play']), '')
        self.combo.addItem(QIcon(resources.images['web']), '')
        self.connect(self.combo, SIGNAL("currentIndexChanged(int)"), self._item_changed)

    def gain_focus(self):
        self._console.setFocus()

    @pyqtSignature('int')
    def _item_changed(self, val):
        if not self.isVisible():
            self._main.containerIsVisible = True
            self.show()
        self.stack.show_display(val)

    def load_toolbar(self, toolbar):
        toolbar.addSeparator()
        toolbar.addWidget(self.combo)

    def run_application(self, fileName, pythonPath=False):
        self.combo.setCurrentIndex(1)
        self.runWidget.start_process(fileName, pythonPath)

    def kill_application(self):
        self.runWidget.kill_process()

    def render_web_page(self, url):
        self.combo.setCurrentIndex(2)
        self.web.render_page(url)

    def add_to_stack(self, widget, icon):
        self.stack.addWidget(widget)
        self.combo.addItem(QIcon(icon), '')


class StackedWidget(QStackedWidget):

    def __init__(self):
        QStackedWidget.__init__(self)

    def setCurrentIndex(self, index):
        self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)

    def show_display(self, index):
        self.setCurrentIndex(index)


class FaderWidget(QWidget):

    def __init__(self, old_widget, new_widget):
        QWidget.__init__(self, new_widget)

        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0

        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(555)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()

    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()
