"""
Summer 2018
1) Add working functions here
2) Put your name in comments of functions that you contribute
3) Maintain similarity in variable naming with prior posted code, unless you see some egregious errors.
"""

import face_recognition, cv2, os, pickle, heapq, itertools, hashlib, sqlite3
from sqlite3 import Error
from tqdm import tqdm
import time
from shutil import move, copy, rmtree
from colorsys import hsv_to_rgb
from pwd import getpwuid

from wheezy.core.feistel import make_feistel_number
from wheezy.core.feistel import sample_f
from wheezy.core.luhn import luhn_sign
key_gen = lambda n: luhn_sign(make_feistel_number(sample_f)(n))

encodings = {}
distances = {}
distance_map = {}
THRESHOLD = 0.51
F_D_MODEL = "hog"
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



################################################################################
# Auxillary functions used in storing values in the database. May be useful for
# data shelving/persistent data storage with some editing.
###############################################################################

def save_landmarks(dirPath, landmarks_dir):
    """ saves a pickled list of dictionaries of point data  for facial landmarks, 
        one for each face in an image (Jess)
    :param dirPath: source directory containing images
    :param landmarks_dir: destination directory for landmarks
    """
    if not os.path.isdir(landmarks_dir):
        os.mkdir(landmarks_dir)
    for entry in os.scandir(dirPath):
        if entry.is_file():
            image = face_recognition.load_image_file(entry.path)
            face_landmarks = face_recognition.face_landmarks(image)
            if len(face_landmarks) > 0:
                path = os.path.join(landmarks_dir, (entry.name + ".landmarks"))
                fil_des = open(path, 'wb')
                pickle.dump(face_landmarks, fil_des)
                fil_des.close()
            

def load_encodings(encodings_dir='./encodings', encodings_dict=encodings):
    """ creates a dictionary of face encodings for all image files in dirPath (Jess)
    :param encodings_dir: filepath to directory containing face encodings 
    :param encodings_dict: A dictionary. A global/class parameter that associates 
        an image with numPy array of all face encodings detected in this image
    """
    files = [f.path for f in os.scandir(encodings_dir) if f.is_file()]
    for file in files:
        fil_des = open(file, 'rb')
        encodings_dict[file] = pickle.load(fil_des)
        fil_des.close()

               
def encode_dir(dirPath='./pictures/', encodings_dict=encodings):
    """ creates a dictionary of face encodings for all image files in dirPath (Jess)
    :param dirpath: filepath to directory containing photos 
    :param encodings_dict: A dictionary. A global/class parameter that associates 
        an image with numPy array of all face encodings detected in this image,
        an empty array when no faces are detected
    """
    for file in tqdm(os.listdir(dirPath)):
        file_name = dirPath+'/'+file
        if os.path.isfile(file_name):
            image = face_recognition.load_image_file(file_name)
            imageEncodings = face_recognition.face_encodings(image)
            if file_name not in encodings:
                encodings_dict[file_name] = imageEncodings


def all_distances(encodings_dict=encodings, distances_dict=distances):
    """ creates a dictionary of distances between all pairs of faces (Jess)    
    :param encodings_dict: same as in encode_dir() 
    :param distances_dict: A dictionary. A global/class parameter that associates 
        a min heap of distances between a face and all other faces
    """
    
    keys = list(filter(lambda x: encodings_dict.get(x) != [], encodings_dict.keys()))
    key_pairs = list(itertools.combinations_with_replacement(keys, 2))
    for (imageA, imageB) in key_pairs:
        heap = distances_dict[(imageA, imageB)] = []
        facesA = encodings_dict.get(imageA)
        facesB = encodings_dict.get(imageB)
        for idxA, faceA in enumerate(facesA):
            for idxB, distance in enumerate(face_recognition.face_distance (facesB, faceA)):
                if (imageA == imageB and not idxA==idxB) or imageA != imageB:
                    if dict.__contains__(distances_dict, (imageA, imageB)): 
                        heapq.heappush(heap, ((distance, idxA, idxB)))
                    else:
                        heap.append((distance, idxA, idxB))                        
                 
