import dlib, os, sys, time, csv
import face_recognition
from tqdm import tqdm
from PIL import Image
from shutil import copyfile
from multiprocessing import Process, Pool, cpu_count
from collections import OrderedDict

# ---------------------------------------------------#

class PhotoProject:
    
# ---------------------------------------------------#
    
    def __init__(self):
        try:
            print ("")
            print ("Modules Successfully Imported")
        except:
            print ("")
            print ("Import Error")
	
# ---------------------------------------------------#
    
    def save_find_faces(self,filename):
        try:
            boxes=[]
            area_ratio=[]
            image = face_recognition.load_image_file(filename)
            face_locations = face_recognition.face_locations(image)
            img = Image.open(filename)
            #get width and height of entire image
            pic_width, pic_height = img.size
            #get width and height of ea face
            for x in face_locations:
                top, right, bottom, left = x
                height = bottom-top
                width = right-left
                boxes.append(height*width)
            #compute the average
            average_face = sum(boxes)/len(boxes)
            area_ratio.append(average_face/(pic_width*pic_height))
            counter = 0
            filename = filename.split('/')[-1]
            
            for x in face_locations:
                img2 = img.crop((x[3],x[0],x[1],x[2]))
                img2.save('faces/'+str(counter)+filename)
                counter += 1
            return True
        except:
            print("Found Error, Crash Error Code 100")
            return False
                      
# ---------------------------------------------------#

    def line_split(self, N, K=1):
        length = len(N)
        return [N[i*length/K:(i+1)*length/K] for i in range(K)]

# ---------------------------------------------------#

    def save_find_faces_all(self):
        try:
            print ("")
            print ("== Detecting Faces in Images ==")
            print ("")
            pool = []
            dat = (os.listdir("./pictures"))
            chunked = self.line_split(dat,cpu_count()-1)
            for y in chunked:         
                p1 = Process(target=self.save_find_faces, args=(y,"./pictures/",))
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
	
    def compare_faces(self,face1,face2):
        try:
            try:
                picture_of_me = face_recognition.load_image_file('./faces/nonclustered/'+face1)
                my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
            except:
                print ("Error Loading Image 1")
                return -1
            try:         
                unknown_picture = face_recognition.load_image_file('./faces/nonclustered/'+face2)
                unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]
            except:
                print ("Error Loading Image 2")
                return -1
            results = face_recognition.face_distance([my_face_encoding], unknown_face_encoding) 
            return results[0]
        except:
            print ("Found Error, Crash Error Code 102")
            return -1

# ---------------------------------------------------#

    def compare_all_faces(self):
        try:
            # Initializing Variables and Data Types
            ifile  = open('facedata.csv', "wb")
            writer = csv.writer(ifile)
            data,names,badfiles = [],[],[]

            # Writing Initial Row to CSV
            writer.writerow(['Picture1','Picture2','Distance'])

            # Process all files in nonclustered
            available_files = os.listdir('./faces/nonclustered/')

            print ("")
            print ("== Comparing Faces ==")
            print ("")
            print ("Encoding Faces")

            # Encoding all files to memory
            for x in tqdm(range(len(available_files))):
                try:
                    image_file =  face_recognition.load_image_file('./faces/nonclustered/'+available_files[x])
                    data.append(face_recognition.face_encodings(image_file)[0])
                    names.append(available_files[x])
                except:
                    badfiles.append(available_files[x])
            
            # Comparing the encoded files
            print ("Comparing Faces")
            for y in tqdm(range(len(data))):
                for z in range(y+1, len(data)):    
                    try:
                        results = face_recognition.face_distance([data[y]], data[z]) 
                        writer.writerow([names[y],names[z],str(results[0])])
                    except:
                        continue
            print ("Number of Bad Faces ", len(badfiles))
            # Removing Bad Face Encoded Files
            for x in badfiles:
                os.remove("./faces/nonclustered/"+x)

        except:
            print ("Found Error, Crash Error Code 103")
            return -1

# ---------------------------------------------------#

    def check_exist(self,branch,file1):
        for x in branch:
            if file1 in x:
                return True
        return False

# ---------------------------------------------------#

    def check_existance(self,branch,to_search1,to_search2):
        for x in range(len(branch)):
            if to_search1 in branch[x] or to_search2 in branch[x]:
                return (x)
        return (-1)

# ---------------------------------------------------#

    def cluster_faces(self,threshold=0.45):
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
                        tag = self.check_existance(branch,x[0],x[1])   # Checking Existance in any pre-existing branch
                        if tag >= 0:
                            if x[0] in branch[tag]:
                                if self.check_exist(branch,x[1])==False:
                                    branch[tag].append(x[1])
                            elif x[1] in branch[tag]:
                                if self.check_exist(branch,x[0])==False:
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
                if self.check_exist(branch,y)==False:
                    if str(folder_id) not in os.listdir("./faces/clustered/"):
                        os.mkdir("./faces/clustered/"+str(folder_id))
                    copyfile("./faces/nonclustered/"+y, "./faces/clustered/"+str(folder_id)+"/"+y)
                    folder_id += 1
                
        except:
            print ("Found Error, Crash Error Code 104")
            return -1
        
# ---------------------------------------------------#
