"""
Summer 2018
1) Add working functions here
2) Put your name in comments of functions that you contribute
3) Maintain similarity in variable naming with prior posted code, unless you see some egregious errors.
"""

import face_recognition, cv2, os, pickle
import time
from tqdm import tqdm
from shutil import move, copy, rmtree

def resizeImg( img, newSize ):
	r = newSize / img.shape[1]
	dim = (newSize, int(img.shape[0] * r))
	resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
	return resized

"""
Highlight faces in a photo (Lily)
Draws red rectangles around each identified face
Parameters: path to photo (e.g. './pictures/my_photo.jpg')
"""
def highlight_faces(imgPath):
    # Loads the image first into face_recognition to find the faces, then to cv2
    # to draw rectangles
    img = face_recognition.load_image_file(imgPath)
    cvimg = cv2.imread(imgPath, 1)
	

    face_locations = face_recognition.face_locations(img)
    # Each item in face_locations is the dimensions of a box around a face
    # We can pass these dimensions into the cv2 rectangle function to highlight
    for face in face_locations:
        top, right, bottom, left = face
        cv2.rectangle(cvimg, (left, top), (right, bottom), (0,0,255), 5)

    # Display image
    cvimg = resizeImg(cvimg, 700)
    cv2.imshow("highlighted faces", cvimg)
    cv2.waitKey(5000)
    cv2.destroyAllWindows()

"""
# Sort out photos without faces (Lily)
# Moves faces without faces into a directory named "sorted_out"
# Parameters: path of directory containing a set of photos (defaults to
# './pictures/'
"""
def sort_out(dirPath='./pictures/'):
    # Make sure the directory path ends in a slash
    if dirPath[-1] != '/':
        dirPath += '/'
    # Create the sorted_out folder if it doesn't already exist
    if not os.path.isdir("./sorted_out"):
        os.mkdir("./sorted_out")
    for file in tqdm(os.listdir(dirPath)):
        imgPath = dirPath + file
        img = face_recognition.load_image_file(imgPath)
        face_locations = face_recognition.face_locations(img)
        if len(face_locations) == 0:
            move(imgPath, './sorted_out/')

"""
# Find photos of a person (Lily)
# Given a photo of just one person, copies all photos containing that person
# into a directory 'found_person'
# Parameters: path of subject's photo; path of directory containing a set of
# photos
"""
def find_person(subjectPath, dirPath='./pictures/'):
    # Make sure the directory path ends in a slash
    if dirPath[-1] != '/':
        dirPath += '/'
    # Create the sorted_out folder if it doesn't already exist
    if not os.path.isdir('./found_person/'):
        os.mkdir('./found_person/')
    subject = face_recognition.load_image_file(subjectPath)
    # The subject's face encoding should be the first & only item in the list
    subject_encoding = face_recognition.face_encodings(subject)[0]
    for file in tqdm(os.listdir(dirPath)):
        testPath = dirPath + file
        test = face_recognition.load_image_file(testPath)
        test_encodings = face_recognition.face_encodings(test)
        distances = face_recognition.face_distance(test_encodings, \
        subject_encoding)
        for d in distances:
            # In the original github PhotoProject.py, 0.45 is the optimal
            # threshold, but I found that a little higher worked better for me
            if d <= 0.51:
                copy(testPath, './found_person/')
                break

"""
# Make clean (Lily)
# Undo any changes made by other functions, to easily reset for testing - feel
# free to change this as more functions are added!
# Parameters: Path to the directory containing a set of photos
"""
def make_clean(dirPath='./pictures/'):
    if dirPath[-1] != '/':
        dirPath += '/'
    if os.path.isdir('./sorted_out/'):
        for picture in os.listdir('./sorted_out/'):
            if picture[0] != '.':
                move('./sorted_out/' + picture, dirPath)
        os.rmdir('./sorted_out/')
    if os.path.isdir('./found_person/'):
        rmtree('./found_person/')
    if os.path.isdir('./find_and/'):
        rmtree('./find_and/')
    if os.path.isdir('./find_xor/'):
        rmtree('./find_xor/')
    if os.path.isdir('./no_scrubs/'):
        rmtree('./no_scrubs/')
    if os.path.isdir('./encodings/'):
        rmtree('./encodings/')

