from pymongo import *
import gridfs
from bson.objectid import ObjectId
import os

db = MongoClient().photoproject1
fs = gridfs.GridFS(db)

'''
for x in os.listdir('./faces/nonclustered/'):
    file1 = open('./faces/nonclustered/'+x,'rb')
    a = fs.put(file1,filename=x)
'''

for grid_out in fs.list():
    for demo in fs.find({"filename": grid_out}):
        a = open(grid_out,'wb')
        a.write(demo.read())
        a.close()
    print (grid_out)
'''z = fs.get(a)

print (z.upload_date)

k = open('abc.jpg','wb')
k.write(z.read())
k.close()'''
