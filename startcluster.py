# Import Statements
from PhotoProject_distributed import save_find_faces
from mongocommands import *
from celery.result import AsyncResult
import os, time

# Intializing
task = []
task_status = []

# Sending Tasks to Cluster (Save Find Faces)

for x in list_directory_mongo('photo'):
    if x != '.DS_Store':
        z = save_find_faces.delay(x)
        task.append(z)
        
print ("Tasks Submitted to Cluster")

# Checking for Completion

task_status = [x.ready() for x in task]
while False in task_status:
    print task_status.count(False)
    task_status = [x.ready() for x in task]
    time.sleep(4)

print ("Completed Processing Images")
