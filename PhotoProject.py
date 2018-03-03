import face_recognition
import os
import sys
import csv
from tqdm import tqdm
from PIL import Image
from shutil import copyfile
from multiprocessing import Process
from multiprocessing import Pool
class PhotoProject:
    
    def __init__(self):
        try:
            print ("")
            print ("Modules Successfully Imported")
        except:
            print ("")
            print ("Import Error")
    
    def save_find_faces(self,filename, accessor=""):
        image = face_recognition.load_image_file(accessor+filename)
        face_locations = face_recognition.face_locations(image, model="hog")
        img = Image.open(accessor+filename)
        counter = 0
        filename = filename.split('/')[-1]

        for x in face_locations:
            img2 = img.crop((x[3],x[0],x[1],x[2]))
            img2.save('faces/nonclustered/'+str(counter)+filename)
            counter += 1
            
    def save_find_faces_all(self):
        print ("")
        print ("== Detecting Faces in Images ==")
        print ("")
        pool = []
        print ("Distributing Processes")
        for x in tqdm(os.listdir("./pictures")):
            p = Process(target=self.save_find_faces, args=(x,"./pictures/",))
            p.start()
            pool.append(p)
        print ("Processing Images")
        for x in tqdm(pool):
            x.join()

    def compare_faces(self,face1, face2):
        try:
            picture_of_me = face_recognition.load_image_file('./faces/nonclustered/'+face1)
            my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
        except:
            print ("Error Loading Image 1")
            sys.exit()
        try:         
            unknown_picture = face_recognition.load_image_file('./faces/nonclustered/'+face2)
            unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]
        except:
            print ("Error Loading Image 2")
            sys.exit()

        results = face_recognition.face_distance([my_face_encoding], unknown_face_encoding) 
        return results[0]
    
    def check_existance(self,branch,to_search1,to_search2):
        for x in range(len(branch)):
            if to_search1 in branch[x] or to_search2 in branch[x]:
                return x
        return -1

    def compare_all_faces(self):
        ifile  = open('facedata.csv', "wb")
        writer = csv.writer(ifile)
        writer.writerow(['Picture1','Picture2','Distance'])
        data = []
        names = []
        bad = []
        a = os.listdir('./faces/nonclustered/')
        print ("")
        print ("== Comparing Faces ==")
        print ("")
        print ("Encoding Faces")
        for x in tqdm(range(len(a))):
            try:
                picture_of_me =  face_recognition.load_image_file('./faces/nonclustered/'+a[x])
                data.append(face_recognition.face_encodings(picture_of_me)[0])
                names.append(a[x])
            except:
                bad.append(a[x])
        print ("Comparing Faces")
        for y in tqdm(range(len(data))):
            for z in range(y+1, len(data)):    
                try:
                    results = face_recognition.face_distance([data[y]], data[z]) 
                    writer.writerow([names[y],names[z],str(results[0])])
                except:
                    continue
        for x in bad:
            os.remove("./faces/nonclustered/"+x)


    def check_exist(self,branch,file1):
        for x in branch:
            if file1 in x:
                return True
        return False

    def cluster_faces(self):
        ifile  = open('facedata.csv', "rb")
        writer = csv.reader(ifile)
        branch = []

        for x in writer:
            try:
                if float(x[-1]) <= 0.5:
                    tag = self.check_existance(branch,x[0],x[1])

                    if tag >= 0:
                        if x[0] in branch[tag]:
                            branch[tag].append(x[1])
                        elif x[1] in branch[tag]:
                            branch[tag].append(x[0])
                    else:
                        branch.append([x[0],x[1]])
            except:
                pass

        counter = 0
        print (branch)
        for x in branch:
            if str(counter) in os.listdir("./faces/clustered/"):
                pass
            else:
                os.mkdir("./faces/clustered/"+str(counter))
            for y in x:
                copyfile("./faces/nonclustered/"+y, "./faces/clustered/"+str(counter)+"/"+y)
            counter += 1

        for y in os.listdir('./faces/nonclustered/'):
            if self.check_exist(branch,y):
                pass
            else:
                if str(counter) in os.listdir("./faces/clustered/"):
                    pass
                else:
                    os.mkdir("./faces/clustered/"+str(counter))
                copyfile("./faces/nonclustered/"+y, "./faces/clustered/"+str(counter)+"/"+y)
                counter += 1
