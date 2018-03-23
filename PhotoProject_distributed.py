import face_recognition, os, sys, time, csv
from tqdm import tqdm
from PIL import Image
from shutil import copyfile
from multiprocessing import Process, Pool, cpu_count
from mongocommands import *
import gc,random
from celery import Celery

# ---------------------------------------------------#

address = "raspberrypi1-umh.cs.umn.edu"
broker_url = 'amqp://prateek:Welcome123@'+address+':5672/myvhost'
backend_url = 'rpc://prateek:Welcome123@'+address+':5672/myvhost'

app = Celery('tasks',backend=backend_url, broker=broker_url)

# ---------------------------------------------------#
''' 
    Automatically saves any found face into a folder. 
    Naming convention is [x][photoID].jpg (ie 01138, 11138, 21138)
'''
@app.task
def save_find_faces(filename):
    get_file_mongo(filename,'photo')
    image = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(image)
    img = Image.open(filename)
    counter = 0
    img2 = ""
    for x in face_locations:
        img2 = img.crop((x[3],x[0],x[1],x[2]))
        new_filename = str(counter)+filename
        img2.save(new_filename)
        send_file_mongo(new_filename,new_filename,'faces')
        os.remove(new_filename)
        counter += 1
    print ("Successfully Completed File "+filename)
    os.remove(filename)
    del image
    del face_locations
    del img
    del img2
    gc.collect()
            
# ---------------------------------------------------#

def line_split(N, K=1):
    length = len(N)
    return [N[i*length/K:(i+1)*length/K] for i in range(K)]

# ---------------------------------------------------#
def save_find_faces_all():
    try:
        print ("")
        print ("== Detecting Faces in Images ==")
        print ("")
        pool = []
        dat = (os.listdir("./pictures"))
        chunked = line_split(dat,cpu_count()-1)
        for y in chunked:         
            p1 = Process(target=save_find_faces, args=(y,"./pictures/",))
            pool.append(p1)
        for y in pool:
            y.start()
        print ("Processing Started")
        for y in pool:
            y.join()
        print ("Successfully Identified Faces")
        print ("")
        return True
    except:
        print ("Found Error, Crash Error Code 101")
        return False

# ---------------------------------------------------#

''' 
    Compare distance between two faces to see if its the same person. 
    .45 is optimal threshold (per face rec library, referencing CMU OpenFace algorithm)
    Below .45 means its the same person, and above means its not. 
'''
@app.task
def compare_faces(index):
    try:
        file_directory = list_directory_mongo('faces')
        bad_pics = get_list_bad_mongo()
        stored = os.listdir('./')

        face1 = file_directory[index]
        if face1 not in bad_pics:
            try:
                if face1 not in stored:
                    get_file_mongo(face1,'faces')

                picture_of_me = face_recognition.load_image_file(face1)
                my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]

            except:
                remove_image_mongo(face1,'faces')
                return "Face1 is bad", face1

        else:
            return "Face1 is bad", face1

        for y in tqdm(range(index+1,len(file_directory))):
            bad_pics = get_list_bad_mongo()
            face2 = file_directory[y]

            if face2 not in bad_pics:
                try:
                    if face2 not in stored:
                        get_file_mongo(face2,'faces')
                    unknown_picture = face_recognition.load_image_file(face2)
                    unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]
                except:
                    remove_image_mongo(face2,'faces')
                    #print ("Face2 is bad", face2)
                    continue
            else:
                #print ("Face2 is bad", face2)
                continue
            results = face_recognition.face_distance([my_face_encoding], unknown_face_encoding) 
            store_comparision_value(face1,face2,results[0])
            #print "Successfully Completed Files "+ face1+" "+face2

    except Exception as e:
        print (e)
        print ("Found Error, Crash Error Code 102")

# ---------------------------------------------------#
@app.task
def compare_all_faces():
    try:
        # Initializing Variables and Data Types
        data,names= [],[]

        # Process all files in nonclustered
        available_files = list_directory_mongo('faces')

        print ("")
        print ("== Comparing Faces ==")
        print ("")
        print ("-------------------------------Getting Faces------------------------")
        get_all_images_mongo('faces/','faces')
        print ("-------------------------------Encoding Faces------------------------")
        # Encoding all files to memory
        for x in tqdm(range(len(available_files))):
            try:
                image_file =  face_recognition.load_image_file('./faces/'+available_files[x])
                data.append(face_recognition.face_encodings(image_file)[0])
                names.append(available_files[x])
            except:
                remove_image_mongo(x,'faces')
        gc.collect()
        # Comparing the encoded files
        print ("-------------------------------Comparing Faces------------------------")
        for y in tqdm(range(len(data))):
            for z in range(y+1, len(data)):    
                try:
                    results = face_recognition.face_distance([data[y]], data[z]) 
                    store_comparision_value(names[y],names[z],results[0])
                except:
                    continue
        # Removing Bad Face Encoded Files
        print "DONE WITH EVERYTHING"
    except:
        print ("Found Error, Crash Error Code 103")
        return -1

# ---------------------------------------------------#

def check_exist(branch,file1):
    for x in branch:
        if file1 in x:
            return True
    return False

# ---------------------------------------------------#

def check_existance(branch,to_search1,to_search2):
    for x in range(len(branch)):
        if to_search1 in branch[x] or to_search2 in branch[x]:
            return (x)
    return (-1)

# ---------------------------------------------------#

def cluster_faces(threshold=0.45):
    try:
        # Initializing Variables and Data Types
        ifile  = open('facedata.csv', "rb")
        writer = csv.reader(ifile)
        branch = []
        folder_id = 0

        # Iterating through CSV File
        for x in writer:
            try:
                if float(x[-1]) <= threshold:       # Evaluating Face Distance with Threshold
                    tag = check_existance(branch,x[0],x[1])   # Checking Existance in any pre-existing branch
                    if tag >= 0:
                        if x[0] in branch[tag]:
                            if check_exist(branch,x[1])==False:
                                branch[tag].append(x[1])
                        elif x[1] in branch[tag]:
                            if check_exist(branch,x[0])==False:
                                branch[tag].append(x[0])
                    else:
                        branch.append([x[0],x[1]])
            except:
                pass


        # Sorting Facial Images with Existing Branch Classifications
        for x in branch:
            if str(folder_id) in os.listdir("./faces/clustered/"):
                pass
            else:
                os.mkdir("./faces/clustered/"+str(folder_id))
            for y in x:
                copyfile("./faces/nonclustered/"+y, "./faces/clustered/"+str(folder_id)+"/"+y)
            folder_id += 1


        # Generating Branches for Independent Facial Images
        for y in os.listdir('./faces/nonclustered/'):
            if check_exist(branch,y)==False:
                if str(folder_id) not in os.listdir("./faces/clustered/"):
                    os.mkdir("./faces/clustered/"+str(folder_id))
                copyfile("./faces/nonclustered/"+y, "./faces/clustered/"+str(folder_id)+"/"+y)
                folder_id += 1
            
    except:
        print ("Found Error, Crash Error Code 104")
        return False
        
# ---------------------------------------------------#