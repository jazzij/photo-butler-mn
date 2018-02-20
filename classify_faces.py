import face_recognition
from os import listdir

good = 0
bad = 0
badfiles = []
for x in listdir('./faces'):
    for y in listdir('./faces'):
        if x == y or x in badfiles or y in badfiles:
            pass
        else:
            try:
                picture_of_me = face_recognition.load_image_file('./faces/'+x)
            except:
                badfiles.append(x)

            try:  
                unknown_picture = face_recognition.load_image_file('./faces/'+y)
            except:
                badfiles.append(y)
                break
            
            try:
                my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
            except:
                badfiles.append(x)

            try:
                unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]
            except:
                badfiles.append(y)
                break
            try:
                results = face_recognition.compare_faces([my_face_encoding], unknown_face_encoding)    
                good += 1            
            except:
                bad += 1
            
            print good, bad, good/float(good+bad)*100
            print badfiles
print good, bad
