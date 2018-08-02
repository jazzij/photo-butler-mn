import sqlite3
from sqlite3 import Error


    
#Create a Connection object to represent the database (DB)
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

def create_table(conn, sql_create_table):
    """ create a table from the sql_create_table statement
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

##############################
# sql_create_table statements
#############################
def sql_create_photos_table ():
    """
    :param file_ref_of_numpy_array: a file reference to the numpy array of this image
    :param file_ref_encoding: a reference to a file containing an array of 128-dimension 
         face encoding for each face in an image
    :param permissions: the read, write, execute file permissions for the image 
    :param modification_date: the date the image was last modified. 
    :param owner: whomever owns the rights to the image
    :param creator: the artist who created this work. 
    :param creation_date: the date the photo was taken
    :param color_format: color format 
    :param has_a_face: whether or not there are faces in a photo
    :param RASTER_format: e.g. TIFF, JPEG, PNG etc.
    :param face_detection_model: face detection model used, HOG or CNN. CNN is slower but 
         more accurate. Useful to document in the event of false negatives
	 in face detection
    """
    return """ CREATE TABLE IF NOT EXISTS photos (
                    file_ref_of_numpy_array text PRIMARY KEY,
                    file_ref_encoding text,                  
                    file_permissions text,
                    modification_date text,
                    owner text,
                    creator text,
                    creation_date text,              
                    color_format text,
                    has_a_face text,
                    RASTER_format text,
                    face_detection_model text,
                    UNIQUE (file_ref_encoding)
                 ); """

        

def sql_create_faces_table():
    """
    :param file_ref_of_facial_encodings: a reference to a file containing 
         an array of 128-dimension face encoding for each face in an image
    :param position_of_face_in_image: the index for this face in the array 
         mentioned above
    :param name: the name of the person this face belongs to
    :param file_ref_of_large_point_data: a file containing the point data 
         for the attributes of this face
    :param file_ref_of_distances_between_images: a file containing the 
         distance between this face, and every (photo, face) pair it has been 
         compared to
    """
    return """CREATE TABLE IF NOT EXISTS faces (
                  file_ref_of_facial_encodings text,
                  position_of_face_in_image integer, 
                  name text,
                  file_ref_of_distances_between_images text,
                  file_ref_of_large_point_data text, 
                  PRIMARY KEY(file_ref_of_facial_encodings, position_of_face_in_image),
                  FOREIGN KEY (file_ref_of_facial_encodings) 
                      REFERENCES photos(file_ref_encoding)
                      ON UPDATE CASCADE                  
                      ON DELETE CASCADE
              ); """ 
 
###########################################
# row insertion for tables photos and faces
##########################################

def create_photo(conn, photo_entry):

    """
    INSERT new data entry INTO photos table
    :param conn: Connection object
    :param photo_entry: new photo data
    :return: reference to new data entry
    """
    sql = ''' INSERT INTO photos (file_ref_of_numpy_array, file_ref_encoding, 
                                  file_permissions, modification_date, owner, creator, 
                                  creation_date, color_format, has_a_face, RASTER_format,
                                  face_detection_model)
              VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, photo_entry)
    return cur.lastrowid


def create_face(conn, face_entry):
    """ 
    INSERT new data entry INTO faces table
    :param conn: Connection object
    :param photo_entry: new person data
    :return: reference to new data entry
    """
    sql = ''' INSERT INTO faces (file_ref_of_facial_encodings, position_of_face_in_image, 
                                 name, file_ref_of_large_point_data, 
                                 file_ref_of_distances_between_images)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, face_entry)
    return cur.lastrowid 

##############################################
# row deletion for the tables photos and faces
#############################################

def delete_photo_entry(conn, file_ref_of_numpy_array):
    """
    Delete a photo by primary key value
    :param conn:  Connection to the SQLite database
    :param id: primary key of the photo
    :return:
    """
    sql = 'DELETE FROM photos WHERE file_ref_of_numpy_array =? '
    cur = conn.cursor()
    cur.execute(sql, (file_ref_of_numpy_array,))

def delete_face_entry(conn, file_ref_of_facial_encodings, position_of_face_in_image):
    """
    Delete a face by primary key value
    :param conn:  Connection to the SQLite database
    :param file_ref_of_faceial_encodings: the file where the array of encodings for all faces 
        in the image is stored
    :param position_of_face_in_image: the index of that array for this face 
    :return:
    """
    sql = 'DELETE FROM faces WHERE file_ref_of_facial_encodings =? AND position_of_face_in_image=?'
    cur = conn.cursor()
    cur.execute(sql, (file_ref_of_facial_encodings, position_of_face_in_image))

def drop_table(conn, table):
    """
    Delete a table from the database
    :param conn:  Connection to the SQLite database
    :param table: the name of the table to delete. 
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
# interface, definitely a manageble one if you already know SQL.
####################################################################################

######################
# update table values
#####################

def update_table(conn, table, update_keys, values, location):
    """
    update values in a table
    :param conn: Connection object
    :param table: the table in which values are changed 
    :param update_keys: a list columns to replace data in
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


def main():
    database = "./encodings.db"
    # create a database connection
    conn = create_connection(database)
    create_table(conn, sql_create_photos_table())
    create_table(conn, sql_create_faces_table())

  
    with conn:
        photo_entry = ('bubble', 'bubble_en', 'bubble_perm', 'bubble_mod', 'bubble_owner',
                       'bubble_creator', 'bubble_creation_date', 'bubble_color_format',
                       'bubble_has_a_face', 'bubble_RASTER_format', 'bubble_face_detection')
        create_photo(conn, photo_entry)
        create_face(conn, ('bubble_en',2,'face', 'face', 'face')) 
        update_table(conn, 'photos', ['file_ref_of_numpy_array', 'file_ref_encoding', 
                                      'file_permissions'], ('bubble1', 'bubble1_en', 'bubble1_perm'), None)
        delete_photo_entry(conn, ('bubble1'))

        photo_entry1 = ('bubble3', 'bubble3_en', 'bubble_perm', 'bubble_mod', 'bubble_owner',
                       'bubble_creator', 'bubble4_creation_date', 'bubble4_color_format',
                       'bubble_has_a_face', 'bubble_RASTER_format', 'bubble_face_detection')
        create_photo(conn, photo_entry1)

        update_table(conn, 'photos', ['file_ref_of_numpy_array', 'file_ref_encoding', 
                                      'file_permissions'], ('bubble2', 'bubble2_en', 'bubble2_perm', 'bubble3' ),
                     'file_ref_of_numpy_array')
        drop_table(conn, 'faces')
       
    conn.close()

if __name__ == '__main__':
    main()
