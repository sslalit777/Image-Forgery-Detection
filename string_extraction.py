import numpy as np
from PIL import Image,ImageChops
from datetime import datetime
from prettytable import PrettyTable
import os

def detect(input_path,output_path, filename):
    
    image = os.path.join(input_path, filename)
    x=PrettyTable()
    x.field_names = ["Bytes", "8-bit", "string"]
    # x.border = False
    with open(image, "rb") as f:
            n = 0
            b = f.read(16)

            while b:
                s1 = " ".join([f"{i:02x}" for i in b])  # hex string
                # insert extra space between groups of 8 hex values
                s1 = s1[0:23] + " " + s1[23:]

                # ascii string; chained comparison
                s2 = "".join([chr(i) if 32 <= i <= 127 else "." for i in b])

                # print(f"{n * 16:08x}  {s1:<48}  |{s2}|")
                x.add_row([f"{n * 16:08x}",f"{s1:<48}",f"{s2}"])

                n += 1
                b = f.read(16)

            return "<pre>"+str(x)+"</pre>"