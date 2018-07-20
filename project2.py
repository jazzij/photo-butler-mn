import os
import face_recognition
from shutil import copy
def or_operator(path,picture):
    original_img = face_recognition.load_image_file(path+picture)
    original_img_encoding = face_recognition.face_encodings(original_img)
    result_list = []
    for i in os.listdir(path):
        if i != "project2.py":
            img = face_recognition.load_image_file(path+i)
            img_encoding = face_recognition.face_encodings(img)
            boolean_list = []
            for j in original_img_encoding:
                result = face_recognition.compare_faces(img_encoding,j)
                if True in result:
                    boolean_list.append(True)
                else:
                    boolean_list.append(False)
            if True in boolean_list:
                result_list.append(i)
                if os.path.exists(path+"or_operation"):
                    copy(path+i,path+"or_operation\\"+i)
                else:
                    os.mkdir(path+"or_operation")
                    copy(path+i,path+"or_operation\\"+i)
    return result_list
def not_operator(path,picture):
    original_img = face_recognition.load_image_file(path+picture)
    original_img_encoding = face_recognition.face_encodings(original_img)
    result_list = []
    for i in os.listdir(path):
        if i != "project2.py":
            img = face_recognition.load_image_file(path+i)
            img_encoding = face_recognition.face_encodings(img)
            boolean_list = []
            for j in original_img_encoding:
                result = face_recognition.compare_faces(img_encoding,j)
                if True in result:
                    boolean_list.append(True)
                else:
                    boolean_list.append(False)
            if True == boolean_list[0]:
                if not True in boolean_list:
                    result_list.append(i)
                    if os.path.exists(path+"not_operation"):
                        copy(path+i,path+"not_operation\\"+i)
                    else:
                        os.mkdir(path+"not_operation")
                        copy(path+i,path+"not_operation\\"+i)
    return result_list
def nested_operator(path,picture,operations):
    original_img = face_recognition.load_image_file(path+picture)
    original_img_encoding = face_recognition.face_encodings(original_img)
    result_list = []
    for i in os.listdir(path):
        if i != "project2.py":
            img = face_recognition.load_image_file(path+i)
            img_encoding = face_recognition.face_encodings(img)
            boolean_list = []
            final_boolean = True
            for j in original_img_encoding:
                result = face_recognition.compare_faces(img_encoding,j)
                if True in result:
                    boolean_list.append(True)
                else:
                    boolean_list.append(False)
            for k in range(len(boolean_list)-1):
                final_boolean = boolean_list[0]
                if k >= len(operations):
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
            if final_boolean == True:
                result_list.append(i)
                if os.path.exists(path+"nested_operations"):
                    copy(path+i,path+"nested_operations\\"+i)
                else:
                    os.mkdir(path+"nested_operations")
                    copy(path+i,path+"nested_operations\\"+i)
    return result_list
