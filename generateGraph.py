# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 21:40:21 2023

@author: Veysel
"""

import sys
import matplotlib
import codecs
import datetime
import os
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.sc1 = MplCanvas(self, width=5, height=4, dpi=100)
        self.sc1.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.sc2 = self.sc1.axes.twinx()
        self.currentFile = ""
        self.data = dict()
        
        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar1 = NavigationToolbar(self.sc1, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar1)
        layout.addWidget(self.sc1)
        
        self.combo_tarih = QComboBox(self)
        files = os.listdir()
        for ff in files:
            if "2023_" in ff:
                self.combo_tarih.addItem(ff.split(".")[0])
        
        self.combo_hisse = QComboBox(self)
        self.combo_va1 = QComboBox(self)
        self.combo_va2 = QComboBox(self)        
                
        self.button_generate = QPushButton(self)
        self.button_generate.setText("Tarihi Güncelle")
        
        self.button_generate.pressed.connect(self.onPressed)

        self.combo_hisse.activated[str].connect(self.onChanged)
        self.combo_va1.activated[str].connect(self.onChanged)
        self.combo_va2.activated[str].connect(self.onChanged)

        layout2 = QtWidgets.QHBoxLayout()
        
        layout2.addWidget(self.combo_tarih)
        layout2.addWidget(self.combo_hisse)
        layout2.addWidget(self.combo_va1)
        layout2.addWidget(self.combo_va2)
        layout2.addWidget(self.button_generate)

        layout.addLayout(layout2)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

    def onChanged(self,text):
        try:
            hisse = self.combo_hisse.currentText()
            va1 = self.combo_va1.currentText()
            va2 = self.combo_va2.currentText()
            self.sc1.axes.cla()
            self.sc2.cla()
            time1 = [(x-self.data[hisse][hisse+"."+va1][0][0])/(60*1000000) for x in self.data[hisse][hisse+"."+va1][0]]
            time2 = [(x-self.data[hisse][hisse+"."+va1][0][0])/(60*1000000) for x in self.data[hisse][hisse+"."+va2][0]]
            data1 = self.data[hisse][hisse+"."+va1][1]
            data2 = self.data[hisse][hisse+"."+va2][1]
            self.sc1.axes.plot(time1, data1)
            self.sc2.plot(time2, data2, 'red')


            self.sc1.draw()
        except Exception as exp:
            print(exp)

        
    def onPressed(self):
        try:
            date = self.combo_tarih.currentText()
            print(date)
            print(self.currentFile)
            if not self.currentFile == date:
                self.currentFile = date
                self.data = dict()
                g = codecs.open(date+".csv","r","utf8")
                c = [x.replace("\n","").split(",") for x in g.readlines()]
                g.close()
                print(len(c))
                hisseler = []
                valar = []
                for x in c:
                    try:
                        cdate = datetime.datetime.fromtimestamp(int(x[0])/1000000)
                        if float(x[2]) > 0 and cdate.hour > 10 and cdate.hour < 18:
                            valar.append(x[1].replace("'","").split(".")[1])
                            hisseler.append(x[1].replace("'","").split(".")[0])
                            if x[3] in self.data.keys():
                                if x[1] in self.data[x[3]].keys():
                                    self.data[x[3]][x[1]][0].append(int(x[0]))
                                    self.data[x[3]][x[1]][1].append(float(x[2]))
                                else:
                                    self.data[x[3]][x[1]] = [[int(x[0])],[float(x[2])]]
                            else:
                                self.data[x[3]] = dict()
                                self.data[x[3]][x[1]] = [[int(x[0])],[float(x[2])]]
                    except Exception as exp:
                        print(exp)
                hisseler = sorted(list(set(hisseler)))
                valar = sorted(list(set(valar)))
                self.combo_hisse.clear()
                self.combo_va1.clear()
                self.combo_va2.clear()
                for x in hisseler:
                    self.combo_hisse.addItem(x)
                for x in valar:
                    self.combo_va1.addItem(x)
                    self.combo_va2.addItem(x)
        except Exception as exp:
            print(exp)
                
            

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()
