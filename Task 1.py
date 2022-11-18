from __future__ import print_function
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
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import random
import matplotlib.image as img




class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi(r"Task22.ui", self)
        self.Browse_Button.clicked.connect(self.Browse)
        self.Apply_Button.clicked.connect(self.Apply_Zoom)
        self.Rotate_Button.clicked.connect(self.Apply_rotation)
        self.Shear_Button.clicked.connect(self.Apply_Nearest_Neighbor_Shearing)
        self.Browse_Equalization_Button.clicked.connect(self.Equalization_Browse)
        self.Apply_Equalization_Button.clicked.connect(self.Apply_Equalization)
        self.Normal_tableWidget.setColumnWidth(0,470)
        self.Normal_tableWidget.setColumnWidth(1,470)
        self.Dicom_tableWidget.setColumnWidth(0,470)
        self.Dicom_tableWidget.setColumnWidth(1,470)
        self.set_Equalization_Histogram_UI()
        # self.New_Dimensions_tableWidget.setColumnWidth(0,1000)
        # self.New_Dimensions_tableWidget.setColumnWidth(1,1000)
        
        self.Draw_T_image()
        self.show()
##########################################################################################################################################################
######################################################### SET UI ELEMENTS #########################################################################################
    def set_Equalization_Histogram_UI(self):
        self.Equalized_Histogram_graphicsView.canvas.axes.set_xlabel('Intensity')
        self.Equalized_Histogram_graphicsView.canvas.axes.set_ylabel('Probability')
        self.Original_Histogram_graphicsView.canvas.axes.set_xlabel('Intensity')
        self.Original_Histogram_graphicsView.canvas.axes.set_ylabel('Probability')
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
                self.cv_image=cv2.imread(file_name[0],0)
            except:
                QMessageBox.about(self,"Error","Error in type")
            else:
                self.Normal_pix_image=QPixmap(file_name[0])
                self.Read_Normal()
                self.Show_Normal_Readings()
                self.Image_label.setPixmap(self.Normal_pix_image)
                #self.Original_Image_Equalization_label.setPixmap(self.Normal_pix_image)

###########################################  IF DICOM FILE  ############################################################
        elif file_name[0].endswith(".dcm"):
            try:
                #self.cv_image=cv2.open()

                self.ds = pydicom.dcmread(file_name[0])

            except:
                QMessageBox.about(self,"Error","Error in type")
            else:
                self.normal_pil_image=self.convert_dicom()
                self.Read_Normal()
                self.Show_Normal_Readings()
                self.Read_Dicom()
                self.Show_Dicom_Readings()
                self.Image_label.setPixmap(self.Dicom_image)
                #self.Original_Image_Equalization_label.setPixmap(self.Dicom_image)
            

###########################################  CONVERT DICOM TO PIL  ############################################################
    def convert_dicom(self):
        self.new_image = self.ds.pixel_array.astype(float)
        scaled_image = (np.maximum(self.new_image, 0) / self.new_image.max()) * 255.0
        scaled_image = np.uint8(scaled_image)
        self.final_pil_image = Image.fromarray(scaled_image)
        self.final_pil_image.save('image.jpeg')
        self.Dicom_image=QPixmap('image.jpeg')
        return self.final_pil_image


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
                self.Apply_Nearest_Neighbor_zooming()
                self.Apply_Bilinear_zooming()
                #self.Show_new_dimensions()
            else:
                    QMessageBox.about(self,"Error","Value not acceptable!")


########################################################### convert to pixmap ############################################################################
    def Convert_to_pixmap(self,pil_image):
        Image_array=np.asarray(pil_image)
        New_Image=Image_array.astype('uint8')
        New_Image=Image.fromarray(New_Image,mode='L')
        Pixmap_Image=New_Image.toqpixmap()
        return Pixmap_Image
        
        
################################################################# CONVERT TO GRAY SCALE ################################################################
    def Convert_to_gray(self):
        if file_name[0].endswith(".bmp") | file_name[0].endswith(".jpeg")| file_name[0].endswith(".jpg") | file_name[0].endswith(".png"):
            self.Gray_Image=self.normal_pil_image.convert('L')
        elif file_name[0].endswith(".dcm"):
            self.Gray_Image=self.final_pil_image.convert('L')
