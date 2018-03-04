import face_recognition, os, sys, time, csv
from tqdm import tqdm
from PIL import Image
from shutil import copyfile
from multiprocessing import Process, Pool

class PhotoProject:
    
    def __init__(self):
        try:
            print ("")
            print ("Modules Successfully Imported")
        except:
            print ("")
            print ("Import Error")
    


    def save_find_faces(self,filename, accessor=""):
        if type(filename)=="str":
            filename = [filename]
        for z in (filename):
            image = face_recognition.load_image_file(accessor+z)
            face_locations = face_recognition.face_locations(image, model="hog")
            img = Image.open(accessor+z)
            counter = 0
            z = z.split('/')[-1]

            for x in face_locations:
                img2 = img.crop((x[3],x[0],x[1],x[2]))
                img2.save('faces/nonclustered/'+str(counter)+z)
                counter += 1
            


    def save_find_faces_all(self):
        start_time = time.time()

        print ("")
        print ("== Detecting Faces in Images ==")
        print ("")
        pool = []
        dat = (os.listdir("./pictures"))
        chunk1 = dat[:len(dat)/2]
        chunk2 = dat[len(dat)/2:]
        chunk3 = chunk1[:len(chunk1)/2]
        chunk4 = chunk2[:len(chunk2)/2]
        chunk1 = chunk1[len(chunk1)/2:]
        chunk2 = chunk2[len(chunk2)/2:]            
        p1 = Process(target=self.save_find_faces, args=(chunk1,"./pictures/",))
        p2 = Process(target=self.save_find_faces, args=(chunk2,"./pictures/",))
        p3 = Process(target=self.save_find_faces, args=(chunk3,"./pictures/",))
        p4 = Process(target=self.save_find_faces, args=(chunk4,"./pictures/",))
        p1.start()
        p2.start()
        p3.start()
        p4.start()
        print ("Processing Started")
        p1.join()
        p2.join()
        p3.join()
        p4.join()
        print ("Successfully Identified Faces")
        print("--- %s seconds ---" % (time.time() - start_time))
        print ("")



    def compare_faces(self,face1,face2):
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
                return (x)
        return (-1)



    def compare_all_faces(self):
        start_time = time.time()
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
        print("--- %s seconds ---" % (time.time() - start_time))
        print ("")
        


    def check_exist(self,branch,file1):
        for x in branch:
            if file1 in x:
                return True
        return False



    def cluster_faces(self,threshold=0.5):
        ifile  = open('facedata.csv', "rb")
        writer = csv.reader(ifile)
        branch = []

        for x in writer:
            try:
                if float(x[-1]) <= threshold:
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