def all_distances2(encodings_dict=encodings, distances_dict=distances):
    """ creates a dictionary of distances between all pairs of faces (Jess)     
    :param encodings_dict: same as in encode_dir() 
    :param distances_dict: A dictionary. A global/class parameter that associates
        the results of get_distances() for each face in photoA with photoB in an 
        array of arrays. This function assumes the use of load_encodings() and 
        calls face_recognition.face_distance() rather than get_distances(). 
        Currently overwrites the values stored to dict by all_distances()
    """
    keys = list(filter(lambda x: encodings_dict.get(x) != [], encodings_dict.keys()))
    key_pairs = list(itertools.combinations_with_replacement(keys, 2))
    for (imageA, imageB) in key_pairs:
        facesA = encodings_dict.get(imageA)
        facesB = encodings_dict.get(imageB)
        entry = distances_dict[(imageA, imageB)] = []
        for idxA, faceA in enumerate(facesA):
            entry.append(((idxA), list(itertools.starmap(face_recognition.face_distance,
                                                         [(facesB, faceA) for faceA in facesA]))))

#(Jess)           
def distance_mappings(dirPath='./encodings', encoding_function=load_encodings,
                      encodings_dict=encodings, distances_dict=distances,
                      distance_map_dict=distance_map ):
    if len(encodings_dict) == 0:
        encoding_function(dirPath, encodings_dict)
    if len(distances_dict) == 0:
        all_distances(encodings_dict, distances_dict)
    for (imageA, imageB), list_vals in distances.items():
        for (distance, idxA, idxB) in list_vals:
            distance_map_dict[((imageA, idxA), (imageB, idxB))] = distance

