import numpy as np
import cv2
import random
import os

def detect(input_path,output_path, filename):
    
    image = os.path.join(input_path, filename)
    
    # Encrypted image
    img = cv2.imread(image)
    width = img.shape[0]
    height = img.shape[1]
    
    # img1 and img2 are two blank images
    img1 = np.zeros((width, height, 3), np.uint8)
    img2 = np.zeros((width, height, 3), np.uint8)
    
    for i in range(width):
        for j in range(height):
            for l in range(3):
                v1 = format(img[i][j][l], '08b')
                v2 = v1[:4] + chr(random.randint(0, 1)+48) * 4
                v3 = v1[4:] + chr(random.randint(0, 1)+48) * 4
                
                # Appending data to img1 and img2
                img1[i][j][l]= int(v2, 2)
                img2[i][j][l]= int(v3, 2)

    cv2.imwrite(os.path.join(output_path, filename), img2)
    return True