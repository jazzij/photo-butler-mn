import face_recognition
from os import listdir

import csv


ifile  = open('facedata.csv', "wb")
writer = csv.writer(ifile)
writer.writerow(['Picture1','Picture2','Distance'])

good = 0
bad = 0
badfiles = []
a = listdir('./faces')
for x in range(len(a)):
    for y in range(x,len(a)):
        if a[x] == a[y] or a[x] in badfiles or a[y] in badfiles:
            pass
        else:
            try:
                picture_of_me = face_recognition.load_image_file('./faces/'+a[x])
            except:
                badfiles.append(a[x])

            try:  
                unknown_picture = face_recognition.load_image_file('./faces/'+a[y])
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
                print [a[x],a[y],results[0]]

                good += 1            
            except:
                bad += 1
            
            #print good, bad, good/float(good+bad)*100
            #print badfiles
print good, bad
