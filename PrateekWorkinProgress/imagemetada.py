
def imageMeta(filename):

from PIL import Image 
from PIL.ExifTags import TAGS, GPSTAGS 
image = Image.open("IMG_1688.JPG") 
print(image) 
info = image._getexif() 
for tag, value in info.items(): 
    key = TAGS.get(tag, tag) 
    print(str(key) + " " + str(value))