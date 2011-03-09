from __future__ import absolute_import

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QLabel
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize

from ninja_ide import resources

class AboutNinja(QDialog):
    
    def __init__(self, parent=None):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setModal(True)
        self.setWindowTitle('Acerca de NINJA-IDE')
        self.setMaximumSize(QSize(0,0))
        v_box = QVBoxLayout(self)

        pixmap = QPixmap(resources.images['icon'])
        labIcon = QLabel('')
        labIcon.setPixmap(pixmap)
        hbox = QHBoxLayout()
        hbox.addWidget(labIcon)
        lblTitle = QLabel('<h1>NINJA-IDE</h1>\n<i>Ninja Is Not Just Another IDE<i>')
        lblTitle.setTextFormat(Qt.RichText)
        lblTitle.setAlignment(Qt.AlignLeft)
        hbox.addWidget(lblTitle)
        v_box.addLayout(hbox)
        v_box.addWidget(QLabel("""NINJA-IDE (from: "Ninja Is Not Just Another IDE"), es un
Entorno de desarrollo integrado, diseñado especialmente para 
contruir aplicaciones de python.
NINJA-IDE Proveen herramientas que facilitan el desarrollo de aplicaciones
en python y maneja todo tipo de situaciones gracias a su Numero de extenciones."""))
        v_box.addWidget(QLabel('Version: 1.0'))
        v_box.addWidget(QLabel('Pagina del Proyecto: http://ninja-ide.org.ar'))
        v_box.addWidget(QLabel('Codigo Fuente: http://ninja-ide.googlecode.com'))
	v_box.addWidget(QLabel('Pagina de los Traductores: http://aztli.cs.buap.mx'))
