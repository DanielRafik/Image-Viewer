from PIL import Image
import numpy as np
import os

Image_jpg = Image.open('coin.jpg')
Image_bmp=Image.open('sample_640×426.bmp')
Image_bmp.show()
Image_jpg.show()
print(Image_jpg.format)
print(Image_jpg.mode)
print(Image_jpg.width)
print(Image_jpg.height)
print(os.stat('coin.jpg').st_size)
