import os
import time
def timeline():
    result = []
    for i in os.listdir():
        file_info = os.stat(i)
        timeData = time.localtime(file_info.st_ctime)
        readableTime = time.ctime(file_info.st_ctime)
        tupleData = (timeData,i,readableTime)
        result.append(tupleData)
    ordered_result = sorted(result)
    for j in fin_res:
        print(str(j[-2])+" "+str(j[-1]))
