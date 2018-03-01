import face_recognition
import os
import csv
from PIL import Image
from AWSS3 import *

## Distributed Systems? - YES
## Single Node? - YES
## Return to Master Node? - NO
## Note - Generates a Folder faces, which has all cropped faces
def save_find_faces(filename):
    image = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(image)
    img = Image.open(filename)
    counter = 0
    filename = filename.split('/')[-1]

    for x in face_locations:
        img2 = img.crop((x[3],x[0],x[1],x[2]))
        img2.save('faces/'+str(counter)+filename)
        print send_file_s3('faces/'+str(counter)+filename,str(counter)+filename,'faces/')
        os.remove('faces/'+str(counter)+filename)
        counter += 1

## Distributed Systems? - YES
## Single Node? - YES
## Return to Master Node? - YES (List of Bad Files)
## Notes - This reads all files in AWS S3 faces folder
def compare_faces(indexlocation):
    ifile  = open('facedata.csv', "wb")
    writer = csv.writer(ifile)
    writer.writerow(['Picture1','Picture2','Distance'])
    badfiles = []
    a = [x.split('/')[-1] for x in list_directory_s3('faces')][1:]
    x = indexlocation
    for y in range(indexlocation,len(a)):
        if a[x] == a[y] or a[x] in badfiles or a[y] in badfiles:
            pass
        else:
            try:
                if len(a[x]) > 0:
                    if a[x] not in os.listdir('./faces'):
                        get_file_s3('faces/'+a[x])
                    picture_of_me = face_recognition.load_image_file('./faces/'+a[x])
            except:
                badfiles.append(a[x])

            try:
                if len(a[y]) > 0:
                    if a[y] not in os.listdir('./faces'):
                        get_file_s3('faces/'+a[y])
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
            results = face_recognition.face_distance([my_face_encoding], unknown_face_encoding) 
            writer.writerow([a[x],a[y],str(results[0])])
            print [a[x],a[y],results[0]]
    return badfiles


def main():
    picture_count = 0
    for x in listdir('./pictures/'):
        #save_find_faces('pictures/'+x)
        print 'Completed Picture #'+str(picture_count)
        picture_count += 1
    #print 'Saved ALL'
    compare_faces(0)
main()

