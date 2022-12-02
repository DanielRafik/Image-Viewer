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
        uic.loadUi(r"Task2222.ui", self)
        self.Browse_Button.clicked.connect(self.Browse)
        self.Apply_Button.clicked.connect(self.Apply_Zoom)
        self.Rotate_Button.clicked.connect(self.Apply_rotation)
        self.Shear_Button.clicked.connect(self.Apply_Nearest_Neighbor_Shearing)
        self.Browse_Equalization_Button.clicked.connect(self.Equalization_Browse)
        self.Apply_Equalization_Button.clicked.connect(self.Apply_Equalization)
        self.Apply_Filter_Button.clicked.connect(self.Apply_Kernel_Filter)
        self.Add_Noise_Button.clicked.connect(self.Apply_Noise)
        self.Filter_Noise_Button.clicked.connect(self.filter_noise)
        self.Apply_Fourier_Transform_Button.clicked.connect(self.Apply_Fourier)
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
                imag=np.asarray(self.normal_pil_image)
                self.Original_Image_Fourier_tab_graphicsView.canvas.axes.clear()
                self.Original_Image_Fourier_tab_graphicsView.canvas.axes.imshow(imag,cmap='gray')
                self.Original_Image_Fourier_tab_graphicsView.canvas.draw()
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
                imag=np.asarray(self.normal_pil_image)
                self.Image_label.setPixmap(self.Dicom_image)
                self.Original_Image_Fourier_tab_graphicsView.canvas.axes.clear()
                self.Original_Image_Fourier_tab_graphicsView.canvas.axes.imshow(imag,cmap='gray')
                self.Original_Image_Fourier_tab_graphicsView.canvas.draw()
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
            print(self.Gray_Image)
        elif file_name[0].endswith(".dcm"):
            self.Gray_Image=self.final_pil_image.convert('L')
################################################################# NEAREST NEIGHBOR FUNCTION ############################################################################
    def Apply_Nearest_Neighbor_zooming(self):
        Zoomed_image=np.random.randint(100,size=(self.New_height,self.New_width))
        for i in range (0,self.New_height):
            for j in range (0,self.New_width):
                Zoomed_image[i,j]=self.Gray_image_array[int(i/self.zooming_factor),int(j/self.zooming_factor)]
        
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
        self.Browse()
        Pil_img=self.normal_pil_image
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
        tr2=np.array(tr)
        tr2=tr2.astype('uint8')
        img_new=tr2[self.flat]
        img_new=np.reshape(img_new,self.iimg.shape)
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

#####################################################################################################################################################
##################################################### FILTER TAB  `######################################################################################
######################################################################################################################################################
    def Apply_Kernel_Filter(self):
        try:
            self.Convert_to_gray()
            gray_array=np.asarray(self.Gray_Image)
        except:
            QMessageBox.about(self,"Error","Please Browse an image!")
        else:
            
            global Filter_Size
            try:
                Filter_Size=int(self.Filter_Size_lineEdit.text())
                multiplication_factor=int(self.Multiplication_Factor_lineEdit.text())
            except:
                QMessageBox.about(self,"Error","Please enter Requirements as intergers!")
            else:
                Kernel_Filter=np.ones((Filter_Size, Filter_Size), np.float32)
                Kernel_Filter.shape
                test= np.array([[1, 2, 3], [3, 4, 5], [6, 7, 8]])
                Kernel_Filter=Kernel_Filter/(Filter_Size**2)
                padding=(int(Filter_Size/2))
                Post_convolution_image=self.convolve2D(gray_array,Kernel_Filter,padding=padding)
                Post_substraction_array=self.substarct_arrays(Post_convolution_image,gray_array)
                print("##########################################Convolution image###################################")
                print(Post_convolution_image)
                print('############################## Post substarction ###################################')
                print(Post_substraction_array)
                Post_multiplication_array=multiplication_factor*Post_substraction_array
                print('############################## Post multiplication ###################################')
                print(Post_multiplication_array)
                global Final_Enhanced_image
                Final_Enhanced_image=self.addition_arrays(Post_multiplication_array,gray_array)
                for x in range(Final_Enhanced_image.shape[0]):
                    for y in range(Final_Enhanced_image.shape[1]):
                        if(Final_Enhanced_image[x,y]<0):
                            Final_Enhanced_image[x,y]=0
                        elif(Final_Enhanced_image[x,y]>255):
                            Final_Enhanced_image[x,y]=255
                
                self.Original_Image_Filter_Tab_graphicsView.canvas.axes.clear()
                self.Original_Image_Filter_Tab_graphicsView.canvas.axes.imshow(gray_array,cmap='gray')
                self.Original_Image_Filter_Tab_graphicsView.canvas.draw()
                self.Enhanced_Image_Filter_graphicsView.canvas.axes.clear()
                self.Enhanced_Image_Filter_graphicsView.canvas.axes.imshow(Final_Enhanced_image,cmap='gray')
                self.Enhanced_Image_Filter_graphicsView.canvas.draw()



