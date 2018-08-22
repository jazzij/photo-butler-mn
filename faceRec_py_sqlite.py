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

##############################
# sql_create_table statements
#############################
def sql_create_photos_table ():
    return """ CREATE TABLE IF NOT EXISTS photos (
                    photo_id integer PRIMARY KEY,
                    file_ref_of_numpy_array text, 
                    file_ref_encoding text,                  
                    permissions text,
                    modification_date text,
                    owner text,
                    creator text,
                    creation_date text,              
                    color_format text,
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
                  UNIQUE (photo_id, position_of_face_in_image),
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

    """
    INSERT new data entry INTO photos table
    :param conn: Connection object
    :param photo_entry: new photo data
    :return: reference to new data entry
    """
    sql = ''' INSERT INTO photos (photo_id, file_ref_of_numpy_array, file_ref_encoding, 
                                  permissions, modification_date, owner, creator, 
                                  creation_date, color_format, has_a_face, faces_detected, 
                                  RASTER_format, face_detection_model)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, photo_entry)
    return cur.lastrowid


def create_face(conn, face_entry):
    """ 
    INSERT new data entry INTO faces table
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
    """
    INSERT new data entry INTO distances table
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
    """
    Delete a photo by primary key value
    :param conn:  Connection to the SQLite database
    :param id: primary key of the photo
    :return:
    """
    sql = 'DELETE FROM photos WHERE photo_id =? '
    cur = conn.cursor()
    cur.execute(sql, (photo_id,))

def delete_face_entry(conn, photo_id, position_of_face_in_image):
    """
    Delete a face by primary key value
    :param conn:  Connection to the SQLite database
    :param photo_id: photo designation
    :param position_of_face_in_image: the index of this face's encoding  
    :return:
    """
    sql = 'DELETE FROM faces WHERE photo_id =? AND position_of_face_in_image=?'
    cur = conn.cursor()
    cur.execute(sql, (photo_id, position_of_face_in_image))

def delete_distance_entry(conn, A_id, B_id):
    """
    Delete a face by primary key value
    :param conn:  Connection object to the database
    :param A_id: face designation
    :param B_id: face designation 
    :return:
    """
    sql = 'DELETE FROM faces WHERE photo_id =? AND position_of_face_in_image=?'
    cur = conn.cursor()
    cur.execute(sql, (A_id, B_id))


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
# interface, definitely a manageble one if you already know SQL. I don't think you
# need to create this interface yourself. 
####################################################################################

######################
# update table values
#####################

def update_table(conn, table, update_keys, values, location):
    """
    update values in a table
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

def main():
    database = "./encodings.db"
    # create a database connection
    conn = create_connection(database)
    create_table(conn, sql_create_photos_table())
    create_table(conn, sql_create_faces_table())
    create_table(conn, sql_create_distances_table())
    
    photo_entry = ('bubble', 'bubble_en', 'bubble_perm', 'bubble_mod', 'bubble_owner',
                       'bubble_creator', 'bubble_creation_date', 'bubble_color_format',
                       'bubble_has_a_face', 2, 'bble_RASTER_format', 'bubble_face_detection')

    photo_entry1 = ( 'bubble3', 'bubble3_en', 'bubble_perm', 'bubble_mod', 'bubble_owner',
                       'bubble_creator', 'bubble4_creation_date', 'bubble4_color_format',
                       'bubble_has_a_face', 0, 'bubble_RASTER_format', 'bubble_face_detection')
    face_entry = (1, 1, 1, 'face')
    face_entry1 = (2,2, 1, 'face1')

    distance = (1 , 2, 0.5)

    with conn:
        create_photo(conn, photo_entry)
        create_photo(conn, photo_entry1)
        create_face(conn, face_entry)
        create_face(conn, face_entry1)
        create_distance(conn, distance)
        delete_photo_entry(conn, 1)
    
    conn.close()

if __name__ == '__main__':
    main()
