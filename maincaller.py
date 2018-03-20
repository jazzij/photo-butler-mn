from PhotoProject_distributed import save_find_faces
from mongocommands import *
from celery.result import AsyncResult
import os
task = []
task_status = []

#send_all_images_mongo('pictures','photo')
for x in list_directory_mongo('photo'):
    if x != '.DS_Store':
        z = save_find_faces.delay(x)
        task.append(z)
print ("Tasks Submitted to Cluster")
task_status = [x.ready() for x in task]
while False in task_status:
    task_status = [x.ready() for x in task]
print "DONE"