"""
# Find set AND (Lily)
# Given a list of photos, finds all photos that contain every person in those
# photos and copies them into a separate directory.
# The photos in the list you pass in can have any number of people in them.
# Parameters: List of paths to subject photos; path to the directory containing
# a set of photos; boolean indicating whether photos in the directory have
# already had their encodings saved using encode_all().
"""
def find_and(subjectPhotoList, dirPath='./pictures/', encoded=False):
    if dirPath[-1] != '/':
        dirPath += '/'
    if not os.path.isdir('./find_and/'):
        os.mkdir('./find_and/')
    subject_encodings = []
    if encoded:
        for subjPhoto in subjectPhotoList:
            # Get just the name of the photo, not the full path
            subjPhoto = subjPhoto.split('/')[-1]
            try:
                # Load the photo encodings and add to subject_encodings list
                encodingsFile = open('./encodings/' + subjPhoto + '.encodings',\
                'rb')
                subject_encodings += pickle.load(encodingsFile)
                encodingsFile.close()
            except FileNotFoundError:
                # When encode_all finds a photo with no faces, it does not save
                # an encodings file. If we can't find an encoding file, that is
                # probably why, so we can safely skip this photo.
                continue
    else:
        # If the encodings haven't already been saved, find each photo's
        # encodings and add to subject_encodings list
        for subjPhoto in subjectPhotoList:
            subjImg = face_recognition.load_image_file(subjPhoto)
            subject_encodings += face_recognition.face_encodings(subjImg)
    if len(subject_encodings) == 0:
        print('No subject faces found.')
        return
    print("{} subject faces found.".format(len(subject_encodings)))
    for picture in tqdm(os.listdir(dirPath)):
        # Set up a switchboard to track which subjects have appeared in the
        # photo. If the switchboard is all True, then the photo includes all the
        # subjects and should be included.
        switchboard = [False] * len(subject_encodings)
        if encoded:
            try:
                encodingsFile = open('./encodings/' + picture + '.encodings', \
                'rb')
                testEncodings = pickle.load(encodingsFile)
                encodingsFile.close()
            except FileNotFoundError:
                continue
        else:
            testPath = dirPath + picture
            testImg = face_recognition.load_image_file(testPath)
            testEncodings = face_recognition.face_encodings(testImg)
            if len(testEncodings) == 0:
                continue
        for i in range(len(subject_encodings)):
            # Get distances between test encodings and each subject encoding
            distances = face_recognition.face_distance(testEncodings, \
            subject_encodings[i])
            for d in distances:
                if d <= 0.51:
                    # If the subject encoding matches one of the test encodings,
                    # flip the space on the switchboard to True
                    switchboard[i] = True
                    break
        if False not in switchboard:
            testPath = dirPath + picture
            copy(testPath, './find_and/')

"""
# Find XOR (Lily)
# Given a list of photos, finds photos that contain exactly one of the people in
# the photos and copies them into a separate directory.
# Parameters: List of paths to subject photos; path to the directory containing
# a set of photos; boolean indicating whether photos in the directory have
# already had their encodings saved using encode_all().
"""
def find_xor(subjectPhotoList, dirPath='./pictures/', encoded=False):
    if dirPath[-1] != '/':
        dirPath += '/'
    if not os.path.isdir('./find_xor/'):
        os.mkdir('./find_xor/')
    subject_encodings = []
    if encoded:
        for subjPhoto in subjectPhotoList:
            # Get just the name of the photo, not the full path
            subjPhoto = subjPhoto.split('/')[-1]
            try:
                # Load the photo encodings and add to subject_encodings list
                encodingsFile = open('./encodings/' + subjPhoto + '.encodings',\
                'rb')
                subject_encodings += pickle.load(encodingsFile)
                encodingsFile.close()
            except FileNotFoundError:
                # When encode_all finds a photo with no faces, it does not save
                # an encodings file. If we can't find an encoding file, that is
                # probably why, so we can safely skip this photo.
                continue
    else:
        # If the encodings haven't already been saved, find each photo's
        # encodings and add to subject_encodings list
        for subjPhoto in subjectPhotoList:
            subjImg = face_recognition.load_image_file(subjPhoto)
            subject_encodings += face_recognition.face_encodings(subjImg)
    if len(subject_encodings) == 0:
        print('No subject faces found.')
        return
    print("{} subject faces found.".format(len(subject_encodings)))
    for picture in tqdm(os.listdir(dirPath)):
        # Just keeps track of how many of the subjects are found in the photo.
        # The count has to be exactly one to be included.
        foundCount = 0
        if encoded:
            try:
                encodingsFile = open('./encodings/' + picture + '.encodings', \
                'rb')
                testEncodings = pickle.load(encodingsFile)
                encodingsFile.close()
            except FileNotFoundError:
                continue
        else:
            testPath = dirPath + picture
            testImg = face_recognition.load_image_file(testPath)
            testEncodings = face_recognition.face_encodings(testImg)
            if len(testEncodings) == 0:
                continue
        for subj in subject_encodings:
            # Get distances between test encodings and each subject encoding
            distances = face_recognition.face_distance(testEncodings, subj)
            for d in distances:
                if d <= 0.51:
                    foundCount += 1
                    break
            if foundCount > 1:
                break
        if foundCount == 1:
            testPath = dirPath + picture
            copy(testPath, './find_xor/')

