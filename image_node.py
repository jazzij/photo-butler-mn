from tasks import save_find_faces
from AWSS3 import *

dataset = []
for x in list_directory_s3('pictures'):
    save_find_faces.delay(x)
    break

while True:
    print ('PROCESSING')
    flag = 0
    for x in dataset:
        if x.ready():
            flag = 1
        else:
            flag = 0
        break
    break
    if flag == 1:
        print 'Images Classified'
        break

