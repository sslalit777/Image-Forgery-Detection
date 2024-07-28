import numpy as np
from PIL import ImageTk,Image,ImageChops
from datetime import datetime
import os
from ForgeryDetection import Detect
import re
import cv2

def detect(input_path,output_path, filename):
    
    image = os.path.join(input_path, filename)
    eps = 60
    min_samples = 2
    
    detect = Detect(image)
    key_points, descriptors = detect.siftDetector()
    forgery = detect.locateForgery(eps, min_samples)

    if forgery is None:
        return False
    else:
        cv2.imwrite(os.path.join(output_path, filename), forgery)
        return True
                
                
def getImage(path, width, height):
    """
    Function to return an image as a PhotoImage object
    :param path: A string representing the path of the image file
    :param width: The width of the image to resize to
    :param height: The height of the image to resize to
    :return: The image represented as a PhotoImage object
    """
    img = Image.open(path)
    img = img.resize((width, height), Image.BICUBIC)

    return ImageTk.PhotoImage(img)