"""
# Find and highlight in a group photo (Lily)
# Parameters: Path to photo of just one person, path to the group photo
"""
def find_and_highlight(subjectPath, groupPath):
    # Get the encoding of the subject
    subject = face_recognition.load_image_file(subjectPath)
    subjectEncoding = face_recognition.face_encodings(subject)[0]
    # Get the list of encodings in the group picture
    group = face_recognition.load_image_file(groupPath)
    groupEncodings = face_recognition.face_encodings(group)
    # Get the distances of each face from the subject and the locations of
    # each face
    distances = face_recognition.face_distance(groupEncodings, subjectEncoding)
    locations = face_recognition.face_locations(group)
    # Load the image with openCV so we can draw on it
    cvimg = cv2.imread(groupPath, 1)
    # Iterate through the distances until one is below the threshold
    for i in range(len(distances)):
        if distances[i] <= 0.51:
            # Get the face location and draw a rectangle
            top, right, bottom, left = locations[i]
            cv2.rectangle(cvimg, (left, top), (right, bottom), (0,0,255), 5)
            break
    # Show the image
    cv2.imshow('Image', cvimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

"""
# 'Scrub out' the face of a person in a group of photos (Lily)
# Given a photo of just one person (a scrub), blocks out that person's face in
# every photo in a given directory and copies the resulting photos into a new
# directory.
# Parameters: path to scrub photo; path to the directory containing a set of
# photos.
"""
def scrub(scrubPath, dirPath='./pictures/'):
    if dirPath[-1] != '/':
        dirPath += '/'
    if not os.path.isdir('./no_scrubs/'):
        os.mkdir('./no_scrubs/')
    # Load the scrub photo and get scrub encoding
    scrub = face_recognition.load_image_file(scrubPath)
    scrubEncoding = face_recognition.face_encodings(scrub)[0]
    # Iterate through each photo
    for file in tqdm(os.listdir(dirPath)):
        testPath = dirPath + file
        test = face_recognition.load_image_file(testPath)
        testEncodings = face_recognition.face_encodings(test)
        # Get the distances and face locations of the test photo
        distances = face_recognition.face_distance(testEncodings, scrubEncoding)
        locations = face_recognition.face_locations(test)
        found = False
        for i in range(len(distances)):
            if distances[i] <= 0.51:
                # If the scrub is found, get that face location
                top, right, bottom, left = locations[i]
                # Load the image with openCV and draw a box on the face
                cvimg = cv2.imread(testPath, 1)
                cv2.rectangle(cvimg, (left, top), (right, bottom), (0,0,0), -1)
                # Save the new image into the new directory
                newPath = './no_scrubs/' + file
                cv2.imwrite(newPath, cvimg)
                found = True
                break
        # If the scrub is not in the photo, copy it to the new directory
        # unchanged
        if not found:
            copy(testPath, './no_scrubs/')

"""
# Finds face encodings of all photos in a directory and saves the encodings
# using pickle, so that later functions (find_and, find_xor) can load them later
# rather than redoing the encodings every time.
# Parameters: path to the directory containing a set of photos.
"""
def encode_all(dirPath='./pictures/'):
    if dirPath[-1] != '/':
        dirPath += '/'
    if not os.path.isdir('./encodings/'):
        os.mkdir('./encodings/')
    for file in tqdm(os.listdir(dirPath)):
        imagePath = dirPath + file
        image = face_recognition.load_image_file(imagePath)
        imageEncodings = face_recognition.face_encodings(image)
        # Only save an encodings file if there are faces in the photo
        if len(imageEncodings) > 0:
            encodingsFile = open('./encodings/' + file + '.encodings', 'wb')
            pickle.dump(imageEncodings, encodingsFile)
            encodingsFile.close()
#Applying "or" operation to all the faces in a given picture (Binh)
#Return a list of all the images that contain any person in the given picture
#Create a folder that contains of those image files.
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
#Applying "not" operation to all the faces in a given picture(Binh)
#Return a list of images containing  the first face of the given picture but not containing any other faces in the given picture.
#Create a folder containing all those images
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
#An integrated version of all the four operations that have been written so far(Binh)
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
#Print out the list of the files in a certain directory in the order of the times they were created(Binh) 
def timeline(path):
    result = []
    for i in os.listdir(path):
        file_info = os.stat(i)
        timeData = time.localtime(file_info.st_ctime)
        readableTime = time.ctime(file_info.st_ctime)
        tupleData = (timeData,i,readableTime)
        result.append(tupleData)
    ordered_result = sorted(result)
    for j in fin_res:
        print(str(j[-2])+" "+str(j[-1]))
