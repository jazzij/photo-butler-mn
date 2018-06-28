"""
Summer 2018
1) Add working functions here
2) Put your name in comments of functions that you contribute
3) Maintain similarity in variable naming with prior posted code, unless you see some egregious errors.
"""

import face_recognition, cv2, os
from tqdm import tqdm
from shutil import move, copy, rmtree

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
    for face in face_locations:
        top, right, bottom, left = face
        cv2.rectangle(cvimg, (left, top), (right, bottom), (0,0,255), 5)

    # Display image
    cv2.imshow("highlighted faces", cvimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Sort out photos without faces (Lily)
# Moves faces without faces into a directory named "sorted_out"
# Parameters: path of directory containing a set of photos (defaults to
# './pictures/'
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

# Find photos of a person (Lily)
# Given a photo of just one person, copies all photos containing that person
# into a directory 'found_person'
# Parameters: path of subject's photo; path of directory containing a set of
# photos
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

# Make clean (Lily)
# Undo any changes made by other functions, to easily reset for testing - feel
# free to change this as more functions are added!
# Parameters: Path to the directory containing a set of photos
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

# Find set AND (Lily)
# Given a photo with a set of people, finds all photos that contain every person
# in the set and copies them into a separate directory.
# I haven't been able to get 100% accuracy even with a higher threshold; it
# might be that the pictures I'm using to test are too different?
# Parameters: path to the photo containing the subjects; path to the directory
# containing a set of photos
def find_and(setPath, dirPath='./pictures/'):
    if dirPath[-1] != '/':
        dirPath += '/'
    if not os.path.isdir('./find_and/'):
        os.mkdir('./find_and/')
    setImg = face_recognition.load_image_file(setPath)
    setEncodings = face_recognition.face_encodings(setImg)
    if len(setEncodings) == 0:
        print("No faces were found in the set.")
        return
    print("{} faces were found in the set.".format(len(setEncodings)))
    for picture in tqdm(os.listdir(dirPath)):
        # Creates a list of boolean values for each test photo. Each boolean
        # represents one of the faces we're looking for. Once it's found, it
        # flips to True. Once every value in the switchboard is True, we know
        # the photo matches the set we're looking for.
        switchboard = [False] * len(setEncodings)
        testPath = dirPath + picture
        testImg = face_recognition.load_image_file(testPath)
        testEncodings = face_recognition.face_encodings(testImg)
        if len(testEncodings) == 0:
            continue
        # For each person in the subject photo, check if they are in the test
        # photo
        for i in range(len(setEncodings)):
            distances = face_recognition.face_distance(testEncodings, \
            setEncodings[i])
            for d in distances:
                if d <= 0.51:
                    switchboard[i] = True
                    break
        if False not in switchboard:
            copy(testPath, './find_and/')
