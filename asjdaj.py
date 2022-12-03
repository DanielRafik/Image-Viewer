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



maze=np.array([[1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 2, 0, 1], [1, 0, 1, 1, 0, 0, 1], [1, 1, 1, 1, 0, 0, 1], [1, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 1]])
print(maze)
maze_flattened=maze.flatten()
goal=2
index=0
for i in range(len(maze_flattened)):
    if maze_flattened[i] ==goal:
        index=i

print(index)