"""
Summer 2018
1) Add working functions here
2) Put your name in comments of functions that you contribute
3) Maintain similarity in variable naming with prior posted code, unless you see some egregious errors.
"""

import face_recognition, cv2, os, pickle
from tqdm import tqdm
from shutil import move, copy, rmtree
from colorsys import hsv_to_rgb

# Make clean (Lily)
# Undo any changes made by other functions, to easily reset for testing - feel
# free to change this as more functions are added!
# Parameters: Path to the directory containing a set of photos; boolean option
# to also remove encoding files
def make_clean(dirPath='./pictures/', cleanEncodings=False):
    if dirPath[-1] != '/':
        dirPath += '/'
    # Move photos that were sorted out back into the dirPath directory
    if os.path.isdir('./sorted_out/'):
        for fileName in os.listdir('./sorted_out/'):
            if fileName[0] != '.':
                move('./sorted_out/' + fileName, dirPath)
        os.rmdir('./sorted_out/')
    # Completely remove the following folders if they exist:
    dirList = ['./found_person/', './find_and/', './find_xor/', './no_scrubs/']
    if cleanEncodings:
        dirList.append('./encodings/')
    for dir in dirList:
        if os.path.isdir(dir):
            rmtree(dir)

# Encode all (Lily)
# Finds face encodings of all photos in a directory and saves the encodings
# using pickle, so that later functions (find_and, find_xor) can load them later
# rather than redoing the encodings every time.
# Parameters: path to the directory containing a set of photos.
def encode_all(dirPath='./pictures/'):
    dirPath = init_function(dirPath, './encodings/')
    for file in tqdm(os.listdir(dirPath)):
        imagePath = dirPath + file
        image = face_recognition.load_image_file(imagePath)
        imageEncodings = face_recognition.face_encodings(image)
        # Only save an encodings file if there are faces in the photo
        if len(imageEncodings) > 0:
            encodingsFile = open('./encodings/' + file + '.encodings', 'wb')
            pickle.dump(imageEncodings, encodingsFile)
            encodingsFile.close()

# Get distances (Lily)
# Returns the list of distances between a subject face and all the faces in a
# test photo
# Parameters: the encoding for one subject face; the file name of a test photo
def get_distances(subjectEncoding, testFileName):
    try:
        encodingsFile = open('./encodings/' + testFileName + '.encodings', 'rb')
        testEncodings = pickle.load(encodingsFile)
        encodingsFile.close()
    except FileNotFoundError:
        return []
    return face_recognition.face_distance(testEncodings, subjectEncoding)

# Get subject encodings (Lily)
# Returns the list of encodings for a photo
# Parameters: path to a subject photo
def get_subject_encodings(subjectPath):
    subjectPath = subjectPath.split('/')[-1]
    try:
        encodingsFile = open('./encodings/' + subjectPath + '.encodings', 'rb')
        subjectEncodings = pickle.load(encodingsFile)
        encodingsFile.close()
    except FileNotFoundError:
        # If the encoding is not found, then the subject photo must not have any
        # faces
        return [[None]]
    return subjectEncodings

