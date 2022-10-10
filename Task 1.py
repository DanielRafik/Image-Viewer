from PIL import Image
import numpy as np
import os
import sys
import pydicom as dicom
import matplotlib.pylab as plt
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtGui import QPixmap



class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi(r"task11.ui", self)
        self.Browse_Button.clicked.connect(self.Browse)
        self.show()

    def Browse(self):
        global file_name
        file_name=QFileDialog.getOpenFileName(self, "Browse Image", "../", ".dcm;;" " *.bmp;;" ".jpeg;;" )
        if file_name[0].endswith(".bmp") | file_name[0].endswith(".jpg"):
            print(file_name)
            self.Normal_Image=QPixmap(file_name)
            self.Image_label.setPixmap(self.Normal_Image)






print(os.stat('coin.jpg').st_size)
#def calculate_image_info(self):
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()

