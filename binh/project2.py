import os
import face_recognition
def or_operator():
    picture = input("Enter the name of the file: ")
    im = face_recognition.load_image_file(picture)
    original_img = face_recognition.face_encodings(im)
    res = []
    for i in original_img:
        for j in os.listdir():
            if j != "project2.py":
                img = face_recognition.load_image_file(j)
                img_encoding = face_recognition.face_encodings(img)
                result = face_recognition.compare_faces(img_encoding,i)
                if True in result:
                    if not j in res:
                        res.append(j)
    return res
def not_operator():
    picture = input("Enter the name of the file: ")
    im = face_recognition.load_image_file(picture)
    original_img = face_recognition.face_encodings(im)
    res = []
    for i in original_img:
        for j in os.listdir():
            if j != "project2.py":
                img = face_recognition.load_image_file(j)
                img_encoding = face_recognition.face_encodings(img)
                result1 = face_recognition.compare_faces(img_encoding,original_img[0])
                result2 = face_recognition.compare_faces(img_encoding,i)
                if True in result1:
                    if not True in result2:
                        if not j in res:
                            res.append(j)
    return res
