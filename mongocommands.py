from pymongo import *
import gridfs,os
from PIL import Image
import PIL

mongo = "10.146.140.197"
def send_file_mongo(fileloc,filename,database,quality=100):
    global mongo
    db = MongoClient(mongo, 27017)[database]
    fs = gridfs.GridFS(db)
    try:
        if filename in list_directory_mongo(database):
            print ("File Exists")
        else:
            if quality!=100:
                foo = Image.open(fileloc)
                basewidth = 1080
                wpercent = (basewidth / float(foo.size[0]))
                hsize = int((float(foo.size[1]) * float(wpercent)))
                foo = foo.resize((basewidth, hsize), Image.ANTIALIAS)
                foo.save(fileloc,optimize=True)
            file_to_send = open(fileloc,'rb')
            fs.put(file_to_send,filename=filename)
            return True
    except Exception as e:
        print e
        print ("Error 101")

def list_directory_mongo(database):
    global mongo
    try:
        db = MongoClient(mongo, 27017)[database]
        fs = gridfs.GridFS(db)
        return (fs.list())
    except:
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
                send_file_mongo('./'+foldername+'/'+x,x,database,50)
        return True
    except Exception as e:
        print e
        print ("Error 104")


#send_file_mongo('IMG_1222.JPG','IMG_1222.JPG','photoproject')
#print (list_directory_mongo('photoproject'))
#get_file_mongo('IMG_1222.JPG','photoproject')
#send_all_images_mongo('pictures','photoproject')