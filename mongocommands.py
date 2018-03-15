from pymongo import *
import gridfs,os

mongo = "10.146.187.41"
def send_file_mongo(fileloc,filename,database):
    global mongo
    db = MongoClient(mongo, 27017)[database]
    fs = gridfs.GridFS(db)
    try:
        if filename in list_directory_mongo(database):
            print ("File Exists")
        else:
            file_to_send = open(fileloc,'rb')
            fs.put(file_to_send,filename=filename)
            return True
    except:
        print ("Error 101")

def list_directory_mongo(database):
        global mongo
    #try:
        db = MongoClient(mongo, 27017)[database]
        fs = gridfs.GridFS(db)
        return (fs.list())
    #except:
        print ("Error 102")

def get_file_mongo(filename,database):
    global mongo
    try:
        db = MongoClient(mongo, 27017)[database]
        fs = gridfs.GridFS(db)
        for demo in fs.find({"filename": filename}):
            a = open(filename,'wb')
            a.write(demo.read())
            a.close()
        return True
    except:
        print ("Error 103")

def send_all_images_mongo(foldername, database):
    try:
        for x in os.listdir('./'+foldername+'/'):
            if x != '.DS_Store':
                send_file_mongo('./'+foldername+'/'+x,x,database)
        return True
    except:
        print ("Error 104")


#send_file_mongo('IMG_1222.JPG','IMG_1222.JPG','photoproject')
#print (list_directory_mongo('photoproject'))
#get_file_mongo('IMG_1222.JPG','photoproject')
#send_all_images_mongo('pictures','photoproject')