################################################################# NEAREST NEIGHBOR FUNCTION ############################################################################
    def Apply_Nearest_Neighbor_zooming(self):
        Zoomed_image=np.random.randint(100,size=(self.New_height,self.New_width))
        for i in range (0,self.New_height):
            for j in range (0,self.New_width):
                Zoomed_image[i,j]=self.Gray_image_array[round(i/self.zooming_factor),round(j/self.zooming_factor)]
        
        Zoomed_image=Zoomed_image.astype('uint8')
        Final_Zoomed_image=Image.fromarray(Zoomed_image,mode='L')
        Pixmap_Final_Zoomed_image=Final_Zoomed_image.toqpixmap()
        self.Nearest_Image_label.setPixmap(Pixmap_Final_Zoomed_image)

##################################################################### Show new dimensions ###############################################################  
    
    # def Show_new_dimensions(self):
    #     Readings=[{"Property":"Height","Value":self.New_height},{"Property":"width","Value":self.New_width}]
    #     self.New_Dimensions_tableWidget.setRowCount(len(Readings))
    #     row=0
    #     for i in Readings:
    #         self.New_Dimensions_tableWidget.setItem(row,0, QtWidgets.QTableWidgetItem(i["Property"]))
    #         self.New_Dimensions_tableWidget.setItem(row,1, QtWidgets.QTableWidgetItem(str(i["Value"])))
    #         row=row+1

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


######################################################### Draw T image ##############################################################################
    def Draw_T_image(self):
        self.T_image_height=128
        self.T_image_width=128
        self.T_image_array=np.zeros((self.T_image_height,self.T_image_width))
        self.T_image_array[29:49,29:99]=255
        self.T_image_array[49:99,54:74]=255
        self.T_image=self.T_image_array.astype('uint8')
        self.T_image=Image.fromarray(self.T_image,mode='L')
        self.T_image=self.T_image.toqpixmap()
        
        self.Nearest_Neighbor_Rotation_graphicsView.canvas.axes.clear()
        self.Nearest_Neighbor_Rotation_graphicsView.canvas.axes.imshow(self.T_image_array,cmap=("gray"))
        self.Nearest_Neighbor_Rotation_graphicsView.canvas.draw()
        self.Bilinear_Rotation_graphicsView.canvas.axes.clear()
        self.Bilinear_Rotation_graphicsView.canvas.axes.imshow(self.T_image_array,cmap=("gray"))
        self.Bilinear_Rotation_graphicsView.canvas.draw()
        self.Shearing_graphicsView.canvas.axes.clear()
        self.Shearing_graphicsView.canvas.axes.imshow(self.T_image_array,cmap=("gray"))
        self.Shearing_graphicsView.canvas.draw()
        
        

    
#####################################################################################################################################################
##################################################### ROTATION TAB  `######################################################################################
######################################################################################################################################################
    def Apply_rotation(self):
        try:
            self.degree=int(self.lineEdit.text())
        except:
            QMessageBox.about(self,"Error","Please enter a value!")
        else:
            if(self.degree>0):
                self.lineEdit_2.setText("Anticlockwise")
            elif self.degree ==0:
                
                self.lineEdit_2.setText("No rotation")
            else:
                self.lineEdit_2.setText("Clockwise")
            self.rads = math.radians(self.degree)
    # We consider the rotated image to be of the same size as the original
            self.rot_img = np.uint8(np.zeros(self.T_image_array.shape))
    # Finding the center point of rotated (or original) image.
            self.Height = self.rot_img.shape[0]
            self.Width  = self.rot_img.shape[1]
        
        self.Apply_Nearest_Neighbor_rotation()
        self.Apply_Binlinear_rotation()


