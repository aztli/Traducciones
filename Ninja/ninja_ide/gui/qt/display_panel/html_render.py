from PyQt4 import QtGui, QtCore, QtWebKit

class WebRender(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        v_box = QtGui.QVBoxLayout(self)
        #Web Frame
        self.webFrame = QtWebKit.QWebView()
        v_box.addWidget(self.webFrame)

    def render_page(self, url):
        self.webFrame.load(QtCore.QUrl('file:///'+url))