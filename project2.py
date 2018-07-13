import os
import face_recognition
from shutil import copy
def or_operator(path,picture):
    img = face_recognition.load_image_file(path+picture)
    img_encoding = face_recognition.face_encodings(img)
    result_list = []
    for i in img_encoding:
        for j in os.listdir(path):
            if j != "project2.py":
                image = face_recognition.load_image_file(j)
                image_encoding = face_recognition.face_encodings(image)
                result = face_recognition.compare_faces(image_encoding,i)
                if True in result:
                    if not j in result_list:
                        result_list.append(j)
                        copy(path+j,path+"/or_operator/"+j)
    return result_list
def not_operator(path,picture):
    img = face_recognition.load_image_file(path+picture)
    img_encoding = face_recognition.face_encodings(img)
    result_list = []
    for i in img_encoding:
        for j in os.listdir(path):
            if j != "project2.py":
                image = face_recognition.load_image_file(j)
                image_encoding = face_recognition.face_encodings(image)
                result1 = face_recognition.compare_faces(image_encoding,original_img[0])
                result2 = face_recognition.compare_faces(image_encoding,i)
                if True in result1:
                    if not True in result2:
                        if not j in result_list:
                            result_list.append(j)
                            copy(path+j,path+"/not_operator/"+j)
    return result_list
def nested_operator(path,picture,operations):
    img = face_recognition.load_image_file(path+picture)
    img_encoding = face_recognition.face_encodings(img)
    result_list = []
    for i in os.listdir(path):
        if i != "project2.py":
            image = face_recognition.load_image_file(i)
            image_encoding = face_recognition.face_encodings(image)
            boolean_list = []
            final_boolean = True
            for j in img_encoding:
                result = face_recognition.compare_faces(image_encoding,j)
                if True in result:
                    boolean_list.append(True)
                if not True in result:
                    boolean_list.append(False)
            for k in range(len(boolean_list)-1):
                final_boolean = boolean_list[0]
                if k == len(operations):
                    operator = operations[-1]
                else:
                    operator = operations[k]
                if operator.lower() == "and":
                    final_boolean = final_boolean and boolean_list[k+1]
                elif operator.lower() == "or":
                    final_boolean = final_boolean or boolean_list[k+1]
                elif operator.lower() == "not":
                    if boolean_list[k+1] == True:
                        final_boolean = False
                    else:
                        final_boolean = True
                elif operator.lower() == "xor":
                    if final_boolean == boolean_list[k+1]:
                        final_boolean = False
                    else:
                        final_boolean = True
            if final_boolean = True:
                result_list.append(i)
                copy(path+i,path+"/nested_operations/"+i)
    return result_list
