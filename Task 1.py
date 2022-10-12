from PIL import Image
import cv2
import numpy as np
import os
import sys
import pydicom as dicom
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog,QMessageBox
from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
import pydicom

from pydicom.data import get_testdata_files



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
        self.Dicom_tableWidget.clearContents()
        global file_name
        file_name=QFileDialog.getOpenFileName(self, "Browse Image", "../", "*.dcm;;" " *.bmp;;" "*.jpeg;;" )
########################################  IF JPEG OR BMP FILE ##################################################
        if file_name[0].endswith(".bmp") | file_name[0].endswith(".jpeg"):
######################################  HANDLING THE ERROR  ####################################################
            try:
                self.normal_pil_image=Image.open(file_name[0])
               
            except:
                QMessageBox.about(self,"Error","Error in type")
            else:
                self.Normal_pix_image=QPixmap(file_name[0])
                self.Read_Normal()
                self.Show_Normal_Readings()
                self.Image_label.setPixmap(self.Normal_pix_image)

###########################################  IF DICOM FILE  ############################################################
        elif file_name[0].endswith(".dcm"):
            try:
                self.ds = pydicom.dcmread(file_name[0])
            except:
                QMessageBox.about(self,"Error","Error in type")
            else:
                self.convert_dicom()
                self.Read_Normal()
                self.Show_Normal_Readings()
                self.Read_Dicom()
                self.Show_Dicom_Readings()
                self.Image_label.setPixmap(self.Dicom_image)
            

###########################################  CONVERT DICOM TO PIL  ############################################################
    def convert_dicom(self):
        self.new_image = self.ds.pixel_array.astype(float)
        scaled_image = (np.maximum(self.new_image, 0) / self.new_image.max()) * 255.0
        scaled_image = np.uint8(scaled_image)
        self.final_pil_image = Image.fromarray(scaled_image)
        self.final_pil_image.save('image.jpeg')
        self.Dicom_image=QPixmap('image.jpeg')


#########################################  READ DICOM DATA ########################################################
#########################################  FUNCTION 'GET' TO CHECK IF THE INFO EXISTS ########################################
    def Read_Dicom(self):
        self.Modality=self.ds.get('Modality','Not Found')
        self.Patient_Name=self.ds.get('PatientName','Not Found')
        self.Patient_Age=self.ds.get('PatientAge','Not Found')
        self.Body_Parts=self.ds.get('BodyPartExamined','Not Found')



############################################### READ NORMAL DATA ####################################################
    def Read_Normal(self):
        if file_name[0].endswith(".bmp") | file_name[0].endswith(".jpeg"):
            self.color=self.normal_pil_image.mode
            self.Image_height=self.Normal_pix_image.height()
            self.Image_width=self.Normal_pix_image.width()
            
            if file_name[0].endswith(".bmp"):
                self.image_depth=int(os.path.getsize(file_name[0])*8/(self.Image_width*self.Image_height))
            else:
                self.image_depth=self.normal_pil_image.bits    
        else:
            self.color=self.ds.PhotometricInterpretation
            self.Image_height=self.Dicom_image.height()
            self.Image_width=self.Dicom_image.width()
            self.image_depth=self.ds.BitsAllocated
            
        self.image_size=self.image_depth*self.Image_height*self.Image_width


##############################################  LOAD NORMAL READINGS ON THE TABLES ######################################################
    def Show_Normal_Readings(self):
        Readings=[{"Property":"Height","Value":self.Image_height},{"Property":"width","Value":self.Image_width},{"Property":"Size","Value":self.image_size},{"Property":"Depth","Value":self.image_depth},{"Property":"Color","Value":self.color}]
        row=0
        self.Normal_tableWidget.setRowCount(len(Readings))
        for i in Readings:
            self.Normal_tableWidget.setItem(row,0, QtWidgets.QTableWidgetItem(i["Property"]))
            self.Normal_tableWidget.setItem(row,1, QtWidgets.QTableWidgetItem(str(i["Value"])))
            row=row+1

##############################################  LOAD DICOM READINGS ON THE TABLES ######################################################
    def Show_Dicom_Readings(self):
        Readings=[{"Property":"Modality","Value":self.Modality},{"Property":"Patient Name","Value":self.Patient_Name},{"Property":"Patient Age","Value":self.Patient_Age},{"Property":"Body Part","Value":self.Body_Parts}]
        row=0
        self.Dicom_tableWidget.setRowCount(len(Readings))
        for i in Readings:
            self.Dicom_tableWidget.setItem(row,0, QtWidgets.QTableWidgetItem(i["Property"]))
            self.Dicom_tableWidget.setItem(row,1, QtWidgets.QTableWidgetItem(str(i["Value"])))
            row=row+1
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()

