import face_recognition
import os
import sys
import csv
from PIL import Image


class PhotoProject:
    
    def __init__(self):
        try:
            print ("Modules Successfully Imported")
        except:
            print ("Import Error")
    """ Automatically saves any found face into a folder. Naming convention is [x][photoID].jpg (ie 01138, 11138, 21138)
    """
    def save_find_faces(self,filename):
        image = face_recognition.load_image_file(filename)
        face_locations = face_recognition.face_locations(image)
        img = Image.open(filename)
        counter = 0
        filename = filename.split('/')[-1]

        for x in face_locations:
            img2 = img.crop((x[3],x[0],x[1],x[2]))
            img2.save('faces/'+str(counter)+filename)
            counter += 1
    
    """ Compare distance between two faces to see if its the same person. .500 is optimal threshold (per face rec library, referencing MIT algorithm)
        Below .5 means its the same person, and above means its not. 
    """
    def compare_faces(self,face1, face2):
        try:
            picture_of_me = face_recognition.load_image_file('./faces/'+face1)
        except:
            print ("Error Loading Image 1")
            sys.exit()
        

        try:        
            unknown_picture = face_recognition.load_image_file('./faces/'+face2)
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
