# Import Statements
from PhotoProject_distributed import compare_faces, compare_all_faces
from mongocommands import *
from celery.result import AsyncResult
import os, time



# Intializing
task = []
task_status = []


# Sending Tasks to Cluster (Save Find Faces)
task.append(compare_all_faces.delay())
        
print ("Tasks Submitted to Cluster")

# Checking for Completion

task_status = [x.ready() for x in task]
while False in task_status:
    time.sleep(3)
    print task_status.count(False)
    task_status = [x.ready() for x in task]

print ("Completed Processing Images")