################################################################## Apply Noise ########################################################################
    def Apply_Noise (self):
        global Noisy_image
        try:
            Noisy_image=self.add_noise(Final_Enhanced_image)
        except:
            QMessageBox.about(self,"Error","Apply Kernel Filter!")
        else:
            self.Enhanced_Image_Filter_graphicsView.canvas.axes.clear()
            self.Original_Image_Filter_Tab_graphicsView.canvas.axes.clear()
            self.Original_Image_Filter_Tab_graphicsView.canvas.axes.imshow(Noisy_image,cmap='gray')
            self.Original_Image_Filter_Tab_graphicsView.canvas.draw()


################################################################## Filter Noise ####################################################################
    def filter_noise(self):
        try:
            Filtered_Noise_Image=self.median_filter(Noisy_image,Filter_Size)
        except:
            QMessageBox.about(self,"Error","Please enter add noise!")
        else:
            print('##################################### After Noise FIlter ################')
            print(Filtered_Noise_Image)
            self.Enhanced_Image_Filter_graphicsView.canvas.axes.clear()
            self.Enhanced_Image_Filter_graphicsView.canvas.axes.imshow(Filtered_Noise_Image,cmap='gray')
            self.Enhanced_Image_Filter_graphicsView.canvas.draw()
            

#################################################################### Median Filter #####################################################################
    def median_filter(self,data, filter_size):
        temp = []
        indexer = filter_size // 2
        data_final = []
        data_final = np.zeros((len(data),len(data[0])))
        for i in range(len(data)):

            for j in range(len(data[0])):

                for z in range(filter_size):
                    if i + z - indexer < 0 or i + z - indexer > len(data) - 1:
                        for c in range(filter_size):
                            temp.append(0)
                    else:
                        if j + z - indexer < 0 or j + indexer > len(data[0]) - 1:
                            temp.append(0)
                        else:
                            for k in range(filter_size):
                                temp.append(data[i + z - indexer][j + k - indexer])

                temp.sort()
                data_final[i][j] = temp[len(temp) // 2]
                temp = []
        return data_final
################################################################### cv open image ########################################################################
    def processImage(self,image): 
        image = cv2.imread(image) 
        image = cv2.cvtColor(src=image, code=cv2.COLOR_BGR2GRAY) 
        return image


################################################################### Substract arrays ########################################################################
    def substarct_arrays(self,array_substracted,original_array):
        output = np.zeros((array_substracted.shape[0], array_substracted.shape[1]))
        for x in range(array_substracted.shape[0]):
            for y in range(array_substracted.shape[1]):
                output[x, y] = original_array[x,y]-array_substracted[x,y]
        return output


################################################################### addition to arrays ########################################################################
    def addition_arrays(self,array_substracted,original_array):
        output = np.zeros((array_substracted.shape[0], array_substracted.shape[1]))
        for x in range(array_substracted.shape[0]):
            for y in range(array_substracted.shape[1]):
                output[x, y] = original_array[x,y]+array_substracted[x,y]  
        return output


############################################################### add Noise function ########################################################
    def add_noise(self, img):
         # Getting the dimensions of the image
        row , col = img.shape
        # Pick a random number between 600 and 20000
        number_of_pixels = random.randint(600, 20000)
        for i in range(number_of_pixels):
            # Pick a random y coordinate
            y_coord=random.randint(0, row - 1)
            # Pick a random x coordinate
            x_coord=random.randint(0, col - 1)
            # Color that pixel to white
            img[y_coord][x_coord] = 255
        
        number_of_pixels = random.randint(600, 20000)
        for i in range(number_of_pixels):
            # Pick a random y coordinate
            y_coord=random.randint(0, row - 1)
            # Pick a random x coordinate
            x_coord=random.randint(0, col - 1)
            # Color that pixel to black
            img[y_coord][x_coord] = 0
            
        return img
            
################################################################### Convolution #####################################################################
    def convolve2D(self,image, kernel, padding=0, strides=1):
        # Cross Correlation
        kernel = np.flipud(np.fliplr(kernel))
        
        # Gather Shapes of Kernel + Image + Padding
        xKernShape = kernel.shape[0]
        yKernShape = kernel.shape[1]
        xImgShape = image.shape[0]
        yImgShape = image.shape[1]

        # Shape of Output Convolution
        xOutput = xImgShape
        yOutput = yImgShape
        output = np.zeros((xOutput, yOutput))

        # Apply Equal Padding to All Sides
        if padding != 0:
            imagePadded = np.zeros((image.shape[0] + padding*2, image.shape[1] + padding*2))
            imagePadded[int(padding):int(-1 * padding), int(padding):int(-1 * padding)] = image
            print('############################## Padded image ###############################')
            print(imagePadded)
        else:
            imagePadded = image

        # Iterate through image
        for y in range(image.shape[1]):
            # Exit Convolution
            if y > image.shape[1]:
                break
            # Only Convolve if y has gone down by the specified Strides
            if y % strides == 0:
                for x in range(image.shape[0]):
                    # Go to next row once kernel is out of bounds
                    if x > image.shape[0]:
                        break
                    try:
                        # Only Convolve if x has moved by the specified Strides
                        if x % strides == 0:
                            output[x, y] = (kernel * imagePadded[x: x + xKernShape, y: y + yKernShape]).sum()
                    except:
                        break
        
        return output

#####################################################################################################################################################
##################################################### FOURIER TAB  `######################################################################################
######################################################################################################################################################

############################################# Apply Fourier ################################################################
    def Apply_Fourier(self):
        print()

######################################################### RUN THE APP ##############################################################################
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()
