from flask import jsonify
import numpy as np
import cv2
import random
import os
from PIL import ImageTk, Image, ExifTags, ImageChops

def detect(input_path,output_path, filename):
    
    image = os.path.join(input_path, filename)
    
    if image is None:
        return False

    img = Image.open(image)
    img_exif = img.getexif()
    
    print(img)
    print(img_exif)

    if img_exif is None:
        return False
    else:
        html_content = ''
        for key, val in img_exif.items():
            if key in ExifTags.TAGS:
                html_content += f'<p><strong>{ExifTags.TAGS[key]}</strong>: {val}</p>'
        return html_content

