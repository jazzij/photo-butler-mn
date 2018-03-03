import face_recognition
import os
import sys
import csv
from tqdm import tqdm
from PIL import Image
from shutil import copyfile
from multiprocessing import Process
from multiprocessing import Pool

def compare_all_faces():
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
                    print "BROKEN"
        print bad
                
compare_all_faces()