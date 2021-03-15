from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget
from PyQt5.QtWidgets import QWidget, QProgressBar, QSpinBox, QAbstractSpinBox
from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit, QRadioButton, QButtonGroup
from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QGroupBox, QHBoxLayout
from PyQt5.QtWidgets import QTableWidget
from PyQt5 import QtWidgets, QtGui
from PyQt5.Qt import Qt

import pyqtgraph as pg
import numpy as np

import sys
sys.path.append("D:\\DSO\\pyqt5\\pyqttable")
from commonWidgets import QLineEditFileDialog, get_buttonless_QSpinBox, QRadioButtonsGroup

		
class Config(QGroupBox):
    def __init__(self, parent):
        super(Config, self).__init__(parent=parent)
        self.setTitle("Signal Config")
        layout = QFormLayout()

        self.srcfile = QLineEditFileDialog(self, filedialogmode="openFile")
        layout.addRow(QLabel("Signal File:"), self.srcfile)
        self.IQFormat = QRadioButtonsGroup(self, options=["IQ", "Real"])
        layout.addRow(QLabel("IQ Format:"), self.IQFormat)
        self.dtype = QRadioButtonsGroup(self, options=["int16", "float32"])
        layout.addRow(QLabel("dtype:"), self.dtype)
        
        self.headerskip = get_buttonless_QSpinBox(self, 0, 10000)
        layout.addRow(QLabel("Header Skip:"), self.headerskip)
        
        self.nsamples = get_buttonless_QSpinBox(self, 0, 99999999)
        layout.addRow(QLabel("Nsamples to plot:"), self.nsamples)
        self.setLayout(layout)
        
class ResultsView(QWidget):
    def __init__(self, parent):
        super(ResultsView, self).__init__(parent=parent)
        layout = QHBoxLayout()


        self.timedomain_widget = pg.PlotWidget(self, title="TimeSignal")
        layout.addWidget(self.timedomain_widget)
        
        self.spectrum_widget = pg.PlotWidget(self, title="20Log10(Spectrum)")
        layout.addWidget(self.spectrum_widget)
        
        self.setLayout(layout)


class TabView(QWidget):
    def __init__(self, parent):
        super(TabView, self).__init__(parent=parent)
        layout = QVBoxLayout()

        self.config = Config(self)
        layout.addWidget(self.config)
        
        self.runbtn = QPushButton(parent=self, text="Run")
        self.runbtn.clicked.connect(self.readfile)
        layout.addWidget(self.runbtn)
        
        self.results = ResultsView(self)
        layout.addWidget(self.results)
        
        self.setLayout(layout)
        
    def readfile(self):
        filepath = self.config.srcfile.text()
        if filepath:
            dtype = self.config.dtype.get_selected()
            print("Reading File")
            data = np.fromfile(filepath, dtype=dtype)
            print("Reading File Done")
            skip = self.config.headerskip.value()
            if skip:
                data = data[skip:]
                
            nsamples = self.config.nsamples.value()
            if nsamples:
                data = data[:nsamples]
            fmt = self.config.IQFormat.get_selected()
            if fmt == "IQ":
                data = data.astype(np.float32).view(np.complex64)
                realpart = np.ascontiguousarray(np.real(data))
                imagpart = np.ascontiguousarray(np.imag(data))
                x = np.arange(len(realpart))
                self.results.timedomain_widget.clear()
                self.results.timedomain_widget.addItem(pg.PlotDataItem(x, realpart, pen='w'))
                self.results.timedomain_widget.addItem(pg.PlotDataItem(x, imagpart, pen='r'))
                self.results.timedomain_widget.autoRange()
                
                spec = np.fft.fftshift(np.fft.fft(data))
                spec = 20*np.log10(1e-10+np.abs(spec))
                xx = np.linspace(-0.5,0.5, len(realpart), endpoint=False)
                self.results.spectrum_widget.clear()
                self.results.spectrum_widget.addItem(pg.PlotDataItem(xx, spec, pen='w'))
                self.results.spectrum_widget.autoRange()
            else:
                x = np.arange(len(data))
                self.results.timedomain_widget.clear()
                self.results.timedomain_widget.addItem(pg.PlotDataItem(x, data, pen='w'))
                self.results.timedomain_widget.autoRange()
                
                spec = np.fft.rfft(data)
                spec = 20*np.log10(1e-10+np.abs(spec))
                xx = np.linspace(0,1, len(spec), endpoint=False)
                self.results.spectrum_widget.clear()
                self.results.spectrum_widget.addItem(pg.PlotDataItem(xx, spec, pen='w'))
                self.results.spectrum_widget.autoRange()
                

class App(QMainWindow):
    """
    A QMainWindow is a QWidget but with predefined places for a menu bar, a status bar, a toolbar, 
    """
    def __init__(self):
        super().__init__()
        self.title = 'Raw Signal Viewer'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 400
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.view = TabView(self)
        
        
        
        self.setCentralWidget(self.view)
       

if __name__ == "__main__":

    app = QApplication([])
    sigviewer = App()
    sigviewer.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()
