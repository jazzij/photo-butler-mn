from tasks import save_find_faces
from AWSS3 import *

dataset = []
for x in list_directory_s3('pictures'):
    save_find_faces.delay(x)
