from __future__ import absolute_import

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap

from ninja_ide.gui.generic import BaseCentralWidget


class ImageViewer(QLabel, BaseCentralWidget):

    def __init__(self, image):
        QLabel.__init__(self)
        BaseCentralWidget.__init__(self)
        pixmap = QPixmap(image)
        self.setPixmap(pixmap)
        self.path = image
