from PIL import Image
import numpy as np
import os
import sys
import pydicom as dicom
import matplotlib.pylab as plt
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QPixmap



class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi(r"task11.ui", self)
        self.Browse_Button.clicked.connect(self.Browse)
        self.Normal_tableWidget.setColumnWidth(0,182)
        self.Normal_tableWidget.setColumnWidth(1,182)
        self.Dicom_tableWidget.setColumnWidth(0,182)
        self.Dicom_tableWidget.setColumnWidth(1,182)
        self.show()

    def Browse(self):
        global file_name
        file_name=QFileDialog.getOpenFileName(self, "Browse Image", "../", "*.dcm;;" " *.bmp;;" "*.jpeg;;" )
        if file_name[0].endswith(".bmp") | file_name[0].endswith(".jpeg"):
            self.n_img=Image.open(file_name[0])
            self.Normal_Image=QPixmap(file_name[0])
            self.Read_Normal()
            self.Show_Normal_Readings()
            self.Image_label.setPixmap(self.Normal_Image)


    def Read_Normal(self):
        self.color=self.n_img.mode
        self.Image_height=self.Normal_Image.height()
        self.Image_width=self.Normal_Image.width()
        self.image_size=os.stat(file_name[0]).st_size
        self.image_depth=self.Normal_Image.depth()

    def Show_Normal_Readings(self):
        Readings=[{"Property":"Height","Value":self.Image_height},{"Property":"width","Value":self.Image_width},{"Property":"Size","Value":self.image_size},{"Property":"Depth","Value":self.image_depth},{"Property":"Color","Value":self.color}]
        row=0
        self.Normal_tableWidget.setRowCount(len(Readings))
        for i in Readings:
            self.Normal_tableWidget.setItem(row,0, QtWidgets.QTableWidgetItem(i["Property"]))
            self.Normal_tableWidget.setItem(row,1, QtWidgets.QTableWidgetItem(str(i["Value"])))
            row=row+1
#print(os.stat('coin.jpg').st_size)
#def calculate_image_info(self):
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()

