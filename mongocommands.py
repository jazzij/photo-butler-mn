# Import Statements
from pymongo import *
import gridfs,os
from PIL import Image
import PIL
from tqdm import tqdm

# ---------------------------------------------------#

mongo = "10.144.214.83"            # IP Address of MongoDB Host

# ---------------------------------------------------#

# Sending Image Files to MongoDB

def send_file_mongo(fileloc,filename,database):
    
    global mongo
    db = MongoClient(mongo, 27017)[database]
    fs = gridfs.GridFS(db)
    
    try:
    
        if filename in list_directory_mongo(database):
            print ("File Exists")
    
        else:
            
            if filename.split('.')[-1].lower()=='jpg' or filename.split('.')[-1].lower()=='jpeg' or filename.split('.')[-1].lower()=='png':
                foo = Image.open(fileloc)
                basewidth = 1500
                wpercent = (basewidth / float(foo.size[0]))
                hsize = int((float(foo.size[1]) * float(wpercent)))
                foo = foo.resize((basewidth, hsize), Image.ANTIALIAS)
                foo.save(fileloc,optimize=True)

            file_to_send = open(fileloc,'rb')
            fs.put(file_to_send,filename=filename)
            return True

    except Exception as e:
    
        print (e)
        print ("Error 101")

# ---------------------------------------------------#

# List filenames in a  Mongo DB

def list_directory_mongo(database):
    
    global mongo
    
    try:
        db = MongoClient(mongo, 27017)[database]
        fs = gridfs.GridFS(db)
        return (fs.list())
    
    except Exception as e:
    
        print (e)
        print ("Error 102")

# ---------------------------------------------------#

# Get file from Mongo DB

def get_file_mongo(filename,database,foldertowrite=""):
    
    global mongo
    
    try:
        db = MongoClient(mongo, 27017)[database]
        fs = gridfs.GridFS(db)
        for demo in fs.find({"filename": filename}):
            a = open(foldertowrite+filename,'wb')
            a.write(demo.read())
            a.close()
        return True
        
    except Exception as e:
        print (e)
        print ("Error 103")

# ---------------------------------------------------#

# Send all files from a folder to Mongo DB

def send_all_images_mongo(foldername, database):
    
    try:
        for x in tqdm(os.listdir('./'+foldername+'/')):
            if x != '.DS_Store':
                send_file_mongo('./'+foldername+'/'+x,x,database)
        return True

    except Exception as e:
        print (e)
        print ("Error 104")
        
# ---------------------------------------------------#

# Send all files from a folder to Mongo DB

def get_all_images_mongo(foldername, database):
    try:
        for x in tqdm(list_directory_mongo(database)):
            if x != '.DS_Store':
                get_file_mongo(x,database,foldername)
        return True

    except Exception as e:
        print (e)
        print ("Error 105")
        
# ---------------------------------------------------#

