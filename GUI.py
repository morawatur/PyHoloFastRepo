import math
import re
import sys
from functools import partial
import numpy as np
from PyQt4 import QtGui

import ImageSupport as imsup
import Constants as const

# --------------------------------------------------------

class LineEditWithLabel(QtGui.QWidget):
    def __init__(self, parent, labText='df', defaultValue=''):
        super(LineEditWithLabel, self).__init__(parent)
        self.label = QtGui.QLabel(labText)
        self.input = QtGui.QLineEdit(defaultValue)
        self.initUI()

    def initUI(self):
        # self.label.setFixedWidth(50)
        # self.input.setFixedWidth(50)
        self.setFixedWidth(50)
        self.input.setMaxLength(10)

        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(0)
        vbox.setSpacing(0)
        vbox.addWidget(self.label)
        vbox.addWidget(self.input)
        self.setLayout(vbox)

# --------------------------------------------------------

class PixmapOnLabel(QtGui.QLabel):
    def __init__(self, image, gridDim, parent):
        super(PixmapOnLabel, self).__init__(parent)
        self.grid = QtGui.QGridLayout()
        self.gridDim = gridDim
        self.image = image
        self.initUI()

    def initUI(self):
        self.image.ReIm2AmPh()
        self.image.UpdateBuffer()
        self.createPixmap()
        self.grid.setMargin(0)
        self.grid.setSpacing(0)
        self.setLayout(self.grid)
        self.createGrid()

    def createPixmap(self):
        qImg = QtGui.QImage(imsup.ScaleImage(self.image.buffer, 0.0, 255.0).astype(np.uint8),
                            self.image.width, self.image.height, QtGui.QImage.Format_Indexed8)
        pixmap = QtGui.QPixmap(qImg)
        # pixmap.convertFromImage(qImg)
        pixmap = pixmap.scaledToWidth(const.ccWidgetDim)
        self.setPixmap(pixmap)
        imgNumLabel, defocusLabel = self.parent().accessLabels()
        imgNumLabel.setText('Image {0}'.format(self.image.numInSeries))
        defocusLabel.setText('df = {0:.1e} um'.format(self.image.defocus * 1e6))

    def changePixmap(self, toNext=True):
        newImage = self.image.next if toNext else self.image.prev
        if newImage is not None:
            newImage.ReIm2AmPh()
            self.image = newImage
            self.createPixmap()

# --------------------------------------------------------

class HoloWidget(QtGui.QWidget):
    def __init__(self, image, parent):
        super(HoloWidget, self).__init__(parent)
        self.display = QtGui.QLabel()
        self.imageSim = image
        self.exitWave = image
        self.createPixmap()
        self.initUI()

    def initUI(self):
        self.numOfFirstEdit = LineEditWithLabel(self, labText='First to EWR', defaultValue='1')
        self.numOfFirstEdit.setFixedWidth(100)

        self.amplitudeRadioButton = QtGui.QRadioButton('Amplitude', self)
        self.amplitudeRadioButton.setChecked(True)
        self.phaseRadioButton = QtGui.QRadioButton('Phase', self)
        self.fftRadioButton = QtGui.QRadioButton('FFT', self)

        simulateButton = QtGui.QPushButton('Simulate image', self)
        simulateButton.clicked.connect(self.simulateImage)

        vbox_main = QtGui.QVBoxLayout()
        vbox_main.addWidget(self.display)

        self.setLayout(vbox_main)

        self.amplitudeRadioButton.toggled.connect(self.displayAmplitude)
        self.phaseRadioButton.toggled.connect(self.displayPhase)
        self.fftRadioButton.toggled.connect(self.displayFFT)

    def createPixmap(self):
        pass

    def changePixmap(self, toNext=True):
        pass

# --------------------------------------------------------

class HoloWindow(QtGui.QMainWindow):
    def __init__(self, image, gridDim):
        super(HoloWindow, self).__init__(None)
        self.centralWidget = QtGui.QWidget(self)
        self.holoWidget = HoloWidget(image, gridDim, self)
        self.initUI()

    def initUI(self):
        self.statusBar().showMessage('Ready')

        hbox_main = QtGui.QHBoxLayout()
        hbox_main.addWidget(self.ccWidget)
        hbox_main.addWidget(self.iwfrWidget)
        self.centralWidget.setLayout(hbox_main)
        self.setCentralWidget(self.centralWidget)

        self.move(300, 300)
        self.setWindowTitle('Cross correlation window')
        self.setWindowIcon(QtGui.QIcon('world.png'))
        self.show()
        self.setFixedSize(self.width(), self.height())     # disable window resizing

    def getCcWidgetRef(self):
        return self.ccWidget

    def getIwfrWidgetRef(self):
        return self.iwfrWidget

# --------------------------------------------------------

def RunEwrWindow(image, gridDim):
    app = QtGui.QApplication(sys.argv)
    holoWindow = HoloWindow(image, gridDim)
    sys.exit(app.exec_())