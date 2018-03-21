# Import Statements
from PhotoProject_distributed import compare_faces
from mongocommands import *
from celery.result import AsyncResult
import os, time


# Intializing
task = []
task_status = []


# Sending Tasks to Cluster (Save Find Faces)
file_directory = list_directory_mongo('faces')
for x in range(len(file_directory)):
    for y in range(x+1, len(file_directory)):
            z = compare_faces.delay(file_directory[x],file_directory[y])
            task.append(z)
        
print ("Tasks Submitted to Cluster")

# Checking for Completion

task_status = [x.ready() for x in task]
while False in task_status:
    time.sleep(15)
    print task_status.count(False)
    task_status = [x.ready() for x in task]

print ("Completed Processing Images")
