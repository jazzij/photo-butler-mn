from tasks import save_find_faces
from os import listdir
import time

dataset = []
for x in listdir('./pictures/'):
    save_find_faces.delay('pictures/'+x)

while True:
    print ('PROCESSING')
    flag = 0
    for x in dataset:
        if x.ready():
            flag = 1
        else:
            flag = 0
            break
    if flag == 1:
        print 'Images Classified'
        break
