from PhotoProject_distributed import save_find_faces
from mongocommands import *
import os

send_all_images_mongo('pictures','photo')
#for x in os.listdir('pictures'):
#    if x != '.DS_Store':
#        save_find_faces.delay(x)