# Highlight faces in a photo (Lily)
# Draws red rectangles around each identified face
# Parameters: path to photo (e.g. './pictures/my_photo.jpg')
def highlight_faces(imgPath):
    # Loads the image first into face_recognition to find the faces, then to cv2
    # to draw rectangles
    img = face_recognition.load_image_file(imgPath)
    cvimg = cv2.imread(imgPath, 1)

    face_locations = face_recognition.face_locations(img)
    # Each item in face_locations is the dimensions of a box around a face
    # We can pass these dimensions into the cv2 rectangle function to highlight
    for i in range(len(face_locations)):
        top, right, bottom, left = face_locations[i]
        # The hue of each rectangle increases with each face so that the order
        # is visible
        hue = (float(i) / len(face_locations))
        (r, g, b) = hsv_to_rgb(hue, 0.6, 0.6)
        cv2.rectangle(cvimg, (left, top), (right, bottom), (b*255, g*255, \
        r*255), 5)

    # Display image
    cv2.imshow("highlighted faces", cvimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Sets up path and directory for each function to run (Lily)
# Parameters: path of directory containing a set of photos ('dirPath' in calling
# functions); path of directory to be created
def init_function(oldDirPath, newDirPath):
    # Create the sorted_out folder if it doesn't already exist
    if not os.path.isdir(newDirPath):
        os.mkdir(newDirPath)
    # Make sure the directory path ends in a slash
    if oldDirPath[-1] != '/':
        return oldDirPath + '/'
    else:
        return oldDirPath

# Sort out photos without faces (Lily)
# Moves faces without faces into a directory named "sorted_out"
# Parameters: path of directory containing a set of photos (defaults to
# './pictures/'); boolean indicating whether the photos in dirPath have already
# been encoded
def sort_out(dirPath='./pictures/', encoded=True):
    dirPath = init_function(dirPath, './sorted_out/')
    if not encoded:
        encode_all(dirPath)
    encodings = os.listdir('./encodings/')
    for fileName in os.listdir(dirPath):
        imgPath = dirPath + fileName
        encodingName = fileName + '.encodings'
        if encodingName not in encodings:
            move(imgPath, './sorted_out/')

# Find photos of a person (Lily)
# Given a photo of just one person, copies all photos containing that person
# into a directory named "found_person"
# Parameters: path of subject's photo; path of directory containing a set of
# photos; boolean indicating whether the photos in dirPath have already been
# encoded
def find_person(subjectPath, dirPath='./pictures/', encoded=True):
    dirPath = init_function(dirPath, './found_person/')
    if not encoded:
        encode_all(dirPath)
    subjectEncoding = get_subject_encodings(subjectPath)[0]
    for fileName in os.listdir(dirPath):
        testPath = dirPath + fileName
        distances = get_distances(subjectEncoding, fileName)
        for d in distances:
            # In the original github PhotoProject.py, 0.45 is the optimal
            # threshold, but I found that a little higher worked better for me
            if d <= 0.51:
                copy(testPath, './found_person/')
                break

# Find set AND (Lily)
# Given a list of photos, finds all photos that contain every person in those
# photos and copies them into a separate directory.
# The photos in the list you pass in can have any number of people in them.
# Parameters: List of paths to subject photos; path to the directory containing
# a set of photos; boolean indicating whether photos in the directory have
# already had their encodings saved using encode_all()
def find_and(subjectPathList, dirPath='./pictures/', encoded=True):
    dirPath = init_function(dirPath, './find_and/')
    allSubjectEncodings = []
    if not encoded:
        encode_all(dirPath)
    for subjectPath in subjectPathList:
        subjectEncodings = get_subject_encodings(subjectPath)
        if subjectEncodings[0][0] == None:
            # If there are no faces in the subject photo, get_subject_encodings
            # returns [None]
            return
        else:
            allSubjectEncodings += subjectEncodings
    receipt = []
    for fileName in os.listdir(dirPath):
        # Set up a switchboard to track which subjects have appeared in the
        # photo. If the switchboard is all True, then the photo includes all the
        # subjects and should be included.
        switchboard = [False] * len(allSubjectEncodings)
        testPath = dirPath + fileName
        for i in range(len(allSubjectEncodings)):
            distances = get_distances(allSubjectEncodings[i], fileName)
            for d in distances:
                if d <= 0.51:
                    # If the subject encoding matches one of the test encodings,
                    # flip the space on the switchboard to True
                    switchboard[i] = True
                    break
        if False not in switchboard:
            testPath = dirPath + fileName
            copy(testPath, './find_and/')
            receipt.append(fileName)
    print("Matching photos:")
    for p in receipt:
        print(p)

# Find XOR (Lily)
# Given a list of photos, finds photos that contain exactly one of the people in
# the photos and copies them into a separate directory named "./find_xor/"
# Parameters: List of paths to subject photos; path to the directory containing
# a set of photos; boolean indicating whether photos in the directory have
# already had their encodings saved using encode_all()
def find_xor(subjectPathList, dirPath='./pictures/', encoded=True):
    dirPath = init_function(dirPath, './find_xor/')
    allSubjectEncodings = []
    if not encoded:
        encode_all(dirPath)
    for subjectPath in subjectPathList:
        subjectEncodings = get_subject_encodings(subjectPath)
        if subjectEncodings[0][0] == None:
            # If there are no faces in the subject photo, get_subject_encodings
            # returns [None]
            return
        else:
            allSubjectEncodings += subjectEncodings
    receipt = []
    for fileName in os.listdir(dirPath):
        foundCount = 0;
        testPath = dirPath + fileName
        for subject in allSubjectEncodings:
            distances = get_distances(subject, fileName)
            for d in distances:
                if d <= 0.51:
                    # If the subject encoding matches one of the test encodings,
                    # flip the space on the switchboard to True
                    foundCount += 1
                    break
        if foundCount == 1:
            testPath = dirPath + fileName
            copy(testPath, './find_xor/')
            receipt.append(fileName)
    print("Matching photos:")
    for p in receipt:
        print(p)

# Find and highlight in a group photo (Lily)
# Assumes encodings are not saved because it only needs the encodings for the 2
# photos
# Parameters: Path to photo of just one person, path to the group photo
def find_and_highlight(subjectPath, groupPath, encoded=False):
    # Get the encoding of the subject
    if encoded:
        subjectEncoding = get_subject_encodings(subjectPath)[0]
    else:
        subject = face_recognition.load_image_file(subjectPath)
        subjectEncoding = face_recognition.face_encodings(subject)[0]
    # Get the list of encodings in the group picture
    group = face_recognition.load_image_file(groupPath)
    # Get the distances of each face from the subject and the locations of
    # each face
    if encoded:
        distances = get_distances(subjectEncoding, groupPath.split('/')[-1])
    else:
        groupEncodings = face_recognition.face_encodings(group)
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

# 'Scrub out' the face of a person in a group of photos (Lily)
# Given a photo of just one person (a scrub), blocks out that person's face in
# every photo in a given directory and copies the resulting photos into a new
# directory.
# Parameters: path to scrub photo; path to the directory containing a set of
# photos.
def scrub(scrubPath, dirPath='./pictures/', encoded=True):
    dirPath = init_function(dirPath, './no_scrubs/')
    if not encoded:
        encode_all(dirPath)
    scrubEncoding = get_subject_encodings(scrubPath)[0]
    # Iterate through each photo
    for fileName in tqdm(os.listdir(dirPath)):
        testPath = dirPath + fileName
        # Get the distances and face locations of the test photo
        distances = get_distances(scrubEncoding, fileName)
        test = face_recognition.load_image_file(testPath)
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
                newPath = './no_scrubs/' + fileName
                cv2.imwrite(newPath, cvimg)
                found = True
                break
        # If the scrub is not in the photo, copy it to the new directory
        # unchanged
        if not found:
            copy(testPath, './no_scrubs/')