########                    end section                    ########        


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
            if d <= THRESHOLD:
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
                if d <= THRESHOLD:
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
                if d <= THRESHOLD:
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
        if distances[i] <= THRESHOLD:
            # Get the face location and draw a rectangle
            top, right, bottom, left = locations[i]
            cv2.rectangle(cvimg, (left, top), (right, bottom), (0,0,255), 5)
            break
    # Show the image
    cv2.imshow('Image', cvimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

'''
# 'Scrub out' the face of a person in a group of photos (Lily)
# Given a photo of just one person (a scrub), blocks out that person's face in
# every photo in a given directory and copies the resulting photos into a new
# directory.
# Parameters: path to scrub photo; path to the directory containing a set of
# photos.
'''
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
            if distances[i] <= THRESHOLD:
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

'''
#Applying "or" operation to all the faces in a given picture (Binh)
#Return a list of all the images that contain any person in the given picture
#Create a folder that contains of those image files.
'''
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

'''
#Applying "not" operation to all the faces in a given picture(Binh)
#Return a list of images containing  the first face of the given picture but not containing any other faces in the given picture.
#Create a folder containing all those images
'''
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

'''
#An integrated version of all the four operations that have been written so far(Binh)
'''
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

'''
#Print out the list of the files in a certain directory in the order of the times they were created(Binh) 
'''
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

######################
# Database functions  
####################

#Create a Connection object to represent the database (DB) (Jess)
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.execute('pragma foreign_keys=ON')
        return conn
    except Error as e:
        print(e)
    return None

#Create table function (Jess)
def create_table(conn, sql_create_table):
    """ create a table from an sql_create_table statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        #represent a database cursor to iterate/manipulate DB 
        db_cursor = conn.cursor()
        
        db_cursor.execute(sql_create_table) 
    except Error as e:
        print(e)

################################################################
# sql_create_table statements in create_table() function (Jess)
###############################################################
def sql_create_photos_table ():
    return """ CREATE TABLE IF NOT EXISTS photos (
                    photo_id integer PRIMARY KEY,
                    file_ref_encoding text,                  
                    permissions integer,
                    owner text,
                    creator text,
                    creation_date text,              
                    color_palette text,
                    has_a_face integer,
                    faces_detected integer,
                    RASTER_format text,
                    face_detection_model text
               ); """

        

def sql_create_faces_table():
    return """CREATE TABLE IF NOT EXISTS faces (
                  face_id integer PRIMARY KEY,
                  photo_id integer,
                  position_of_face_in_image integer, 
                  file_ref_of_large_point_data text,
                  UNIQUE (face_id, photo_id),
                  FOREIGN KEY (photo_id)
                      REFERENCES photos(photo_id)
                      ON UPDATE CASCADE
                      ON DELETE CASCADE
              ); """

def sql_create_distances_table():
    return """CREATE TABLE IF NOT EXISTS distances (
                  A_id integer,
                  B_id integer,
                  distance real,
                  PRIMARY KEY (A_id, B_id),
                  FOREIGN KEY (A_id)
                      REFERENCES faces (face_id)
                      ON UPDATE CASCADE
                      ON DELETE CASCADE,
                  FOREIGN KEY (B_id)
                      REFERENCES faces (face_id)
                      ON UPDATE CASCADE
                      ON DELETE CASCADE
              );"""

def sql_create_person_table():
    return """CREATE TABLE IF NOT EXISTS person (
                  face_id integer,
                  photo_id integer, 
                  name: text,
                  DOB: text,
                  PRIMARY KEY (face_id, photo_id), 
                  FOREIGN KEY (face_id)
                      REFERENCES faces (face_id)
                      ON UPDATE CASCADE 
                      ON DELETE CASCADE, 
                  FOREIGN KEY (photo_id) 
                      REFERENCES photos (photo_id)
                      ON UPDATE CASCADE 
                      ON DELETE CASCADE
              );"""

 
###########################################
# row insertion for tables photos and faces 
##########################################

def create_photo(conn, photo_entry):

    """ INSERT new data entry INTO photos table (Jess)
    :param conn: Connection object
    :param photo_entry: new photo data
    :return: reference to new data entry
    """
    sql = ''' INSERT INTO photos (file_ref_encoding, 
                                  permissions, owner, creator, 
                                  creation_date, color_palette, has_a_face, faces_detected, 
                                  RASTER_format, face_detection_model)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, photo_entry)
    return cur.lastrowid


def create_face(conn, face_entry):
    """ INSERT new data entry INTO faces table (Jess)
    :param conn: Connection object
    :param photo_entry: new face data
    :return: reference to new data entry
    """
    sql = ''' INSERT INTO faces (face_id, photo_id, position_of_face_in_image, 
                                 file_ref_of_large_point_data)
              VALUES(?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, face_entry)
    return cur.lastrowid

def create_distance(conn, distance_entry):
    """ INSERT new data entry INTO distances table (Jess)
    :param conn: Connection object
    :param distance_entry: new distance data
    :return: reference to new data entry
    """
    sql = ''' INSERT INTO distances (A_id, B_id, distance)
              VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, distance_entry)
    return cur.lastrowid

##############################################
# row deletion for the tables photos and faces
#############################################

def delete_photo_entry(conn, photo_id):
    """ Delete a photo by primary key value (Jess)
    :param conn:  Connection to the SQLite database
    :param id: primary key of the photo
    :return:
    """
    sql = 'DELETE FROM photos WHERE photo_id =? '
    cur = conn.cursor()
    cur.execute(sql, (photo_id,))

def delete_face_entry(conn, photo_id, position_of_face_in_image):
    """ Delete a face by primary key value (Jess)
    :param conn:  Connection to the SQLite database
    :param photo_id: photo designation
    :param position_of_face_in_image: the index of this face's encoding  
    :return:
    """
    sql = 'DELETE FROM faces WHERE photo_id =? AND position_of_face_in_image=?'
    cur = conn.cursor()
    cur.execute(sql, (photo_id, position_of_face_in_image))

def delete_distance_entry(conn, A_id, B_id):
    """ Delete a face by primary key value (Jess)
    :param conn:  Connection object to the database
    :param A_id: face designation
    :param B_id: face designation 
    :return:
    """
    sql = 'DELETE FROM faces WHERE photo_id =? AND position_of_face_in_image=?'
    cur = conn.cursor()
    cur.execute(sql, (A_id, B_id))


def drop_table(conn, table):
    """ Delete a table from the database (Jess)
    :param conn:  Connection to the SQLite database
    :param table: the table to delete. 
    :return:
    """
    sql = 'DROP TABLE ' + table
    curr = conn.cursor()
    curr.execute(sql)


#####################################################################################
# sql generating code.
# This works, but it isn't very well designed. The intent was to create something
# for the user who doesn't know SQL. I.e., an interface where the user can plug
# in search terms and the code will write the SQL required to perform the search.
# Not completely unlike searching through a library catalog where you can search by
# keyword, author, print format etc. It's an entirely separate project to create this
# interface, definitely a manageble one if you already know SQL. I don't think you
# need to create this interface yourself. 
####################################################################################

######################
# update table values
#####################
 
def update_table(conn, table, update_keys, values, location):
    """ update values in a table (Jess)
    :param conn: Connection object
    :param table: the table in which values are changed 
    :param update_keys: a list of column names to replace data in
    :param values: replacement data in order corresponding to order of update_keys
        >=0 additional values correspond to values used as entry identifiers  
    :param location: None results in all values of a column replaced, currently takes
        a single value primary key to update a single row. In reality, you can input
        whatever sql language makes sense to conduct the query you want by appropriately
        splitting your query into location and value. 
    :return: 
    """
    sql = "UPDATE " + table + " SET " + update_keys[0] + " = ? "
    idx = 1
    while idx < len(update_keys):
        sql += ", " + update_keys[idx] + " = ? "
        idx += 1
    if location != None:
        sql += "WHERE " + location + " = ?\n"
    cur = conn.cursor()
    cur.execute(sql, values)


###################
# table population
##################

def load_photos(dirPath, database, encodingsPath= "./encodings",  ext = ".encodings", creator = ''):
    """ store photo entries into photos table (Jess)
    :param dirPath: directory containing photos that have 
        been encoded
    :param database: path to db file
    :param encodingsPath: directory containing photo encodings
        of photos in dirPath
    :param ext: encodings extension
    :param creator: photographer of image. a column in photos table can store this value 
    """
    conn = create_connection(database) 
    if not os.path.isdir(encodingsPath):
        encode_all(encodingsPath)
    if dict.__eq__(encodings, {}):
        load_encodings(encodingsPath)
   
    create_table(conn, sql_create_photos_table())
    for entry in os.scandir(dirPath):
           
        if entry.is_file():
            stat = os.stat(entry.path, follow_symlinks=False)
            has_a_face = 1
            num_faces = 0
            encoding_entry = os.path.join(encodingsPath, entry.name + ext)
        if dict.__contains__(encodings, encoding_entry):
            
            num_faces = len(encodings.get(encoding_entry))
            
            photo_entry = (encoding_entry, stat.st_mode, time.ctime(stat.st_mtime),
                       '', getpwuid(stat.st_uid).pw_name, creator, has_a_face, num_faces,
                           entry.name.split('.')[-1], F_D_MODEL)
           
            with conn:
                create_photo(conn, photo_entry)
    conn.close()
    

def load_faces(dirPath, database, encodingsPath= "./encodings",
               encodings_ext = ".encodings", landmarks_dir = "./landmarks",
               landmarks_ext = ".landmarks"):
    """ store face entries into faces table (Jess)
    :param dirPath: directory containing photos that have 
        been encoded
    :param database: path to db file
    :param landmarks_dir: directory holding a pickled list of 
        dictionaries of point data  for facial landmarks, one 
        dictionary each face in an image, one file per image
    :param ext: landmarks extension
    """
    if dict.__eq__(encodings, {}):
        load_encodings(encodingsPath)
    if not os.path.isdir(landmarks_dir):
        save_landmarks(dirPath, landmarks_dir)
    counter = 0
        
    conn = create_connection(database)
    create_table(conn, sql_create_faces_table())
    for entry in os.scandir(dirPath):
        if entry.is_file():
            
        
            landmarks_entry = os.path.join(landmarks_dir, entry.name + landmarks_ext)
            encoding_entry = os.path.join(encodingsPath, entry.name + encodings_ext)
            if dict.__contains__(encodings, encoding_entry):
                ids = conn.cursor().execute('SELECT photo_id FROM photos WHERE file_ref_encoding =?',
                                             (encoding_entry,)).fetchall()
                
                photo_id = ids[0][0]
                
                for face_idx, face in enumerate(encodings.get(encoding_entry)):
                    face_id = key_gen(counter)
                    counter += 1
                    face_entry = (face_id, photo_id, face_idx, landmarks_entry)
                    with conn:
                        create_face(conn, face_entry) 
                    
    conn.close()

                   
                
                   
    
    

