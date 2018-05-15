import face_recognition, os, sys, time, csv
from tqdm import tqdm
from PIL import Image
from shutil import copyfile
from multiprocessing import Process, Pool, cpu_count
from mongocommands import *
import gc,random, pickle
from celery import Celery

# ---------------------------------------------------#

address = "raspberrypi5-umh.cs.umn.edu"                             # Replace with RabbitMQ Instance IP Address
broker_url = 'amqp://username:password@'+address+':5672/myvhost'    # Replace username and password with RabbitMQ username and RabbitMQ password
backend_url = 'rpc://username:password@'+address+':5672/myvhost'    # Replace username and password with RabbitMQ username and RabbitMQ password

app = Celery('tasks',backend=backend_url, broker=broker_url)

# ---------------------------------------------------#
''' 
    Automatically saves any found face into a folder. 
    Naming convention is [x][photoID].jpg (ie 01138, 11138, 21138)
'''
@app.task
def save_find_faces(filename):      # Detecting, Processing and Sending the processed face data back to mongodb
    get_file_mongo(filename,'photo')


    y = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(y,model='hog')
    y = face_recognition.face_encodings(y,face_locations)

    img = Image.open(filename)
    counter = 0
    img2 = ""
    for x in face_locations:
        img2 = img.crop((x[3],x[0],x[1],x[2]))
        new_filename = str(counter)+filename
        img2.save(new_filename)
        send_file_mongo(new_filename,new_filename,'faces')
        
        c = open(new_filename+'.dat','wb')
        pickle.dump(y[counter],c)
        c.close()

        send_file_mongo(new_filename+'.dat',new_filename+'.dat','meta')

        os.remove(new_filename+'.dat')
        os.remove(new_filename)
        counter += 1

    print ("Successfully Completed File "+filename)
    del img
    del y
    os.remove(filename)
    gc.collect()
            
# ---------------------------------------------------#

def line_split(N, K=1):         # Split array N into K halves
    length = len(N)
    return [N[i*length/K:(i+1)*length/K] for i in range(K)]

# ---------------------------------------------------#

@app.task
def compare_all_faces():        # Comparing and detecting similarity in faces in all processed faces available in MongoDB
    try:
        # Initializing Variables and Data Types
        data,names= [],[]

        # Process all files in nonclustered
        available_files = list_directory_mongo('meta')

        print ("")
        print ("== Comparing Faces ==")
        print ("")
        print ("-------------------------------Getting Faces------------------------")
        get_all_images_mongo('meta/','meta')
        print ("-------------------------------Encoding Faces------------------------")
        
        # Encoding all files to memory
        for x in tqdm(range(len(available_files))):
            data.append(pickle.load(open('./meta/'+available_files[x],'rb')))
            names.append(available_files[x][:-4])


        gc.collect()
        
        # Comparing the encoded files
        print ("-------------------------------Comparing Faces------------------------")
        for y in tqdm(range(len(data))):
            for z in range(y+1, len(data)):    
                try:
                    results = face_recognition.face_distance([data[y]], data[z]) 
                    store_comparision_value(names[y],names[z],results[0])
                except:
                    pass
        # Removing Bad Face Encoded Files
        print "DONE WITH EVERYTHING"
    except:
        print ("Found Error, Crash Error Code 103")
        return -1

# ---------------------------------------------------#

def check_exist(branch,file1):      # Check existence of file1 in subset of branch
    for x in branch:
        if file1 in x:
            return True
    return False

# ---------------------------------------------------#

def check_existance(branch,to_search1,to_search2):      # Check existence of to_search1 or to_search2 in subset of branch
    for x in range(len(branch)):
        if to_search1 in branch[x] or to_search2 in branch[x]:
            return (x)
    return (-1)

# ---------------------------------------------------#