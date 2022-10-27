from PIL import Image
import cv2
from joblib import PrintTime
import numpy as np
import os
import sys
import pydicom as dicom
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog,QMessageBox
from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
import pydicom
import math
from pydicom.data import get_testdata_files
from sympy import maximum



class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi(r"Task2222.ui", self)
        self.Browse_Button.clicked.connect(self.Browse)
        self.Apply_Button.clicked.connect(self.Apply_Zoom)
        self.Normal_tableWidget.setColumnWidth(0,470)
        self.Normal_tableWidget.setColumnWidth(1,470)
        self.Dicom_tableWidget.setColumnWidth(0,470)
        self.Dicom_tableWidget.setColumnWidth(1,470)
        self.New_Dimensions_tableWidget.setColumnWidth(0,1000)
        self.New_Dimensions_tableWidget.setColumnWidth(1,1000)
        self.show()

#####################################################################################################################################################
##################################################### IMAGE VIEWER TAB######################################################################################
######################################################################################################################################################

########################################################## BROWSE #####################################################################################
    def Browse(self):
        self.Dicom_tableWidget.clearContents()
        global file_name
        file_name=QFileDialog.getOpenFileName(self, "Browse Image", "../", "*.dcm;;" " *.bmp;;" "*.jpeg;;" "*.jpg;;" "*.png;;" )
########################################  IF JPEG OR BMP FILE ##################################################
        if file_name[0].endswith(".bmp") | file_name[0].endswith(".jpeg") | file_name[0].endswith(".jpg") | file_name[0].endswith(".png"):
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
        if file_name[0].endswith(".bmp") | file_name[0].endswith(".jpeg")| file_name[0].endswith(".jpg") | file_name[0].endswith(".png"):
            self.color=self.normal_pil_image.mode
            self.Image_height=self.Normal_pix_image.height()
            self.Image_width=self.Normal_pix_image.width()


            self.image_array=np.asarray(self.normal_pil_image)
            self.channels=self.image_array.shape[2]
            minimum=int(np.amin(self.normal_pil_image))
            maximum=int(np.amax(self.normal_pil_image))
            self.image_depth=int((np.ceil(np.log2(maximum-minimum+1)))*self.channels)
               
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


#####################################################################################################################################################
#####################################################ZOOMING TAB######################################################################################
######################################################################################################################################################

###################################################### APPLY FUCTION ######################################################################################
    def Apply_Zoom(self):   
        try:
            self.Convert_to_gray()
        except:
            QMessageBox.about(self,"Error","Image not selected")
        else:
            if self.ZoomingFactor_doubleSpinBox.value()>0:
                self.zooming_factor=self.ZoomingFactor_doubleSpinBox.value()
                self.Gray_image_array=np.asarray(self.Gray_Image)
                self.New_width=int(self.Image_width*self.zooming_factor)
                self.New_height=int(self.Image_height*self.zooming_factor)
                self.Apply_Nearest_Neighbor()
                self.Apply_Bilinear_zooming()
                self.Show_new_dimensions()
            else:
                    QMessageBox.about(self,"Error","Value not acceptable!")
        
        
################################################################# CONVERT TO GRAY SCALE ################################################################
    def Convert_to_gray(self):
        if file_name[0].endswith(".bmp") | file_name[0].endswith(".jpeg")| file_name[0].endswith(".jpg") | file_name[0].endswith(".png"):
            self.Gray_Image=self.normal_pil_image.convert('L')
        elif file_name[0].endswith(".dcm"):
            self.Gray_Image=self.final_pil_image.convert('L')
################################################################# NEAREST NEIGHBOR FUNCTION ############################################################################
    def Apply_Nearest_Neighbor(self):
        Zoomed_image=np.random.randint(100,size=(self.New_height,self.New_width))
        for i in range (0,self.New_height):
            for j in range (0,self.New_width):
                Zoomed_image[i,j]=self.Gray_image_array[int(i/self.zooming_factor),int(j/self.zooming_factor)]
        
        Zoomed_image=Zoomed_image.astype('uint8')
        Final_Zoomed_image=Image.fromarray(Zoomed_image,mode='L')
        Pixmap_Final_Zoomed_image=Final_Zoomed_image.toqpixmap()
        self.Nearest_Image_label.setPixmap(Pixmap_Final_Zoomed_image)
        # print(Zoomed_image.shape)
        # print('######################################################')
        # print(self.Gray_image_array.shape)


##################################################################### Show new dimensions ###############################################################  
    
    def Show_new_dimensions(self):
        Readings=[{"Property":"Height","Value":self.New_height},{"Property":"width","Value":self.New_width}]
        self.New_Dimensions_tableWidget.setRowCount(len(Readings))
        row=0
        for i in Readings:
            self.New_Dimensions_tableWidget.setItem(row,0, QtWidgets.QTableWidgetItem(i["Property"]))
            self.New_Dimensions_tableWidget.setItem(row,1, QtWidgets.QTableWidgetItem(str(i["Value"])))
            row=row+1

###################################################################### BILINEAR FUNCTION ############################################################################
    def Apply_Bilinear_zooming(self):
        Zoomed_image=np.zeros((self.New_height, self.New_width))
        for i in range (0,self.New_height):
            for j in range (0,self.New_width):
                #map the coordinates back to the original image
                x = i / self.zooming_factor
                y = j / self.zooming_factor
                #calculate the coordinate values for 4 surrounding pixels.
                x_floor = math.floor(x)
                # min to avoid index error
                x_ceil = min( self.Image_height - 1, math.ceil(x))
                y_floor = math.floor(y)
                y_ceil = min(self.Image_width - 1, math.ceil(y))

                # if x is integer so it doesn't need interpolation
                if (x_ceil == x_floor) and (y_ceil == y_floor):
                    q = self.Gray_image_array[int(x), int(y)]

                # if it is a point between 2 points on the y-axis  
                elif (x_ceil == x_floor):
                    q1 = self.Gray_image_array[int(x), int(y_floor)]
                    q2 = self.Gray_image_array[int(x), int(y_ceil)]
                    q = q1 * (y_ceil - y) + q2 * (y - y_floor)

                # if it is a point between 2 points on the x-axis  
                elif (y_ceil == y_floor):
                    q1 = self.Gray_image_array[int(x_floor), int(y)]
                    q2 = self.Gray_image_array[int(x_ceil), int(y)]
                    q = (q1 * (x_ceil - x)) + (q2	 * (x - x_floor))
                else:
                # get the 4 surrounding pixels
                    value_of_1st_pixel = self.Gray_image_array[x_floor, y_floor]
                    value_of_2nd_pixel = self.Gray_image_array[x_ceil, y_floor]
                    value_of_3rd_pixel = self.Gray_image_array[x_floor, y_ceil]
                    value_of_4th_pixel = self.Gray_image_array[x_ceil, y_ceil]
                # Bilinear interpolation calculations
                    q1 = value_of_1st_pixel * (x_ceil - x) + value_of_2nd_pixel * (x - x_floor)
                    q2 = value_of_3rd_pixel * (x_ceil - x) + value_of_4th_pixel * (x - x_floor)
                    q = q1 * (y_ceil - y) + q2 * (y - y_floor)
                Zoomed_image[i,j]=q
        Zoomed_image=Zoomed_image.astype('uint8')
        Final_Zoomed_image=Image.fromarray(Zoomed_image,mode='L')
        Pixmap_Final_Zoomed_image=Final_Zoomed_image.toqpixmap()
        self.Bilinear_Image_label.setPixmap(Pixmap_Final_Zoomed_image)

######################################################### RUN THE APP ##############################################################################
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()

