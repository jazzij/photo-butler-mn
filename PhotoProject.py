import face_recognition
import os
import sys
import csv
from tqdm import tqdm
from PIL import Image
from shutil import copyfile

class PhotoProject:
    
    def __init__(self):
        try:
            print ("Modules Successfully Imported")
        except:
            print ("Import Error")
    
    def save_find_faces(self,filename):
        image = face_recognition.load_image_file(filename)
        face_locations = face_recognition.face_locations(image)
        img = Image.open(filename)
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
        for x in tqdm(os.listdir("./pictures")):
            image = face_recognition.load_image_file("./pictures/"+x)
            face_locations = face_recognition.face_locations(image)
            img = Image.open("./pictures/"+x)
            counter = 0
            filename = x.split('/')[-1]

            for x in face_locations:
                img2 = img.crop((x[3],x[0],x[1],x[2]))
                img2.save('faces/nonclustered/'+str(counter)+filename)
                counter += 1
            #print ("Successfully Found Faces in "+x)

    def compare_faces(self,face1, face2):
        try:
            picture_of_me = face_recognition.load_image_file('./faces/nonclustered/'+face1)
        except:
            print ("Error Loading Image 1")
            sys.exit()
        

        try:        
            unknown_picture = face_recognition.load_image_file('./faces/nonclustered/'+face2)
        except:
            print ("Error Loading Image 2")
            sys.exit()


        try:
            my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
        except:
            print ("Error Encoding Image 1")
            sys.exit()


        try:
            unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]
        except:
            print ("Error Encoding Image 2")
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

        good = 0
        bad = 0
        badfiles = []
        a = os.listdir('./faces/nonclustered/')
        print ("")
        print ("== Comparing Faces ==")
        print ("")
        for x in tqdm(range(len(a))):
            for y in range(x,len(a)):
                if a[x] == a[y] or a[x] in badfiles or a[y] in badfiles or a[x] == "clustered" or a[y] == "clustered":
                    pass
                else:
                    try:
                        picture_of_me = face_recognition.load_image_file('./faces/nonclustered/'+a[x])
                    except:
                        badfiles.append(a[x])

                    try:  
                        unknown_picture = face_recognition.load_image_file('./faces/nonclustered/'+a[y])
                    except:
                        badfiles.append(a[y])
                        break
                    
                    try:
                        my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
                    except:
                        badfiles.append(a[x])

                    try:
                        unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]
                    except:
                        badfiles.append(a[y])
                        break
                    try:
                        results = face_recognition.face_distance([my_face_encoding], unknown_face_encoding) 
                        writer.writerow([a[x],a[y],str(results[0])])
                        good += 1            
                    except:
                        bad += 1
            #print ("Successfully Processed Image #"+str(x))

        print (badfiles)
        for x in badfiles:
            os.remove("./faces/nonclustered/"+x)


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
