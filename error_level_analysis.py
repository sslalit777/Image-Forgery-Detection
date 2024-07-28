import numpy as np
from PIL import Image,ImageChops
from datetime import datetime
import os

def detect(input_path,output_path, filename):
    
    image = os.path.join(input_path, filename)
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    TEMP = f'temp/temp_{current_time}.jpg'
    SCALE = 10
    
    original = Image.open(image)
    original.save(TEMP, quality=90)
    temporary = Image.open(TEMP)

    diff = ImageChops.difference(original, temporary)
    d = diff.load()
    WIDTH, HEIGHT = diff.size
    for x in range(WIDTH):
        for y in range(HEIGHT):
            d[x, y] = tuple(k * SCALE for k in d[x, y])

    diff.save(os.path.join(output_path, filename))
    return True