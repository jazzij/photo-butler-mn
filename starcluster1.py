# Import Statements
from PhotoProject_distributed import compare_faces, compare_all_faces
from mongocommands import *
from celery.result import AsyncResult
import os, time


compare_all_faces.delay()
'''
# Intializing
task = []
task_status = []


# Sending Tasks to Cluster (Save Find Faces)
file_directory = list_directory_mongo('faces')
for x in range(len(file_directory)):
    z = compare_faces.delay(x)
    task.append(z)
        
print ("Tasks Submitted to Cluster")

# Checking for Completion

task_status = [x.ready() for x in task]
while False in task_status:
    time.sleep(15)
    print task_status.count(False)
    task_status = [x.ready() for x in task]

print ("Completed Processing Images")
'''