################################################ Nearest Neighbor Rotation ######################################################           
    def Apply_Nearest_Neighbor_rotation(self):

        Rotated_image_array=np.zeros((self.T_image_height,self.T_image_width))

        midx,midy = (self.Width//2, self.Height//2)

        for i in range(self.rot_img.shape[0]):
            for j in range(self.rot_img.shape[1]):

                x= (i-midx)*math.cos(self.rads)+(j-midy)*math.sin(self.rads)
                y= -(i-midx)*math.sin(self.rads)+(j-midy)*math.cos(self.rads)


                if x>self.T_image_height-1 or y>self.T_image_width-1:
                    x=int(x)+midx 
                    y=int(y)+midy 
                    
                else:
                    x=round(x)+midx 
                    y=round(y)+midy 

                if (x>=0 and y>=0 and x<self.T_image_array.shape[0]-1 and  y<self.T_image_array.shape[1]-1):
                        
                    Rotated_image_array[i,j]=self.T_image_array[x,y]
                        
        self.Nearest_Neighbor_Rotation_graphicsView.canvas.axes.clear()
        self.Nearest_Neighbor_Rotation_graphicsView.canvas.axes.imshow(Rotated_image_array,cmap=("gray"))
        self.Nearest_Neighbor_Rotation_graphicsView.canvas.draw()
                



######################################################## Bilinear Rotation ################################################################
    def Apply_Binlinear_rotation(self):
        Rotated_image_array=np.zeros((self.T_image_height,self.T_image_width))
        
    # We consider the rotated image to be of the same size as the original
        rot_img = np.uint8(np.zeros(self.T_image_array.shape))
        # Finding the center point of rotated (or original) image.
        height = rot_img.shape[0]
        width  = rot_img.shape[1]

        midx,midy = (width//2, height//2)

        for i in range(rot_img.shape[0]):
            for j in range(rot_img.shape[1]):
                x= (i-midx)*math.cos(self.rads)+(j-midy)*math.sin(self.rads)
                y= -(i-midx)*math.sin(self.rads)+(j-midy)*math.cos(self.rads)

        
                x=x+midx
                y=y+midy

                if (round(x)>=0 and round(y)>=0 and round(x)<self.T_image_array.shape[0]-1 and  round(y)<self.T_image_array.shape[1]-1):
                    x_floor = math.floor(x)
                    # min to avoid index error
                    x_ceil = min(self.T_image_height - 1, math.ceil(x))
                    y_floor = math.floor(y)
                    y_ceil = min(self.T_image_width - 1, math.ceil(y))

                    # if x is integer so it doesn't need interpolation
                    if (x_ceil == x_floor) and (y_ceil == y_floor):
                        q = self.T_image_array[int(x), int(y)]

                        # if it is a point between 2 points on the y-axis  
                    elif (x_ceil == x_floor):
                        q1 = self.T_image_array[int(x), int(y_floor)]
                        q2 = self.T_image_array[int(x), int(y_ceil)]
                        q = q1 * (y_ceil - y) + q2 * (y - y_floor)

                        # if it is a point between 2 points on the x-axis  
                    elif (y_ceil == y_floor):
                        q1 = self.T_image_array[int(x_floor), int(y)]
                        q2 = self.T_image_array[int(x_ceil), int(y)]
                        q = (q1 * (x_ceil - x)) + (q2	 * (x - x_floor))
                    else:
                        # get the 4 surrounding pixels
                        value_of_1st_pixel = self.T_image_array[x_floor, y_floor]
                        value_of_2nd_pixel = self.T_image_array[x_ceil, y_floor]
                        value_of_3rd_pixel = self.T_image_array[x_floor, y_ceil]
                        value_of_4th_pixel = self.T_image_array[x_ceil, y_ceil]
                        # Bilinear interpolation calculations
                        q1 = value_of_1st_pixel * (x_ceil - x) + value_of_2nd_pixel * (x - x_floor)
                        q2 = value_of_3rd_pixel * (x_ceil - x) + value_of_4th_pixel * (x - x_floor)
                        q = q1 * (y_ceil - y) + q2 * (y - y_floor)
                    Rotated_image_array[i,j]=q
            
        self.Bilinear_Rotation_graphicsView.canvas.axes.clear()
        self.Bilinear_Rotation_graphicsView.canvas.axes.imshow(Rotated_image_array,cmap=("gray"))
        self.Bilinear_Rotation_graphicsView.canvas.draw()
            




############################################################################################################################################################
###########################################################  SHEARING ######################################################################################
############################################################################################################################################################
    


    def Apply_Nearest_Neighbor_Shearing(self):
        Sheared_image_array=np.zeros((self.T_image_height,self.T_image_width*2))
        rads = math.radians(-45)
    # We consider the rotated image to be of the same size as the original
        
        for i in range(Sheared_image_array.shape[0]):
            for j in range(Sheared_image_array.shape[1]):

                x= i
                y= i*math.tan(rads)+j

                if (round(x)>=0 and round(y)>=0 and round(x)<self.T_image_array.shape[0]-1 and  round(y)<self.T_image_array.shape[1]-1):
                    
                    Sheared_image_array[i,j]=self.T_image_array[round(x),round(y)]
                    
                    

            
        self.Shearing_graphicsView.canvas.axes.clear()
        self.Shearing_graphicsView.canvas.axes.imshow(Sheared_image_array,cmap=("gray"))
        self.Shearing_graphicsView.canvas.draw()
                



#####################################################################################################################################################
##################################################### EQUALIZATION TAB  `######################################################################################
######################################################################################################################################################
    def Equalization_Browse(self):
        #file_name=QFileDialog.getOpenFileName(self, "Browse Image", "../", "*.dcm;;" "*.bmp;;" "*.jpeg;;" "*.png;;" )
        #global file_path
        #file_path =file_name[0]
        #Pil_img=Image.open(file_path)

        self.Browse()

        Pil_img=self.normal_pil_image
        # Pil_img=Pil_img.convert(mode='L')
        #self.Convert_to_gray()
        #global Final_Gray_image
        #self.Gray_image_array=np.asarray(self.Gray_Image)
        #Final_Gray_image=self.Convert_to_pixmap(self.Gray_image_array)
        # Pil_imggg=Pil_img.convert(mode='L')
        self.iimg=np.asarray(Pil_img)
        self.flat=self.iimg.flatten()
        
        self.Original_Image_graphicsView.canvas.axes.clear()
        self.Original_Image_graphicsView.canvas.axes.imshow(Pil_img,cmap='gray')
        self.Original_Image_graphicsView.canvas.draw()
        global pixels,counts
        pixels,counts=self.Histogram(Pil_img)
        self.Original_Histogram_graphicsView.canvas.axes.clear()
        self.Original_Histogram_graphicsView.canvas.axes.bar(pixels,counts)
        self.set_Equalization_Histogram_UI()
        self.Original_Histogram_graphicsView.canvas.draw()
        


    def Apply_Equalization(self):
        #self.Original_Image_Equalization_label.setPixmap(Final_Gray_image)
        global new_pixels,new_counts
        new_pixels,new_counts,tr=self.Equalize_Histogram(pixels,counts)
        self.Equalized_Histogram_graphicsView.canvas.axes.clear()
        self.Equalized_Histogram_graphicsView.canvas.axes.bar(new_pixels,new_counts)
        self.set_Equalization_Histogram_UI()
        self.Equalized_Histogram_graphicsView.canvas.draw()
        
        # for i in range(len(new_counts)):
        #     new_counts[i]=new_counts[i]*counts_sum
        tr2=np.array(tr)
        #trr=tr2[self.flat]
        tr2=tr2.astype('uint8')
        #trr=np.reshape(trr,self.cv_image)
        # New_Image=np.asarray(new_counts)
        img_new=tr2[self.flat]
        img_new=np.reshape(img_new,self.iimg.shape)
        # # self.Original_Image_graphicsView.canvas.axes.clear()
        # # self.Original_Image_graphicsView.canvas.axes.bar(new_pixels,new_counts)
        # # self.Original_Image_graphicsView.canvas.draw()
        self.Equalized_Image_graphicsView.canvas.axes.clear()
        self.Equalized_Image_graphicsView.canvas.axes.imshow(img_new,cmap='gray')
        self.Equalized_Image_graphicsView.canvas.draw()

########################################################## Histogram Function #######################################################################
    def Histogram(self,img):
        pixels=[]
        #create list of values 0-255
        for x in range(256):
            pixels.append(x)
        #initialize width and height of image
        # img=img.convert(mode='L')
        img_array=np.asarray(img)
        New_array=img_array.reshape(-1)
        img_array_length=len(New_array)
        counts=[]
        #for each intensity value
        for i in pixels:
            #set counter to 0
            temp=0
            #traverse through the pixels
            for x in range(img_array_length):
                #if pixel intensity equal to intensity level  
                #increment counter
                if (New_array[x]==i):
                    temp=temp+1

            #append frequency of intensity level 
            #print(temp)
            counts.append(temp)

         # Normalizing histogram 
        global counts_sum
        counts_sum=sum(counts)
        pdf=[]
        for i in counts:
            pdf.append(i/counts_sum)
        return pixels,pdf



############################################################### Equalizing Histogram ##############################################################
    def Equalize_Histogram(self,pixels,counts):
        #initialize list for cumulative probability 
        cdf=[]
        total=0
        for i in range(len(counts)):
            total=total+counts[i]
            cdf.append(total)

        #intialize list for mapping cdf
        tr=[]
        for i in range (len(cdf)):
            t=round(cdf[i]*255)
            tr.append(t)

        #intialize list for mapping cdf
        Final=[]
        for i in pixels:
            count=0
            tot=0
            for j in tr:
                if (j==i):
                    tot=tot+counts[count]
                count=count+1
            Final.append(tot)
        return pixels,Final,tr


######################################################### RUN THE APP ##############################################################################
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()

